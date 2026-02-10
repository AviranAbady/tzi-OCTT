# Charging Points Configuration - E (Transactions) Test Suite

## Overview

All tests in the E test suite validate **CSMS** (Charging Station Management System) behavior for OCPP 2.0.1 Transaction Management use cases. The tests simulate a mock Charging Point that connects to the CSMS under test.

---

## Charging Point Identity & Connection

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Charging Point ID** | `BASIC_AUTH_CP` | `CP_1` | The identity used to connect to the CSMS |
| **Password** | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for CP_1 |
| **CSMS Address** | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket endpoint of the CSMS |
| **Security Profile** | - | **1 (Basic Authentication)** | All E tests use HTTP Basic Auth over ws:// |
| **WebSocket Subprotocol** | - | `ocpp2.0.1` | OCPP 2.0.1 protocol |

### Boot Notification Parameters

| Field | Value |
|---|---|
| `chargingStation.model` | `CP Model 1.0` |
| `chargingStation.vendorName` | `tzi.app` |
| `reason` | `PowerUp` |

---

## EVSE & Connector Configuration

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **EVSE ID** | `CONFIGURED_EVSE_ID` | `1` | The EVSE used for tests |
| **Connector ID** | `CONFIGURED_CONNECTOR_ID` | `1` | The connector within the EVSE |

---

## Authorization / IdToken Configuration

Required for most E tests that involve transactions.

### Valid IdToken

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Valid IdToken** | `VALID_ID_TOKEN` | `100000C01` | A token the CSMS must accept as Authorized |
| **Valid IdToken Type** | `VALID_ID_TOKEN_TYPE` | `Central` | Token type (Central, ISO14443, ISO15693, etc.) |

> **CSMS Requirement:** The CSMS must have this idToken pre-configured and respond with `AuthorizationStatus: Accepted` when it receives an `AuthorizeRequest` with this token.

### Invalid IdToken (TC_E_16 only)

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Invalid IdToken** | `INVALID_ID_TOKEN` | `100000C02` | A token the CSMS must reject (Invalid/Unknown) |
| **Invalid IdToken Type** | `INVALID_ID_TOKEN_TYPE` | `Cash` | Token type |

> **CSMS Requirement:** The CSMS must respond with a non-valid `idTokenInfo` (e.g. `Invalid` or `Unknown`) when this token is presented in a `TransactionEventRequest`.

---

## Timeout Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **CSMS Action Timeout** | `CSMS_ACTION_TIMEOUT` | `30` (seconds) | All tests |
| **Transaction Duration** | `TRANSACTION_DURATION` | `5` (seconds) | TC_E_29, TC_E_31, TC_E_33 (offline simulation wait) |

---

## CSMS Configuration Requirements Per Test

### Start Transaction Tests (Use Case E01)

| Test | Name | Use Case | Requirement | IdToken Required | Key Scenario |
|---|---|---|---|---|---|
| **TC_E_01** | PowerPathClosed | E01(S5) | E01.FR.05 | Yes | Auth first, then EV connection; chargingState: SuspendedEVSE -> Charging |
| **TC_E_02** | EnergyTransfer | E01(S6) | E01.FR.06 | Yes | Direct to charging; chargingState: Charging |
| **TC_E_09** | EVConnected | E01(S2) | E01.FR.02 | No | Cable triggers transaction; chargingState: EVConnected |
| **TC_E_10** | Authorized | E01(S3) | E01.FR.03 | Yes | Authorization triggers transaction; triggerReason: Authorized |
| **TC_E_11** | DataSigned | E01(S4) | E01.FR.04 | Yes | Signed meter value triggers transaction; includes signed meter data |
| **TC_E_12** | ParkingBayOccupied | E01(S1) | E01.FR.01 | No | EV detected by sensor; triggerReason: EVDetected |

### Local Start Transaction Tests (Use Cases E02, E03)

