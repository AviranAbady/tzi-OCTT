"""
Test case name      Authorization through authorization cache - Accepted
Test case Id        TC_C_08_CSMS
Use case Id(s)      C12
Requirement(s)      C12_FR_03
System under test   CSMS

Description         This test case describes how the EV Driver is authorized to start a transaction while the Charging Station
                    uses Cached IdToken. This enables the EV Driver to Online start a transaction by using the Authorization
                    Cache in which the Charging Station can respond faster, as no AuthorizeRequest is being sent.
                    Purpose To verify if the CSMS is able to respond correctly when an idToken which has status "Accepted" in the
                    charging stations cache is presented according to the mechanism as described in the OCPP specification.

Prerequisite(s) N/a
Before (Preparations)
Configuration State: N/a
Memory State: N/a
Charging State: State is EVConnectedPreSession

Test scenario
Charging Station CSMS
1. The OCTT sends a TransactionEventRequest with
    - triggerReason Authorized
    - idToken <Valid id token configured in AuthorizationCache>
    - eventType Updated

    Note(s):
        - TxStartPoint contains ParkingBayOccupancy

2. The CSMS responds with a TransactionEventResponse
    - idTokenInfo.status Accepted
"""