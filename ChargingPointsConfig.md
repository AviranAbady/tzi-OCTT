# Master Charging Points Configuration

## Overview

This document consolidates all charging point configurations needed to run **every test case across all test blocks (A through P)**. By reusing charging points across blocks, you only need to create **3 charging points** in your CSMS.

---

## Charging Points Summary

| # | Charging Point | Security Profile | Transport | Used By Test Blocks |
|---|----------------|-----------------|-----------|---------------------|
| 1 | `BASIC_AUTH_CP` | 1 (Basic Auth) | WS | A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P |
| 2 | `SECURITY_PROFILE_2_CP` | 2 (TLS + Basic Auth) | WSS | A |
| 3 | `SECURITY_PROFILE_3_CP` | 3 (mTLS) | WSS | A |

---

## Charging Point 1: BASIC_AUTH_CP (Security Profile 1)

This is the primary charging point used by **all 16 test blocks**.

### Identity & Authentication

| Property | Value |
|---|---|
| **Env Variable** | `BASIC_AUTH_CP` |
| **Default ID** | `CP_1` |
| **Security Profile** | 1 |
| **Transport** | WS (unsecured WebSocket) |
| **Authentication** | HTTP Basic Auth (username = Charging Station ID) |
| **Password Env Variable** | `BASIC_AUTH_CP_PASSWORD` |
| **Default Password** | `0123456789123456` |
| **Connection URL** | `{CSMS_ADDRESS}/{BASIC_AUTH_CP}` |
| **WebSocket Subprotocol** | `ocpp2.0.1` |

### Hardware Topology

| Component | Env Variable | Default | Required By |
|---|---|---|---|
| **EVSE 1** | `CONFIGURED_EVSE_ID` | `1` | B, C, E, F, G, H, I, J, K, L, N, O, P |
| **EVSE 2** | — | `2` | C (TC_C_47, TC_C_49 — Master Pass multi-EVSE tests) |
| **Connector 1** (on each EVSE) | `CONFIGURED_CONNECTOR_ID` | `1` | All blocks |
| **Connector Type** | `CONFIGURED_CONNECTOR_TYPE` | `cType2` | H (TC_H_15 — connector-type reservation) |
| **Number of EVSEs** | `CONFIGURED_NUMBER_OF_EVSES` | `1` | H (TC_H_14 — all-EVSE reservation) |
| **Number of Phases** | `CONFIGURED_NUMBER_PHASES` | `3` | K (AC phase configuration) |

### Boot Notification Parameters

| Field | Value |
|---|---|
| `chargingStation.model` | `CP Model 1.0` |
| `chargingStation.vendorName` | `tzi.app` |
| `reason` | `PowerUp` |

### Used By Tests

| Block | Category | Test Cases |
|---|---|---|
| **A** | Security | TC_A_01, TC_A_02, TC_A_03, TC_A_09, TC_A_10, TC_A_19 |
| **B** | Provisioning | TC_B_01, TC_B_02, TC_B_06–TC_B_10, TC_B_12–TC_B_14, TC_B_18, TC_B_20–TC_B_22, TC_B_25–TC_B_27, TC_B_30, TC_B_31, TC_B_42, TC_B_44, TC_B_58 |
| **C** | Authorization | TC_C_02, TC_C_06–TC_C_08, TC_C_20, TC_C_37–TC_C_40, TC_C_43, TC_C_47–TC_C_52 |
| **D** | Local Auth List | TC_D_01–TC_D_04, TC_D_08, TC_D_09 |
| **E** | Transactions | TC_E_01–TC_E_04, TC_E_07–TC_E_12, TC_E_14–TC_E_17, TC_E_19–TC_E_22, TC_E_26, TC_E_29–TC_E_31, TC_E_33, TC_E_34, TC_E_38, TC_E_39, TC_E_53 |
| **F** | Remote Control | TC_F_01–TC_F_04, TC_F_06, TC_F_11–TC_F_15, TC_F_18, TC_F_20, TC_F_23, TC_F_24, TC_F_27 |
| **G** | Availability | TC_G_03–TC_G_08, TC_G_11, TC_G_14, TC_G_17, TC_G_20 |
| **H** | Reservation | TC_H_01, TC_H_07, TC_H_08, TC_H_14, TC_H_15, TC_H_17, TC_H_19, TC_H_20, TC_H_22 |
| **I** | Tariff & Cost | TC_I_01, TC_I_02 |
| **J** | Meter Values | TC_J_01–TC_J_04, TC_J_07–TC_J_11 |
| **K** | Smart Charging | TC_K_01–TC_K_06, TC_K_08, TC_K_10, TC_K_15, TC_K_19, TC_K_29–TC_K_37, TC_K_43, TC_K_44, TC_K_48, TC_K_50–TC_K_53, TC_K_55, TC_K_57–TC_K_60, TC_K_70 |
| **L** | Firmware Mgmt | TC_L_01–TC_L_11, TC_L_13, TC_L_17, TC_L_19–TC_L_24 |
| **M** | Certificate Mgmt | TC_M_01–TC_M_05, TC_M_12–TC_M_21, TC_M_24, TC_M_26, TC_M_28 |
| **N** | Diagnostics & Monitoring | TC_N_01–TC_N_03, TC_N_05, TC_N_08, TC_N_09, TC_N_16–TC_N_18, TC_N_21, TC_N_24, TC_N_25, TC_N_27–TC_N_32, TC_N_34–TC_N_36, TC_N_44, TC_N_46–TC_N_50, TC_N_60, TC_N_62, TC_N_63 |
| **O** | Display Message | TC_O_01–TC_O_14, TC_O_17–TC_O_19, TC_O_25–TC_O_28 |
| **P** | Data Transfer | TC_P_02, TC_P_03 |

