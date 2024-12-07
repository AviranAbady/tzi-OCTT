import json
import base64
import asyncio
import pytest
import os
from enum import Enum
from mock_charge_point import MockChargePoint

"""
Test case name      TLS - server-side certificate - Valid certificate
Test case Id        TC_A_04_CSMS
Use case Id(s)      A00
Requirement(s)      A00.FR.306,A00.FR.307,A00.FR.312,A00.FR.318,A00.FR.321,A00.FR.502,A00.FR.503,A00.FR.507,A00.FR.50
8,A00.FR.510
System under test   CSMS

Description         The CSMS uses a server-side certificate to identify itself to the Charging Station, when using
                    security profile 2 or 3.
                    
Purpose             To verify whether the CSMS is able to provide a valid server certificate and setup a secured
                    WebSocket connection.
                    
Prerequisite(s)     The CSMS supports security profile 2 and/or 3

Test Scenario
1. The OCTT terminates the connection and initiates a TLS handshake and sends a Client Hello to the CSMS.
2. The CSMS responds with a Server Hello With the <Configured server certificate>
3. The OCTT performs the following actions:
    Send client certificate
    Client Key Exchange
    Certificate verify
    Change Cipher Spec
    Finished

    Note(s):
    - The client certificate is only sent when the CSMS uses security profile 3.

4. The CSMS performs the following actions:
    Change Cipher Spec
    Finished
    
5. The OCTT sends a HTTP upgrade request to the CSMS
    Note(s):
    - The HTTP request only contains a username/password combination when the CSMS uses security profile 2.
    
6. The CSMS upgrades the connection to a (secured) WebSocket connection.
7. The OCTT sends a BootNotificationRequest with reason PowerUp
    chargingStation.model <Configured model>
    chargingStation.vendorName <Configured vendorName>
8. The CSMS responds with a BootNotificationResponse
9. The OCTT notifies the CSMS about the current state of all connectors.
    Message: StatusNotificationRequest
    - connectorStatus Available
    Message: NotifyEventRequest
    - trigger Delta
    - actualValue "Available"
    - component.name "Connector"
    - variable.name "AvailabilityState"
10. The CSMS responds according
"""

# async def test_tc_a_04():
#     pass