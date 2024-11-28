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