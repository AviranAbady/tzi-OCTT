# Charging Points Configuration - Test Set B (Provisioning)

## Overview

Test set B requires **1 charging point** configured in the CSMS using Security Profile 1 (Basic Auth over WS). Several tests also require transaction-related configuration (EVSE, connector, ID tokens) and network profile settings.

---

## Charging Points

### 1. BASIC_AUTH_CP (Security Profile 1)

| Property | Value |
|---|---|
| **Env Variable** | `BASIC_AUTH_CP` |
| **Security Profile** | 1 |
| **Transport** | WS (unsecured WebSocket) |
| **Authentication** | HTTP Basic Auth (username = Charging Station ID) |
| **Password Env Variable** | `BASIC_AUTH_CP_PASSWORD` |
| **Connection URL** | `{CSMS_ADDRESS}/{BASIC_AUTH_CP}` |

**Used in tests:** All 22 tests (TC_B_01 through TC_B_58)

**CSMS requirements:**
- Must accept valid Basic Auth credentials
- Must accept BootNotification and respond with Accepted
- Must be configurable to respond with Pending or Rejected to BootNotification (TC_B_02, TC_B_30, TC_B_31)
- Must support Get/Set Variables operations
- Must support GetBaseReport (ConfigurationInventory, FullInventory, SummaryInventory)
- Must support GetReport with componentCriteria
- Must support Reset (OnIdle and Immediate) for both Charging Station and EVSE level
- Must support SetNetworkProfile
- Must support TriggerMessage
- Must validate WebSocket subprotocol negotiation (ocpp2.0.1)
- Must respond with SecurityError CALLERROR for unauthorized messages during Pending/Rejected state

---

## Environment Variables

### Connection Endpoints

| Variable | Description | Example |
|---|---|---|
| `CSMS_ADDRESS` | WebSocket (WS) endpoint for SP1 connections | `ws://csms.example.com:8080` |

### Charging Point Identifiers

| Variable | Description |
|---|---|
| `BASIC_AUTH_CP` | Charging Station ID for SP1 (Basic Auth) |

### Credentials

| Variable | Description |
|---|---|
| `BASIC_AUTH_CP_PASSWORD` | Password for Basic Auth |

### EVSE / Connector Configuration

| Variable | Description | Default |
|---|---|---|
| `CONFIGURED_EVSE_ID` | EVSE ID used in transaction and reset tests | `1` |
| `CONFIGURED_CONNECTOR_ID` | Connector ID used in transaction tests | `1` |

### ID Token Configuration

| Variable | Description | Default |
|---|---|---|
| `VALID_ID_TOKEN` | Valid ID token for authorization in transaction tests | `100000C01` |
| `VALID_ID_TOKEN_TYPE` | Type of the valid ID token | `Central` |

### Network Profile Configuration (TC_B_42)

| Variable | Description | Default |
|---|---|---|
| `CONFIGURED_CONFIGURATION_SLOT` | Expected configuration slot in SetNetworkProfileRequest | *(optional)* |
| `CONFIGURED_MESSAGE_TIMEOUT` | Expected messageTimeout value | *(optional)* |
| `CONFIGURED_OCPP_CSMS_URL` | Expected ocppCsmsUrl value | *(optional)* |
| `CONFIGURED_OCPP_INTERFACE` | Expected ocppInterface value | *(optional)* |
| `CONFIGURED_SECURITY_PROFILE` | Expected securityProfile value | *(optional)* |

### Timeouts

| Variable | Description | Default |
|---|---|---|
| `CSMS_ACTION_TIMEOUT` | Timeout (seconds) for waiting on CSMS-initiated actions | `30` |

---

## CSMS Configuration Prerequisites

Some tests require the CSMS to be pre-configured in a specific state:

| Prerequisite | Required By |
|---|---|
| CSMS responds to first BootNotification with **Pending** | TC_B_02 |
| CSMS responds to first BootNotification with **Pending or Rejected** | TC_B_30, TC_B_31 |
| CSMS supports optional **SummaryInventory** report | TC_B_14 |

---

## Test-to-Charging-Point Matrix

All tests use the single **BASIC_AUTH_CP** charging point.

