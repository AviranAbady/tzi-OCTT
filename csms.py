"""
CSMS (Charging Station Management System) implementation for OCPP 2.0.1 test suite.

Note: This CSMS is intended solely for testing, debugging, and stepping through
the tzi-octt test suite. It must NOT be used in production.

Written entirely by Claude Code, the magnificent.

Runs two servers:
  - WS  on port 9000 (Security Profile 1: Basic Auth, no TLS)
  - WSS on port 8082 (Security Profile 2: TLS + Basic Auth, Profile 3: mTLS)

Usage:
  python csms.py [test_mode]

  Examples:
    python csms.py                         # Auto-detect mode (handles all A tests)
    python csms.py password_update         # TC_A_09, A_10
    python csms.py clear_cache             # TC_C_37, C_38
    python csms.py send_local_list_full    # TC_D_01

Test mode configuration (three options, can be combined):

  1. CLI argument (first positional arg):
       python csms.py <test_mode>

  2. Global mode via CSMS_TEST_MODE env var (applies to all CPs):
       CSMS_TEST_MODE=password_update python csms.py

  3. Per-CP mode via CSMS_CP_ACTIONS env var (JSON mapping, takes precedence):
       CSMS_CP_ACTIONS='{"CP001": "password_update"}' python csms.py

  Priority: Per-CP actions > CLI arg / env var.

  When no test mode is set, the CSMS uses auto-detection:
    - Waits briefly after connection to see if CP sends BootNotification
    - If boot is received: no proactive action (quiet connection)
    - If no boot: determines action based on security profile and
      connection sequence (password_update, cert_renewal, profile_upgrade)

Available test modes:
  ""                          Auto-detect / reactive
  "password_update"           SetVariables(BasicAuthPassword)         (TC_A_09, A_10)
  "cert_renewal_cs"           TriggerMessage(SignCSCertificate)       (TC_A_11, A_14)
  "cert_renewal_v2g"          TriggerMessage(SignV2GCertificate)      (TC_A_12)
  "cert_renewal_combined"     TriggerMessage(SignCombinedCertificate) (TC_A_13)
  "profile_upgrade"           SetNetworkProfile + SetVariables + Reset(TC_A_19)
  "clear_cache"               ClearCacheRequest                      (TC_C_37, C_38)
  "get_local_list_version"    GetLocalListVersionRequest              (TC_D_08, D_09)
  "send_local_list_full"      SendLocalList(Full, with entries)       (TC_D_01)
  "send_local_list_diff_update" SendLocalList(Differential, add)      (TC_D_02)
  "send_local_list_diff_remove" SendLocalList(Differential, remove)   (TC_D_03)
  "send_local_list_full_empty"  SendLocalList(Full, empty)            (TC_D_04)

Reactive handlers (always active, no test mode needed):
  - BootNotification, StatusNotification, NotifyEvent, Heartbeat
  - SignCertificate -> CertificateSigned
  - SecurityEventNotification
  - Authorize (token lookup from TOKEN_DATABASE)
  - TransactionEvent (token lookup if id_token present)

Token database:
  Hardcoded token entries used by Authorize/TransactionEvent handlers.
  Override group via VALID_TOKEN_GROUP / MASTERPASS_GROUP_ID env vars.

Actions fire only once per CP (except profile_upgrade which uses a state machine).
"""

import asyncio
import json
import logging
import sys
import websockets
import ssl
import base64
import http
import os
from datetime import datetime, timedelta, timezone

from ocpp.routing import on
from ocpp.v201 import ChargePoint, call, call_result
from ocpp.v201.enums import Action, GenericStatusEnumType
from ocpp.v201.enums import RegistrationStatusEnumType
from websockets import ConnectionClosedOK

try:
    from ocpp.exceptions import SecurityError as OCPPSecurityError
except ImportError:
    from ocpp.exceptions import OCPPError
    class OCPPSecurityError(OCPPError):
        code = 'SecurityError'
        default_description = 'Not authorized'

from utils import now_iso

logging.basicConfig(level=logging.INFO)

# ─── Configuration ───────────────────────────────────────────────────────────

BASIC_AUTH_CP_PASSWORD = os.environ.get('BASIC_AUTH_CP_PASSWORD', '0123456789123456')
NEW_BASIC_AUTH_PASSWORD = os.environ.get('NEW_BASIC_AUTH_PASSWORD', 'new_password_12345678')
WS_PORT = int(os.environ.get('CSMS_WS_PORT', '9000'))
WSS_PORT = int(os.environ.get('CSMS_WSS_PORT', '8082'))
TEST_MODE = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('CSMS_TEST_MODE', '')

# Per-CP action mapping (JSON). Takes precedence over global TEST_MODE.
# Example: '{"CP001": "password_update", "SP3_CP": "cert_renewal_cs"}'
_cp_actions_raw = os.environ.get('CSMS_CP_ACTIONS', '')
CP_ACTIONS = json.loads(_cp_actions_raw) if _cp_actions_raw else {}

# TLS paths (server-side)
SERVER_CERT = os.environ.get('CSMS_SERVER_CERT', 'certs/server.pem')
SERVER_KEY = os.environ.get('CSMS_SERVER_KEY', 'certs/server.key')
SERVER_RSA_CERT = os.environ.get('CSMS_SERVER_RSA_CERT', 'certs/server_rsa.pem')
SERVER_RSA_KEY = os.environ.get('CSMS_SERVER_RSA_KEY', 'certs/server_rsa.key')
CA_CERT = os.environ.get('CSMS_CA_CERT', 'certs/ca.pem')
CA_KEY_PATH = os.environ.get('CSMS_CA_KEY', 'certs/ca.key')

# Profile upgrade configuration
CSMS_WSS_URL = os.environ.get('CSMS_WSS_URL', 'wss://localhost:8082')
MESSAGE_TIMEOUT = int(os.environ.get('CSMS_MESSAGE_TIMEOUT', '30'))
OCPP_INTERFACE = os.environ.get('CSMS_OCPP_INTERFACE', 'Wired0')

