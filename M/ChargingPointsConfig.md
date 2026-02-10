# Charging Points Configuration - M Test Suite (Certificate Management)

## Overview

All tests in the M suite target **OCPP 2.0.1** and test the **CSMS** as the system under test. The simulated Charging Station connects via WebSocket using **Basic Authentication (Security Profile 1)**.

---

## Charging Point: CP_1

This is the single charging point used across **all 18 test cases** (TC_M_01 through TC_M_28).

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
| Connector ID | `CONFIGURED_CONNECTOR_ID` | `1` | All tests |

### Timing

| Parameter | Env Variable | Default Value | Description |
|-----------|-------------|---------------|-------------|
| CSMS Action Timeout | `CSMS_ACTION_TIMEOUT` | `30` seconds | Max time to wait for CSMS-initiated requests |

---

## CSMS Configuration Requirements Per Test

The CSMS must be configured to initiate specific actions when the Charging Station connects and reaches the `Available` state.

### Install CA Certificate Tests (Use Case M05)

| Test | Name | CSMS Action Required | Certificate Type | Expected CS Response |
|------|------|---------------------|-----------------|---------------------|
| TC_M_01 | Install CSMSRootCertificate | Send `InstallCertificateRequest` | `CSMSRootCertificate` | `Accepted` |
| TC_M_02 | Install ManufacturerRootCertificate | Send `InstallCertificateRequest` | `ManufacturerRootCertificate` | `Accepted` |
| TC_M_03 | Install V2GRootCertificate | Send `InstallCertificateRequest` | `V2GRootCertificate` | `Accepted` |
| TC_M_04 | Install MORootCertificate | Send `InstallCertificateRequest` | `MORootCertificate` | `Accepted` |
| TC_M_05 | Install Failed | Send `InstallCertificateRequest` | `CSMSRootCertificate` | `Failed` |

**Notes for TC_M_01 through TC_M_04:**
- CSMS must send `InstallCertificateRequest` with the specified `certificateType` and a valid PEM-encoded `certificate`
- These are automatic tests — CSMS should trigger the install after the CS boots and reports `Available`

**Notes for TC_M_05:**
- Manual action: Trigger the CSMS to send `InstallCertificateRequest` with `certificateType=CSMSRootCertificate`
- The CS will respond with `status=Failed` — CSMS must handle this gracefully

### Retrieve Certificates Tests (Use Case M03)

| Test | Name | CSMS Action Required | Certificate Type Filter | Hash Algorithms | Expected CS Response |
|------|------|---------------------|------------------------|----------------|---------------------|
| TC_M_12 | Retrieve CSMSRootCertificate | Send `GetInstalledCertificateIdsRequest` **3 times** | `[CSMSRootCertificate]` | SHA256, SHA384, SHA512 | `Accepted` with hash data |
| TC_M_13 | Retrieve ManufacturerRootCertificate | Send `GetInstalledCertificateIdsRequest` | `[ManufacturerRootCertificate]` | SHA256 | `Accepted` with hash data |
| TC_M_14 | Retrieve V2GRootCertificate | Send `GetInstalledCertificateIdsRequest` | `[V2GRootCertificate]` | SHA256 | `Accepted` with hash data |
| TC_M_15 | Retrieve V2GCertificateChain | Send `GetInstalledCertificateIdsRequest` | `[V2GCertificateChain]` | SHA256 | `Accepted` with hash data + child certs |
| TC_M_16 | Retrieve MORootCertificate | Send `GetInstalledCertificateIdsRequest` | `[MORootCertificate]` | SHA256 | `Accepted` with hash data |
| TC_M_17 | Retrieve CSMS + Manufacturer | Send `GetInstalledCertificateIdsRequest` | `[CSMSRootCertificate, ManufacturerRootCertificate]` | SHA256 | `Accepted` with both types |
| TC_M_18 | Retrieve All Types | Send `GetInstalledCertificateIdsRequest` | **Omitted** (no filter) | SHA256 | `Accepted` with all cert types |
| TC_M_19 | No Matching Certificate | Send `GetInstalledCertificateIdsRequest` | `[ManufacturerRootCertificate]` | — | `NotFound` (no chain) |

**Notes for TC_M_12:**
- CSMS must send the request **3 separate times** so the CS can respond with different hash algorithms each time (SHA256, SHA384, SHA512)

**Notes for TC_M_17:**
- CSMS must include **both** `CSMSRootCertificate` and `ManufacturerRootCertificate` in the `certificateType` list

**Notes for TC_M_18:**
- Manual action: Trigger the CSMS to send `GetInstalledCertificateIdsRequest` **without** the `certificateType` field

**Notes for TC_M_19:**
- Manual action: Trigger the CSMS to send `GetInstalledCertificateIdsRequest` with `certificateType=[ManufacturerRootCertificate]`
- The CS will respond with `status=NotFound` and no `certificateHashDataChain` — CSMS must handle this gracefully

