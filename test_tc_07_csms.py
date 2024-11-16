"""
Test case name      Local start transaction - Authorization Expired
Test case Id        TC_C_07_CSMS
Use case Id(s)      C01
Requirement(s)      C01.FR.07
System under test   CSMS

Description         When a Charging Station needs to charge an EV, it needs to authorize the EV Driver first at the CSMS before
                    the charging can be started or stopped.

Purpose             To verify whether the CSMS is able to report that an idToken is Expired.

Prerequisite(s)     N/a

Before (Preparations)
Configuration State:    The IdToken configured as Expired at the OCTT, must be set as Expired at the CSMS.
Memory State:           N/a
Reusable State(s):      N/a

Test scenario
1. The OCTT sends an AuthorizeRequest with idToken.idToken <Configured expired_idtoken_idtoken>
idToken.type <Configured expired_idtoken_type>

2. The CSMS responds with an AuthorizeResponse
    - idTokenInfo.status Expired or Invalid
"""