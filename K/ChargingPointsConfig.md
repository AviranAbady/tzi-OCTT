# Charging Points Configuration - K (Smart Charging) Test Suite

## Overview

All tests in the K test suite validate **CSMS** (Charging Station Management System) behavior for OCPP 2.0.1 Smart Charging use cases. The tests simulate a mock Charging Point that connects to the CSMS under test.

---

## Charging Point Identity & Connection

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Charging Point ID** | `BASIC_AUTH_CP` | `CP_1` | The identity used to connect to the CSMS |
| **Password** | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for CP_1 |
| **CSMS Address** | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket endpoint of the CSMS |
| **Security Profile** | - | **1 (Basic Authentication)** | All K tests use HTTP Basic Auth over ws:// |
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
| **EVSE ID** | `CONFIGURED_EVSE_ID` | `1` | The EVSE used for specific-EVSE tests |
| **Connector ID** | `CONFIGURED_CONNECTOR_ID` | `1` | The connector within the EVSE |
| **Number of Phases** | `CONFIGURED_NUMBER_PHASES` | `3` | AC phases supported |

---

## Authorization / IdToken Configuration

Required for tests that involve transactions (K29, K37, K51, K53, K55, K57, K58, K59, K60, K70).

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Valid IdToken** | `VALID_ID_TOKEN` | `100000C01` | A token the CSMS must accept as Authorized |
| **Valid IdToken Type** | `VALID_ID_TOKEN_TYPE` | `Central` | Token type (Central, ISO14443, ISO15693, etc.) |

> **CSMS Requirement:** The CSMS must have this idToken pre-configured and respond with `AuthorizationStatus: Accepted` when it receives an `AuthorizeRequest` with this token.

---

## Timeout Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **CSMS Action Timeout** | `CSMS_ACTION_TIMEOUT` | `30` (seconds) | Most tests |
| **Extended Timeout** | `CSMS_ACTION_TIMEOUT` | `60` (seconds) | K53, K55, K57, K58, K59 (ISO 15118 tests) |

---

## CSMS Configuration Requirements Per Test

### Set Charging Profile Tests

| Test | Use Case | CSMS Must Send | EVSE ID | Profile Purpose | Profile Kind | Expected Response |
|---|---|---|---|---|---|---|
| **TC_K_01** | K01 | `SetChargingProfileRequest` | Configured (1) | TxDefaultProfile | Absolute | Accepted |
| **TC_K_02** | K01 | `SetChargingProfileRequest` | Configured (1) | TxProfile | Relative | **Rejected** |
| **TC_K_03** | K01 | `SetChargingProfileRequest` | **0** (all EVSEs) | ChargingStationMaxProfile | Absolute | Accepted |
| **TC_K_04** | - | `SetChargingProfileRequest` x2 | Any | TxDefaultProfile OR ChargingStationMaxProfile | Absolute or Recurring | Accepted (both) |
| **TC_K_10** | K01 | `SetChargingProfileRequest` | **0** (all EVSEs) | TxDefaultProfile | Absolute | Accepted |
| **TC_K_15** | K01 | `SetChargingProfileRequest` | Configured (1) | TxDefaultProfile | Absolute | **CALLERROR: NotSupported** |
| **TC_K_19** | K01 | `SetChargingProfileRequest` | Configured (1) | TxDefaultProfile | **Recurring** | Accepted |
| **TC_K_60** | K01 | `SetChargingProfileRequest` | Configured (1) | **TxProfile** | Relative or Absolute | Accepted |
| **TC_K_70** | - | `SetChargingProfileRequest` x2 | Any | 1st: TxDefaultProfile, 2nd: ChargingStationMaxProfile | 1st: Absolute/Recurring, 2nd: Absolute | Accepted (both) |

### Clear Charging Profile Tests

| Test | Use Case | CSMS Must Send | Criteria | Expected Response |
|---|---|---|---|---|
| **TC_K_05** | K10 | `ClearChargingProfileRequest` | `chargingProfileId` only (criteria omitted) | Accepted |
| **TC_K_06** | K10 | `ClearChargingProfileRequest` | `purpose=TxDefaultProfile`, `evseId`, `stackLevel` | Accepted |
| **TC_K_08** | K10 | `ClearChargingProfileRequest` | `purpose=TxDefaultProfile`, `evseId`, `stackLevel` | **Unknown** |

