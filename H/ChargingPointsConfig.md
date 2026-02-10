# Charging Points Configuration - H (Reservation) Test Suite

## Overview

All tests in the H test suite validate **CSMS** (Charging Station Management System) behavior for OCPP 2.0.1 Reservation use cases. The tests simulate a mock Charging Point that connects to the CSMS under test.

---

## Charging Point Identity & Connection

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Charging Point ID** | `BASIC_AUTH_CP` | `CP_1` | The identity used to connect to the CSMS |
| **Password** | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for CP_1 |
| **CSMS Address** | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket endpoint of the CSMS |
| **Security Profile** | - | **1 (Basic Authentication)** | All H tests use HTTP Basic Auth over ws:// |
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
| **EVSE ID** | `CONFIGURED_EVSE_ID` | `1` | The EVSE used for specific-EVSE reservation tests |
| **Connector ID** | `CONFIGURED_CONNECTOR_ID` | `1` | The connector within the EVSE |
| **Number of EVSEs** | `CONFIGURED_NUMBER_OF_EVSES` | `1` | Total EVSEs in the charging station (used by H14) |
| **Connector Type** | `CONFIGURED_CONNECTOR_TYPE` | `cType2` | Connector type for type-based reservation (used by H15) |

---

## Authorization / IdToken Configuration

Required for most reservation tests (H01, H07, H08, H14, H15, H17, H19, H20).

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Valid IdToken** | `VALID_ID_TOKEN` | `100000C01` | A token the CSMS must accept as Authorized |
| **Valid IdToken Type** | `VALID_ID_TOKEN_TYPE` | `Central` | Token type (Central, ISO14443, ISO15693, etc.) |
| **Group IdToken** | `GROUP_ID` | `GROUP001` | Group idToken for group-based reservations (used by H19) |

> **CSMS Requirement:** The CSMS must have idToken `100000C01` pre-configured and respond with `AuthorizationStatus: Accepted` when it receives an `AuthorizeRequest` with this token. For H19, a groupIdToken must also be configured and associated with the idToken.

---

## Timeout & Duration Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **CSMS Action Timeout** | `CSMS_ACTION_TIMEOUT` | `30` (seconds) | All tests |
| **Transaction Duration** | `TRANSACTION_DURATION` | `5` (seconds) | H07 (reservation expiry duration) |

---

## CSMS Configuration Requirements Per Test

### Reserve EVSE Tests (Specific EVSE)

| Test | Use Case | CSMS Must Send | evseId | connectorType | idToken | groupIdToken | CS Response |
|---|---|---|---|---|---|---|---|
| **TC_H_01** | H01(S2), H03 | `ReserveNowRequest` | Configured (1) | omit | Valid | omit | Accepted |
| **TC_H_07** | H01(S2), H04 | `ReserveNowRequest` | Configured (1) | omit | Valid | omit | Accepted |
| **TC_H_19** | H01, H03 | `ReserveNowRequest` | Configured (1) | omit | Valid | **Required** | Accepted |
| **TC_H_20** | H01 | `ReserveNowRequest` | Configured (1) | omit | Valid | omit | Accepted |

### Reserve EVSE Tests (Unspecified EVSE)

| Test | Use Case | CSMS Must Send | evseId | connectorType | idToken | CS Response |
|---|---|---|---|---|---|---|
| **TC_H_08** | H01(S1), H03 | `ReserveNowRequest` | **omit** | omit | Valid | Accepted |
| **TC_H_14** | H01(S1) | `ReserveNowRequest` x N | **omit** | omit | Valid | Accepted (each) |

### Reserve by Connector Type

| Test | Use Case | CSMS Must Send | evseId | connectorType | idToken | CS Response |
|---|---|---|---|---|---|---|
| **TC_H_15** | H01(S3), H03 | `ReserveNowRequest` | **omit** | **cType2** (configured) | Valid | Accepted |

### Cancel Reservation Tests

| Test | Use Case | CSMS Must Send | Details | CS Response |
|---|---|---|---|---|
| **TC_H_17** | H02 | `ReserveNowRequest` then `CancelReservationRequest` | reservationId must match the one from ReserveNowRequest | Accepted (both) |

### Reservation Rejection Tests