---

## Charging Point 2: SECURITY_PROFILE_2_CP (Security Profile 2)

Used **only by Block A** (Security tests).

### Identity & Authentication

| Property | Value |
|---|---|
| **Env Variable** | `SECURITY_PROFILE_2_CP` |
| **Security Profile** | 2 |
| **Transport** | WSS (TLS-secured WebSocket) |
| **Authentication** | HTTP Basic Auth over TLS |
| **Password Env Variable** | `BASIC_AUTH_CP_PASSWORD` (same password as CP1) |
| **Connection URL** | `{CSMS_WSS_ADDRESS}/{SECURITY_PROFILE_2_CP}` |

### CSMS Requirements

- Must provide a valid server-side TLS certificate
- Must use TLS 1.2 or above
- Must reject TLS connections below v1.2
- Must support required cipher suites (see TLS Requirements)
- Must accept valid Basic Auth credentials over TLS
- Server certificate CN must match FQDN

### Used By Tests

| Test Case | Name |
|---|---|
| TC_A_04 | TLS server cert - Valid (security_profile=2) |
| TC_A_06 | TLS server cert - TLS version too low (security_profile=2) |
| TC_A_19 | Upgrade security profile (initial_security_profile=2) |

---

## Charging Point 3: SECURITY_PROFILE_3_CP (Security Profile 3)

Used **only by Block A** (Security tests).

### Identity & Authentication

| Property | Value |
|---|---|
| **Env Variable** | `SECURITY_PROFILE_3_CP` |
| **Security Profile** | 3 |
| **Transport** | WSS (mTLS - mutual TLS) |
| **Authentication** | Client-side certificate (no Basic Auth) |
| **Client Cert Env Variable** | `TLS_CLIENT_CERT` |
| **Client Key Env Variable** | `TLS_CLIENT_KEY` |
| **Connection URL** | `{CSMS_WSS_ADDRESS}/{SECURITY_PROFILE_3_CP}` |

### CSMS Requirements

- Must provide a valid server-side TLS certificate
- Must validate client certificate (CN = Charging Station serial number)
- Must reject invalid/unknown/expired client certificates
- Must use TLS 1.2 or above
- Must support required cipher suites (see TLS Requirements)
- Must handle certificate renewal flows (TriggerMessage -> SignCertificate -> CertificateSigned)
- No Basic Auth required

### Used By Tests

| Test Case | Name |
|---|---|
| TC_A_04 | TLS server cert - Valid (security_profile=3) |
| TC_A_06 | TLS server cert - TLS version too low (security_profile=3) |
| TC_A_07 | TLS client cert - Valid |
| TC_A_08 | TLS client cert - Invalid |
| TC_A_11 | Update CS cert - CS Certificate |
| TC_A_12 | Update CS cert - V2G Certificate |
| TC_A_13 | Update CS cert - Combined Certificate |
| TC_A_14 | Update CS cert - Invalid certificate |
| TC_A_19 | Upgrade security profile (target SP3) |

