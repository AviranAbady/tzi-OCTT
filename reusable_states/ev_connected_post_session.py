"""
State               EVConnectedPostSession
System under test   CSMS
Description         This state will simulate that the Charging Station is in a state where the energy transfer has
                    been stopped and the transaction is NOT authorized to resume energy transfer without
                    re-authorization.
Before
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): If State is NOT StopAuthorized then execute Reusable State StopAuthorized

Scenario

1. The OCTT sends a TransactionEventRequest With triggerReason is ChargingStateChanged
   transactionInfo.chargingState is EVConnected
   eventType is Updated

2. The CSMS responds with a TransactionEventResponse

Post condition State is EVConnectedPostSession
"""

from ocpp.v201.call import TransactionEvent
from ocpp.v201.enums import (
    TransactionEventEnumType as TransactionEventType,
    TriggerReasonEnumType as TriggerReasonType,
    ChargingStateEnumType as ChargingStateType,
)

from tzi_charge_point import TziChargePoint
from utils import now_iso, generate_transaction_id


async def ev_connected_post_session(cp: TziChargePoint, evse_id: int = 1, connector_id: int = 1,
                                    transaction_id: str = None):
    if transaction_id is None:
        transaction_id = generate_transaction_id()

    event = TransactionEvent(
        event_type=TransactionEventType.updated,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.charging_state_changed,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
            "charging_state": ChargingStateType.ev_connected,
        },
        evse={
            "id": evse_id,
            "connector_id": connector_id,
        }
    )

    response = await cp.send_transaction_event_request(event)
    assert response is not None