| Test Case | Name | Category | Requires EVSE/Connector | Requires ID Token |
|---|---|---|---|---|
| TC_B_01 | Cold Boot CS - Accepted | Boot | | |
| TC_B_02 | Cold Boot CS - Pending | Boot | | |
| TC_B_06 | Get Variables - single value | Get/Set Variables | | |
| TC_B_07 | Get Variables - multiple values | Get/Set Variables | | |
| TC_B_08 | Get Variables - limit to max | Get/Set Variables | | |
| TC_B_09 | Set Variables - single value | Get/Set Variables | | |
| TC_B_10 | Set Variables - multiple values | Get/Set Variables | | |
| TC_B_12 | Get Base Report - ConfigurationInventory | Reporting | | |
| TC_B_13 | Get Base Report - FullInventory | Reporting | | |
| TC_B_14 | Get Base Report - SummaryInventory | Reporting | | |
| TC_B_18 | Get Custom Report - componentCriteria | Reporting | X | |
| TC_B_20 | Reset CS - No transaction - OnIdle | Reset | | |
| TC_B_21 | Reset CS - With transaction - OnIdle | Reset | X | X |
| TC_B_22 | Reset CS - With transaction - Immediate | Reset | X | X |
| TC_B_25 | Reset EVSE - No transaction | Reset | X | |
| TC_B_26 | Reset EVSE - With transaction - OnIdle | Reset | X | X |
| TC_B_27 | Reset EVSE - With transaction - Immediate | Reset | X | X |
| TC_B_30 | Cold Boot CS - Pending/Rejected - SecurityError | Boot | | |
| TC_B_31 | Cold Boot CS - Pending/Rejected - TriggerMessage | Boot | | |
| TC_B_42 | Set NetworkConnectionProfile - Accepted | Network Profile | | |
| TC_B_44 | Set NetworkConnectionProfile - Failed | Network Profile | | |
| TC_B_58 | WebSocket Subprotocol validation | WebSocket | | |

---

## Test Categories

### Boot / Registration (4 tests)
- **TC_B_01**: Cold Boot - CSMS accepts BootNotification
- **TC_B_02**: Cold Boot - CSMS responds Pending first, then Accepted
- **TC_B_30**: Cold Boot - CSMS responds Pending/Rejected, then rejects unauthorized messages with SecurityError
- **TC_B_31**: Cold Boot - CSMS responds Pending/Rejected, then sends TriggerMessage for BootNotification

### Get / Set Variables (5 tests)
- **TC_B_06**: Get single variable (OCPPCommCtrlr.OfflineThreshold)
- **TC_B_07**: Get multiple variables (OfflineThreshold + AuthorizeRemoteStart)
- **TC_B_08**: Get variables respecting ItemsPerMessageGetVariables limit (max 4)
- **TC_B_09**: Set single variable (OCPPCommCtrlr.OfflineThreshold = "123")
- **TC_B_10**: Set multiple variables (OfflineThreshold = "123", AuthorizeRemoteStart = "false")

### Reporting (4 tests)
- **TC_B_12**: GetBaseReport - ConfigurationInventory
- **TC_B_13**: GetBaseReport - FullInventory
- **TC_B_14**: GetBaseReport - SummaryInventory (optional)
- **TC_B_18**: GetReport with componentCriteria (Problem -> EmptyResultSet, Available -> Accepted)

### Reset (6 tests)
- **TC_B_20**: Reset Charging Station - No transaction - OnIdle (evseId omitted)
- **TC_B_21**: Reset Charging Station - With transaction - OnIdle (Scheduled, transaction ends, reboot)
- **TC_B_22**: Reset Charging Station - With transaction - Immediate (transaction stopped, reboot)
- **TC_B_25**: Reset EVSE - No transaction - OnIdle (evseId = configured EVSE)
- **TC_B_26**: Reset EVSE - With transaction - OnIdle (Scheduled, transaction ends)
- **TC_B_27**: Reset EVSE - With transaction - Immediate (transaction stopped)

### Network Profile (2 tests)
- **TC_B_42**: SetNetworkProfile - Accepted (validates all connectionData fields)
- **TC_B_44**: SetNetworkProfile - Failed (CS rejects the request)

### WebSocket (1 test)
- **TC_B_58**: Validates CSMS rejects unsupported subprotocol and selects ocpp2.0.1
