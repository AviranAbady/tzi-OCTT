# Charging Points Configuration - Test Set J (Meter Values)

## Overview

Test set J requires **1 charging point** configured in the CSMS using Security Profile 1 (Basic Auth over WS). These tests verify that the CSMS correctly handles clock-aligned and sampled meter values in various transaction lifecycle stages: no transaction, transaction ongoing, transaction started, transaction ended, and with signed meter data.

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
| **EVSEs** | EVSE 1 |
| **Connectors** | Connector 1 on EVSE 1 |

**Used in tests:** TC_J_01, TC_J_02, TC_J_03, TC_J_04, TC_J_07, TC_J_08, TC_J_09, TC_J_10, TC_J_11

**CSMS requirements:**
- Must accept valid Basic Auth credentials (username = CP ID, password = configured password)
- Must respond to `BootNotificationRequest` with `status = Accepted`
- Must respond to `StatusNotificationRequest`
- Must respond to `MeterValuesRequest` with `MeterValuesResponse` (J01.FR.18)
- Must respond to `NotifyEventRequest` with `NotifyEventResponse`
- Must respond to `TransactionEventRequest` with `TransactionEventResponse` (J02.FR.19)
- Must handle `AuthorizeRequest` and respond with `idTokenInfo.status = Accepted` for valid tokens
- Must handle signed meter values in `sampledValue.signedMeterValue` (J01.FR.21, J02.FR.21)

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
| `BASIC_AUTH_CP_PASSWORD` | Password for Basic Auth (minimum 16 characters) |

### Valid ID Tokens

| Variable | Description | Used By |
|---|---|---|
| `VALID_ID_TOKEN` | Valid ID token value | TC_J_02, TC_J_03, TC_J_04, TC_J_08, TC_J_09, TC_J_10, TC_J_11 |
| `VALID_ID_TOKEN_TYPE` | Type of the valid ID token (e.g., `Central`) | TC_J_02, TC_J_03, TC_J_04, TC_J_08, TC_J_09, TC_J_10, TC_J_11 |

### EVSE and Connector Configuration

| Variable | Description | Default |
|---|---|---|
| `CONFIGURED_EVSE_ID` | EVSE identifier | `1` |
| `CONFIGURED_CONNECTOR_ID` | Connector identifier | `1` |

### Timeouts and Intervals

| Variable | Description | Default | Used By |
|---|---|---|---|
| `CLOCK_ALIGNED_METER_VALUES_INTERVAL` | Interval (seconds) between clock-aligned meter value reports | `1` | TC_J_01, TC_J_02 |
| `SAMPLED_METER_VALUES_INTERVAL` | Interval (seconds) between periodic sampled meter value reports | `1` | TC_J_09 |
| `TRANSACTION_DURATION` | Duration (seconds) of the simulated charging transaction | `5` | TC_J_02, TC_J_03, TC_J_04, TC_J_10, TC_J_11 |
| `TX_ENDED_METER_VALUES_INTERVAL` | Interval (seconds) between meter values in the Ended TransactionEventRequest | `1` | TC_J_03, TC_J_04, TC_J_10, TC_J_11 |

---

## ID Token Configuration in CSMS

The CSMS must have the following ID token configured:

| Token | CSMS Status | Notes |
|---|---|---|
| `VALID_ID_TOKEN` | **Accepted** | Must be authorized for charging on the configured EVSE |

---

## Test-to-Charging-Point Matrix

All tests use the single **BASIC_AUTH_CP** charging point.

| Test Case | Name | Requirement | Reusable State(s) | ID Tokens Used |
|---|---|---|---|---|
| TC_J_01 | Clock-aligned Meter Values - No transaction ongoing | J01.FR.18 | None | None |
| TC_J_02 | Clock-aligned Meter Values - Transaction ongoing | J01.FR.18 | EnergyTransferStarted | VALID_ID_TOKEN |
| TC_J_03 | Clock-aligned Meter Values - EventType Ended | J01.FR.18 | EnergyTransferStarted, EVDisconnected | VALID_ID_TOKEN |
| TC_J_04 | Clock-aligned Meter Values - Signed | J01.FR.21 | EnergyTransferStarted, EVDisconnected | VALID_ID_TOKEN |
| TC_J_07 | Sampled Meter Values - EventType Started - EVSE known | J02.FR.19 | EVConnectedPreSession | None |
| TC_J_08 | Sampled Meter Values - Context Transaction.Begin - EVSE not known | J02.FR.19 | Authorized, EVConnectedPreSession, EnergyTransferStarted | VALID_ID_TOKEN |
| TC_J_09 | Sampled Meter Values - EventType Updated | J02.FR.19 | EnergyTransferStarted | VALID_ID_TOKEN |
| TC_J_10 | Sampled Meter Values - EventType Ended | J02.FR.19 | EnergyTransferStarted, EVDisconnected | VALID_ID_TOKEN |
| TC_J_11 | Sampled Meter Values - Signed | J02.FR.21 | EnergyTransferStarted, EVDisconnected | VALID_ID_TOKEN |

