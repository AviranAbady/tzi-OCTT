"""
Test case name      Authorization using Contract Certificates 15118 - Online - Central contract certificate validation - Accepted
Test case Id        TC_C_52_CSMS
Use case Id(s)      C07
Requirement(s)      C07.FR.04, C07.FR.05

Requirement Details:
    C07.FR.04: If the CSMS receives an AuthorizeRequest. It SHALL respond with an AuthorizeResponse and SHALL include an authorization status value indicating acceptance or a reason for rejection.
        Precondition: If the CSMS receives an AuthorizeRequest.
    C07.FR.05: The CSMS SHALL verify validity of the certificate and certificate chain via real-time or cached OCSP data.
        Precondition: C07.FR.02
System under test   CSMS

Description         The Charging Station is able to authorize with contract certificates when it supports ISO 15118.
                    Purpose To verify if the CSMS is able to validate the provided certificate and eMAID. The field
                    iso15118CertificateHashData is NOT provided, forcing the CSMS to calculate certificate hash data
                    for the OCSP request itself.

Prerequisite(s)
    - The configured eMAID is known by the CSMS as valid.
    - The configured contract certificate is signed by the configured V2GRoot or MORoot certificate at the CSMS.
    - The contract certificate has a responder URL that points to an OCSP service operated by the OCTT.
    - CSMS does not have a cached OCSP response for the contract certificate.

Before (Preparations)
    Configuration State:    N/a
    Memory State:           N/a
    Reusable State(s):      State is EVConnectedPreSession

Test Scenario
1. The OCTT sends an AuthorizeRequest with
    - idToken.idToken  <Configured valid_idtoken_idtoken> (eMAID)
    - idToken.type     <Configured valid_idtoken_type> (eMAID)
    - certificate      <Configured contract_certificate> (PEM-encoded)
    - iso15118CertificateHashData is ABSENT

    Note: By not including iso15118CertificateHashData, the CSMS must calculate the hash data
    itself from the provided certificate in order to perform the OCSP check.

2. The CSMS sends an OCSP request to the responder URL derived from the certificate to check validity

3. The OCTT OCSP service responds that the certificate is valid

4. The CSMS responds with an AuthorizeResponse
    - idTokenInfo.status Accepted
    - certificateStatus Accepted

5. The OCTT sends a TransactionEventRequest with triggerReason Authorized

6. The CSMS responds with a TransactionEventResponse
    - idTokenInfo.status Accepted

7. Execute Reusable State EnergyTransferStarted

Tool validations
* Step 2: CSMS sends an OCSP request for the certificate (verified externally by OCTT OCSP service)
* Step 4:
    - idTokenInfo.status Accepted
    - certificateStatus Accepted
* Step 6:
    - idTokenInfo.status Accepted

Configuration
    VALID_ID_TOKEN / VALID_ID_TOKEN_TYPE:   eMAID token known as valid at the CSMS
    CONTRACT_CERT_FILE:                      path to PEM-encoded contract certificate file.
                                              The certificate must be signed by the CSMS's configured V2GRoot or MORoot.
                                              The certificate must contain an OCSP responder URL in the AIA extension
                                              that points to an OCTT-controlled OCSP service returning "valid".
    CONTRACT_CERT_EMAID:                     the eMAID encoded in the contract certificate (for documentation/reference)
"""

import asyncio
import pytest
import os

from ocpp.v201.enums import (
    AuthorizationStatusEnumType as AuthorizationStatusType,
    TriggerReasonEnumType as TriggerReasonType,
    TransactionEventEnumType as TransactionEventType,
    AuthorizeCertificateStatusEnumType,
)
from ocpp.v201.call import TransactionEvent
from ocpp.v201.datatypes import IdTokenType
from tzi_charge_point import TziChargePoint
from reusable_states.ev_connected_pre_session import ev_connected_pre_session
from reusable_states.parking_bay_occupied import parking_bay_occupied
from reusable_states.energy_transfer_started import energy_transfer_started
from utils import get_basic_auth_headers, generate_transaction_id, now_iso, validate_schema

BASIC_AUTH_CP = os.environ['BASIC_AUTH_CP_C']
BASIC_AUTH_CP_PASSWORD = os.environ['BASIC_AUTH_CP_PASSWORD']


def load_certificate_pem(file_path: str) -> str:
    """Load a PEM-encoded certificate from file and return as a string."""
    with open(file_path) as f:
        return f.read()


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [(BASIC_AUTH_CP, get_basic_auth_headers(BASIC_AUTH_CP, BASIC_AUTH_CP_PASSWORD))],
                         indirect=True)
async def test_tc_c_52(connection):
    token_id = os.environ['VALID_ID_TOKEN']
    token_type = os.environ['VALID_ID_TOKEN_TYPE']
    contract_cert_file = os.environ['CONTRACT_CERT_FILE']
    evse_id = 1
    connector_id = 1

    assert connection.open
    cp = TziChargePoint(BASIC_AUTH_CP, connection)

    start_task = asyncio.create_task(cp.start())
    await parking_bay_occupied(cp, evse_id=evse_id)
    await ev_connected_pre_session(cp, evse_id=evse_id, connector_id=connector_id)

    # Load the contract certificate PEM
    contract_certificate = load_certificate_pem(contract_cert_file)

    # 1. AuthorizeRequest with eMAID and certificate (NO iso15118CertificateHashData)
    #    CSMS must calculate OCSP hash data from the certificate itself
    auth_response = await cp.send_authorization_request_with_iso15118(
        id_token=token_id,
        token_type=token_type,
        certificate=contract_certificate,
        iso15118_certificate_hash_data=None,  # Absent - CSMS must compute it
    )

    # 4. CSMS responds: Accepted + certificateStatus Accepted
    assert auth_response is not None
    assert validate_schema(data=auth_response, schema_file_name='../schema/AuthorizeResponse.json')
    assert auth_response.id_token_info['status'] == AuthorizationStatusType.accepted
    assert auth_response.certificate_status == AuthorizeCertificateStatusEnumType.accepted

    transaction_id = generate_transaction_id()

    # 5. TransactionEventRequest: Authorized
    event = TransactionEvent(
        event_type=TransactionEventType.started,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.authorized,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
            "charging_state": "EVConnected",
        },
        id_token=IdTokenType(id_token=token_id, type=token_type),
        evse={
            "id": evse_id,
            "connector_id": connector_id
        }
    )
    tx_response = await cp.send_transaction_event_request(event)

    # 6. CSMS responds: Accepted
    assert tx_response is not None
    assert validate_schema(data=tx_response, schema_file_name='../schema/TransactionEventResponse.json')
    assert tx_response.id_token_info is not None
    assert tx_response.id_token_info.status == AuthorizationStatusType.accepted

    # 7. Execute Reusable State EnergyTransferStarted
    await energy_transfer_started(cp, evse_id=evse_id, connector_id=connector_id, transaction_id=transaction_id)

    start_task.cancel()
