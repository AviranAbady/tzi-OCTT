# Charging Points Configuration - F (Remote Control) Test Suite

## Overview

> **Scope Notice:** This configuration is intended only for the `tzi-OCTT` OCPP 2.0.1 test suite and is not intended for production or general-purpose CSMS deployments.

All tests in the F test suite validate **CSMS** (Charging Station Management System) behavior for OCPP 2.0.1 Remote Control use cases. The tests simulate a mock Charging Point that connects to the CSMS under test. This suite covers Remote Start Transaction, Remote Unlock Connector, and Trigger Message scenarios.

---

## Charging Point Identity & Connection

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Charging Point ID** | `BASIC_AUTH_CP` | `CP_1` | The identity used to connect to the CSMS |
| **Password** | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for CP_1 |
| **CSMS Address** | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket endpoint of the CSMS |
| **Security Profile** | - | **1 (Basic Authentication)** | All F tests use HTTP Basic Auth over ws:// |
| **WebSocket Subprotocol** | - | `ocpp2.0.1` | OCPP 2.0.1 protocol |

### Boot Notification Parameters

| Field | Value |
|---|---|
| `chargingStation.model` | `CP Model 1.0` |
| `chargingStation.vendorName` | `tzi.app` |
| `reason` | `PowerUp` |

---

## IdToken Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **Valid IdToken** | `VALID_ID_TOKEN` | `100000C01` | F01, F02, F03, F04, F13, F14 |
| **Valid IdToken Type** | `VALID_ID_TOKEN_TYPE` | `Central` | F01, F02, F03, F04, F13, F14 |

---

## EVSE & Connector Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **EVSE ID** | `CONFIGURED_EVSE_ID` | `1` | F01, F02, F03, F04, F06, F11, F12, F13, F14, F23, F24 |
| **Connector ID** | `CONFIGURED_CONNECTOR_ID` | `1` | F01, F02, F03, F04, F06, F13, F14, F23, F24 |

---

## Timeout & Duration Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **CSMS Action Timeout** | `CSMS_ACTION_TIMEOUT` | `30` (seconds) | All tests |
| **Transaction Duration** | `TRANSACTION_DURATION` | `5` (seconds) | F04 (EVConnectTimeout wait) |

---

## CSMS Configuration Requirements Per Test

### Remote Start Transaction Tests (Use Cases F01, F02)

| Test | Name | CSMS Must Send | Key Behavior | idToken Required | AuthorizeRemoteStart |
|---|---|---|---|---|---|
| **TC_F_01** | Cable plugin first | `RequestStartTransactionRequest` | EV connects first, then CSMS sends remote start | Yes (validated) | N/a |
| **TC_F_02** | Remote start first - AuthorizeRemoteStart true | `RequestStartTransactionRequest` | CSMS sends remote start first, CS authorizes before starting | Yes (validated) | **true** |
| **TC_F_03** | Remote start first - AuthorizeRemoteStart false | `RequestStartTransactionRequest` | CSMS sends remote start first, CS starts without authorization | Yes (validated) | **false** |
| **TC_F_04** | Remote start first - Cable plugin timeout | `RequestStartTransactionRequest` | CSMS sends remote start, EV never connects, EVConnectTimeout fires | Yes (validated) | N/a |

### Remote Unlock Connector Tests (Use Case F05)

| Test | Name | CSMS Must Send | Expected Response |
|---|---|---|---|
| **TC_F_06** | Without ongoing transaction - Accepted | `UnlockConnectorRequest` (evseId, connectorId) | Unlocked |

### Trigger Message Tests (Use Case F06)