### Get Charging Profile Tests

| Test | Use Case | CSMS Must Send | EVSE ID | Filter Criteria | Expected Response |
|---|---|---|---|---|---|
| **TC_K_29** | K09 | `GetChargingProfilesRequest` | **0** | `chargingProfilePurpose` only | Accepted + Report |
| **TC_K_30** | K09 | `GetChargingProfilesRequest` | **> 0** (configured) | `chargingProfilePurpose` only | Accepted + Report |
| **TC_K_31** | K09 | `GetChargingProfilesRequest` | **omitted** | `chargingProfilePurpose` only | Accepted + Report (per EVSE) |
| **TC_K_32** | K09 | `GetChargingProfilesRequest` | **omitted** | `chargingProfileId` only | Accepted + Report |
| **TC_K_33** | K09 | `GetChargingProfilesRequest` | **> 0** (configured) | `stackLevel` only | Accepted + Report |
| **TC_K_34** | K09 | `GetChargingProfilesRequest` | **> 0** (configured) | `chargingLimitSource` only | Accepted + Report |
| **TC_K_35** | K09 | `GetChargingProfilesRequest` | **> 0** (configured) | `chargingProfilePurpose` only | Accepted + Report |
| **TC_K_36** | K09 | `GetChargingProfilesRequest` | **> 0** (configured) | `chargingProfilePurpose` + `stackLevel` | Accepted + Report |

### Get Composite Schedule Tests

| Test | Use Case | CSMS Must Send | EVSE ID | Required Fields |
|---|---|---|---|---|
| **TC_K_43** | K08 | `GetCompositeScheduleRequest` | **1** | `duration`, `chargingRateUnit` |
| **TC_K_44** | K08 | `GetCompositeScheduleRequest` | **0** | `duration`, `chargingRateUnit` |

### Remote Start with Charging Profile

| Test | Use Case | CSMS Must Send | Required Fields |
|---|---|---|---|
| **TC_K_37** | K05, F01 | `RequestStartTransactionRequest` | `idToken` (valid), `evseId`, `chargingProfile` (purpose=TxProfile, transactionId=omitted, kind=Relative or Absolute) |

### External Charging Limit Tests

| Test | Use Case | Direction | Message |
|---|---|---|---|
| **TC_K_48** | K12 | CP -> CSMS | `NotifyChargingLimitRequest` (chargingLimitSource=EMS) |
| **TC_K_50** | K13 | CP -> CSMS | `ClearedChargingLimitRequest` (chargingLimitSource=EMS) |
| **TC_K_51** | K13 | CP -> CSMS | `ClearedChargingLimitRequest` + `TransactionEventRequest` (ChargingRateChanged) |
| **TC_K_52** | K12 | Both | CSMS sends `GetChargingProfilesRequest`, CP reports `ChargingStationExternalConstraints` |

### ISO 15118 Smart Charging Tests

| Test | Use Case | Description | CSMS Must Handle |
|---|---|---|---|
| **TC_K_53** | K15 | Load leveling - Success | `NotifyEVChargingNeeds` -> Accepted/Processing, send `SetChargingProfile`, accept `NotifyEVChargingSchedule` |
| **TC_K_55** | K15,K16,K17 | EV profile exceeds limits | Same as K53 + reject exceeding schedule, renegotiate with new profile |
| **TC_K_57** | K17 | Renegotiation - EV initiated | Handle second `NotifyEVChargingNeeds`, send new `SetChargingProfile` |
| **TC_K_58** | K16 | Renegotiation - CSMS initiated | Proactively send new `SetChargingProfile` (TxProfile with transactionId) |
| **TC_K_59** | K16 | Renegotiation - CSMS + EV needs | Send new profile, then handle `NotifyEVChargingNeeds` and send another |

---

## Pre-Requisite States Per Test