### Delete Certificate Tests (Use Case M04)

| Test | Name | CSMS Actions Required | Hash Algorithms | Expected CS Response |
|------|------|----------------------|----------------|---------------------|
| TC_M_20 | Delete Success | 1. `InstallCertificateRequest` (CSMSRootCertificate) 2. `GetInstalledCertificateIdsRequest` 3. `DeleteCertificateRequest` | SHA256, SHA384, SHA512 | `Accepted` for all |
| TC_M_21 | Delete Failed | 1. `InstallCertificateRequest` (CSMSRootCertificate) 2. `GetInstalledCertificateIdsRequest` 3. `DeleteCertificateRequest` | SHA256 | Delete response: `Failed` |

**Notes for TC_M_20:**
- Steps 1–3 are **repeated for each hash algorithm** (SHA256, SHA384, SHA512), each in a separate WebSocket session
- The `DeleteCertificateRequest` must use the **same `certificateHashData`** returned in the `GetInstalledCertificateIdsResponse` (M04.FR.07)
- CSMS may send `GetInstalledCertificateIdsRequest` with `certificateType` containing `CSMSRootCertificate` or omitted

**Notes for TC_M_21:**
- Before (Reusable State): CSMS installs a `CSMSRootCertificate` first
- Manual action: Trigger the CSMS to request deletion
- The CS will respond with `status=Failed` — CSMS must handle this gracefully
- The `DeleteCertificateRequest` must use the **same `certificateHashData`** from the `GetInstalledCertificateIdsResponse` (M04.FR.07)

### Get Certificate Status Tests (Use Case M06)

| Test | Name | CS Action | CSMS Response Required |
|------|------|----------|----------------------|
| TC_M_24 | Get Status Success | CS sends `GetCertificateStatusRequest` with OCSP data | `GetCertificateStatusResponse` with `status=Accepted` and `ocspResult` |

**Notes for TC_M_24:**
- The **CS initiates** this request (not the CSMS)
- CSMS must respond with `status=Accepted` and a valid `ocspResult` (OCSPResponse per IETF RFC 6960, DER encoded, then Base64 encoded)
- The request contains `ocspRequestData` with hashes from configured V2G certificate chain SubCA's

### ISO 15118 EV Certificate Tests (Use Cases M01, M02)

| Test | Name | CS Action | Action Type | CSMS Response Required |
|------|------|----------|------------|----------------------|
| TC_M_26 | Certificate Installation EV | CS sends `Get15118EVCertificateRequest` | `Install` | `Get15118EVCertificateResponse` with `status=Accepted` and `exiResponse` |
| TC_M_28 | Certificate Update EV | CS sends `Get15118EVCertificateRequest` | `Update` | `Get15118EVCertificateResponse` with `status=Accepted` and `exiResponse` |

**Notes for TC_M_26 and TC_M_28:**
- The **CS initiates** these requests (not the CSMS)
- `iso15118SchemaVersion`: `urn:iso:15118:2:2013:MsgDef`
- CSMS must respond with `status=Accepted` and a valid `exiResponse` (Raw CertificateInstallationRes, Base64 encoded)
- CSMS must support forwarding to a contract certificate pool or signing authority

---

## CSMS Charging Point Setup Summary

To run the full M test suite, configure the following in your CSMS:

1. **Register Charging Point**
   - ID: `CP_1`
   - Security Profile: 1 (Basic Authentication)
   - Password: `0123456789123456`

2. **Hardware Topology**
   - 1 Connector (ID: `1`)

3. **Certificate Management Capabilities**
   - CSMS must be able to trigger `InstallCertificateRequest` with:
     - `certificateType`: any of `CSMSRootCertificate`, `ManufacturerRootCertificate`, `V2GRootCertificate`, `MORootCertificate`
     - A valid PEM-encoded `certificate`
   - CSMS must be able to trigger `GetInstalledCertificateIdsRequest` with:
     - Specific `certificateType` filter (single or multiple types)
     - No `certificateType` filter (to retrieve all)
   - CSMS must be able to trigger `DeleteCertificateRequest` with:
     - `certificateHashData` matching data from a prior `GetInstalledCertificateIdsResponse`
     - Support for SHA256, SHA384, and SHA512 hash algorithms

4. **ISO 15118 / V2G Support**
   - CSMS must respond to `Get15118EVCertificateRequest` (actions: `Install`, `Update`)
   - CSMS must respond to `GetCertificateStatusRequest` with valid OCSP data
   - CSMS must have access to a certificate signing authority or contract certificate pool

5. **Boot Notification Handling**
   - CSMS must respond with `status=Accepted` to `BootNotificationRequest`
