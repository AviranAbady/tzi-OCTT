"""
State               EVConnectedPreSession
System under test   CSMS
Description         This state will simulate that the EV and EVSE (Electric Vehicle Supply Equipment) of the simulated
                    Charging Station are connected.

Before (Preparations)
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): N/a

(Scenario)

1. The OCTT notifies the CSMS about the status change of the connector
    Message: StatusNotificationRequest
        - connectorStatus is Occupied
    Message: NotifyEventRequest
        - trigger is Delta
        - actualValue is Occupied
        - component.name is Connector
        - variable.name is AvailabilityState

2. The CSMS responds accordingly.

3. The OCTT sends a TransactionEventRequest With triggerReason is CablePluggedIn transactionInfo.chargingState is EVConnected
    evse.id <Configured evseId>
    evse.connectorId <Configured connectorId>
    If State is Authorized then
        eventType is Updated
    else
        eventType is Started

4. The CSMS responds with a TransactionEventResponse

Tool validations N/a
Post condition State is EVConnectedPreSession
"""
from ocpp.v201.call import TransactionEvent
from ocpp.v201.datatypes import EventDataType, ComponentType, VariableType
from ocpp.v201.enums import ConnectorStatusType, EventTriggerType

from mock_charge_point import MockChargePoint


def ev_connected_pre_session(cp: MockChargePoint, evse_id, connector_id):
    response = cp.send_status_notification(connector_id=1, status=ConnectorStatusType.occupied)

    data = [
        EventDataType(
            trigger=EventTriggerType('delta'),
            actual_value='Occupied',
            component=ComponentType(name='Connector'),
            variable=VariableType(name='AvailabilityState')
        )
    ]

    response = cp.send_notify_event(data=data)

    event = TransactionEvent(trigger_reason='CablePluggedIn',
                             transaction_info=dict(chargingState='EVConnected'),
                             evse=dict(id=evse_id,connectorId=connector_id))

    response = cp.send_transaction_event_request(event)

    pass
