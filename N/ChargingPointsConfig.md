# Charging Points Configuration - N Test Suite (Diagnostics, Monitoring & Customer Information)

## Overview

All tests in the N suite target **OCPP 2.0.1** and test the **CSMS** as the system under test. The simulated Charging Station connects via WebSocket using **Basic Authentication (Security Profile 1)**.

---

## Charging Point: CP_1

This is the single charging point used across **all 30 test cases** (TC_N_01 through TC_N_63).

### Identity & Authentication

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| Charging Point ID | `BASIC_AUTH_CP` | `CP_1` | Unique identifier for the charging point in the CSMS |
| Password | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password (16 characters) |
| Security Profile | — | **1 (Basic Auth)** | HTTP Basic Authentication over WebSocket |
| OCPP Protocol | — | `ocpp2.0.1` | WebSocket subprotocol |

### Connection

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| CSMS Address | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket URL of the CSMS |
| Connection URI | — | `{CSMS_ADDRESS}/{CP_ID}` | Full WebSocket URI (e.g. `ws://localhost:9000/CP_1`) |

### Hardware Configuration

| Parameter | Env Variable | Default Value | Used By |
|-----------|-------------|---------------|---------|
| EVSE ID | `CONFIGURED_EVSE_ID` | `1` | TC_N_03, TC_N_08, TC_N_09, TC_N_21, TC_N_24, TC_N_48, TC_N_49, TC_N_50, TC_N_60 |
| Connector ID | `CONFIGURED_CONNECTOR_ID` | `1` | All tests |

### Timing

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| CSMS Action Timeout | `CSMS_ACTION_TIMEOUT` | `30` seconds | Max time to wait for CSMS-initiated requests |

### Authorization & Customer Information

| Parameter | Env Variable | Default Value | Used By |
|-----------|-------------|---------------|---------|
| ID Token | `VALID_ID_TOKEN` | `100000C01` | TC_N_27, TC_N_28, TC_N_29, TC_N_30, TC_N_31, TC_N_32, TC_N_46 |
| ID Token Type | `VALID_ID_TOKEN_TYPE` | `Central` | TC_N_27, TC_N_28, TC_N_29, TC_N_30, TC_N_31, TC_N_32, TC_N_46 |
| Local List Version | `LOCAL_LIST_VERSION` | `1` | TC_N_46 |

---

## CSMS Configuration Requirements Per Test

The CSMS must be configured to initiate specific actions when the Charging Station connects and reaches the `Available` state.

### Retrieve Log Information Tests (Use Case N01)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_25 | Diagnostics Log - Success | Send `GetLogRequest` | `logType = DiagnosticsLog`; CS responds Accepted, then sends Uploading → Uploaded status |
| TC_N_34 | Rejected | Send `GetLogRequest` | CS will respond `Rejected` |
| TC_N_35 | Security Log - Success | Send `GetLogRequest` | `logType = SecurityLog`; CS responds Accepted, then sends Uploading → Uploaded status |
| TC_N_36 | Second Request | Send **2** `GetLogRequest`s | First request triggers Uploading; second sent while first in progress; CS responds `AcceptedCanceled` for first, then processes second normally |

### Get Monitoring Report Tests (Use Case N02)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_01 | With monitoringCriteria | Send **2** `GetMonitoringReportRequest`s | 1st: `monitoringCriteria=DeltaMonitoring` (→ EmptyResultSet); 2nd: `monitoringCriteria=ThresholdMonitoring` (→ Accepted + report) |
| TC_N_02 | With component/variable | Send **2** `GetMonitoringReportRequest`s | 1st: `componentVariable[0]` = ChargingStation/Power (→ EmptyResultSet); 2nd: `componentVariable[0]` = EVSE(evse.id=1)/AvailabilityState (→ Accepted + report) |
| TC_N_03 | With criteria + component/variable | Send **2** `GetMonitoringReportRequest`s | 1st: `DeltaMonitoring` + EVSE/AvailabilityState (→ EmptyResultSet); 2nd: `ThresholdMonitoring` + ChargingStation/Power (→ Accepted + report) |
| TC_N_47 | Report all | Send `GetMonitoringReportRequest` | Both `monitoringCriteria` and `componentVariable` **omitted** (→ Accepted + report) |
| TC_N_60 | With criteria + list of components/variables | Send **2** `GetMonitoringReportRequest`s | 1st: `DeltaMonitoring` + [ChargingStation/AvailabilityState, EVSE/AvailabilityState] (→ EmptyResultSet); 2nd: `ThresholdMonitoring` + same list (→ Accepted + report) |