# Provisioning configuration (B tests)
CONFIGURED_EVSE_ID = int(os.environ.get('CONFIGURED_EVSE_ID', '1'))
CONFIGURED_CONFIGURATION_SLOT = int(os.environ.get('CONFIGURED_CONFIGURATION_SLOT', '1'))
CONFIGURED_SECURITY_PROFILE = int(os.environ.get('CONFIGURED_SECURITY_PROFILE', '2'))
CONFIGURED_OCPP_CSMS_URL = os.environ.get('CONFIGURED_OCPP_CSMS_URL', 'wss://localhost:8082')
CONFIGURED_OCPP_INTERFACE = os.environ.get('CONFIGURED_OCPP_INTERFACE', 'Wired0')
CONFIGURED_MESSAGE_TIMEOUT_B = int(os.environ.get('CONFIGURED_MESSAGE_TIMEOUT', '30'))

# ─── Token Database ──────────────────────────────────────────────────────────

VALID_TOKEN_GROUP = os.environ.get('VALID_TOKEN_GROUP', 'GROUP001')
MASTERPASS_GROUP_ID = os.environ.get('MASTERPASS_GROUP_ID', 'MasterPassGroupId')

TOKEN_DATABASE = {
    '100000C01':       {'status': 'Accepted', 'group': VALID_TOKEN_GROUP},
    '100000C39B':      {'status': 'Accepted', 'group': VALID_TOKEN_GROUP},
    '100000C02':       {'status': 'Invalid'},
    '100000C06':       {'status': 'Blocked'},
    '100000C07':       {'status': 'Expired'},
    'MASTERC47':       {'status': 'Accepted', 'group': MASTERPASS_GROUP_ID},
    'D001001':         {'status': 'Accepted'},
    'D001002':         {'status': 'Accepted'},
    'DE-TZI-C12345-A': {'status': 'Accepted'},
}


def lookup_token(token_value):
    return TOKEN_DATABASE.get(token_value.upper(), {'status': 'Invalid'})


# ─── Global State ────────────────────────────────────────────────────────────

cp_passwords = {}                # cp_id -> current password
cp_min_security_profile = {}     # cp_id -> minimum required security profile
cp_test_state = {}               # cp_id -> test flow state (profile_upgrade)
cp_action_fired = {}             # cp_id -> set of action types already executed

# Auto-detect mode: per-(cp_id, security_profile) action counters
# Tracks how many "no-boot" connections have been handled per profile
_auto_action_counter = {}

# Auto-detect action sequences per security profile.
# These define which proactive action to perform for each successive
# "no-boot" connection (where the CP waits for CSMS-initiated action).
_AUTO_SP1_ACTIONS = ['password_update', 'password_update', 'profile_upgrade']
_AUTO_SP2_ACTIONS = ['cert_renewal_cs', 'profile_upgrade']
_AUTO_SP3_ACTIONS = [
    'cert_renewal_cs',        # TC_A_11
    'cert_renewal_v2g',       # TC_A_12
    'cert_renewal_combined',  # TC_A_13
    'cert_renewal_cs',        # TC_A_14
]

# ─── SP1 Provisioning Sequence ──────────────────────────────────────────────
# Defines the boot response and post-boot action for each successive
# BootNotification received on SP1 (WS) connections.
# Format: (boot_status, action_name_or_None)

_sp1_boot_counter = {}   # cp_id -> boot count on SP1
_auto_detect_used = False  # Set when auto-detect fires a no-boot action

_SP1_PROVISIONING = [
    # Boot/registration
    ('Accepted', None),
    ('Pending', None),
    ('Accepted', None),
    # GetVariables
    ('Accepted', 'get_variables_single'),
    ('Accepted', 'get_variables_multiple'),
    ('Accepted', 'get_variables_split'),
    # SetVariables
    ('Accepted', 'set_variables_single'),
    ('Accepted', 'set_variables_multiple'),
    # GetBaseReport
    ('Accepted', 'get_base_report_config'),
    ('Accepted', 'get_base_report_full'),
    ('Accepted', 'get_base_report_summary'),
    # GetReport with criteria
    ('Accepted', 'get_report_criteria'),
    # Reset CS
    ('Accepted', 'reset_on_idle_cs'),
    ('Accepted', None),
    ('Accepted', 'reset_on_idle_cs'),
    ('Accepted', None),
    ('Accepted', 'reset_immediate_cs'),
    ('Accepted', None),
    # Reset EVSE
    ('Accepted', 'reset_on_idle_evse'),
    ('Accepted', 'reset_on_idle_evse'),
    ('Accepted', 'reset_immediate_evse'),
    # Pending/Rejected flows
    ('Pending', None),
    ('Pending', 'trigger_boot'),
    ('Accepted', None),
    # Network profile
    ('Accepted', 'set_network_profile'),
    ('Accepted', 'set_network_profile'),
]


# ─── Per-CP Test Mode ───────────────────────────────────────────────────────

def get_test_mode_for_cp(cp_id):
    """Get the test mode for a specific charge point.
    Per-CP mapping (CSMS_CP_ACTIONS) takes precedence over global TEST_MODE.
    """
    if CP_ACTIONS:
        return CP_ACTIONS.get(cp_id, '')
    return TEST_MODE


# ─── Certificate Signing ─────────────────────────────────────────────────────

