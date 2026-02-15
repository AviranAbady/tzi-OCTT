# Charging Points Configuration - Test Set I (Tariff and Cost)

## Overview

> **Scope Notice:** This configuration is intended only for the `tzi-OCTT` OCPP 2.0.1 test suite and is not intended for production or general-purpose CSMS deployments.

Test set I requires **1 charging point** configured in the CSMS using Security Profile 1 (Basic Auth over WS). These tests focus on tariff and cost reporting scenarios - verifying that the CSMS correctly communicates running cost during charging and final total cost after charging ends. The CSMS must be configured with an energy-based tariff.

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

**Used in tests:** TC_I_01, TC_I_02

**CSMS requirements:**
- Must accept valid Basic Auth credentials (username = CP ID, password = configured password)
- Must handle AuthorizeRequest and respond with `idTokenInfo.status = Accepted` for valid tokens
- Must handle TransactionEventRequest messages and respond with TransactionEventResponse
- Must be configured with a tariff based on energy consumed (required for TC_I_02)
- Must send CostUpdatedRequest with running cost during charging sessions, or include `totalCost` in TransactionEventResponse (TC_I_01)
- Must include `totalCost` (not omitted) in the TransactionEventResponse for `eventType = Ended` transactions (TC_I_02)

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

### Valid ID Tokens

| Variable | Description | Used By |
|---|---|---|
| `VALID_ID_TOKEN` | Valid ID token value | TC_I_01, TC_I_02 |
| `VALID_ID_TOKEN_TYPE` | Type of the valid ID token (e.g., `Central`) | TC_I_01, TC_I_02 |

### EVSE and Connector Configuration

| Variable | Description | Default |
|---|---|---|
| `CONFIGURED_EVSE_ID` | EVSE identifier | `1` |
| `CONFIGURED_CONNECTOR_ID` | Connector identifier | `1` |

### Timeouts and Intervals

| Variable | Description | Default |
|---|---|---|
| `CSMS_ACTION_TIMEOUT` | Timeout (seconds) for waiting on CSMS-initiated actions (e.g., CostUpdatedRequest) | `30` |
| `SAMPLED_METER_VALUES_INTERVAL` | Interval (seconds) between periodic meter value reports | `1` |

---

## ID Token Configuration in CSMS

The CSMS must have the following ID token configured:

| Token | CSMS Status | Notes |
|---|---|---|
| `VALID_ID_TOKEN` | **Accepted** | Must be authorized for charging on the configured EVSE |

---

## Tariff Configuration in CSMS

| Requirement | Description | Required By |
|---|---|---|
| Energy-based tariff | CSMS must be configured with a tariff that calculates cost based on energy consumed (Wh/kWh) | TC_I_02 |
| Running cost updates | CSMS must either send `CostUpdatedRequest` after periodic meter values or include `totalCost` in `TransactionEventResponse` | TC_I_01 |
| Final total cost | CSMS must include `totalCost` (not omitted) in the `TransactionEventResponse` for `eventType = Ended` when the total cost is known | TC_I_02 |

---

## Test-to-Charging-Point Matrix

All tests use the single **BASIC_AUTH_CP** charging point.

| Test Case | Name | Requirement | ID Tokens Used |
|---|---|---|---|
| TC_I_01 | Show EV Driver running total cost during charging - costUpdatedRequest | I02.FR.01 | VALID_ID_TOKEN |
| TC_I_02 | Show EV Driver Final Total Cost After Charging | I03.FR.02 | VALID_ID_TOKEN |

---

## Test Descriptions

### TC_I_01 - Running Cost During Charging (I02.FR.01)

Verifies that the CSMS sends running cost updates during an ongoing charging session. After each periodic meter value, the CSMS must either include `totalCost` in the `TransactionEventResponse` or send a separate `CostUpdatedRequest` with the running total cost and the correct `transactionId`.

**Flow:** Authorize -> EVConnectedPreSession -> EnergyTransferStarted -> MeterValuePeriodic (x2) with CostUpdated check after each.

### TC_I_02 - Final Total Cost After Charging (I03.FR.02)

Verifies that the CSMS includes the final total cost in the `TransactionEventResponse` when the transaction ends. The CSMS must have an energy-based tariff configured. The test runs a complete charging session from connection to disconnection with begin meter value of 1000 and end meter value of 6000.

**Flow:** EVConnectedPreSession (meterValue=1000) -> Authorized -> EnergyTransferStarted -> StopAuthorized -> EVConnectedPostSession -> StatusNotification(Available) -> TransactionEvent(Ended, meterValue=6000) -> Validate totalCost is present.
