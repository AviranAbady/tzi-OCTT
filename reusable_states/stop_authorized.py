"""
State               StopAuthorized
System under test   CSMS
Description         This state will simulate that the Charging Station is in a state where the charging session is
                    authorized to stop.
Before
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): If State is NOT EnergyTransferStarted then execute Reusable State EnergyTransferStarted

Scenario

Notes(s): The tool will wait for <Configured Transaction Duration> seconds

1. The OCTT sends a TransactionEventRequest With triggerReason is StopAuthorized eventType is Updated
2. The CSMS responds with a TransactionEventResponse

Tool validations
* Step 2:
    Message: TransactionEventResponse
        - idTokenInfo.status must be Accepted

Post condition State is StopAuthorized
"""

from ocpp.v201.enums import (
    TransactionEventType,
    TriggerReasonType,
    AuthorizationStatusType,
    ChargingStateType
)
from ocpp.v201.call import TransactionEvent

from mock_charge_point import MockChargePoint
from utils import now_iso


async def stop_authorized(cp: MockChargePoint, evse_id: int = 1, connector_id: int = 1, 
                         transaction_id: str = "transaction_id", id_token_id: str = None, 
                         id_token_type: str = None):
    
    # Create and send the transaction event
    transaction_event = TransactionEvent(
        event_type=TransactionEventType.updated,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.stop_authorized,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
            "charging_state": ChargingStateType.charging,
        },
        evse={
            "id": evse_id,
            "connector_id": connector_id,
        }
    )
    
    # Add id_token if provided
    if id_token_id is not None and id_token_type is not None:
        transaction_event.id_token = {
            "id_token": id_token_id,
            "type": id_token_type
        }
    
    # Send the transaction event and get the response
    transaction_event_response = await cp.send_transaction_event_request(transaction_event)
    
    # Validate the response
    assert transaction_event_response is not None
    if hasattr(transaction_event_response, 'id_token_info') and transaction_event_response.id_token_info is not None:
        assert transaction_event_response.id_token_info.status == AuthorizationStatusType.accepted
    
    return transaction_event_response