---

## Complete Environment Variables Reference

### Connection Endpoints

| Variable | Description | Example | Used By |
|---|---|---|---|
| `CSMS_ADDRESS` | WebSocket (WS) endpoint for SP1 connections | `ws://localhost:9000` | All blocks |
| `CSMS_WSS_ADDRESS` | Secure WebSocket (WSS) endpoint for SP2/SP3 | `wss://csms.example.com:8443` | A |

### Charging Point Identifiers

| Variable | Description | Used By |
|---|---|---|
| `BASIC_AUTH_CP` | Charging Station ID for SP1 (Basic Auth) — default `CP_1` | All blocks |
| `SECURITY_PROFILE_2_CP` | Charging Station ID for SP2 (TLS + Basic Auth) | A |
| `SECURITY_PROFILE_3_CP` | Charging Station ID for SP3 (mTLS) | A |

### Credentials

| Variable | Description | Used By |
|---|---|---|
| `BASIC_AUTH_CP_PASSWORD` | Password for Basic Auth — default `0123456789123456` | All blocks (SP1), A (SP2) |

### EVSE / Connector / Hardware

| Variable | Description | Default | Used By |
|---|---|---|---|
| `CONFIGURED_EVSE_ID` | Primary EVSE ID | `1` | B, C, E, F, G, H, I, J, K, L, N, O, P |
| `CONFIGURED_CONNECTOR_ID` | Connector ID on EVSE | `1` | All blocks |
| `CONFIGURED_NUMBER_OF_EVSES` | Total EVSEs in station | `1` | H (TC_H_14) |
| `CONFIGURED_CONNECTOR_TYPE` | Connector type for reservation | `cType2` | H (TC_H_15) |
| `CONFIGURED_NUMBER_PHASES` | AC phases supported | `3` | K |

### ID Tokens — Valid

| Variable | Description | Default | Used By |
|---|---|---|---|
| `VALID_ID_TOKEN` | Primary valid ID token | `100000C01` | B, C, E, F, G, H, I, J, K, L, N |
| `VALID_ID_TOKEN_TYPE` | Type of primary valid token | `Central` | B, C, E, F, G, H, I, J, K, L, N |
| `VALID_ID_TOKEN_2` | Second valid ID token (same GroupId) | — | C (TC_C_39, TC_C_40, TC_C_43, TC_C_47, TC_C_49) |
| `VALID_ID_TOKEN_TYPE_2` | Type of second valid token | — | C |
| `VALID_IDTOKEN_IDTOKEN` | Valid ID token for display message tests | `TEST_TOKEN_1` | O (TC_O_06, TC_O_10, TC_O_27, TC_O_28) |
| `VALID_IDTOKEN_TYPE` | Type of display message valid token | `ISO14443` | O |

### ID Tokens — Invalid / Blocked / Expired

| Variable | Description | Default | Used By |
|---|---|---|---|
| `INVALID_ID_TOKEN` | Invalid/unknown ID token | `100000C02` | C (TC_C_02, TC_C_20), E (TC_E_16) |
| `INVALID_ID_TOKEN_TYPE` | Type of invalid token | `Cash` | C, E |
| `BLOCKED_ID_TOKEN` | Blocked ID token | — | C (TC_C_06) |
| `BLOCKED_ID_TOKEN_TYPE` | Type of blocked token | — | C |
| `EXPIRED_ID_TOKEN` | Expired ID token | — | C (TC_C_07) |
| `EXPIRED_ID_TOKEN_TYPE` | Type of expired token | — | C |

### GroupId & Master Pass

| Variable | Description | Default | Used By |
|---|---|---|---|
| `GROUP_ID` | Shared GroupId for token1 & token2 | `GROUP001` | C (TC_C_39, TC_C_40, TC_C_43), H (TC_H_19) |
| `MASTERPASS_ID_TOKEN` | Master Pass ID token | — | C (TC_C_47, TC_C_48, TC_C_49) |
| `MASTERPASS_ID_TOKEN_TYPE` | Type of Master Pass token | — | C |
| `MASTERPASS_GROUP_ID` | MasterPass group identifier | — | C |

### TLS Certificates (Block A only)

