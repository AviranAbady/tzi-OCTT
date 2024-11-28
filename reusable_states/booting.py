"""
State               Booting
System under test   Charging Station
Description         This state will prepare the Charging Station, so that it is still booting. The connection has not
                    been setup yet.
Before
    Configuration State:    N/a
    Memory State:           N/a
    Reusable State(s):      N/a

Scenario
1. The OCTT sends a ResetRequest with type Immediate
2. The Charging Station responds with a ResetResponse

Tool validations
* Step 2: Message: ResetResponse - status must be Accepted

Post condition - State is Booting
"""
