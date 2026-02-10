"""
Test case name      Authorization using Contract Certificates 15118 - Online - Local contract certificate validation - Rejected
Test case Id        TC_C_51_CSMS
Use case Id(s)      C07
Requirement(s)      C07.FR.16

Requirement Details:
    C07.FR.16: C07.FR.04 AND the certificate chain (provided in certificate or iso15118CertificateHashData) has been revoked CSMS SHALL return an AuthorizationResponse containing a certificateStatus = CertificateRevoked and an idTokenInfo.status = Invalid If certificate is revoked,
        Precondition: C07.FR.04 AND the certificate chain (provided in certificate or iso15118CertificateHashData) has been revoked
System under test   CSMS

Description         The Charging Station is able to authorize with contract certificates when it supports ISO 15118.
                    Purpose To verify if the CSMS is able to validate the certificate hash data and the provided eMAID.

Prerequisite(s)
    - The configured eMAID is known by the CSMS as valid.
    - The contract certificate is REVOKED.
    - iso15118CertificateHashData has a responder URL that points to an OCSP service operated by the OCTT.
    - CSMS does not have a cached OCSP response for the contract certificate.

Before (Preparations)
    Configuration State:    N/a
    Memory State:           N/a
    Reusable State(s):      State is EVConnectedPreSession

Test Scenario
1. The OCTT sends an AuthorizeRequest with
    - idToken.idToken  <Configured valid_idtoken_idtoken> (eMAID)
    - idToken.type     <Configured valid_idtoken_type> (eMAID)
    - iso15118CertificateHashData <hashes from configured (V2G) certificate chain - certificate is REVOKED>

2. The CSMS sends an OCSP request to the responder URL from iso15118CertificateHashData to check validity

3. The OCTT OCSP service responds that the certificate is REVOKED

4. The CSMS responds with an AuthorizeResponse
    - idTokenInfo.status Invalid (authorization rejected because certificate is revoked)

Tool validations
* Step 2: CSMS sends an OCSP request for iso15118CertificateHashData (verified externally by OCTT OCSP service)
* Step 4:
    - idTokenInfo.status Invalid
    - certificateStatus CertificateRevoked

Configuration
    VALID_ID_TOKEN / VALID_ID_TOKEN_TYPE:           eMAID token known as valid at the CSMS
    ISO15118_REVOKED_CERT_HASH_DATA_FILE:            path to JSON file with OCSP request data for REVOKED certificate chain.
                                                      File format: JSON array of objects with fields:
                                                      hash_algorithm, issuer_name_hash, issuer_key_hash,
                                                      serial_number, responder_url
                                                      The responder_url must point to an OCTT-controlled OCSP service
                                                      configured to return "revoked" for this certificate.
                                                      Example:
                                                      [
                                                        {
                                                          "hash_algorithm": "SHA256",
                                                          "issuer_name_hash": "<base64-encoded>",
                                                          "issuer_key_hash": "<base64-encoded>",
                                                          "serial_number": "DEADBEEF",
                                                          "responder_url": "http://ocsp.example.com"
                                                        }
                                                      ]
"""

import asyncio
import json
import pytest
import os

from ocpp.v201.enums import (
    AuthorizationStatusEnumType as AuthorizationStatusType,
    AuthorizeCertificateStatusEnumType,
    HashAlgorithmEnumType,
)
from ocpp.v201.datatypes import OCSPRequestDataType
from tzi_charge_point import TziChargePoint
from reusable_states.ev_connected_pre_session import ev_connected_pre_session
from reusable_states.parking_bay_occupied import parking_bay_occupied
from utils import get_basic_auth_headers, validate_schema

BASIC_AUTH_CP = os.environ['BASIC_AUTH_CP']
BASIC_AUTH_CP_PASSWORD = os.environ['BASIC_AUTH_CP_PASSWORD']


def load_cert_hash_data(file_path: str):
    """Load ISO 15118 certificate hash data from a JSON file."""
    with open(file_path) as f:
        data = json.load(f)
    result = []
    for entry in data:
        result.append(OCSPRequestDataType(
            hash_algorithm=HashAlgorithmEnumType(entry['hash_algorithm']),
            issuer_name_hash=entry['issuer_name_hash'],
            issuer_key_hash=entry['issuer_key_hash'],
            serial_number=entry['serial_number'],
            responder_url=entry['responder_url'],
        ))
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [(BASIC_AUTH_CP, get_basic_auth_headers(BASIC_AUTH_CP, BASIC_AUTH_CP_PASSWORD))],
                         indirect=True)
async def test_tc_c_51(connection):
    token_id = os.environ['VALID_ID_TOKEN']
    token_type = os.environ['VALID_ID_TOKEN_TYPE']
    revoked_cert_hash_data_file = os.environ['ISO15118_REVOKED_CERT_HASH_DATA_FILE']
    evse_id = 1
    connector_id = 1

    assert connection.open
    cp = TziChargePoint(BASIC_AUTH_CP, connection)

    start_task = asyncio.create_task(cp.start())
    await parking_bay_occupied(cp, evse_id=evse_id)
    await ev_connected_pre_session(cp, evse_id=evse_id, connector_id=connector_id)

    # Load the certificate hash data for the REVOKED certificate
    iso15118_cert_hash_data = load_cert_hash_data(revoked_cert_hash_data_file)

    # 1. AuthorizeRequest with eMAID idToken and iso15118CertificateHashData (revoked cert)
    auth_response = await cp.send_authorization_request_with_iso15118(
        id_token=token_id,
        token_type=token_type,
        iso15118_certificate_hash_data=iso15118_cert_hash_data,
    )

    # 4. CSMS responds: authorization rejected because the certificate is revoked
    assert auth_response is not None
    assert validate_schema(data=auth_response, schema_file_name='../schema/AuthorizeResponse.json')
    assert auth_response.id_token_info['status'] == AuthorizationStatusType.invalid
    assert auth_response.certificate_status == AuthorizeCertificateStatusEnumType.certificate_revoked

    start_task.cancel()
