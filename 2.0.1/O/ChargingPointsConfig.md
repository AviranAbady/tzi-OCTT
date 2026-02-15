# Charging Points Configuration - O Test Suite (Display Message)

## Overview

> **Scope Notice:** This configuration is intended only for the `tzi-OCTT` OCPP 2.0.1 test suite and is not intended for production or general-purpose CSMS deployments.

All tests in the O suite target **OCPP 2.0.1** and test the **CSMS** as the system under test. The simulated Charging Station connects via WebSocket using **Basic Authentication (Security Profile 1)**.

---

## Charging Point: CP_1

This is the single charging point used across **all 21 test cases** (TC_O_01 through TC_O_28).

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
| EVSE ID | `CONFIGURED_EVSE_ID` | `1` | TC_O_06, TC_O_10, TC_O_27, TC_O_28 |
| Connector ID | `CONFIGURED_CONNECTOR_ID` | `1` | All tests |

### Timing

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| CSMS Action Timeout | `CSMS_ACTION_TIMEOUT` | `30` seconds | Max time to wait for CSMS-initiated requests |

### Authorization (Transaction Tests Only)

| Parameter | Env Variable | Default Value | Used By |
|-----------|-------------|---------------|---------|
| ID Token | `VALID_IDTOKEN_IDTOKEN` | `TEST_TOKEN_1` | TC_O_06, TC_O_10, TC_O_27, TC_O_28 |
| ID Token Type | `VALID_IDTOKEN_TYPE` | `ISO14443` | TC_O_06, TC_O_10, TC_O_27, TC_O_28 |

---

## CSMS Configuration Requirements Per Test

The CSMS must be configured to initiate specific actions when the Charging Station connects and reaches the `Available` state.

### Set Display Message Tests (Use Case O01 — Non-Transaction)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_O_01 | Set Display Message - Success | Send `SetDisplayMessageRequest` | `message.state` = configured state; CS responds `Accepted`. **O01.FR.04**: `message.transactionId` must be omitted |
| TC_O_13 | Display message at StartTime | Send `SetDisplayMessageRequest` | `message.startDateTime` = configured start time; CS responds `Accepted`. **O01.FR.05** |
| TC_O_14 | Remove message after EndTime | Send `SetDisplayMessageRequest` | `message.endDateTime` = configured end time; CS responds `Accepted`. **O01.FR.05** |
| TC_O_17 | NotSupportedPriority | Send `SetDisplayMessageRequest` | `message.priority` = a configured priority; CS will respond `NotSupportedPriority` |
| TC_O_18 | NotSupportedState | Send `SetDisplayMessageRequest` | `message.state` = a configured state; CS will respond `NotSupportedState` |
| TC_O_19 | NotSupportedMessageFormat | Send `SetDisplayMessageRequest` | CS will respond `NotSupportedMessageFormat` |
| TC_O_25 | Send Specific state | Send `SetDisplayMessageRequest` | `message.state` = a configured state (e.g. `Charging`); CS responds `Accepted` |
| TC_O_26 | Rejected | Send `SetDisplayMessageRequest` | `message.priority` = `NormalCycle`; CS will respond `Rejected` |

### Set Display Message - Specific Transaction Tests (Use Case O02)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_O_06 | Specific transaction - Success | Send `SetDisplayMessageRequest` | Reusable State: `EnergyTransferStarted`. `message.transactionId` must match the CS transaction. CS responds `Accepted`, then executes `EVDisconnected` |
| TC_O_10 | Specific transaction - UnknownTransaction | Send `SetDisplayMessageRequest` | Reusable State: `EnergyTransferStarted`. `message.transactionId` must be present (not omitted) but does not match a known transaction. CS responds `UnknownTransaction` |
| TC_O_27 | Specific transaction - StartTime | Send `SetDisplayMessageRequest` | Reusable State: `EnergyTransferStarted`. `message.state` = omitted, `message.startDateTime` = configured, `message.endDateTime` = omitted, `message.transactionId` = CS transaction. CS responds `Accepted` |
| TC_O_28 | Specific transaction - EndTime | Send `SetDisplayMessageRequest` | Reusable State: `EnergyTransferStarted`. `message.state` = omitted, `message.startDateTime` = omitted, `message.endDateTime` = configured, `message.transactionId` = CS transaction. CS responds `Accepted` |