| Test | Name | CSMS Must Send | Requested Message | EVSE Specified | Before State | Expected Response |
|---|---|---|---|---|---|---|
| **TC_F_11** | MeterValues - Specific EVSE | `TriggerMessageRequest` | MeterValues | Yes | - | Accepted |
| **TC_F_12** | MeterValues - All EVSE | `TriggerMessageRequest` | MeterValues | No (omitted) | - | Accepted |
| **TC_F_13** | TransactionEvent - Specific EVSE | `TriggerMessageRequest` | TransactionEvent | Yes | EnergyTransferStarted | Accepted |
| **TC_F_14** | TransactionEvent - All EVSE | `TriggerMessageRequest` | TransactionEvent | No (omitted) | EnergyTransferStarted | Accepted |
| **TC_F_15** | LogStatusNotification - Idle | `TriggerMessageRequest` | LogStatusNotification | No | - | Accepted |
| **TC_F_18** | FirmwareStatusNotification - Idle | `TriggerMessageRequest` | FirmwareStatusNotification | No | - | Accepted |
| **TC_F_20** | Heartbeat | `TriggerMessageRequest` | Heartbeat | No | - | Accepted |
| **TC_F_23** | StatusNotification - Available | `TriggerMessageRequest` | StatusNotification | Yes | - | Accepted |
| **TC_F_24** | StatusNotification - Occupied | `TriggerMessageRequest` | StatusNotification | Yes | - (CS sets Occupied first) | Accepted |
| **TC_F_27** | NotImplemented | `TriggerMessageRequest` | Any | N/a | - | **NotImplemented** |

---

## Requirements & Validations Per Test

| Test | Requirements | Key Validations |
|---|---|---|
| **TC_F_01** | N/a | RequestStartTransactionRequest: idToken matches configured, remoteStartId present |
| **TC_F_02** | F02.FR.01, F01.FR.01 | RequestStartTransactionRequest: idToken matches configured; AuthorizeResponse: idTokenInfo.status=Accepted |
| **TC_F_03** | F02.FR.01, F01.FR.02 | RequestStartTransactionRequest: idToken matches configured; No AuthorizeRequest needed |
| **TC_F_04** | E03.FR.04, E03.FR.05 | RequestStartTransactionRequest: idToken matches configured; EVConnectTimeout event sent |
| **TC_F_06** | N/a | UnlockConnectorRequest: evseId and connectorId match configured |
| **TC_F_11** | F06.FR.01, F06.FR.02 | TriggerMessageRequest: requestedMessage=MeterValues, evse.id matches configured |
| **TC_F_12** | F06.FR.01 | TriggerMessageRequest: requestedMessage=MeterValues, evse omitted |
| **TC_F_13** | F06.FR.01, F06.FR.02 | TriggerMessageRequest: requestedMessage=TransactionEvent, evse.id matches configured |
| **TC_F_14** | F06.FR.01 | TriggerMessageRequest: requestedMessage=TransactionEvent, evse omitted |
| **TC_F_15** | F06.FR.01 | TriggerMessageRequest: requestedMessage=LogStatusNotification |
| **TC_F_18** | F06.FR.01 | TriggerMessageRequest: requestedMessage=FirmwareStatusNotification |
| **TC_F_20** | F06.FR.01 | TriggerMessageRequest: requestedMessage=Heartbeat; HeartbeatResponse has currentTime |
| **TC_F_23** | F06.FR.01, F06.FR.02, F06.FR.13 | TriggerMessageRequest: requestedMessage=StatusNotification, evse.id matches configured |
| **TC_F_24** | F06.FR.01, F06.FR.02, F06.FR.13 | TriggerMessageRequest: requestedMessage=StatusNotification, evse.id matches configured |
| **TC_F_27** | F06.FR.08 | TriggerMessageRequest received; CS responds with NotImplemented |

---

## Pre-Requisite States Per Test

| Test | Boot | Available | Before State | Prerequisites |
|---|---|---|---|---|
| TC_F_01 | Yes | Yes | EVConnectedPreSession | - |
| TC_F_02 | Yes | Yes | - | AuthEnabled NOT ReadOnly with value false |
| TC_F_03 | Yes | Yes | - | - |
| TC_F_04 | Yes | Yes | - | - |
| TC_F_06 | Yes | Yes | - | - |
| TC_F_11 | Yes | Yes | - | - |
| TC_F_12 | Yes | Yes | - | - |
| TC_F_13 | Yes | Yes | Authorized + EnergyTransferStarted | Active charging session required |
| TC_F_14 | Yes | Yes | Authorized + EnergyTransferStarted | Active charging session required |
| TC_F_15 | Yes | Yes | - | - |
| TC_F_18 | Yes | Yes | - | - |
| TC_F_20 | Yes | Yes | - | - |
| TC_F_23 | Yes | Yes | - | - |
| TC_F_24 | Yes | Yes | CS sends Occupied status first | - |
| TC_F_27 | Yes | Yes | - | - |

---

## Manual CSMS Actions Required Per Test

