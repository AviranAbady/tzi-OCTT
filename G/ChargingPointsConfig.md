# Charging Points Configuration - G (Availability) Test Suite

## Overview

All tests in the G test suite validate **CSMS** (Charging Station Management System) behavior for OCPP 2.0.1 Availability use cases (Change Availability and Connector Status Notifications). The tests simulate a mock Charging Point that connects to the CSMS under test.

---

## Charging Point Identity & Connection

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Charging Point ID** | `BASIC_AUTH_CP` | `CP_1` | The identity used to connect to the CSMS |
| **Password** | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for CP_1 |
| **CSMS Address** | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket endpoint of the CSMS |
| **Security Profile** | - | **1 (Basic Authentication)** | All G tests use HTTP Basic Auth over ws:// |
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
| **EVSE ID** | `CONFIGURED_EVSE_ID` | `1` | The EVSE used for EVSE-level and connector-level tests |
| **Connector ID** | `CONFIGURED_CONNECTOR_ID` | `1` | The connector within the EVSE |

---

## Authorization / IdToken Configuration

Required for tests that involve transactions (G11, G14, G17).

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Valid IdToken** | `VALID_ID_TOKEN` | `100000C01` | A token the CSMS must accept as Authorized |
| **Valid IdToken Type** | `VALID_ID_TOKEN_TYPE` | `Central` | Token type (Central, ISO14443, ISO15693, etc.) |

> **CSMS Requirement:** The CSMS must have this idToken pre-configured and respond with `AuthorizationStatus: Accepted` when it receives an `AuthorizeRequest` with this token.

---

## Timeout Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **CSMS Action Timeout** | `CSMS_ACTION_TIMEOUT` | `30` (seconds) | G03, G04, G05, G06, G07, G08, G11, G14, G17 |
| **Transaction Duration** | `TRANSACTION_DURATION` | `5` (seconds) | G11, G14, G17 |

---

## CSMS Configuration Requirements Per Test

### Change Availability Tests

| Test | Use Case | Target Level | CSMS Must Send | operationalStatus | evse.id | evse.connectorId | Expected Response |
|---|---|---|---|---|---|---|---|
| **TC_G_03** | G03 | EVSE | `ChangeAvailabilityRequest` | Inoperative | Configured (1) | omit | Accepted |
| **TC_G_04** | G03 | EVSE | `ChangeAvailabilityRequest` | Operative | Configured (1) | omit | Accepted |
| **TC_G_05** | G04 | Charging Station | `ChangeAvailabilityRequest` | Inoperative | omit | omit | Accepted |
| **TC_G_06** | G04 | Charging Station | `ChangeAvailabilityRequest` | Operative | omit | omit | Accepted |
| **TC_G_07** | G03 | Connector | `ChangeAvailabilityRequest` | Inoperative | Configured (1) | Configured (1) | Accepted |
| **TC_G_08** | G03 | Connector | `ChangeAvailabilityRequest` | Operative | Configured (1) | Configured (1) | Accepted |

### Change Availability During Ongoing Transaction

| Test | Use Case | Target Level | CSMS Must Send | operationalStatus | evse.id | evse.connectorId | Expected Response |
|---|---|---|---|---|---|---|---|
| **TC_G_11** | G03 | EVSE | `ChangeAvailabilityRequest` | Inoperative | Configured (1) | omit | **Scheduled** |
| **TC_G_14** | G04 | Charging Station | `ChangeAvailabilityRequest` | Inoperative | omit | omit | **Scheduled** |
| **TC_G_17** | G03 | Connector | `ChangeAvailabilityRequest` | Inoperative | Configured (1) | Configured (1) | **Scheduled** |

### Connector Status Notification Tests

| Test | Use Case | Requirement | Direction | Message |
|---|---|---|---|---|
| **TC_G_20** | G05 | G05.FR.03 | CP -> CSMS | `NotifyEventRequest` (ConnectorPlugRetentionLock Problem=true) -> CSMS responds `NotifyEventResponse` |

---

## Pre-Requisite States Per Test

| Test | Boot | Available | Unavailable (Before) | Authorized | EnergyTransferStarted |
|---|---|---|---|---|---|
| TC_G_03 | Yes | Yes | - | - | - |
| TC_G_04 | Yes | - | Yes | - | - |
| TC_G_05 | Yes | Yes | - | - | - |
| TC_G_06 | Yes | - | Yes | - | - |
| TC_G_07 | Yes | Yes | - | - | - |
| TC_G_08 | Yes | - | Yes | - | - |
| TC_G_11 | Yes | Yes | - | Yes | Yes |
| TC_G_14 | Yes | Yes | - | Yes | Yes |
| TC_G_17 | Yes | Yes | - | Yes | Yes |
| TC_G_20 | Yes | Yes | - | - | - |

---

## CSMS Capabilities Required

| Capability | Required By Tests |
|---|---|
| Send `ChangeAvailabilityRequest` (EVSE-level, Inoperative) | G03, G11 |
| Send `ChangeAvailabilityRequest` (EVSE-level, Operative) | G04 |
| Send `ChangeAvailabilityRequest` (Station-level, Inoperative) | G05, G14 |
| Send `ChangeAvailabilityRequest` (Station-level, Operative) | G06 |
| Send `ChangeAvailabilityRequest` (Connector-level, Inoperative) | G07, G17 |
| Send `ChangeAvailabilityRequest` (Connector-level, Operative) | G08 |
| Handle `StatusNotificationRequest` | All tests |
| Handle `NotifyEventRequest` | G03, G04, G05, G06, G07, G08, G11, G20 |
| Handle `BootNotificationRequest` (respond Accepted) | All tests |
| Handle `AuthorizeRequest` (respond Accepted) | G11, G14, G17 |
| Handle `TransactionEventRequest` | G11, G14, G17 |

---

## CSMS Charging Point Setup Checklist

To run the full G test suite, the CSMS must have the following charging point configured:

### 1. Charging Point Registration

- **Charging Point ID:** `CP_1`
- **Password:** `0123456789123456`
- **Security Profile:** 1 (Basic Authentication over WebSocket)
- **Protocol:** OCPP 2.0.1

### 2. EVSE Configuration

- **EVSE 1** with **Connector 1** (at minimum)

### 3. Authorization

- **IdToken:** `100000C01` with type `Central` must be authorized (status: `Accepted`)
- Required only for transaction-based tests (G11, G14, G17)

### 4. Environment Variables Summary

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# EVSE/Connector
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"

# Authorization (for G11, G14, G17)
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"
export TRANSACTION_DURATION="5"
```
