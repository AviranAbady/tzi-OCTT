"""
State               Authorized
System under test   CSMS
Description         This state will simulate that the EV Driver is locally authorizing to start a transaction on the
                    simulated Charging Station.
Before
    Configuration State:    N/a
    Memory State:           N/a
    Reusable State(s):      N/a

Main

1. The OCTT sends an AuthorizeRequest With idToken.idToken <Configured valid_idtoken_idtoken>
   idToken.type <Configured valid_idtoken_type>
2. The CSMS responds with an AuthorizeResponse
3. The OCTT sends a TransactionEventRequest With triggerReason is Authorized
   idToken.idToken <Configured valid_idtoken_idtoken> idToken.type <Configured valid_idtoken_type>

If State is EVConnectedPreSession
then
    eventType is Updated
else
    eventType is Started

4. The CSMS responds with a TransactionEventResponse

Tool validations
* Step 2: Message: AuthorizeResponse - idTokenInfo.status must be Accepted
* Step 4: Message: TransactionEventResponse - idTokenInfo.status must be Accepted
Post condition State is Authorized
"""

from ocpp.v201.enums import (
    AuthorizationStatusEnumType as AuthorizationStatusType,
    IdTokenEnumType as IdTokenType,
    TransactionEventEnumType as TransactionEventType,
    TriggerReasonEnumType as TriggerReasonType,
)
from ocpp.v201.call import TransactionEvent

from tzi_charge_point import TziChargePoint
from utils import now_iso


async def authorized(cp: TziChargePoint, id_token_id: str, id_token_type: IdTokenType,
                     transaction_id: str = "transaction_id", evse_id: int = 1, connector_id: int = 1,
                     ev_connected_pre_session=False):

    # 1. The OCTT sends an AuthorizeRequest
    authorize_response = await cp.send_authorization_request(
        id_token=id_token_id, token_type=id_token_type
    )

    # 2. The CSMS responds with an AuthorizeResponse
    assert authorize_response is not None
    id_token_info = authorize_response.id_token_info
    if isinstance(id_token_info, dict):
        assert id_token_info['status'] == 'Accepted', \
            f"Expected AuthorizeResponse.idTokenInfo.status=Accepted, got {id_token_info['status']}"
    else:
        assert id_token_info.status == AuthorizationStatusType.accepted

    # 3. The OCTT sends a TransactionEventRequest
    if ev_connected_pre_session:
        event_type = TransactionEventType.updated
    else:
        event_type = TransactionEventType.started

    transaction_event = TransactionEvent(
        event_type=event_type,
        timestamp=now_iso(),
        trigger_reason=TriggerReasonType.authorized,
        seq_no=cp.next_seq_no(),
        transaction_info={
            "transaction_id": transaction_id,
        },
        id_token={
            "id_token": id_token_id,
            "type": id_token_type
        },
        evse={
            "id": evse_id,
            "connector_id": connector_id,
        }
    )
    transaction_event_response = await cp.send_transaction_event_request(
        transaction_event
    )

    # 4. The CSMS responds with a TransactionEventResponse
    assert transaction_event_response is not None
    if transaction_event_response.id_token_info is not None:
        te_id_token_info = transaction_event_response.id_token_info
        if isinstance(te_id_token_info, dict):
            assert te_id_token_info['status'] == 'Accepted', \
                f"Expected TransactionEventResponse.idTokenInfo.status=Accepted, got {te_id_token_info['status']}"
        else:
            assert te_id_token_info.status == AuthorizationStatusType.accepted
