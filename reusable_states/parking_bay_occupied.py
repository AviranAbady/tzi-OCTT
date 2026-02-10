"""
Reusable State      ParkingBayOccupied
System under test   Charging Station
Description         This state will prepare the Charging Station, so that the EV entered the parking bay.
                    The execution of this State is optional. Because there may not be a parking bay occupancy sensor OR
                    the Charging Station is being tested with a test plug or EV simulator.

Before (Preparations)
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): N/a

Main (Scenario)
Manual Action: Drive EV into parking bay.
    Note(s):
        - This State is optional (Even when TxStartPoint contains ParkingBayOccupancy).

1. The Charging Station sends a TransactionEventRequest
    Note(s):
        - This step needs to be executed when TxStartPoint contains ParkingBayOccupancy AND the EV entered
        the parking bay.

2. The OCTT responds with a TransactionEventResponse

Tool validations * Step 1:
    Message: TransactionEventRequest
        - triggerReason must be EVDetected

Post condition State is ParkingBayOccupied
"""
from ocpp.v201.call import TransactionEvent
from tzi_charge_point import TziChargePoint
from utils import now_iso, generate_transaction_id


async def parking_bay_occupied(cp: TziChargePoint, evse_id: int = 0, connector_id: int = 0):
    event = TransactionEvent(trigger_reason='EVDetected',
                             transaction_info=dict(transaction_id=generate_transaction_id()),
                             evse=dict(id=evse_id, connectorId=connector_id),
                             event_type="Updated", timestamp=now_iso(), seq_no=cp.next_seq_no())

    response = await cp.send_transaction_event_request(event)
    return response
