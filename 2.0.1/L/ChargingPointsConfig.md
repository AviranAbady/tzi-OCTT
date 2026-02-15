# Charging Points Configuration - L Test Suite (Firmware Management)

## Overview

> **Scope Notice:** This configuration is intended only for the `tzi-OCTT` OCPP 2.0.1 test suite and is not intended for production or general-purpose CSMS deployments.

All tests in the L suite target **OCPP 2.0.1** and test the **CSMS** as the system under test. The simulated Charging Station connects via WebSocket using **Basic Authentication (Security Profile 1)**.

---

## Charging Point: CP_1

This is the single charging point used across **all 19 test cases** (TC_L_01 through TC_L_24).

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
| EVSE ID | `CONFIGURED_EVSE_ID` | `1` | TC_L_01, TC_L_02, TC_L_03, TC_L_09, TC_L_10, TC_L_11, TC_L_13 |
| Connector ID | `CONFIGURED_CONNECTOR_ID` | `1` | All tests |

### Timing

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| CSMS Action Timeout | `CSMS_ACTION_TIMEOUT` | `30` seconds | Max time to wait for CSMS-initiated requests |
| Transaction Duration | `TRANSACTION_DURATION` | `5` seconds | Simulated transaction length (TC_L_13 only) |

### Authorization (TC_L_13 only)

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| ID Token | `VALID_ID_TOKEN` | `100000C01` | Valid idToken value for authorization |
| ID Token Type | `VALID_ID_TOKEN_TYPE` | `Central` | idToken type (Central) |

---

## CSMS Configuration Requirements Per Test

The CSMS must be configured to initiate specific actions when the Charging Station connects and reaches the `Available` state.

### Secure Firmware Update Tests (Use Case L01)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_L_01 | Installation successful | Send `UpdateFirmwareRequest` | `firmware.signingCertificate` and `firmware.signature` must be present |
| TC_L_02 | InstallScheduled | Send `UpdateFirmwareRequest` | `firmware.installDateTime` must be **in the future** |
| TC_L_03 | DownloadScheduled | Send `UpdateFirmwareRequest` | `firmware.retrieveDateTime` must be **in the future** |
| TC_L_04 | RevokedCertificate | Send `UpdateFirmwareRequest` | CS will respond `RevokedCertificate` |
| TC_L_05 | InvalidCertificate | Send `UpdateFirmwareRequest` | CS will respond `InvalidCertificate`, then send `SecurityEventNotification` |
| TC_L_06 | InvalidSignature | Send `UpdateFirmwareRequest` | CS will report `InvalidSignature` after download, then send `SecurityEventNotification` |
| TC_L_07 | DownloadFailed | Send `UpdateFirmwareRequest` | CS will report `DownloadFailed` |
| TC_L_08 | InstallVerificationFailed | Send `UpdateFirmwareRequest` | CS will report `InstallVerificationFailed` |
| TC_L_09 | InstallationFailed | Send `UpdateFirmwareRequest` | CS will report `InstallationFailed` after reboot |
| TC_L_10 | AcceptedCanceled | Send **2** `UpdateFirmwareRequest`s | Second sent after CS reports `Downloading`; CS responds `AcceptedCanceled` |
| TC_L_11 | Unable to cancel | Send **2** `UpdateFirmwareRequest`s | Second sent after CS reports `Downloading`; CS responds `Rejected` |
| TC_L_13 | Ongoing transaction | Send `UpdateFirmwareRequest` | `firmware.signingCertificate` must be present; CS is in `EnergyTransferStarted` state |

### Publish Firmware Tests (Use Case L03)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_L_17 | Published | Send `PublishFirmwareRequest` | `location` must be configured/present |
| TC_L_19 | Invalid Checksum | Send `PublishFirmwareRequest` | CS will report `InvalidChecksum` |
| TC_L_20 | PublishFailed | Send `PublishFirmwareRequest` | CS will report `PublishFailed` |
| TC_L_24 | Download failed | Send `PublishFirmwareRequest` | CS will report `DownloadFailed` |

### Unpublish Firmware Tests (Use Case L04)

| Test | Name | CSMS Action Required | Special Requirements |
|------|------|---------------------|----------------------|
| TC_L_21 | Unpublished | Send `UnpublishFirmwareRequest` | CS will respond `Unpublished` |
| TC_L_22 | NoFirmware | Send `UnpublishFirmwareRequest` | CS will respond `NoFirmware` |
| TC_L_23 | Download Ongoing | Send `UnpublishFirmwareRequest` | CS will respond `DownloadOngoing` |

---

## CSMS Charging Point Setup Summary

To run the full L test suite, configure the following in your CSMS:

1. **Register Charging Point**
   - ID: `CP_1`
   - Security Profile: 1 (Basic Authentication)
   - Password: `0123456789123456`

2. **Hardware Topology**
   - 1 EVSE (ID: `1`)
   - 1 Connector per EVSE (ID: `1`)

3. **Authorization**
   - Register idToken `100000C01` (type: `Central`) as valid — required for TC_L_13

4. **Firmware Management**
   - CSMS must be able to trigger `UpdateFirmwareRequest` with:
     - Valid `firmware.signingCertificate`
     - Valid `firmware.signature`
     - Configurable `firmware.installDateTime` (future) for TC_L_02
     - Configurable `firmware.retrieveDateTime` (future) for TC_L_03
   - CSMS must be able to trigger `PublishFirmwareRequest` with a valid `location`
   - CSMS must be able to trigger `UnpublishFirmwareRequest` with a valid `checksum`
   - For TC_L_10 and TC_L_11: CSMS must be able to send a **second** `UpdateFirmwareRequest` while the first is in progress

5. **Boot Notification Handling**
   - CSMS must respond with `status=Accepted` to `BootNotificationRequest` (including `reason=FirmwareUpdate`)