| Variable | Description | Used By |
|---|---|---|
| `TLS_CA_CERT` | Path to CA certificate for verifying CSMS server certificate | A |
| `TLS_CLIENT_CERT` | Path to valid client certificate (for SP3) | A |
| `TLS_CLIENT_KEY` | Path to valid client private key (for SP3) | A |
| `TLS_INVALID_CLIENT_CERT` | Path to invalid client certificate | A (TC_A_08) |
| `TLS_INVALID_CLIENT_KEY` | Path to invalid client private key | A (TC_A_08) |

### ISO 15118 Contract Certificates (Block C only)

| Variable | Description | Used By |
|---|---|---|
| `ISO15118_CERT_HASH_DATA_FILE` | Path to JSON with OCSP request data (valid chain) | C (TC_C_50) |
| `ISO15118_REVOKED_CERT_HASH_DATA_FILE` | Path to JSON with OCSP request data (revoked chain) | C (TC_C_51) |
| `CONTRACT_CERT_FILE` | Path to PEM-encoded contract certificate | C (TC_C_52) |

### Local Authorization List

| Variable | Description | Default | Used By |
|---|---|---|---|
| `LOCAL_LIST_VERSION` | Version number for local auth list | `1` | D, N (TC_N_46) |

### Data Transfer (Block P only)

| Variable | Description | Default | Used By |
|---|---|---|---|
| `CONFIGURED_VENDOR_ID` | Vendor ID (must be unknown to CSMS) | `tzi.app` | P (TC_P_02) |
| `CONFIGURED_MESSAGE_ID` | Message ID (must be unknown to CSMS) | `TestMessage` | P (TC_P_02) |

### Network Profile (Block B only)

| Variable | Description | Used By |
|---|---|---|
| `CONFIGURED_CONFIGURATION_SLOT` | Expected configuration slot | B (TC_B_42) |
| `CONFIGURED_MESSAGE_TIMEOUT` | Expected messageTimeout value | B (TC_B_42) |
| `CONFIGURED_OCPP_CSMS_URL` | Expected ocppCsmsUrl value | B (TC_B_42) |
| `CONFIGURED_OCPP_INTERFACE` | Expected ocppInterface value | B (TC_B_42) |
| `CONFIGURED_SECURITY_PROFILE` | Expected securityProfile value | B (TC_B_42) |

### Timeouts & Intervals

| Variable | Description | Default | Used By |
|---|---|---|---|
| `CSMS_ACTION_TIMEOUT` | Timeout for waiting on CSMS-initiated actions | `30` sec | All blocks |
| `TRANSACTION_DURATION` | Simulated transaction duration | `5` sec | E, F, G, H, J, K, L |
| `CLOCK_ALIGNED_METER_VALUES_INTERVAL` | Clock-aligned meter value interval | `1` sec | J |
| `SAMPLED_METER_VALUES_INTERVAL` | Sampled meter value interval | `1` sec | I, J |
| `TX_ENDED_METER_VALUES_INTERVAL` | Meter values interval in Ended event | `1` sec | J |

---

## CSMS Setup Checklist

### Step 1: Register Charging Points

Register the following 3 charging points in your CSMS:

| Charging Point ID | Security Profile | Password | Protocol |
|---|---|---|---|
| Value of `BASIC_AUTH_CP` (default: `CP_1`) | 1 (Basic Auth over WS) | Value of `BASIC_AUTH_CP_PASSWORD` (default: `0123456789123456`) | OCPP 2.0.1 |
| Value of `SECURITY_PROFILE_2_CP` | 2 (TLS + Basic Auth over WSS) | Value of `BASIC_AUTH_CP_PASSWORD` (same) | OCPP 2.0.1 |
| Value of `SECURITY_PROFILE_3_CP` | 3 (mTLS over WSS) | N/A (client certificate) | OCPP 2.0.1 |

### Step 2: Configure EVSE Topology (for BASIC_AUTH_CP)

- **EVSE 1** with **Connector 1** (type: `cType2`)
- **EVSE 2** with **Connector 1** (required for Master Pass tests TC_C_47, TC_C_49)

### Step 3: Configure ID Tokens in CSMS