def sign_csr_with_ca(csr_pem_str):
    """Sign a CSR with our CA and return the certificate chain as PEM string."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization

    with open(CA_CERT, 'rb') as f:
        ca_cert = x509.load_pem_x509_certificate(f.read())
    with open(CA_KEY_PATH, 'rb') as f:
        ca_key = serialization.load_pem_private_key(f.read(), password=None)

    csr = x509.load_pem_x509_csr(csr_pem_str.encode())
    now = datetime.now(timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(ca_cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=365))
        .sign(ca_key, hashes.SHA256())
    )

    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    ca_pem = ca_cert.public_bytes(serialization.Encoding.PEM).decode()
    return cert_pem + ca_pem


# ─── ChargePoint Handler ─────────────────────────────────────────────────────

class ChargePointHandler(ChargePoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._boot_received = asyncio.Event()
        self._security_profile = 1
        self._boot_status = None

    @on(Action.boot_notification)
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        logging.info(f"BootNotification from {self.id}: reason={reason}")
        self._boot_received.set()

        # Determine boot response from SP1 provisioning sequence
        # (only when auto-detect no-boot actions have NOT been used,
        # i.e., this is a provisioning-focused session like B tests)
        if self._security_profile == 1 and not _auto_detect_used:
            counter = _sp1_boot_counter.get(self.id, 0)
            _sp1_boot_counter[self.id] = counter + 1

            if counter < len(_SP1_PROVISIONING):
                boot_status, action = _SP1_PROVISIONING[counter]
            else:
                boot_status, action = ('Accepted', None)

            self._boot_status = boot_status
            interval = 1 if boot_status in ('Pending', 'Rejected') else 10

            if action:
                asyncio.create_task(self._execute_provisioning(action))

            logging.info(f"SP1 provisioning boot #{counter}: {boot_status}, action={action}")
            return call_result.BootNotification(
                current_time=now_iso(),
                interval=interval,
                status=getattr(RegistrationStatusEnumType, boot_status.lower()),
            )

        # Non-SP1 boots: always Accepted
        self._boot_status = 'Accepted'
        return call_result.BootNotification(
            current_time=now_iso(),
            interval=10,
            status=RegistrationStatusEnumType.accepted
        )

    async def _execute_provisioning(self, action):
        """Execute a provisioning action after a short delay."""
        await asyncio.sleep(2)
        try:
            await _dispatch_provisioning(self, action)
        except Exception as e:
            logging.warning(f"Provisioning action '{action}' failed for {self.id}: {e}")

    @on(Action.status_notification)
    async def on_status_notification(self, **kwargs):
        if self._boot_status in ('Pending', 'Rejected'):
            logging.info(f"StatusNotification from {self.id} rejected (boot={self._boot_status})")
            raise OCPPSecurityError('Not authorized during Pending/Rejected state')
        logging.info(f"StatusNotification from {self.id}: {kwargs}")
        return call_result.StatusNotification()

    @on(Action.notify_event)
    async def on_notify_event(self, **kwargs):
        if self._boot_status in ('Pending', 'Rejected'):
            logging.info(f"NotifyEvent from {self.id} rejected (boot={self._boot_status})")
            raise OCPPSecurityError('Not authorized during Pending/Rejected state')
        logging.info(f"NotifyEvent from {self.id}")
        return call_result.NotifyEvent()

    @on(Action.heartbeat)
    async def on_heartbeat(self, **kwargs):
        return call_result.Heartbeat(current_time=now_iso())

    @on(Action.sign_certificate)
    async def on_sign_certificate(self, csr, certificate_type=None, **kwargs):
        logging.info(f"SignCertificateRequest from {self.id}: type={certificate_type}")
        asyncio.create_task(self._send_certificate_signed(csr, certificate_type))
        return call_result.SignCertificate(status=GenericStatusEnumType.accepted)

    async def _send_certificate_signed(self, csr_pem, certificate_type):
        """Sign the CSR and send CertificateSignedRequest back to the CP."""
        await asyncio.sleep(0.5)
        try:
            cert_chain = sign_csr_with_ca(csr_pem)
            logging.info(f"Sending CertificateSignedRequest to {self.id} "
                         f"(chain length={len(cert_chain)})")
            await self.call(call.CertificateSigned(
                certificate_chain=cert_chain,
                certificate_type=certificate_type,
            ))
        except Exception as e:
            logging.error(f"Failed to send CertificateSignedRequest to {self.id}: {e}")

    @on(Action.authorize)
    async def on_authorize(self, id_token, certificate=None,
                           iso15118_certificate_hash_data=None, **kwargs):
        token_value = id_token.get('id_token', '') if isinstance(id_token, dict) else str(id_token)
        token_info = lookup_token(token_value)
        logging.info(f"Authorize from {self.id}: token={token_value} -> {token_info['status']}")

        id_token_info = {'status': token_info['status']}
        if 'group' in token_info:
            id_token_info['group_id_token'] = {
                'id_token': token_info['group'], 'type': 'Central'
            }

        response_kwargs = {'id_token_info': id_token_info}

        if iso15118_certificate_hash_data or certificate:
            response_kwargs['certificate_status'] = 'Accepted'

        return call_result.Authorize(**response_kwargs)

    @on(Action.transaction_event)
    async def on_transaction_event(self, event_type, timestamp, trigger_reason,
                                   seq_no, transaction_info, id_token=None,
                                   evse=None, **kwargs):
        response_kwargs = {}
        if id_token:
            token_value = (id_token.get('id_token', '')
                           if isinstance(id_token, dict) else str(id_token))
            token_info = lookup_token(token_value)
            logging.info(f"TransactionEvent from {self.id}: token={token_value} -> {token_info['status']}")
            id_token_info = {'status': token_info['status']}
            if 'group' in token_info:
                id_token_info['group_id_token'] = {
                    'id_token': token_info['group'], 'type': 'Central'
                }
            response_kwargs['id_token_info'] = id_token_info
        else:
            logging.info(f"TransactionEvent from {self.id}: type={event_type} trigger={trigger_reason}")
        return call_result.TransactionEvent(**response_kwargs)

    @on(Action.notify_report)
    async def on_notify_report(self, request_id, generated_at, seq_no, tbc=False,
                                report_data=None, **kwargs):
        logging.info(f"NotifyReport from {self.id}: request_id={request_id}, seq_no={seq_no}")
        return call_result.NotifyReport()

    @on(Action.security_event_notification)
    async def on_security_event_notification(self, type, timestamp, **kwargs):
        logging.info(f"SecurityEventNotification from {self.id}: type={type}")
        return call_result.SecurityEventNotification()


# ─── Provisioning Actions (SP1 post-boot) ────────────────────────────────────

_prov_request_id = 0

def _next_request_id():
    global _prov_request_id
    _prov_request_id += 1
    return _prov_request_id


async def _dispatch_provisioning(cp, action):
    """Dispatch a provisioning action by name."""
    dispatch = {
        'get_variables_single': _prov_get_variables_single,
        'get_variables_multiple': _prov_get_variables_multiple,
        'get_variables_split': _prov_get_variables_split,
        'set_variables_single': _prov_set_variables_single,
        'set_variables_multiple': _prov_set_variables_multiple,
        'get_base_report_config': lambda cp: _prov_get_base_report(cp, 'ConfigurationInventory'),
        'get_base_report_full': lambda cp: _prov_get_base_report(cp, 'FullInventory'),
        'get_base_report_summary': lambda cp: _prov_get_base_report(cp, 'SummaryInventory'),
        'get_report_criteria': _prov_get_report_criteria,
        'reset_on_idle_cs': lambda cp: _prov_reset(cp, 'OnIdle', None),
        'reset_immediate_cs': lambda cp: _prov_reset(cp, 'Immediate', None),
        'reset_on_idle_evse': lambda cp: _prov_reset(cp, 'OnIdle', CONFIGURED_EVSE_ID),
        'reset_immediate_evse': lambda cp: _prov_reset(cp, 'Immediate', CONFIGURED_EVSE_ID),
        'trigger_boot': _prov_trigger_boot,
        'set_network_profile': _prov_set_network_profile,
    }
    handler = dispatch.get(action)
    if handler:
        await handler(cp)
    else:
        logging.warning(f"Unknown provisioning action: {action}")


async def _prov_get_variables_single(cp):
    logging.info(f"Provisioning: GetVariables(single) for {cp.id}")
    await cp.call(call.GetVariables(get_variable_data=[
        {'component': {'name': 'OCPPCommCtrlr'}, 'variable': {'name': 'OfflineThreshold'}},
    ]))


async def _prov_get_variables_multiple(cp):
    logging.info(f"Provisioning: GetVariables(multiple) for {cp.id}")
    await cp.call(call.GetVariables(get_variable_data=[
        {'component': {'name': 'OCPPCommCtrlr'}, 'variable': {'name': 'OfflineThreshold'}},
        {'component': {'name': 'AuthCtrlr'}, 'variable': {'name': 'AuthorizeRemoteStart'}},
    ]))


async def _prov_get_variables_split(cp):
    logging.info(f"Provisioning: GetVariables(split 4+1) for {cp.id}")
    await cp.call(call.GetVariables(get_variable_data=[
        {'component': {'name': 'DeviceDataCtrlr'}, 'variable': {'name': 'ItemsPerMessage', 'instance': 'GetReport'}},
        {'component': {'name': 'DeviceDataCtrlr'}, 'variable': {'name': 'ItemsPerMessage', 'instance': 'GetVariables'}},
        {'component': {'name': 'DeviceDataCtrlr'}, 'variable': {'name': 'BytesPerMessage', 'instance': 'GetReport'}},
        {'component': {'name': 'DeviceDataCtrlr'}, 'variable': {'name': 'BytesPerMessage', 'instance': 'GetVariables'}},
    ]))
    await asyncio.sleep(0.5)
    await cp.call(call.GetVariables(get_variable_data=[
        {'component': {'name': 'AuthCtrlr'}, 'variable': {'name': 'AuthorizeRemoteStart'}},
    ]))


async def _prov_set_variables_single(cp):
    logging.info(f"Provisioning: SetVariables(single) for {cp.id}")
    await cp.call(call.SetVariables(set_variable_data=[{
        'component': {'name': 'OCPPCommCtrlr'},
        'variable': {'name': 'OfflineThreshold'},
        'attribute_value': '123',
    }]))


async def _prov_set_variables_multiple(cp):
    logging.info(f"Provisioning: SetVariables(multiple) for {cp.id}")
    await cp.call(call.SetVariables(set_variable_data=[
        {
            'component': {'name': 'OCPPCommCtrlr'},
            'variable': {'name': 'OfflineThreshold'},
            'attribute_value': '123',
        },
        {
            'component': {'name': 'AuthCtrlr'},
            'variable': {'name': 'AuthorizeRemoteStart'},
            'attribute_value': 'false',
        },
    ]))


async def _prov_get_base_report(cp, report_base):
    logging.info(f"Provisioning: GetBaseReport({report_base}) for {cp.id}")
    await cp.call(call.GetBaseReport(
        request_id=_next_request_id(),
        report_base=report_base,
    ))


async def _prov_get_report_criteria(cp):
    logging.info(f"Provisioning: GetReport(Problem then Available) for {cp.id}")
    evse_id = CONFIGURED_EVSE_ID
    cv = [{'component': {'name': 'EVSE', 'evse': {'id': evse_id}},
           'variable': {'name': 'AvailabilityState'}}]

    await cp.call(call.GetReport(
        request_id=_next_request_id(),
        component_criteria=['Problem'],
        component_variable=cv,
    ))
    await asyncio.sleep(0.5)
    await cp.call(call.GetReport(
        request_id=_next_request_id(),
        component_criteria=['Available'],
        component_variable=cv,
    ))


async def _prov_reset(cp, reset_type, evse_id):
    logging.info(f"Provisioning: Reset({reset_type}, evse_id={evse_id}) for {cp.id}")
    kwargs = {'type': reset_type}
    if evse_id is not None:
        kwargs['evse_id'] = evse_id
    try:
        await asyncio.wait_for(cp.call(call.Reset(**kwargs)), timeout=10)
    except (asyncio.TimeoutError, Exception) as e:
        logging.warning(f"Reset call did not complete for {cp.id}: {e}")


async def _prov_trigger_boot(cp):
    logging.info(f"Provisioning: TriggerMessage(BootNotification) for {cp.id}")
    await cp.call(call.TriggerMessage(requested_message='BootNotification'))


async def _prov_set_network_profile(cp):
    logging.info(f"Provisioning: SetNetworkProfile for {cp.id}")
    await cp.call(call.SetNetworkProfile(
        configuration_slot=CONFIGURED_CONFIGURATION_SLOT,
        connection_data={
            'ocpp_version': 'OCPP20',
            'ocpp_transport': 'JSON',
            'ocpp_csms_url': CONFIGURED_OCPP_CSMS_URL,
            'message_timeout': CONFIGURED_MESSAGE_TIMEOUT_B,
            'security_profile': CONFIGURED_SECURITY_PROFILE,
            'ocpp_interface': CONFIGURED_OCPP_INTERFACE,
        },
    ))


# ─── Test Mode Actions ───────────────────────────────────────────────────────

async def execute_test_mode_actions(cp, security_profile):
    """Execute CSMS-initiated actions based on the CP's configured test mode.

    Actions fire only once per CP to prevent re-triggering on reconnections
    (e.g., TC_A_09 reconnects with new password, TC_A_11 reconnects with new cert).
    Profile upgrade uses its own state machine for multi-step flows.
    """
    await asyncio.sleep(1)

    test_mode = get_test_mode_for_cp(cp.id)
    if not test_mode:
        return

    fired = cp_action_fired.get(cp.id, set())

    try:
        if test_mode == 'password_update':
            if 'password_update' not in fired:
                await _action_password_update(cp)
                cp_action_fired.setdefault(cp.id, set()).add('password_update')

        elif test_mode in ('cert_renewal_cs', 'cert_renewal_v2g', 'cert_renewal_combined'):
            if test_mode not in fired:
                trigger_map = {
                    'cert_renewal_cs': 'SignChargingStationCertificate',
                    'cert_renewal_v2g': 'SignV2GCertificate',
                    'cert_renewal_combined': 'SignCombinedCertificate',
                }
                await _action_trigger_cert_renewal(cp, trigger_map[test_mode])
                cp_action_fired.setdefault(cp.id, set()).add(test_mode)

        elif test_mode == 'profile_upgrade':
            await _action_profile_upgrade(cp, security_profile)

        elif test_mode == 'clear_cache':
            if 'clear_cache' not in fired:
                await _action_clear_cache(cp)
                cp_action_fired.setdefault(cp.id, set()).add('clear_cache')

        elif test_mode == 'get_local_list_version':
            if 'get_local_list_version' not in fired:
                await _action_get_local_list_version(cp)
                cp_action_fired.setdefault(cp.id, set()).add('get_local_list_version')

        elif test_mode == 'send_local_list_full':
            if 'send_local_list_full' not in fired:
                await _action_send_local_list_full(cp)
                cp_action_fired.setdefault(cp.id, set()).add('send_local_list_full')

        elif test_mode == 'send_local_list_diff_update':
            if 'send_local_list_diff_update' not in fired:
                await _action_send_local_list_diff_update(cp)
                cp_action_fired.setdefault(cp.id, set()).add('send_local_list_diff_update')

        elif test_mode == 'send_local_list_diff_remove':
            if 'send_local_list_diff_remove' not in fired:
                await _action_send_local_list_diff_remove(cp)
                cp_action_fired.setdefault(cp.id, set()).add('send_local_list_diff_remove')

        elif test_mode == 'send_local_list_full_empty':
            if 'send_local_list_full_empty' not in fired:
                await _action_send_local_list_full_empty(cp)
                cp_action_fired.setdefault(cp.id, set()).add('send_local_list_full_empty')

    except Exception as e:
        logging.error(f"Test mode action failed for {cp.id}: {e}")


# ─── Auto-Detect Actions ─────────────────────────────────────────────────────

async def auto_detect_and_execute(cp, security_profile):
    """Auto-detect whether the CP is waiting for a CSMS-initiated action.

    Strategy: wait briefly after connection. If BootNotification is received,
    this is a "quiet" connection (tests like A_01, A_04, A_07, A_08). If no
    boot is received AND the connection is still open, the CP is waiting for
    a proactive CSMS action (tests like A_09, A_11, A_19).

    The specific action is determined by the security profile and a per-profile
    connection counter that maps to a predefined action sequence.
    """
    # Wait to see if CP sends BootNotification
    try:
        await asyncio.wait_for(cp._boot_received.wait(), timeout=1.5)
        # Boot received - quiet connection, no proactive action needed
        logging.info(f"Auto-detect: boot received from {cp.id} (SP{security_profile}) - no action")
        return
    except asyncio.TimeoutError:
        pass

    # Check if the connection is still alive (short-lived connections like
    # cipher tests or quick connect/close should be skipped)
    if not cp._connection.open:
        logging.info(f"Auto-detect: connection already closed for {cp.id} - skipping")
        return

    # Determine which action to perform based on security profile and counter
    key = (cp.id, security_profile)
    counter = _auto_action_counter.get(key, 0)

    if security_profile == 1:
        actions = _AUTO_SP1_ACTIONS
    elif security_profile == 2:
        actions = _AUTO_SP2_ACTIONS
    else:
        actions = _AUTO_SP3_ACTIONS

    if counter >= len(actions):
        logging.info(f"Auto-detect: no more actions for {cp.id} SP{security_profile} "
                     f"(counter={counter})")
        return

    action = actions[counter]
    _auto_action_counter[key] = counter + 1

    global _auto_detect_used
    _auto_detect_used = True

    logging.info(f"Auto-detect: {cp.id} SP{security_profile} action #{counter} -> {action}")

    try:
        await _execute_auto_action(cp, action, security_profile)
    except Exception as e:
        logging.error(f"Auto-detect action failed for {cp.id}: {e}")


async def _execute_auto_action(cp, action, security_profile):
    """Execute a specific auto-detected action."""
    trigger_map = {
        'cert_renewal_cs': 'SignChargingStationCertificate',
        'cert_renewal_v2g': 'SignV2GCertificate',
        'cert_renewal_combined': 'SignCombinedCertificate',
    }

    if action == 'password_update':
        await _action_password_update(cp)

    elif action in trigger_map:
        await _action_trigger_cert_renewal(cp, trigger_map[action])
        # Mark state as cert_renewed so profile_upgrade can skip cert step
        cp_test_state[cp.id] = 'cert_renewed'

    elif action == 'profile_upgrade':
        await _action_profile_upgrade(cp, security_profile)


async def _action_password_update(cp):
    """TC_A_09/A_10: Send SetVariablesRequest to change BasicAuthPassword.

    Pre-sets the new password before sending so it's accepted for reconnection
    even if cp.call() doesn't complete (test may close the connection after
    receiving the request). Since _check_password accepts both old and new
    passwords, this is safe regardless of whether the CP accepts or rejects.
    """
    new_password = NEW_BASIC_AUTH_PASSWORD
    # Pre-set so reconnection with new password works even if cp.call() hangs
    cp_passwords[cp.id] = new_password
    logging.info(f"Sending SetVariablesRequest(BasicAuthPassword) to {cp.id}")

    try:
        response = await asyncio.wait_for(
            cp.call(call.SetVariables(
                set_variable_data=[{
                    'component': {'name': 'SecurityCtrlr'},
                    'variable': {'name': 'BasicAuthPassword'},
                    'attribute_value': new_password,
                }]
            )),
            timeout=10,
        )

        if response.set_variable_result:
            for result in response.set_variable_result:
                status = result.get('attribute_status', '') if isinstance(result, dict) \
                    else str(getattr(result, 'attribute_status', ''))
                if 'accepted' in str(status).lower():
                    logging.info(f"Password updated for {cp.id}")
                else:
                    logging.info(f"Password update rejected for {cp.id} (status={status})")
    except (asyncio.TimeoutError, Exception) as e:
        logging.warning(f"Password update cp.call did not complete for {cp.id}: {e}")


async def _action_trigger_cert_renewal(cp, trigger_type):
    """TC_A_11-14: Send TriggerMessageRequest to initiate certificate renewal.
    The CP will respond, then send SignCertificateRequest which is handled
    by on_sign_certificate -> _send_certificate_signed.
    """
    logging.info(f"Sending TriggerMessageRequest({trigger_type}) to {cp.id}")
    try:
        response = await asyncio.wait_for(
            cp.call(call.TriggerMessage(requested_message=trigger_type)),
            timeout=10,
        )
        logging.info(f"TriggerMessageResponse from {cp.id}: {response}")
    except (asyncio.TimeoutError, Exception) as e:
        logging.warning(f"TriggerMessage cp.call did not complete for {cp.id}: {e}")


async def _action_profile_upgrade(cp, security_profile):
    """TC_A_19: Upgrade security profile.
    For SP2->SP3: first connection does cert renewal, second does upgrade.
    For SP1->SP2: first connection does upgrade directly.
    """
    state = cp_test_state.get(cp.id, 'initial')

    if state == 'initial' and security_profile == 2:
        # SP2 -> SP3: Need cert renewal first (Memory State)
        logging.info(f"Profile upgrade: cert renewal phase for {cp.id}")
        await _action_trigger_cert_renewal(cp, 'SignChargingStationCertificate')
        cp_test_state[cp.id] = 'cert_renewed'
    elif state in ('initial', 'cert_renewed'):
        # Ready for the actual profile upgrade
        await _action_send_profile_upgrade(cp, security_profile)
    else:
        logging.info(f"Profile upgrade: no action for {cp.id} (state={state})")


async def _action_send_profile_upgrade(cp, current_sp):
    """Send SetNetworkProfile + SetVariables + Reset for profile upgrade.

    Sets cp_min_security_profile BEFORE sending Reset because the test
    closes the connection immediately after receiving Reset (simulating reboot),
    so cp.call(Reset) may not receive the response.
    """
    new_sp = current_sp + 1
    if new_sp > 3:
        logging.info(f"Profile upgrade: already at SP{current_sp}, cannot upgrade beyond SP3")
        cp_test_state[cp.id] = 'upgraded'
        return
    slot = 1

    # Step 1: SetNetworkProfileRequest
    logging.info(f"Sending SetNetworkProfileRequest(SP{new_sp}) to {cp.id}")
    await cp.call(call.SetNetworkProfile(
        configuration_slot=slot,
        connection_data={
            'ocpp_version': 'OCPP20',
            'ocpp_transport': 'JSON',
            'ocpp_csms_url': CSMS_WSS_URL,
            'message_timeout': MESSAGE_TIMEOUT,
            'security_profile': new_sp,
            'ocpp_interface': OCPP_INTERFACE,
        }
    ))

    # Step 3: SetVariablesRequest(NetworkConfigurationPriority)
    logging.info(f"Sending SetVariablesRequest(NetworkConfigurationPriority={slot}) to {cp.id}")
    await cp.call(call.SetVariables(
        set_variable_data=[{
            'component': {'name': 'OCPPCommCtrlr'},
            'variable': {'name': 'NetworkConfigurationPriority'},
            'attribute_value': str(slot),
        }]
    ))

    # Pre-set security profile BEFORE Reset: the test closes the connection
    # immediately after receiving Reset (simulating reboot), so cp.call(Reset)
    # may never receive the response.
    cp_min_security_profile[cp.id] = new_sp
    cp_test_state[cp.id] = 'upgraded'
    logging.info(f"Minimum security profile for {cp.id} set to {new_sp}")

    # Step 5: ResetRequest (response may not arrive - test closes connection)
    logging.info(f"Sending ResetRequest to {cp.id}")
    try:
        await asyncio.wait_for(
            cp.call(call.Reset(type='Immediate')),
            timeout=10,
        )
    except (asyncio.TimeoutError, Exception) as e:
        logging.warning(f"Reset cp.call did not complete for {cp.id}: {e}")


async def _action_clear_cache(cp):
    """TC_C_37, TC_C_38: Send ClearCacheRequest."""
    logging.info(f"Sending ClearCacheRequest to {cp.id}")
    response = await cp.call(call.ClearCache())
    logging.info(f"ClearCacheResponse from {cp.id}: {response}")


async def _action_get_local_list_version(cp):
    """TC_D_08, TC_D_09: Send GetLocalListVersionRequest."""
    logging.info(f"Sending GetLocalListVersionRequest to {cp.id}")
    response = await cp.call(call.GetLocalListVersion())
    logging.info(f"GetLocalListVersionResponse from {cp.id}: {response}")


async def _action_send_local_list_full(cp):
    """TC_D_01: Send SendLocalListRequest with updateType=Full, non-empty list."""
    logging.info(f"Sending SendLocalListRequest(Full) to {cp.id}")
    response = await cp.call(call.SendLocalList(
        version_number=1,
        update_type='Full',
        local_authorization_list=[
            {
                'id_token': {'id_token': 'D001001', 'type': 'Central'},
                'id_token_info': {'status': 'Accepted'},
            },
            {
                'id_token': {'id_token': 'D001002', 'type': 'Central'},
                'id_token_info': {'status': 'Accepted'},
            },
        ]
    ))
    logging.info(f"SendLocalListResponse from {cp.id}: {response}")


async def _action_send_local_list_diff_update(cp):
    """TC_D_02: Send SendLocalListRequest with updateType=Differential, add entries."""
    logging.info(f"Sending SendLocalListRequest(Differential, add) to {cp.id}")
    response = await cp.call(call.SendLocalList(
        version_number=2,
        update_type='Differential',
        local_authorization_list=[
            {
                'id_token': {'id_token': 'D001001', 'type': 'Central'},
                'id_token_info': {'status': 'Accepted'},
            },
        ]
    ))
    logging.info(f"SendLocalListResponse from {cp.id}: {response}")


async def _action_send_local_list_diff_remove(cp):
    """TC_D_03: Send SendLocalListRequest with updateType=Differential, remove entries."""
    logging.info(f"Sending SendLocalListRequest(Differential, remove) to {cp.id}")
    response = await cp.call(call.SendLocalList(
        version_number=3,
        update_type='Differential',
        local_authorization_list=[
            {
                'id_token': {'id_token': 'D001001', 'type': 'Central'},
            },
        ]
    ))
    logging.info(f"SendLocalListResponse from {cp.id}: {response}")


async def _action_send_local_list_full_empty(cp):
    """TC_D_04: Send SendLocalListRequest with updateType=Full, empty list."""
    logging.info(f"Sending SendLocalListRequest(Full, empty) to {cp.id}")
    response = await cp.call(call.SendLocalList(
        version_number=1,
        update_type='Full',
        local_authorization_list=[]
    ))
    logging.info(f"SendLocalListResponse from {cp.id}: {response}")


# ─── Auth Helpers ─────────────────────────────────────────────────────────────

def _check_password(cp_id, provided_password):
    """Check if the provided password matches any valid password for this CP.

    Accepts both the original configured password and any CSMS-updated password.
    This allows tests to reconnect with either the old or new password after
    a SetVariablesRequest(BasicAuthPassword) flow (TC_A_09 uses the new password,
    TC_A_10 uses the old password after rejecting the change).
    """
    if provided_password == BASIC_AUTH_CP_PASSWORD:
        return True
    if cp_id in cp_passwords and provided_password == cp_passwords[cp_id]:
        return True
    return False


def _decode_basic_auth(auth_header):
    """Decode a Basic auth header. Returns (username, password) or None."""
    if not auth_header or not auth_header.startswith('Basic '):
        return None
    try:
        encoded = auth_header.split(' ', 1)[1]
        decoded = base64.b64decode(encoded).decode('utf-8')
        username, password = decoded.split(':', 1)
        return username, password
    except (base64.binascii.Error, UnicodeDecodeError, ValueError):
        return None


def _unauthorized_response():
    return (
        http.HTTPStatus.UNAUTHORIZED,
        [('WWW-Authenticate', 'Basic realm="Access to CSMS"')],
        b'HTTP 401 Unauthorized\n'
    )


# ─── WS Server (Port 9000, SP1: Basic Auth) ─────────────────────────────────

async def ws_process_request(path, request_headers):
    """Validate Basic Auth and subprotocol for the WS (non-TLS) server."""
    cp_id = path.strip('/')

    # Reject unsupported WebSocket subprotocol at HTTP level
    requested_protocols = request_headers.get('Sec-WebSocket-Protocol', '')
    if requested_protocols:
        protos = [p.strip() for p in requested_protocols.split(',')]
        if 'ocpp2.0.1' not in protos:
            logging.warning(f"WS: Unsupported subprotocol(s) from {cp_id}: {protos}")
            return (
                http.HTTPStatus.BAD_REQUEST,
                [],
                b'Unsupported WebSocket subprotocol\n',
            )

    # Reject if CP has been upgraded beyond SP1
    min_sp = cp_min_security_profile.get(cp_id, 1)
    if min_sp > 1:
        logging.warning(f"WS: {cp_id} requires SP{min_sp}, rejecting SP1 connection")
        return _unauthorized_response()

    credentials = _decode_basic_auth(request_headers.get('Authorization'))
    if credentials is None:
        logging.warning(f"WS: No valid auth from {cp_id}")
        return _unauthorized_response()

    username, password = credentials

    if username == cp_id and _check_password(cp_id, password):
        logging.info(f"WS: Authorized {cp_id} (SP1)")
        return None
    else:
        logging.warning(f"WS: Bad credentials for {cp_id} (user={username})")
        return _unauthorized_response()


async def on_connect_ws(websocket, path):
    """Handle WS (non-TLS) connections - Security Profile 1."""
    if not _check_subprotocol(websocket):
        return

    cp_id = path.strip('/')
    cp = ChargePointHandler(cp_id, websocket)
    cp._security_profile = 1

    test_mode = get_test_mode_for_cp(cp_id)
    if test_mode:
        asyncio.create_task(execute_test_mode_actions(cp, security_profile=1))
    else:
        asyncio.create_task(auto_detect_and_execute(cp, security_profile=1))

    try:
        await cp.start()
    except ConnectionClosedOK:
        logging.info(f'WS: {cp_id} disconnected')


# ─── WSS Server (Port 8082, SP2: TLS+Auth, SP3: mTLS) ───────────────────────

async def wss_process_request(path, request_headers):
    """Validate auth for the WSS (TLS) server.
    SP2: Basic Auth header required.
    SP3: No auth header (client cert validated at TLS level).
    """
    cp_id = path.strip('/')
    min_sp = cp_min_security_profile.get(cp_id, 1)

    auth_header = request_headers.get('Authorization')
    if auth_header:
        # SP2 path: Basic Auth over TLS
        if min_sp > 2:
            logging.warning(f"WSS: {cp_id} requires SP{min_sp}, rejecting SP2")
            return _unauthorized_response()

        credentials = _decode_basic_auth(auth_header)
        if credentials is None:
            return _unauthorized_response()

        username, password = credentials

        if username == cp_id and _check_password(cp_id, password):
            logging.info(f"WSS: Authorized {cp_id} (SP2)")
            return None
        else:
            logging.warning(f"WSS: Bad credentials for {cp_id}")
            return _unauthorized_response()
    else:
        # SP3 path: mTLS (client cert verified at TLS handshake level)
        logging.info(f"WSS: No auth header for {cp_id} - SP3 (mTLS)")
        return None


async def on_connect_wss(websocket, path):
    """Handle WSS (TLS) connections - Security Profile 2 or 3."""
    if not _check_subprotocol(websocket):
        return

    cp_id = path.strip('/')
    auth_header = websocket.request_headers.get('Authorization')
    security_profile = 2 if auth_header else 3

    cp = ChargePointHandler(cp_id, websocket)
    cp._security_profile = security_profile

    test_mode = get_test_mode_for_cp(cp_id)
    if test_mode:
        asyncio.create_task(execute_test_mode_actions(cp, security_profile))
    else:
        asyncio.create_task(auto_detect_and_execute(cp, security_profile))

    try:
        await cp.start()
    except ConnectionClosedOK:
        logging.info(f'WSS: {cp_id} disconnected (SP{security_profile})')


# ─── Shared Helpers ──────────────────────────────────────────────────────────

def _check_subprotocol(websocket):
    """Validate WebSocket subprotocol negotiation."""
    try:
        requested = websocket.request_headers['Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("No subprotocol requested. Closing.")
        asyncio.create_task(websocket.close())
        return False

    if websocket.subprotocol:
        logging.info("Subprotocol matched: %s", websocket.subprotocol)
        return True
    else:
        logging.warning("Subprotocol mismatch | Available: %s, Requested: %s",
                        websocket.available_subprotocols, requested)
        asyncio.create_task(websocket.close())
        return False


def create_server_ssl_context():
    """Create SSL context for the WSS server.

    Loads both ECDSA and RSA server certificates so that OpenSSL can
    auto-select the right one based on the negotiated cipher suite
    (A00.FR.318: ECDHE-ECDSA ciphers use the EC cert, TLS_RSA ciphers
    use the RSA cert).
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    # Include RSA key exchange ciphers required by OCPP 2.0.1 (disabled by
    # default at SECLEVEL=2 because they lack forward secrecy).
    ctx.set_ciphers('DEFAULT:AES128-GCM-SHA256:AES256-GCM-SHA384:@SECLEVEL=1')
    # ECDSA certificate (for TLS_ECDHE_ECDSA_WITH_AES_* ciphers)
    ctx.load_cert_chain(certfile=SERVER_CERT, keyfile=SERVER_KEY)
    # RSA certificate (for TLS_RSA_WITH_AES_* ciphers)
    if os.path.exists(SERVER_RSA_CERT) and os.path.exists(SERVER_RSA_KEY):
        ctx.load_cert_chain(certfile=SERVER_RSA_CERT, keyfile=SERVER_RSA_KEY)
    else:
        logging.warning("RSA server cert not found - TLS_RSA_WITH_AES_* ciphers won't work")
    ctx.load_verify_locations(cafile=CA_CERT)
    # CERT_OPTIONAL: accept with or without client cert;
    # if cert IS provided, it must be valid (signed by our CA)
    ctx.verify_mode = ssl.CERT_OPTIONAL
    return ctx


