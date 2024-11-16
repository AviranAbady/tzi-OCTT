"""
Test case name      Authorization by GroupId - Success
Test case Id        TC_C_39_CSMS
Use case Id(s)      C09
Requirement(s)      C09_FR_02, C09_FR_03
System under test   CSMS

Description         This test case covers how a Charging Station can authorize an action for an EV Driver based on GroupId
                    information. This could for example be used if 2 people regularly use the same EV: they can use their own
                    IdToken (e.g. RFID card), and can deauthorize transactions that were started with the other idToken (with
                    the same GroupId).
                    Purpose To verify if the CSMS is able to correctly handle the Authorization of idTokens with the same GroupId
                    according to the mechanism as described in the OCPP specification.

Prerequisite(s)     N/a
Before (Preparations)
    Configuration State:    N/a
    Memory State:           Two valid idTokens with the same GroupId are configured

Reusable State(s):
    state is EVConnectedPreSession

Test Scenario
    1. The OCTT sends an AuthorizeRequest with idToken.idToken <Configured valid_idtoken2_idtoken>
        idToken.type <Configured valid_idtoken2_type>
    2. The CSMS responds with an AuthorizeResponse
    3. The OCTT sends a TransactionEventRequest with
        - triggerReason Authorized
        - idToken.idToken <Configured valid_idtoken_idtoken>
        - idToken.type <Configured valid_idtoken_type>
            if transaction was already started
                - eventType Updated
            else
                - eventType Started

    4. The CSMS responds with a TransactionEventResponse
    5. Execute Reusable State EnergyTransferStarted
    6. The OCTT sends an AuthorizeRequest with idToken.idToken <Configured valid_idtoken2_idtoken> idToken.type <Configured valid_idtoken2_type>
    7. The CSMS responds with an AuthorizeResponse
    8. The OCTT sends a TransactionEventRequest with
        - triggerReason StopAuthorized
        - idToken.idToken <Configured valid_idtoken2_idtoken>
        - idToken.type <Configured valid_idtoken2_type>
        - eventType Updated
    9. The CSMS responds with a TransactionEventResponse
    10. Execute Reusable State EVConnectedPostSession
    11. Execute Reusable State EVDisconnected

Tool validations
* Step 2:
    Message AuthorizeResponse
    - idTokenInfo.status Accepted
    - idTokenInfo.groupIdToken.idToken <Configured groupIdToken>
* Step 4:
    Message TransactionEventResponse
    - idTokenInfo.status Accepted
    - idTokenInfo.groupIdToken.idToken <Configured groupIdToken>
* Step 7:
    Message AuthorizeResponse
    - idTokenInfo.status Accepted
    - idTokenInfo.groupIdToken.idToken <Configured groupIdToken>
* Step 9:
    Message TransactionEventResponse
    - idTokenInfo.status Accepted
    - idTokenInfo.groupIdToken.idToken <Configured groupIdToken>
"""