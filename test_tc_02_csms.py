"""
Test case name      Local start transaction - Authorization Invalid/Unknown
Test case Id        TC_C_02_CSMS
Use case Id(s)      C01, C04, C06
Requirement(s)      C01.FR.07 OR C04.FR.01 OR C06.FR.04
System under test   CSMS

Description         When a Charging Station needs to charge an EV, it needs to authorize the EV Driver first at the CSMS before
                    the charging can be started or stopped.
                    Purpose To verify whether the CSMS is able to report that an idToken is NOT valid

Test Scenario
1. The OCTT sends an AuthorizeRequest with
    idToken.idToken <Configured invalid_idtoken_idtoken>
    idToken.type <Configured invalid_idtoken_type>
    
2. The CSMS responds with an AuthorizeResponse
"""