# ─── Main ────────────────────────────────────────────────────────────────────

async def main():
    # Start WS server (SP1: Basic Auth, no TLS)
    ws_server = await websockets.serve(
        on_connect_ws,
        '0.0.0.0',
        WS_PORT,
        process_request=ws_process_request,
        subprotocols=['ocpp2.0.1'],
    )
    logging.info(f"WS  server started on port {WS_PORT}")

    # Start WSS server (SP2 + SP3: TLS) if certs exist
    wss_server = None
    if os.path.exists(SERVER_CERT) and os.path.exists(SERVER_KEY):
        ssl_ctx = create_server_ssl_context()
        wss_server = await websockets.serve(
            on_connect_wss,
            '0.0.0.0',
            WSS_PORT,
            process_request=wss_process_request,
            subprotocols=['ocpp2.0.1'],
            ssl=ssl_ctx,
        )
        logging.info(f"WSS server started on port {WSS_PORT}")
    else:
        logging.warning("TLS cert files not found - WSS server not started. "
                        "Run: python generate_certs.py")

    if CP_ACTIONS:
        logging.info(f"Per-CP test actions: {CP_ACTIONS}")
    elif TEST_MODE:
        logging.info(f"Global test mode: '{TEST_MODE}'")
    else:
        logging.info("Auto-detect mode: will determine actions based on CP behavior")

    tasks = [ws_server.wait_closed()]
    if wss_server:
        tasks.append(wss_server.wait_closed())
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
