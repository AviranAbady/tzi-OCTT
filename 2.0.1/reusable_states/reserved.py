"""
State               Reserved
System under test   Charging Station
Description         This state will prepare the Charging Station, so that one of its EVSE becomes reserved.
Before
    Configuration State: N/a
    Memory State: N/a
    Reusable State(s): N/a

Scenario
1. The OCTT sends a ReserveNowRequest with evseId is <Specified evseId (Configured evseId as a default)>
   idToken.idToken <Specified valid_idtoken_idtoken (Configured idToken as a default)>
   idToken.type <Specified valid_idtoken_type>
2. The Charging Station responds with a ReserveNowResponse
3. The Charging Station notifies the CSMS about the status change of the connector.
   Note(s):
        - The OCTT expects that the Charging Station sets the
        availabilityState of the EVSE and corresponding
        connectors to Reserved.
        - Reporting the AvailabilityState of the EVSE
        component itself is optional.

4. The OCTT responds accordingly.
Tool validations
* Step 2:
    Message: ReserveNowResponse
        - status must be Accepted
* Step 3:
    Message: StatusNotificationRequest
        - evseId not 0
        - connectorId not 0
        - connectorStatus must be Reserved

    Message: NotifyEventRequest
        - eventData[0].trigger must be Delta
        - eventData[0].actualValue must be Reserved
        - eventData[0].component.name must be Connector
        - eventData[0].evse.id not 0
        - eventData[0].evse.connectorId not 0
        - eventData[0].variable.name must be AvailabilityState

    Message: NotifyEventRequest (Optional)
        - eventData[0].trigger must be Delta
        - eventData[0].actualValue must be Reserved
        - eventData[0].component.name must be EVSE
        - eventData[0].variable.name must be AvailabilityState

Post condition State is Reserved
"""