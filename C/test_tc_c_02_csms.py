"""
Test case name      Local start transaction - Authorization Invalid/Unknown
Test case Id        TC_C_02_CSMS
Use case Id(s)      C01, C04, C06
Requirement(s)      C01.FR.07 OR C04.FR.01 OR C06.FR.04
System under test   CSMS

Description         When a Charging Station needs to charge an EV, it needs to authorize the EV Driver first at the CSMS before
                    the charging can be started or stopped.
                    Purpose To verify whether the CSMS is able to report that an idToken is NOT valid

Test Scenario
1. The OCTT sends an AuthorizeRequest with
    idToken.idToken <Configured invalid_idtoken_idtoken>
    idToken.type <Configured invalid_idtoken_type>

2. The CSMS responds with an AuthorizeResponse

Tool validations * Step 2:
Message: AuthorizeResponse
    - idTokenInfo.status Invalid or Unknown

Post scenario validations:
- N/a
"""

import asyncio
import pytest
import os

from ocpp.v201.enums import AuthorizationStatusType

from mock_charge_point import MockChargePoint
from utils import get_basic_auth_headers, validate_schema

BASIC_AUTH_CP = os.environ['BASIC_AUTH_CP']
BASIC_AUTH_CP_PASSWORD = os.environ['BASIC_AUTH_CP_PASSWORD']

@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [(BASIC_AUTH_CP, get_basic_auth_headers(BASIC_AUTH_CP, BASIC_AUTH_CP_PASSWORD))],
                         indirect=True)
async def test_tc_c_02(connection):
    token_id = os.environ['INVALID_ID_TOKEN']
    token_type = os.environ['INVALID_ID_TOKEN_TYPE']

    assert connection.open

    cp = MockChargePoint(BASIC_AUTH_CP, connection)

    start_task = asyncio.create_task(cp.start())

    authorization_response = await cp.send_authorization_request(id_token=token_id, token_type=token_type, skip_schema_validation=True)

    assert authorization_response is not None
    assert validate_schema(data=authorization_response, schema_file_name='../schema/AuthorizeResponse.json')

    assert authorization_response.id_token_info['status'] in [AuthorizationStatusType.invalid,
                                             AuthorizationStatusType.unknown]


    start_task.cancel()