### Get All Display Messages Tests (Use Case O03)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_O_02 | Get all - Success | Send `SetDisplayMessageRequest` then `GetDisplayMessagesRequest` | Memory State: a display message is configured first. `id`, `priority`, `state` all **omitted**. CS responds `Accepted` + sends `NotifyDisplayMessagesRequest`; CSMS responds with `NotifyDisplayMessagesResponse` |
| TC_O_03 | Get all - No messages configured | Send `GetDisplayMessagesRequest` | No display messages configured. CS responds `Unknown` |

### Get Specific Display Messages Tests (Use Case O04)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_O_07 | By Id | Send `SetDisplayMessageRequest` then `GetDisplayMessagesRequest` | Memory State: message configured. `id` = configured message id, `priority`/`state` **omitted**. CS responds `Accepted` + sends `NotifyDisplayMessagesRequest` |
| TC_O_08 | By Priority | Send `SetDisplayMessageRequest` then `GetDisplayMessagesRequest` | Memory State: message with configured priority. `priority` = configured priority, `id`/`state` **omitted**. CS responds `Accepted` + sends `NotifyDisplayMessagesRequest` |
| TC_O_09 | By State | Send `SetDisplayMessageRequest` then `GetDisplayMessagesRequest` | Memory State: message with configured state. `state` = configured state, `priority`/`id` **omitted**. CS responds `Accepted` + sends `NotifyDisplayMessagesRequest` |
| TC_O_11 | Unknown parameters | Send `SetDisplayMessageRequest` then `GetDisplayMessagesRequest` | Memory State: message configured. `id` = a **different** id (not matching the configured message). CS responds `Unknown` |

### Clear Display Message Tests (Use Case O05)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_O_04 | Clear - Success | Send `SetDisplayMessageRequest` then `ClearDisplayMessageRequest` | Memory State: message configured. `id` must match the previously set message id. CS responds `Accepted` |
| TC_O_05 | Clear - Unknown Key | Send `ClearDisplayMessageRequest` | No matching message configured. CS responds `Unknown` |

### Replace Display Message Tests (Use Case O06)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_O_12 | Replace DisplayMessage | Send **2** `SetDisplayMessageRequest`s | Memory State: message configured. Second request must use **same** `message.id` as the first. CS responds `Accepted` to both |

---

## CSMS Charging Point Setup Summary

To run the full O test suite, configure the following in your CSMS:

1. **Register Charging Point**
   - ID: `CP_1`
   - Security Profile: 1 (Basic Authentication)
   - Password: `0123456789123456`

2. **Hardware Topology**
   - 1 EVSE (ID: `1`)
   - 1 Connector per EVSE (ID: `1`)

3. **Authorization**
   - Register idToken `TEST_TOKEN_1` (type: `ISO14443`) as valid — required for TC_O_06, TC_O_10, TC_O_27, TC_O_28

4. **Display Message Capabilities**
   - CSMS must be able to send `SetDisplayMessageRequest` with configurable `message.id`, `message.priority`, `message.message.format`, `message.state`, `message.startDateTime`, `message.endDateTime`, and `message.transactionId`
   - CSMS must be able to send `GetDisplayMessagesRequest` with optional filters: `id` (list), `priority`, `state`
   - CSMS must be able to send `ClearDisplayMessageRequest` with a specific `id`
   - CSMS must handle `NotifyDisplayMessagesRequest` and respond with `NotifyDisplayMessagesResponse`

5. **Transaction Support (TC_O_06, TC_O_10, TC_O_27, TC_O_28)**
   - CSMS must accept `AuthorizeRequest` and respond with `status=Accepted` for the configured idToken
   - CSMS must accept `TransactionEventRequest` (Started, Updated) and respond with `TransactionEventResponse`
   - CSMS must be able to send `SetDisplayMessageRequest` with `message.transactionId` matching an active transaction
   - For TC_O_10: CSMS must be able to send `SetDisplayMessageRequest` with a `transactionId` that does not match any known transaction

6. **Message Replacement (TC_O_12)**
   - CSMS must be able to send a second `SetDisplayMessageRequest` with the same `message.id` as a previously sent message

7. **Boot Notification Handling**
   - CSMS must respond with `status=Accepted` to `BootNotificationRequest`