### Set Monitoring Base Tests (Use Case N03)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_05 | Success | Send **3** `SetMonitoringBaseRequest`s | `monitoringBase` = `All`, then `FactoryDefault`, then `HardWiredOnly` (all → Accepted) |

### Set Variable Monitoring Tests (Use Case N04)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_08 | One element | Send `SetVariableMonitoringRequest` | `setMonitoringData[0]`: value=1, type=Delta, severity=8, component=EVSE(evse.id=configured), variable=AvailabilityState |
| TC_N_09 | Multiple elements | Send `SetVariableMonitoringRequest` | `setMonitoringData[0]`: EVSE/AvailabilityState (Delta); `setMonitoringData[1]`: ChargingStation/AvailabilityState (Delta) |

### Set Monitoring Level Tests (Use Case N05)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_16 | Success | Send `SetMonitoringLevelRequest` | `severity = 4` (→ Accepted) |
| TC_N_17 | Out of range | Send `SetMonitoringLevelRequest` | `severity = 4`; CS will respond `Rejected` |

### Clear Monitoring Tests (Use Case N06)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_18 | Too many elements | Send `GetVariablesRequest` then **2+** `ClearVariableMonitoringRequest`s | CSMS must first query `MonitoringCtrlr.ItemsPerMessage` (CS reports 3), then split clearing across multiple requests not exceeding that limit |
| TC_N_44 | Rejected | Send `ClearVariableMonitoringRequest` | CS will respond with `clearMonitoringResult[0].status = Rejected` |

### Alert Event Tests (Use Case N07)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_21 | HardWiredMonitor | Respond to `NotifyEventRequest` | CS sends event with `eventNotificationType=HardWiredMonitor`; CSMS responds with empty `NotifyEventResponse` |
| TC_N_48 | Write-only variable | Respond to `NotifyEventRequest` | CS sends event with `actualValue=""` (empty); CSMS responds `NotifyEventResponse` |
| TC_N_49 | Cleared after reboot | Respond to `NotifyEventRequest` | CS sends event with `cleared=true`; CSMS responds `NotifyEventResponse` |
| TC_N_50 | Periodic Triggered | Respond to `NotifyEventRequest` | CS sends event with `trigger=Periodic`; CSMS responds `NotifyEventResponse` |

### Periodic Event Tests (Use Case N08)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_24 | Periodic event | Respond to **3** `NotifyEventRequest`s | CS sends periodic `NotifyEventRequest` 3 times; CSMS responds each time |

### Get Customer Information Tests (Use Case N09)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_27 | Accepted + data | Send `CustomerInformationRequest` | `report=true`, `idToken.idToken=<configured>`, `idToken.type=<configured>` (→ Accepted + NotifyCustomerInformation with data) |
| TC_N_28 | Accepted + no data | Send `CustomerInformationRequest` | `report=true`, `idToken` as above (→ Accepted + NotifyCustomerInformation with empty data) |
| TC_N_29 | Not Accepted | Send `CustomerInformationRequest` | `report=true`, `idToken` as above; CS will respond `Rejected` |