| Token Variable | Default Value | Type Variable | Default Type | CSMS Status | GroupId | Used By |
|---|---|---|---|---|---|---|
| `VALID_ID_TOKEN` | `100000C01` | `VALID_ID_TOKEN_TYPE` | `Central` | **Accepted** | `GROUP_ID` | B, C, E, F, G, H, I, J, K, L, N |
| `VALID_ID_TOKEN_2` | *(configure)* | `VALID_ID_TOKEN_TYPE_2` | *(configure)* | **Accepted** | `GROUP_ID` (same) | C |
| `VALID_IDTOKEN_IDTOKEN` | `TEST_TOKEN_1` | `VALID_IDTOKEN_TYPE` | `ISO14443` | **Accepted** | — | O |
| `INVALID_ID_TOKEN` | `100000C02` | `INVALID_ID_TOKEN_TYPE` | `Cash` | **Invalid/Unknown** | — | C, E |
| `BLOCKED_ID_TOKEN` | *(configure)* | `BLOCKED_ID_TOKEN_TYPE` | *(configure)* | **Blocked** | — | C |
| `EXPIRED_ID_TOKEN` | *(configure)* | `EXPIRED_ID_TOKEN_TYPE` | *(configure)* | **Expired** | — | C |
| `MASTERPASS_ID_TOKEN` | *(configure)* | `MASTERPASS_ID_TOKEN_TYPE` | *(configure)* | **Accepted** | `MASTERPASS_GROUP_ID` | C |

### Step 4: Configure TLS (for Security Profile 2 & 3)

- Provide valid server-side TLS certificates (CN must match FQDN)
- Configure client certificate validation for SP3
- Support TLS 1.2+ with the following cipher suites:

| Cipher Suite (IANA Name) | OpenSSL Name |
|---|---|
| TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 | ECDHE-ECDSA-AES128-GCM-SHA256 |
| TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 | ECDHE-ECDSA-AES256-GCM-SHA384 |
| TLS_RSA_WITH_AES_128_GCM_SHA256 | AES128-GCM-SHA256 |
| TLS_RSA_WITH_AES_256_GCM_SHA384 | AES256-GCM-SHA384 |

### Step 5: Configure Tariff (for Block I)

- Set up an energy-based tariff (cost per kWh) on BASIC_AUTH_CP
- CSMS must send running cost updates during charging (CostUpdatedRequest or totalCost in TransactionEventResponse)
- CSMS must include `totalCost` in TransactionEventResponse for Ended events

### Step 6: Configure Customer Information (for Block N)

- Register customer identifier `OpenChargeAlliance` (TC_N_62)
- Configure a customer certificate with hash data (TC_N_63)

---

## Complete Environment Variables Template

```bash
# ============================================================
# Connection Endpoints
# ============================================================
export CSMS_ADDRESS="ws://localhost:9000"
export CSMS_WSS_ADDRESS="wss://localhost:9443"

# ============================================================
# Charging Point Identifiers
# ============================================================
export BASIC_AUTH_CP="CP_1"
export SECURITY_PROFILE_2_CP="CP_2"
export SECURITY_PROFILE_3_CP="CP_3"

# ============================================================
# Credentials
# ============================================================
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# ============================================================
# EVSE / Connector / Hardware
# ============================================================
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"
export CONFIGURED_NUMBER_OF_EVSES="2"        # 2 for Master Pass tests (C, H)
export CONFIGURED_CONNECTOR_TYPE="cType2"     # For reservation by connector type (H)
export CONFIGURED_NUMBER_PHASES="3"           # AC phases (K)

# ============================================================
# ID Tokens - Valid
# ============================================================
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"
export VALID_ID_TOKEN_2="<your_second_valid_token>"
export VALID_ID_TOKEN_TYPE_2="<type>"
export VALID_IDTOKEN_IDTOKEN="TEST_TOKEN_1"   # Block O only
export VALID_IDTOKEN_TYPE="ISO14443"          # Block O only

# ============================================================
# ID Tokens - Invalid / Blocked / Expired
# ============================================================
export INVALID_ID_TOKEN="100000C02"
export INVALID_ID_TOKEN_TYPE="Cash"
export BLOCKED_ID_TOKEN="<your_blocked_token>"
export BLOCKED_ID_TOKEN_TYPE="<type>"
export EXPIRED_ID_TOKEN="<your_expired_token>"
export EXPIRED_ID_TOKEN_TYPE="<type>"

# ============================================================
# GroupId & Master Pass
# ============================================================
export GROUP_ID="GROUP001"
export MASTERPASS_ID_TOKEN="<your_masterpass_token>"
export MASTERPASS_ID_TOKEN_TYPE="<type>"
export MASTERPASS_GROUP_ID="<your_masterpass_group>"

# ============================================================
# TLS Certificates (Block A)
# ============================================================
export TLS_CA_CERT="/path/to/ca-cert.pem"
export TLS_CLIENT_CERT="/path/to/client-cert.pem"
export TLS_CLIENT_KEY="/path/to/client-key.pem"
export TLS_INVALID_CLIENT_CERT="/path/to/invalid-client-cert.pem"
export TLS_INVALID_CLIENT_KEY="/path/to/invalid-client-key.pem"

# ============================================================
# ISO 15118 Contract Certificates (Block C)
# ============================================================
export ISO15118_CERT_HASH_DATA_FILE="/path/to/valid-cert-hash-data.json"
export ISO15118_REVOKED_CERT_HASH_DATA_FILE="/path/to/revoked-cert-hash-data.json"
export CONTRACT_CERT_FILE="/path/to/contract-cert.pem"

# ============================================================
# Local Authorization List
# ============================================================
export LOCAL_LIST_VERSION="1"

# ============================================================
# Data Transfer (Block P)
# ============================================================
export CONFIGURED_VENDOR_ID="tzi.app"
export CONFIGURED_MESSAGE_ID="TestMessage"

# ============================================================
# Network Profile (Block B - TC_B_42)
# ============================================================
# export CONFIGURED_CONFIGURATION_SLOT="<slot>"
# export CONFIGURED_MESSAGE_TIMEOUT="<timeout>"
# export CONFIGURED_OCPP_CSMS_URL="<url>"
# export CONFIGURED_OCPP_INTERFACE="<interface>"
# export CONFIGURED_SECURITY_PROFILE="<profile>"

# ============================================================
# Timeouts & Intervals
# ============================================================
export CSMS_ACTION_TIMEOUT="30"
export TRANSACTION_DURATION="5"
export CLOCK_ALIGNED_METER_VALUES_INTERVAL="1"
export SAMPLED_METER_VALUES_INTERVAL="1"
export TX_ENDED_METER_VALUES_INTERVAL="1"
```