| Test | Manual Action |
|---|---|
| **TC_F_01** | Trigger the CSMS to send `RequestStartTransactionRequest` to the CS |
| **TC_F_02** | Trigger the CSMS to send `RequestStartTransactionRequest` to the CS |
| **TC_F_03** | Trigger the CSMS to send `RequestStartTransactionRequest` to the CS |
| **TC_F_04** | Trigger the CSMS to send `RequestStartTransactionRequest` to the CS |
| **TC_F_06** | Trigger the CSMS to send `UnlockConnectorRequest` to the CS |
| **TC_F_11** | Trigger the CSMS to send `TriggerMessageRequest` (MeterValues, specific EVSE) |
| **TC_F_12** | Trigger the CSMS to send `TriggerMessageRequest` (MeterValues, all EVSE) |
| **TC_F_13** | Trigger the CSMS to send `TriggerMessageRequest` (TransactionEvent, specific EVSE) |
| **TC_F_14** | Trigger the CSMS to send `TriggerMessageRequest` (TransactionEvent, all EVSE) |
| **TC_F_15** | Trigger the CSMS to send `TriggerMessageRequest` (LogStatusNotification) |
| **TC_F_18** | Trigger the CSMS to send `TriggerMessageRequest` (FirmwareStatusNotification) |
| **TC_F_20** | Trigger the CSMS to send `TriggerMessageRequest` (Heartbeat) |
| **TC_F_23** | Trigger the CSMS to send `TriggerMessageRequest` (StatusNotification, specific EVSE) |
| **TC_F_24** | Trigger the CSMS to send `TriggerMessageRequest` (StatusNotification, specific EVSE) |
| **TC_F_27** | Trigger the CSMS to send `TriggerMessageRequest` (any message) |

---

## CSMS Charging Point Setup Checklist

To run the full F test suite, the CSMS must have the following charging point configured:

### 1. Charging Point Registration

- **Charging Point ID:** `CP_1`
- **Password:** `0123456789123456`
- **Security Profile:** 1 (Basic Authentication over WebSocket)
- **Protocol:** OCPP 2.0.1

### 2. EVSE Configuration

- **EVSE 1** with **Connector 1** (at minimum)

### 3. IdToken Configuration

- A valid idToken `100000C01` of type `Central` must be recognized and accepted by the CSMS
- The CSMS must respond with `AuthorizeResponse(idTokenInfo.status=Accepted)` for this token (required by TC_F_02)

### 4. Remote Control Capabilities the CSMS Must Support

| Capability | Required By Tests |
|---|---|
| Send `RequestStartTransactionRequest` with valid idToken | F01, F02, F03, F04 |
| Respond to `AuthorizeRequest` with status Accepted | F02 |
| Send `UnlockConnectorRequest` with evseId and connectorId | F06 |
| Send `TriggerMessageRequest` with requestedMessage=MeterValues (with evse) | F11 |
| Send `TriggerMessageRequest` with requestedMessage=MeterValues (without evse) | F12 |
| Send `TriggerMessageRequest` with requestedMessage=TransactionEvent (with evse) | F13 |
| Send `TriggerMessageRequest` with requestedMessage=TransactionEvent (without evse) | F14 |
| Send `TriggerMessageRequest` with requestedMessage=LogStatusNotification | F15 |
| Send `TriggerMessageRequest` with requestedMessage=FirmwareStatusNotification | F18 |
| Send `TriggerMessageRequest` with requestedMessage=Heartbeat | F20 |
| Send `TriggerMessageRequest` with requestedMessage=StatusNotification (with evse) | F23, F24 |
| Send `TriggerMessageRequest` with any requestedMessage | F27 |
| Accept `TransactionEventRequest` (Started, Updated, Ended) | F01, F02, F03, F04, F13, F14 |
| Accept `MeterValuesRequest` | F11, F12 |
| Accept `StatusNotificationRequest` | F23, F24 |
| Accept `NotifyEventRequest` | F23, F24 |
| Accept `LogStatusNotificationRequest` | F15 |
| Accept `FirmwareStatusNotificationRequest` | F18 |
| Accept `HeartbeatRequest` and respond with currentTime | F20 |

### 5. Environment Variables Summary

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# IdToken
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"

# EVSE
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"
export TRANSACTION_DURATION="5"
```
