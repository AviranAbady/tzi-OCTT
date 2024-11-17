import asyncio
import pytest
import os

from ocpp.v201.enums import AuthorizationStatusType

from mock_charge_point import MockChargePoint
from utils import get_basic_auth_headers, validate_schema

TEST_USER_NAME = os.environ['TEST_USER_NAME']
TEST_USER_PASSWORD = os.environ['TEST_USER_PASSWORD']

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
"""


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [("CP_1", get_basic_auth_headers(TEST_USER_NAME, TEST_USER_PASSWORD))],
                         indirect=True)
async def test_tc_c_02(connection):
    token_id = os.environ['INVALID_ID_TOKEN']
    token_type = os.environ['INVALID_ID_TOKEN_TYPE']

    assert connection.open
    cp = MockChargePoint('CP_1', connection)

    start_task = asyncio.create_task(cp.start())

    authorization_response = await cp.send_authorization_request(id_token=token_id, token_type=token_type)

    assert authorization_response is not None
    assert validate_schema(data=authorization_response, schema_file_path='../schema/AuthorizeResponse.json')

    assert authorization_response.id_token_info['status'] in [AuthorizationStatusType.invalid,
                                             AuthorizationStatusType.unknown]


    start_task.cancel()
