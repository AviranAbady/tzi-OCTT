"""
Test case name      Clear Authorization Data in Authorization Cache - Rejected
Test case Id        TC_C_38_CSMS
Use case Id(s)      C11
Requirement(s)      N/a
System under test   CSMS

Description         This test case covers how the Charging Station autonomously stores a record of previously presented
                    identifiers that have been successfully authorized by the CSMS in the Authorization Cache. (Successfully
                    meaning: a response received on a message containing an IdToken)
                    Purpose To verify if the CSMS is able to request the Charging Station to clear all identifiers from the Authorization
                    Cache according to the mechanism as described in the OCPP specification.

Prerequisite(s)     N/a
Before (Preparations)
    Configuration State:    N/a
    Memory State:           N/a
    Reusable State(s):      N/a

Test Scenario
1. The CSMS sends a ClearCacheRequest
2. The OCTT responds with a ClearCacheResponse with status Rejected
"""