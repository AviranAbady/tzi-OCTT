"""
Test case name      Cold Boot Charging Station - Pending
Test case Id        TC_B_02_CSMS
Use case Id(s)      B02
Requirement(s)      B02.FR.01, B02.FR.06

Requirement Details:
    B02.FR.01: After the Charging Station received the Pending status. The CSMS MAY send messages to retrieve information from the Charging Station (as described in use cases B06, B07, B08) or change its configuration by SetVariablesRequest (as described in use case B05). The Charging Station SHALL respond to these messages. The Pending status can thus indicate that the
        Precondition: After the Charging Station received the Pending status.
    B02.FR.06: When the CSMS returns the Pending status The communication channel SHALL NOT be closed by either the Charging Station or the CSMS.
        Precondition: When the CSMS returns the Pending status
System under test   CSMS

Description         The booting mechanism allows a Charging Station to provide some general information about the
                    Charging Station to the CSMS on startup AND it allows the Charging Station to request whether
                    it is allowed to start sending other OCPP messages. The CSMS may respond to the
                    BootNotificationRequest with status Pending. The Pending status can indicate that the CSMS
                    wants to retrieve or set certain information on the Charging Station before it will accept
                    the Charging Station.
Purpose             To verify whether the CSMS is able to accept the communications of a registered Charging Station.

Prerequisite(s)     The CSMS is configured to first respond to a BootNotificationRequest with status Pending.

Test Scenario
1. The OCTT sends a BootNotificationRequest with reason PowerUp
2. The CSMS responds with a BootNotificationResponse (status: Pending)
3. The OCTT sends a BootNotificationRequest with reason PowerUp
4. The CSMS responds with a BootNotificationResponse (status: Accepted)
5. The OCTT notifies the CSMS about the current state of all connectors.
6. The CSMS responds accordingly.

Note(s):
- If the interval in the BootNotificationResponse equals 0, the OCTT will wait
  <Configured heartbeatInterval> seconds, before sending another BootNotificationRequest.
- If the interval in the BootNotificationResponse > 0, the OCTT will wait <Interval provided at the
  BootNotificationResponse> seconds, before sending another BootNotificationRequest.

Tool validations
* Step 2:
    Message: BootNotificationResponse
    - status Pending
* Step 3:
    Message: BootNotificationResponse
    - status Accepted

Post scenario validations:
    N/a
"""

import asyncio
import pytest
import os

from ocpp.v201.enums import RegistrationStatusEnumType, ConnectorStatusEnumType

from tzi_charge_point import TziChargePoint
from utils import get_basic_auth_headers, validate_schema

CSMS_ADDRESS = os.environ['CSMS_ADDRESS']
BASIC_AUTH_CP = os.environ['BASIC_AUTH_CP_B']
BASIC_AUTH_CP_PASSWORD = os.environ['BASIC_AUTH_CP_PASSWORD']


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [(BASIC_AUTH_CP, get_basic_auth_headers(BASIC_AUTH_CP, BASIC_AUTH_CP_PASSWORD))],
                         indirect=True)
async def test_tc_b_02(connection):
    """Cold Boot Charging Station - Pending: CSMS first responds Pending, then Accepted."""
    assert connection.open

    cp = TziChargePoint(BASIC_AUTH_CP, connection)
    start_task = asyncio.create_task(cp.start())

    # Step 1-2: First BootNotification - expect Pending
    boot_response = await cp.send_boot_notification()
    assert boot_response is not None
    assert validate_schema(data=boot_response, schema_file_name='BootNotificationResponse.json')
    assert boot_response.status == RegistrationStatusEnumType.pending

    # Wait for the interval specified by the CSMS before retrying
    interval = boot_response.interval if boot_response.interval > 0 else 10
    await asyncio.sleep(interval)

    # Step 3-4: Second BootNotification - expect Accepted
    boot_response = await cp.send_boot_notification()
    assert boot_response is not None
    assert validate_schema(data=boot_response, schema_file_name='BootNotificationResponse.json')
    assert boot_response.status == RegistrationStatusEnumType.accepted

    # Step 5-6: Notify CSMS about connector states
    status_response = await cp.send_status_notification(1, ConnectorStatusEnumType.available)
    assert status_response is not None

    await cp.send_notify_event([{
        'event_id': 1,
        'timestamp': '2024-01-01T00:00:00Z',
        'trigger': 'Delta',
        'actual_value': 'Available',
        'event_notification_type': 'HardWiredNotification',
        'component': {'name': 'Connector'},
        'variable': {'name': 'AvailabilityState'},
    }])

    start_task.cancel()