### Clear Customer Information Tests (Use Case N10)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_N_30 | Clear + report + data | Send `CustomerInformationRequest` | `report=true`, `clear=true`, `idToken` as configured (→ Accepted + NotifyCustomerInformation with data) |
| TC_N_31 | Clear + report + no data | Send `CustomerInformationRequest` | `report=true`, `clear=true`, `idToken` as configured (→ Accepted + NotifyCustomerInformation with empty data) |
| TC_N_32 | Clear + no report | Send `CustomerInformationRequest` | `report=false`, `clear=true`, `idToken` as configured (→ Accepted + NotifyCustomerInformation) |
| TC_N_46 | Update Local Auth List | Send `CustomerInformationRequest` then `SendLocalListRequest` | `report=true`, `clear=true`, `idToken` as configured; then `updateType=Differential`, `versionNumber=<configured>+1`, list entry with configured idToken and no `idTokenInfo` |
| TC_N_62 | Clear + report - customerIdentifier | Send `CustomerInformationRequest` | `report=true`, `clear=true`, `customerIdentifier="OpenChargeAlliance"` (→ Accepted + NotifyCustomerInformation) |
| TC_N_63 | Clear + report - customerCertificate | Send `CustomerInformationRequest` | `report=true`, `clear=true`, `customerCertificate=<hash data>` (→ Accepted + NotifyCustomerInformation) |

---

## CSMS Charging Point Setup Summary

To run the full N test suite, configure the following in your CSMS:

1. **Register Charging Point**
   - ID: `CP_1`
   - Security Profile: 1 (Basic Authentication)
   - Password: `0123456789123456`

2. **Hardware Topology**
   - 1 EVSE (ID: `1`)
   - 1 Connector per EVSE (ID: `1`)

3. **Authorization**
   - Register idToken `100000C01` (type: `Central`) as valid — required for TC_N_27, TC_N_28, TC_N_29, TC_N_30, TC_N_31, TC_N_32, TC_N_46
   - Register customer identifier `OpenChargeAlliance` — required for TC_N_62
   - Configure a customer certificate with hash data — required for TC_N_63

4. **Local Authorization List**
   - Configure a local authorization list with version `1` containing idToken `100000C01` — required for TC_N_46

5. **Monitoring**
   - CSMS must be able to trigger `GetMonitoringReportRequest` with various combinations of `monitoringCriteria` and `componentVariable`
   - CSMS must be able to trigger `SetMonitoringBaseRequest` with `monitoringBase` = All, FactoryDefault, HardWiredOnly
   - CSMS must be able to trigger `SetVariableMonitoringRequest` with one or more `setMonitoringData` elements targeting EVSE/AvailabilityState and ChargingStation/AvailabilityState
   - CSMS must be able to trigger `SetMonitoringLevelRequest` with `severity = 4`
   - CSMS must be able to trigger `ClearVariableMonitoringRequest` — and must respect `ItemsPerMessageClearVariableMonitoring` limit (TC_N_18)
   - CSMS must handle `NotifyEventRequest` (HardWiredMonitor, Periodic, cleared events) and respond with `NotifyEventResponse`

6. **Log Retrieval**
   - CSMS must be able to trigger `GetLogRequest` with `logType` = DiagnosticsLog and SecurityLog
   - CSMS must handle `LogStatusNotification` messages (Uploading, Uploaded, AcceptedCanceled)
   - For TC_N_36: CSMS must be able to send a **second** `GetLogRequest` while the first is in progress

7. **Customer Information**
   - CSMS must be able to trigger `CustomerInformationRequest` with `report=true/false`, `clear=true/false`
   - CSMS must support customer references by `idToken`, `customerIdentifier`, and `customerCertificate`
   - CSMS must handle `NotifyCustomerInformation` responses
   - For TC_N_46: CSMS must send `SendLocalListRequest` (Differential update) after clearing customer information

8. **Boot Notification Handling**
   - CSMS must respond with `status=Accepted` to `BootNotificationRequest`
