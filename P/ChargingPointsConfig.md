# Charging Points Configuration - P Test Suite (Data Transfer)

## Overview

All tests in the P suite target **OCPP 2.0.1** and test the **CSMS** as the system under test. The simulated Charging Station connects via WebSocket using **Basic Authentication (Security Profile 1)**.

---

## Charging Point: CP_1

This is the single charging point used across **all 2 test cases** (TC_P_02, TC_P_03).

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
| EVSE ID | `CONFIGURED_EVSE_ID` | `1` | TC_P_03 |
| Connector ID | `CONFIGURED_CONNECTOR_ID` | `1` | TC_P_02, TC_P_03 |

### Data Transfer Configuration

| Parameter | Env Variable | Default Value | Used By |
|-----------|-------------|---------------|---------|
| Vendor ID | `CONFIGURED_VENDOR_ID` | `tzi.app` | TC_P_02 |
| Message ID | `CONFIGURED_MESSAGE_ID` | `TestMessage` | TC_P_02 |

---

## CSMS Configuration Requirements Per Test

### Data Transfer to the CSMS (Use Case P02)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_P_02 | Rejected / Unknown VendorId / Unknown MessageId | Respond to `DataTransferRequest` | CSMS must respond with `DataTransferResponse` where `status` is `UnknownVendorId`, `UnknownMessageId`, or `Rejected`. The configured `vendorId` and `messageId` must **not** be recognized by the CSMS. **P02.FR.06, P02.FR.07** |

### CustomData Handling

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_P_03 | Receive custom data | Respond to messages containing `customData` | CSMS must accept `StatusNotificationRequest` with `customData` and respond normally. CSMS must accept `TransactionEventRequest` with `customData` at both message level and `transactionInfo.customData` level, and respond normally |

---

## CSMS Charging Point Setup Summary

To run the full P test suite, configure the following in your CSMS:

1. **Register Charging Point**
   - ID: `CP_1`
   - Security Profile: 1 (Basic Authentication)
   - Password: `0123456789123456`

2. **Hardware Topology**
   - 1 EVSE (ID: `1`)
   - 1 Connector per EVSE (ID: `1`)

3. **Data Transfer (TC_P_02)**
   - The configured `vendorId` (`tzi.app`) must **not** be implemented by the CSMS, so it returns `UnknownVendorId`, `UnknownMessageId`, or `Rejected`
   - CSMS must handle `DataTransferRequest` and respond with a valid `DataTransferResponse`

4. **CustomData Support (TC_P_03)**
   - CSMS must accept and handle messages containing `customData` fields without errors
   - CSMS must accept `StatusNotificationRequest` with `customData`
   - CSMS must accept `TransactionEventRequest` with `customData` on both the message and `transactionInfo` levels

5. **Boot Notification Handling**
   - CSMS must respond with `status=Accepted` to `BootNotificationRequest`