---

## CSMS Capability Requirements by Block

| Block | Key CSMS Capabilities Required |
|---|---|
| **A** | Security Profiles 1/2/3, TLS, mTLS, certificate renewal, password management |
| **B** | BootNotification (Accepted/Pending/Rejected), Get/Set Variables, GetBaseReport, Reset, SetNetworkProfile, TriggerMessage, WebSocket subprotocol |
| **C** | Authorization (valid/invalid/blocked/expired), GroupId, MasterPass, ClearCache, ISO 15118 contract certs |
| **D** | SendLocalList (Full/Differential/Remove/Empty), GetLocalListVersion |
| **E** | TransactionEvent (Started/Updated/Ended), RequestStopTransaction, GetTransactionStatus, offline handling |
| **F** | RequestStartTransaction, UnlockConnector, TriggerMessage (MeterValues, TransactionEvent, Log, Firmware, Heartbeat, Status) |
| **G** | ChangeAvailability (EVSE/Station/Connector level, Operative/Inoperative), NotifyEvent |
| **H** | ReserveNow (specific/unspecified EVSE, connector type, GroupId), CancelReservation, ReservationStatusUpdate |
| **I** | Energy-based tariff, CostUpdatedRequest, totalCost in TransactionEventResponse |
| **J** | MeterValues handling (clock-aligned, sampled, signed), TransactionEvent with meter data |
| **K** | SetChargingProfile, ClearChargingProfile, GetChargingProfiles, GetCompositeSchedule, RequestStartTransaction with profile, NotifyEVChargingNeeds, NotifyEVChargingSchedule, NotifyChargingLimit |
| **L** | UpdateFirmware (with signing cert/signature, scheduled install/retrieve, cancel), PublishFirmware, UnpublishFirmware |
| **M** | InstallCertificate (CSMS/Manufacturer/V2G/MO Root), GetInstalledCertificateIds, DeleteCertificate, GetCertificateStatus, Get15118EVCertificate |
| **N** | GetLog (Diagnostics/Security), GetMonitoringReport, SetMonitoringBase, SetVariableMonitoring, SetMonitoringLevel, ClearVariableMonitoring, NotifyEvent, CustomerInformation, SendLocalList |
| **O** | SetDisplayMessage, GetDisplayMessages, ClearDisplayMessage, NotifyDisplayMessages |
| **P** | DataTransfer (UnknownVendorId/UnknownMessageId/Rejected), CustomData handling |