| Test | Name | Use Case | Requirement | IdToken Required | Key Scenario |
|---|---|---|---|---|---|
| **TC_E_03** | Cable plugin first | E02 | E02.FR.02 | Yes | Cable -> Auth -> Charging |
| **TC_E_04** | Authorization first | E03 | E03.FR.02 | Yes | Auth -> Cable -> Charging |
| **TC_E_38** | EV not ready | E03 | - | Yes | EV connects but suspended; chargingState: SuspendedEV |

### Stop Transaction Tests (Use Case E06)

| Test | Name | Use Case | Requirement | IdToken Required | Stopped Reason |
|---|---|---|---|---|---|
| **TC_E_07** | PowerPathClosed - Local | E06(S5) | E06.FR.06 | Yes | Local |
| **TC_E_08** | EnergyTransfer stopped - StopAuthorized | E06(S6) | E06.FR.07 | Yes | Local |
| **TC_E_14** | EVDisconnected - CS side | E06(S2) | E06.FR.02 | Yes | EVDisconnected |
| **TC_E_15** | StopAuthorized - Local | E06(S3) | E06.FR.03 | Yes | Local |
| **TC_E_16** | Deauthorized - Invalid idToken | E06(S3) | E06.FR.04, E01.FR.11, E01.FR.12 | Invalid | DeAuthorized |
| **TC_E_17** | Deauthorized - EV side disconnect | E06(S3) | E06.FR.04 | Yes | EVDisconnected |
| **TC_E_19** | ParkingBayUnoccupied | E06(S1) | E06.FR.01 | Yes | Local |
| **TC_E_20** | EVDisconnected - EV side (IEC 61851-1) | E06(S2), E10 | E06.FR.02 | Yes | EVDisconnected |
| **TC_E_21** | StopAuthorized - Remote (CSMS initiated) | E06(S3), F03 | E06.FR.03, F03.FR.01, F03.FR.09, F03.FR.10 | Yes | Remote |
| **TC_E_22** | EnergyTransfer stopped - SuspendedEV | E06(S6) | E06.FR.07 | Yes | StoppedByEV |
| **TC_E_39** | Deauthorized - Timeout | E03, E06 | E03.FR.04, E03.FR.05, E06.FR.04 | Yes | Timeout |

### Suspend/Resume Transaction Tests (Use Case E10)

| Test | Name | Use Case | Requirement | IdToken Required | Key Scenario |
|---|---|---|---|---|---|
| **TC_E_26** | Disconnect cable on EV-side | E10 | E10.FR.01 | Yes | Suspend then resume transaction |

### Transaction Status Tests (Use Case E14)

| Test | Name | Use Case | Requirements | Query Type | Transaction State | Messages In Queue |
|---|---|---|---|---|---|---|
| **TC_E_29** | Ongoing with messages | E14 | E14.FR.02, E14.FR.04 | With transactionId | Ongoing | Yes |
| **TC_E_30** | Ongoing without messages | E14 | E14.FR.02, E14.FR.05 | With transactionId | Ongoing | No |
| **TC_E_31** | Ended with messages | E14 | E14.FR.03, E14.FR.04 | With transactionId | Ended | Yes |
| **TC_E_33** | Without transactionId with messages | E14 | E14.FR.06, E14.FR.07 | Without transactionId | N/A | Yes |
| **TC_E_34** | Without transactionId without messages | E14 | E14.FR.06, E14.FR.08 | Without transactionId | N/A | No |

### Sequence Number Tests (Use Case E01)

| Test | Name | Use Case | Requirement | Key Scenario |
|---|---|---|---|---|
| **TC_E_53** | Reset Sequence Number | E01 | E01.FR.07 | Verify CSMS accepts seqNo=0 at start of each transaction |

---

## Pre-Requisite States Per Test

