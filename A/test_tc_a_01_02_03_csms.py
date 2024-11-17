import asyncio
import pytest
import os

from ocpp.v201.enums import RegistrationStatusType

from mock_charge_point import MockChargePoint
from utils import get_basic_auth_headers, validate_schema

TEST_USER_NAME = os.environ['TEST_USER_NAME']
TEST_USER_PASSWORD = os.environ['TEST_USER_PASSWORD']

"""
Test case name      Basic Authentication - Valid username/password combination
Test case Id        TC_A_01_CSMS
Use case Id(s)      A00, B01
Requirement(s)      A00.FR.204, B01.FR.02
System under test   CSMS

Description         The Charging Station uses Basic authentication to authenticate itself to the CSMS, when using security
                    profile 1 or 2.
Purpose             To verify whether the CSMS is able to validate the (valid) Basic authentication credentials provided by the
                    Charging Station at the connection request.

Prerequisite(s)     The CSMS supports security profile 1 and/or 2

Test Scenario
1. The OCTT sends a HTTP upgrade request with an Authorization header, containing a username/password combination.
2. The CSMS validates the username/password combination AND upgrades the connection to a (secured) WebSocket connection.
3. The OCTT sends a BootNotificationRequest
4. The CSMS responds with a BootNotificationResponse
5. The OCTT notifies the CSMS about the current state of all connectors.
6. The CSMS responds accordingly.
"""


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [("CP_1", get_basic_auth_headers(TEST_USER_NAME, TEST_USER_PASSWORD))],
                         indirect=True)
async def test_tc_a_01(connection):
    assert connection.open
    cp = MockChargePoint('CP_1', connection)

    start_task = asyncio.create_task(cp.start())
    boot_response = await cp.send_boot_notification()

    assert boot_response is not None
    assert validate_schema(data=boot_response, schema_file_path='../schema/BootNotificationResponse.json')
    assert boot_response.status == RegistrationStatusType.accepted

    status_response = await cp.send_status_notification()
    assert status_response

    start_task.cancel()


"""
Test case name      Basic Authentication - Username does not equal ChargingStationId
Test case Id        TC_A_02_CSMS
Use case Id(s)      A00
Requirement(s)      A00.FR.204
System under test   CSMS

Description         The Charging Station uses Basic authentication to authenticate itself to the CSMS, when using security
                    profile 1 or 2.

Purpose             To verify whether the CSMS is able to validate the (invalid) Basic authentication credentials provided by the
                    Charging Station at the connection request.

Prerequisite(s)     The CSMS supports security profile 1 and/or 2

Test Scenario
1. The OCTT sends a HTTP upgrade request with an Authorization header, containing a username/password combination.
2. The CSMS validates the username/password combination AND rejects the connection upgrade request.
"""


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [("CP_1", get_basic_auth_headers("wrong", TEST_USER_PASSWORD))], indirect=True)
async def test_tc_a_02(connection):
    assert connection.open == False
    assert connection.status_code == 401


"""
Test case name      Basic Authentication - Invalid password
Test case Id        TC_A_03_CSMS
Use case Id(s)      A00
Requirement(s)      A00.FR.204
System under test   CSMS

Description         The Charging Station uses Basic authentication to authenticate itself to the CSMS, when using security
                    profile 1 or 2.

Purpose             To verify whether the CSMS is able to validate the (invalid) Basic authentication credentials provided by the
                    Charging Station at the connection request.
Prerequisite(s)     The CSMS supports security profile 1 and/or 2

Test Scenario
1. The OCTT sends a HTTP upgrade request with an Authorization header, containing a username/password combination.
2. The CSMS validates the username/password combination AND rejects the connection upgrade request.
"""


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [("CP_1", get_basic_auth_headers(TEST_USER_NAME, "wrong"))], indirect=True)
async def test_tc_a_03(connection):
    assert connection.open == False
    assert connection.status_code == 401
