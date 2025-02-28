"""
State               EVDisconnected
System under test   CSMS
Description         This state will simulate that the EV and EVSE of the simulated Charging Station are disconnected,
                    after the charging session is authorized to stop.
Before
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s):
        If State is NOT EVConnectedPostSession then execute Reusable State EVConnectedPostSession

Scenario

1. The OCTT notifies the CSMS about the status change of the connector.
    Message: StatusNotificationRequest
        - connectorStatus is Available
    Message: NotifyEventRequest
        - trigger is Delta
        - actualValue is Available
        - component.name is Connector
        - variable.name is AvailabilityState

2. The CSMS responds accordingly.
3. The OCTT sends a TransactionEventRequest With triggerReason is EVCommunicationLost
   transactionInfo.chargingState is Idle
   transactionInfo.stoppedReason is EVDisconnected
   eventType is Ended
4. The CSMS responds with a TransactionEventResponse

Post condition State is EVDisconnected
"""

from ocpp.v201.call import TransactionEvent
from ocpp.v201.datatypes import EventDataType, ComponentType, VariableType
from ocpp.v201.enums import ConnectorStatusType, EventTriggerType, EventNotificationType

from mock_charge_point import MockChargePoint
from utils import now_iso


async def ev_disconnected(cp: MockChargePoint, evse_id: int = 1, connector_id: int = 1, transaction_id: str = None):
    response = await cp.send_status_notification(connector_id=connector_id, status=ConnectorStatusType.available)

    data = [
        EventDataType(
            trigger=EventTriggerType.delta,
            actual_value='Available',
            component=ComponentType(name='Connector'),
            variable=VariableType(name='AvailabilityState'),
            timestamp=now_iso(),
            event_id=evse_id,
            event_notification_type=EventNotificationType.custom_monitor
        )
    ]

    response = await cp.send_notify_event(data=data)

    event = TransactionEvent(
        trigger_reason='EVCommunicationLost',
        transaction_info=dict(
            chargingState='Idle', 
            transaction_id=transaction_id,
            stoppedReason='EVDisconnected'
        ),
        evse=dict(id=evse_id, connectorId=connector_id),
        event_type='Ended', 
        timestamp=now_iso(), 
        seq_no=cp.next_seq_no()
    )

    response = await cp.send_transaction_event_request(event)