---

## Test Descriptions

### TC_J_01 - Clock-aligned Meter Values - No transaction ongoing (J01.FR.18)

Verifies that the CSMS responds to `MeterValuesRequest` and `NotifyEventRequest` when clock-aligned meter values are sent with no ongoing transaction. Sends 3 meter value messages for `evseId=0` and all configured EVSEs with `sampledValue.context = Sample.Clock`.

**Flow:** Boot -> StatusNotification(Available) -> Loop 3x: MeterValuesRequest(Sample.Clock) + NotifyEventRequest(Periodic, FiscalMetering)

### TC_J_02 - Clock-aligned Meter Values - Transaction ongoing (J01.FR.18)

Verifies that the CSMS handles clock-aligned meter values during an ongoing transaction. Sends `MeterValuesRequest` for idle EVSEs and `TransactionEventRequest` with `triggerReason = MeterValueClock` for the active EVSE.

**Flow:** Boot -> Authorized -> EnergyTransferStarted -> Loop: MeterValuesRequest(evseId=0, Sample.Clock) + NotifyEventRequest(Periodic, FiscalMetering) + TransactionEventRequest(Updated, MeterValueClock, Sample.Clock)

### TC_J_03 - Clock-aligned Meter Values - EventType Ended (J01.FR.18)

Verifies that the CSMS handles clock-aligned meter values when a transaction ends. The `TransactionEventRequest(Ended)` contains the MeterValue field with `sampledValue.context = Sample.Clock` and the last one has `Transaction.End`.

**Flow:** Boot -> Authorized -> EnergyTransferStarted -> Wait(TRANSACTION_DURATION) -> EVDisconnected with MeterValue(Sample.Clock + Transaction.End)

### TC_J_04 - Clock-aligned Meter Values - Signed (J01.FR.21)

Same as TC_J_03 but with `sampledValue.signedMeterValue` present in all sampled values. Verifies the CSMS can handle signed clock-aligned meter values (requires `AlignedDataSignReadings = true`).

**Flow:** Same as TC_J_03 with signed meter data in all sampled values.

### TC_J_07 - Sampled Meter Values - EventType Started - EVSE known (J02.FR.19)

Verifies that the CSMS handles sampled meter values at transaction start when the EVSE is known. The `TransactionEventRequest(Started)` contains `sampledValue.context = Transaction.Begin`.

**Flow:** Boot -> StatusNotification(Occupied) -> NotifyEvent(Occupied) -> TransactionEventRequest(Started, CablePluggedIn, MeterValue=Transaction.Begin)

### TC_J_08 - Sampled Meter Values - Context Transaction.Begin - EVSE not known (J02.FR.19)

Verifies that the CSMS handles sampled meter values at transaction start when the EVSE is not known at authorization time. Authorization happens first, then EV connects and the `TransactionEventRequest(Updated)` contains `sampledValue.context = Transaction.Begin`.

**Flow:** Boot -> Authorized(Started) -> StatusNotification(Occupied) -> NotifyEvent(Occupied) -> TransactionEventRequest(Updated, CablePluggedIn, MeterValue=Transaction.Begin) -> TransactionEventRequest(Updated, ChargingStateChanged=Charging)

### TC_J_09 - Sampled Meter Values - EventType Updated (J02.FR.19)

Verifies that the CSMS handles periodic sampled meter values during an ongoing transaction. Sends 3 `TransactionEventRequest` messages with `triggerReason = MeterValuePeriodic` and `sampledValue.context = Sample.Periodic`.

**Flow:** Boot -> Authorized -> EnergyTransferStarted -> Loop 3x: TransactionEventRequest(Updated, MeterValuePeriodic, Sample.Periodic)

### TC_J_10 - Sampled Meter Values - EventType Ended (J02.FR.19)

Verifies that the CSMS handles sampled meter values when a transaction ends. The `TransactionEventRequest(Ended)` contains `sampledValue.context = Sample.Periodic` and the last one has `Transaction.End`.

**Flow:** Boot -> Authorized -> EnergyTransferStarted -> Wait(TRANSACTION_DURATION) -> EVDisconnected with MeterValue(Sample.Periodic + Transaction.End)

### TC_J_11 - Sampled Meter Values - Signed (J02.FR.21)

Same as TC_J_10 but with `sampledValue.signedMeterValue` present in all sampled values. Verifies the CSMS can handle signed sampled meter values (requires `SampledDataSignReadings = true`).

**Flow:** Same as TC_J_10 with signed meter data in all sampled values.