| Test | Boot | Available | Authorized | EnergyTransferStarted | EVConnectedPreSession | ISO15118SmartCharging |
|---|---|---|---|---|---|---|
| TC_K_01 | Yes | Yes | - | - | - | - |
| TC_K_02 | Yes | Yes | - | - | - | - |
| TC_K_03 | Yes | Yes | - | - | - | - |
| TC_K_04 | Yes | Yes | - | - | - | - |
| TC_K_05 | Yes | Yes | - | - | - | - |
| TC_K_06 | Yes | Yes | - | - | - | - |
| TC_K_08 | Yes | Yes | - | - | - | - |
| TC_K_10 | Yes | Yes | - | - | - | - |
| TC_K_15 | Yes | Yes | - | - | - | - |
| TC_K_19 | Yes | Yes | - | - | - | - |
| TC_K_29 | Yes | Yes | Yes | Yes | - | - |
| TC_K_30 | Yes | Yes | - | - | - | - |
| TC_K_31 | Yes | Yes | - | - | - | - |
| TC_K_32 | Yes | Yes | - | - | - | - |
| TC_K_33 | Yes | Yes | - | - | - | - |
| TC_K_34 | Yes | Yes | - | - | - | - |
| TC_K_35 | Yes | Yes | - | - | - | - |
| TC_K_36 | Yes | Yes | - | - | - | - |
| TC_K_37 | Yes | Yes | - | - | - | - |
| TC_K_43 | Yes | Yes | - | - | - | - |
| TC_K_44 | Yes | Yes | - | - | - | - |
| TC_K_48 | Yes | Yes | - | - | - | - |
| TC_K_50 | Yes | Yes | - | - | - | - |
| TC_K_51 | Yes | Yes | Yes | Yes | - | - |
| TC_K_52 | Yes | Yes | - | - | - | - |
| TC_K_53 | Yes | Yes | Yes | - | Yes | - |
| TC_K_55 | Yes | Yes | Yes | - | Yes | - |
| TC_K_57 | Yes | Yes | Yes | - | Yes | Yes |
| TC_K_58 | Yes | Yes | Yes | - | Yes | Yes |
| TC_K_59 | Yes | Yes | Yes | - | Yes | Yes |
| TC_K_60 | Yes | Yes | Yes | Yes | - | - |
| TC_K_70 | Yes | Yes | Yes | Yes | - | - |

---

## CSMS Charging Point Setup Checklist

To run the full K test suite, the CSMS must have the following charging point configured:

### 1. Charging Point Registration

- **Charging Point ID:** `CP_1`
- **Password:** `0123456789123456`
- **Security Profile:** 1 (Basic Authentication over WebSocket)
- **Protocol:** OCPP 2.0.1

### 2. EVSE Configuration

- **EVSE 1** with **Connector 1** (at minimum)
- EVSE must support configurable number of phases (default: 3)

### 3. Authorization

- **IdToken:** `100000C01` with type `Central` must be authorized (status: `Accepted`)

### 4. Smart Charging Capabilities the CSMS Must Support

| Capability | Required By Tests |
|---|---|
| Send `SetChargingProfileRequest` (TxDefaultProfile) | K01, K04, K10, K15, K70 |
| Send `SetChargingProfileRequest` (TxProfile) | K02, K37, K53, K55, K57, K58, K59, K60 |
| Send `SetChargingProfileRequest` (ChargingStationMaxProfile) | K03, K70 |
| Send `SetChargingProfileRequest` (Recurring kind) | K19 |
| Send `ClearChargingProfileRequest` (by id) | K05 |
| Send `ClearChargingProfileRequest` (by criteria) | K06, K08 |
| Send `GetChargingProfilesRequest` | K05, K29, K30, K31, K32, K33, K34, K35, K36, K52 |
| Send `GetCompositeScheduleRequest` | K43, K44 |
| Send `RequestStartTransactionRequest` with charging profile | K37 |
| Handle `NotifyChargingLimitRequest` | K48 |
| Handle `ClearedChargingLimitRequest` | K50, K51 |
| Handle `NotifyEVChargingNeedsRequest` (respond Accepted/Processing) | K53, K55, K57, K59 |
| Send `SetChargingProfileRequest` after `NotifyEVChargingNeeds` | K53, K55, K57, K58, K59 |
| Handle `NotifyEVChargingScheduleRequest` (respond Accepted) | K53, K57, K58, K59 |
| Handle `NotifyEVChargingScheduleRequest` (respond **Rejected**) | K55 |
| Handle `ReportChargingProfilesRequest` | K05, K29, K30, K31, K32, K33, K34, K35, K36, K52 |
| Handle `TransactionEventRequest` | K37, K51, K53, K55, K57 |

### 5. Environment Variables Summary

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# EVSE/Connector
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"
export CONFIGURED_NUMBER_PHASES="3"

# Authorization
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"  # Use 60 for ISO 15118 tests
```
