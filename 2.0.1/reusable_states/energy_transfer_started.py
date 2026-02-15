"""
State               EnergyTransferStarted
System under test   CSMS
Description         This state will simulate that there is transferring energy between the EV and EVSE of the simulated
                    Charging Station.
Before
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s):
        If State is NOT Authorized then execute Reusable State Authorized
        If EVConnected is true
            then proceed to part 2
        Else
            proceed to part 1.

Scenario (Part 1)

1. The OCTT notifies the CSMS about the status change of the connector.
    Message: StatusNotificationRequest
        - connectorStatus is Occupied
    Message: NotifyEventRequest
        - trigger is Delta
        - actualValue is Occupied
        - component.name is Connector
        - variable.name is AvailabilityState

2. The CSMS responds accordingly.
3. The OCTT sends a TransactionEventRequest With triggerReason is CablePluggedIn transactionInfo.chargingState is
   EVConnected evse.id <Configured evseId> evse.connectorId <Configured connectorId> eventType is Updated
4. The CSMS responds with a TransactionEventResponse


Scenario (Part 2)

5. The OCTT sends a TransactionEventRequest With triggerReason is ChargingStateChanged
   transactionInfo.chargingState is Charging eventType is Updated
6. The CSMS responds with a TransactionEventResponse

Post condition
    State is EnergyTransferStarted
    EVConnected is true
"""

from ocpp.v201.enums import (
    ConnectorStatusEnumType as ConnectorStatusType,
    EventTriggerEnumType as EventTriggerType,
    EventNotificationEnumType as EventNotificationType,
    TransactionEventEnumType as TransactionEventType,
    TriggerReasonEnumType as TriggerReasonType,
    ChargingStateEnumType as ChargingStateType,
)
from ocpp.v201.call import TransactionEvent
from ocpp.v201.datatypes import ComponentType, VariableType, EventDataType

from tzi_charge_point import TziChargePoint
from utils import now_iso


async def energy_transfer_started(cp: TziChargePoint, evse_id: int, connector_id: int = 1, transaction_id: str = "transaction_id"):

    # Part 1 - CP is not connected in our case
    await cp.send_status_notification(connector_id=connector_id,
                                      status=ConnectorStatusType.occupied,
                                      evse_id=evse_id)

    component = ComponentType(name="Connector", instance=str(connector_id))
    variable = VariableType(name="AvailabilityState")
    event_data = EventDataType(
        event_id=evse_id,
        timestamp=now_iso(),
        trigger=EventTriggerType.delta,
        actual_value="Occupied",
        event_notification_type=EventNotificationType.custom_monitor,
        component=component,
        variable=variable,
    )

    await cp.send_notify_event([event_data])

    cable_plugged_event = TransactionEvent(
        event_type=TransactionEventType.updated,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.cable_plugged_in,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
            "charging_state": ChargingStateType.ev_connected,
        },
        evse={
            "id": evse_id,
            "connector_id": connector_id,
        },
    )
    cable_plugged_event_response = await cp.send_transaction_event_request(cable_plugged_event)
    assert cable_plugged_event_response is not None

    # Part 2
    charging_state_changed_event = TransactionEvent(
        event_type=TransactionEventType.updated,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.charging_state_changed,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
            "charging_state": ChargingStateType.charging,
        },
        evse={
            "id": evse_id,
            "connector_id": connector_id,
        },
    )
    charging_state_changed_event_response = await cp.send_transaction_event_request(charging_state_changed_event)
    assert charging_state_changed_event_response is not None
