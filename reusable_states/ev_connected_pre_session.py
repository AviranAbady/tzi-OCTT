"""
Reusable State      EVConnectedPreSession
System under test   Charging Station
Description         This state will prepare the Charging Station, so that the EV and EVSE are connected.

Before (Preparations)
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): If State is NOT ParkingBayOccupied then execute Reusable State ParkingBayOccupied

Main (Scenario)
Manual Action: Connect the EV and EVSE.

1. The Charging Station notifies the CSMS about the status change of the connector.
2. The OCTT responds accordingly.
3. The Charging Station sends a TransactionEventRequest
    Note(s):
        - This step needs to be executed when TxStartPoint contains EVConnected OR the transaction already
        started. So in the case TxStartPoint contains ParkingBayOccupancy OR Authorized

4. The OCTT responds with a TransactionEventResponse

Tool validations * Step 1:
    Message: StatusNotificationRequest
        - evseId <configured evseId>
        - connectorId <configured connectorId>
        - connectorStatus must be Occupied

    Message: NotifyEventRequest
        - eventData[0].trigger must be Delta
        - eventData[0].actualValue must be Occupied
        - eventData[0].component.name must be Connector
        - eventData[0].variable.name must be AvailabilityState
        - evse.id <configured evseId>
        - connector.id <configured connectorId>

* Step 3:
    Message: TransactionEventRequest
        - eventType
                if TxStartPoint is EVConnected or PowerPathClosed and State is Authorized
                    started
                else
                    updated
        - triggerReason must be CablePluggedIn or ChargingStateChanged or RemoteStart
        - transactionInfo.chargingState must be EVConnected or SuspendedEVSE or Charging if State is Authorized
        - evse.id <configured evseId>
        - connector.id <configured connectorId>

Post condition State is EVConnectedPreSession
"""
from ocpp.v201.call import TransactionEvent, TransactionEventPayload
from ocpp.v201.datatypes import EventDataType, ComponentType, VariableType
from ocpp.v201.enums import ConnectorStatusType, EventTriggerType, EventNotificationType

from mock_charge_point import MockChargePoint
from utils import now_iso, generate_transaction_id


async def ev_connected_pre_session(cp: MockChargePoint, evse_id: int = 0, connector_id: int = 0):
    response = await cp.send_status_notification(connector_id=connector_id, status=ConnectorStatusType.occupied)

    data = [
        EventDataType(
            trigger=EventTriggerType.delta,
            actual_value='Occupied',
            component=ComponentType(name='Connector'),
            variable=VariableType(name='AvailabilityState'),
            timestamp=now_iso(),
            event_id=evse_id,
            event_notification_type=EventNotificationType.custom_monitor
        )
    ]

    response = await cp.send_notify_event(data=data)

    event = TransactionEvent(trigger_reason='CablePluggedIn',
                             transaction_info=dict(chargingState='EVConnected', transaction_id=generate_transaction_id()),
                             evse=dict(id=evse_id, connectorId=connector_id),
                             event_type=cp.get_notify_event_type(), timestamp=now_iso(), seq_no=cp.next_seq_no())

    response = await cp.send_transaction_event_request(event)


