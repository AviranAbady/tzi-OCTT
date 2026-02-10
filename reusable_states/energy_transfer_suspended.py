"""
State               EnergyTransferSuspended
System under test   CSMS
Description         This state will simulate that the Charging Station is in a state where the energy transfer is
                     suspended by the EV.
Before
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): If State is NOT EnergyTransferStarted then execute Reusable State EnergyTransferStarted

Scenario
Notes(s): The tool will wait for <Configured Transaction Duration> seconds

1. The OCTT sends a TransactionEventRequest With triggerReason is ChargingStateChanged transactionInfo.chargingState is SuspendedEV
2. The CSMS responds with a TransactionEventResponse

Tool validations N/a
Post condition State is EnergyTransferSuspended
"""

from ocpp.v201.call import TransactionEvent
from ocpp.v201.enums import (
    TransactionEventEnumType as TransactionEventType,
    TriggerReasonEnumType as TriggerReasonType,
    ChargingStateEnumType as ChargingStateType,
)

from tzi_charge_point import TziChargePoint
from utils import now_iso


async def energy_transfer_suspended(cp: TziChargePoint, evse_id: int = 1, connector_id: int = 1,
                                    transaction_id: str = "transaction_id"):
    event = TransactionEvent(
        event_type=TransactionEventType.updated,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.charging_state_changed,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
            "charging_state": ChargingStateType.suspended_ev,
        },
        evse={
            "id": evse_id,
            "connector_id": connector_id,
        },
    )

    response = await cp.send_transaction_event_request(event)
    assert response is not None
