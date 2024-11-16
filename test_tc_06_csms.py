"""
Test case name      Local start transaction - Authorization Blocked
Test case Id        TC_C_06_CSMS
Use case Id(s)      C01
Requirement(s)      C01.FR.07
System under test   CSMS

Description         When a Charging Station needs to charge an EV, it needs to authorize the EV Driver first at the CSMS before
                    the charging can be started or stopped.

Purpose             To verify whether the CSMS is able to report that an idToken is Blocked.

Prerequisite(s)     N/a

Test scenario
1. The OCTT sends an AuthorizeRequest with
    idToken.idToken <Configured blocked_idtoken_idtoken>
    idToken.type <Configured blocked_idtoken_type>

2. The CSMS responds with an AuthorizeResponse
    - idTokenInfo.status Blocked or Invalid
"""