| Test | Use Case | CSMS Must Send | Details | CS Response |
|---|---|---|---|---|
| **TC_H_22** | H01 | `ReserveNowRequest` | CS is configured to reject reservations | **Rejected** |

---

## Test Scenarios Summary

| Test | Description | Key Behavior |
|---|---|---|
| **TC_H_01** | Reserve specific EVSE - Accepted | CSMS reserves a specific EVSE with valid idToken |
| **TC_H_07** | Reserve specific EVSE - Reservation expired | Reservation expires after expiryDateTime; CS sends ReservationStatusUpdate (Expired) |
| **TC_H_08** | Reserve unspecified EVSE - Accepted | CSMS reserves without specifying an EVSE |
| **TC_H_14** | Reserve unspecified EVSE - All EVSEs reserved | CSMS sends N ReserveNowRequests (one per configured EVSE) |
| **TC_H_15** | Reserve by connector type - Success | CSMS reserves using connectorType filter |
| **TC_H_17** | Cancel reservation - Success | CSMS first reserves, then cancels with matching reservationId |
| **TC_H_19** | Reserve with GroupId | CSMS reserves with a groupIdToken for group-based access |
| **TC_H_20** | Reservation canceled on Fault | CS goes Faulted after reservation; sends ReservationStatusUpdate (Removed) |
| **TC_H_22** | Reserve specific EVSE - Rejected | CS is configured to reject; CSMS must handle Rejected response |

---

## Pre-Requisite States Per Test

| Test | Boot | Available | Reserved (Before) |
|---|---|---|---|
| TC_H_01 | Yes | Yes | - |
| TC_H_07 | Yes | Yes | - |
| TC_H_08 | Yes | Yes | - |
| TC_H_14 | Yes | Yes (all EVSEs) | - |
| TC_H_15 | Yes | Yes | - |
| TC_H_17 | Yes | Yes | - |
| TC_H_19 | Yes | Yes | - |
| TC_H_20 | Yes | Yes | - |
| TC_H_22 | Yes | Yes | - |

---

## CSMS Capabilities Required

| Capability | Required By Tests |
|---|---|
| Send `ReserveNowRequest` (specific EVSE) | H01, H07, H17, H19, H20 |
| Send `ReserveNowRequest` (unspecified EVSE) | H08, H14 |
| Send `ReserveNowRequest` (with connectorType) | H15 |
| Send `ReserveNowRequest` (with groupIdToken) | H19 |
| Send `ReserveNowRequest` (with expiryDateTime) | H07 |
| Send `CancelReservationRequest` | H17 |
| Handle `ReservationStatusUpdateRequest` (Expired) | H07 |
| Handle `ReservationStatusUpdateRequest` (Removed) | H20 |
| Handle `StatusNotificationRequest` | All tests |
| Handle `NotifyEventRequest` | H01, H07, H08, H14, H15, H17, H19, H20 |
| Handle `BootNotificationRequest` (respond Accepted) | All tests |
| Handle `ReserveNowResponse` (Rejected) | H22 |

---

## CSMS Charging Point Setup Checklist

To run the full H test suite, the CSMS must have the following charging point configured:

### 1. Charging Point Registration

- **Charging Point ID:** `CP_1`
- **Password:** `0123456789123456`
- **Security Profile:** 1 (Basic Authentication over WebSocket)
- **Protocol:** OCPP 2.0.1

### 2. EVSE Configuration

- **EVSE 1** with **Connector 1** (at minimum)
- Connector type: `cType2` (for H15)
- For H14: configure the number of EVSEs matching `CONFIGURED_NUMBER_OF_EVSES`

### 3. Authorization

- **IdToken:** `100000C01` with type `Central` must be authorized (status: `Accepted`)
- **GroupIdToken:** `GROUP001` must be configured and associated (for H19)

### 4. Reservation Support

- CSMS must support creating reservations for specific EVSEs, unspecified EVSEs, and by connector type
- CSMS must support canceling reservations
- CSMS must handle reservation expiry and fault-based removal notifications from the CS

### 5. Environment Variables Summary

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# EVSE/Connector
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"
export CONFIGURED_NUMBER_OF_EVSES="1"
export CONFIGURED_CONNECTOR_TYPE="cType2"

# Authorization
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"
export GROUP_ID="GROUP001"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"
export TRANSACTION_DURATION="5"
```