| Test | Boot | Available | Authorized | EnergyTransferStarted | EnergyTransferSuspended | StopAuthorized | EVConnectedPostSession | EVDisconnected |
|---|---|---|---|---|---|---|---|---|
| TC_E_01 | Yes | Yes | - | - | - | - | - | - |
| TC_E_02 | Yes | Yes | - | - | - | - | - | - |
| TC_E_03 | Yes | Yes | Yes | - | - | - | - | - |
| TC_E_04 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_07 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_08 | Yes | Yes | Yes | Yes | - | Yes | - | - |
| TC_E_09 | Yes | Yes | - | - | - | - | - | - |
| TC_E_10 | Yes | Yes | - | - | - | - | - | - |
| TC_E_11 | Yes | Yes | - | - | - | - | - | - |
| TC_E_12 | Yes | Yes | - | - | - | - | - | - |
| TC_E_14 | Yes | Yes | Yes | Yes | - | Yes | Yes | Yes |
| TC_E_15 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_16 | Yes | Yes | - | - | - | - | - | - |
| TC_E_17 | Yes | Yes | Yes | Yes | Yes | - | - | - |
| TC_E_19 | Yes | Yes | Yes | Yes | - | Yes | Yes | - |
| TC_E_20 | Yes | Yes | Yes | Yes | Yes | - | - | Yes |
| TC_E_21 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_22 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_26 | Yes | Yes | Yes | Yes | Yes | - | - | - |
| TC_E_29 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_30 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_31 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_33 | Yes | Yes | Yes | Yes | - | - | - | - |
| TC_E_34 | Yes | Yes | - | - | - | - | - | - |
| TC_E_38 | Yes | Yes | Yes | - | - | - | - | - |
| TC_E_39 | Yes | Yes | Yes | - | - | - | - | - |
| TC_E_53 | Yes | Yes | Yes | Yes | - | Yes | Yes | Yes |

---

## CSMS Charging Point Setup Checklist

To run the full E test suite, the CSMS must have the following charging point configured:

### 1. Charging Point Registration

- **Charging Point ID:** `CP_1`
- **Password:** `0123456789123456`
- **Security Profile:** 1 (Basic Authentication over WebSocket)
- **Protocol:** OCPP 2.0.1

### 2. EVSE Configuration

- **EVSE 1** with **Connector 1** (at minimum)

### 3. Authorization

- **Valid IdToken:** `100000C01` with type `Central` must be authorized (status: `Accepted`)
- **Invalid IdToken:** `100000C02` with type `Cash` must be rejected (status: `Invalid` or `Unknown`)

### 4. Transaction Capabilities the CSMS Must Support

| Capability | Required By Tests |
|---|---|
| Accept `TransactionEventRequest` (eventType=Started) | E01, E02, E03, E04, E09, E10, E11, E12, E38 |
| Accept `TransactionEventRequest` (eventType=Updated) | E07, E08, E14, E15, E17, E19, E20, E21, E22, E26, E29, E30, E31, E33, E39, E53 |
| Accept `TransactionEventRequest` (eventType=Ended) | E07, E08, E14, E15, E16, E17, E19, E20, E21, E22, E39, E53 |
| Respond with `idTokenInfo` in `TransactionEventResponse` | E16, E17, E39 |
| Respond with non-valid `idTokenInfo` for invalid tokens | E16 |
| Respond with non-valid `idTokenInfo` to trigger deauthorization | E17, E39 |
| Send `RequestStopTransactionRequest` (remote stop) | E21 |
| Send `GetTransactionStatusRequest` (with transactionId) | E29, E30, E31 |
| Send `GetTransactionStatusRequest` (without transactionId) | E33, E34 |
| Handle offline/queued `TransactionEventRequest` (offline=true) | E29, E31, E33 |
| Handle `StatusNotificationRequest` | All tests |
| Handle `AuthorizeRequest` and respond with valid status | E01, E02, E03, E04, E10, E11, E15, E21, E26, E38, E39 |

### 5. Environment Variables Summary

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# EVSE/Connector
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"

# Authorization (Valid)
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"

# Authorization (Invalid - for TC_E_16)
export INVALID_ID_TOKEN="100000C02"
export INVALID_ID_TOKEN_TYPE="Cash"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"
export TRANSACTION_DURATION="5"  # Seconds for offline simulation (TC_E_29, TC_E_31, TC_E_33)
```
