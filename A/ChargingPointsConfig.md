# Charging Points Configuration - Test Set A (Security)

## Overview

Test set A requires **3 distinct charging points** configured in the CSMS, each using a different security profile. Tests also require TLS certificates and environment variables to be properly set.

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

**Used in tests:** TC_A_01, TC_A_02, TC_A_03, TC_A_09, TC_A_10, TC_A_19 (initial_security_profile=1)

**CSMS requirements:**
- Must accept valid Basic Auth credentials (username = CP ID, password = configured password)
- Must reject invalid username (username != CP ID)
- Must reject invalid password
- Must reject connections with no Authorization header
- Must be able to send `SetVariablesRequest` to update `BasicAuthPassword`
- Must accept connection with new password after successful password change
- Must still accept old password after rejected password change

---

### 2. SECURITY_PROFILE_2_CP (Security Profile 2)

| Property | Value |
|---|---|
| **Env Variable** | `SECURITY_PROFILE_2_CP` |
| **Security Profile** | 2 |
| **Transport** | WSS (TLS-secured WebSocket) |
| **Authentication** | HTTP Basic Auth over TLS |
| **Password Env Variable** | `BASIC_AUTH_CP_PASSWORD` |
| **Connection URL** | `{CSMS_WSS_ADDRESS}/{SECURITY_PROFILE_2_CP}` |

**Used in tests:** TC_A_04 (security_profile=2), TC_A_06 (security_profile=2), TC_A_19 (initial_security_profile=2)

**CSMS requirements:**
- Must provide a valid server-side TLS certificate
- Must use TLS 1.2 or above
- Must reject TLS connections below v1.2
- Must support required cipher suites (see TLS Requirements below)
- Must accept valid Basic Auth credentials over TLS
- Server certificate CN must match FQDN

---

### 3. SECURITY_PROFILE_3_CP (Security Profile 3)

| Property | Value |
|---|---|
| **Env Variable** | `SECURITY_PROFILE_3_CP` |
| **Security Profile** | 3 |
| **Transport** | WSS (mTLS - mutual TLS) |
| **Authentication** | Client-side certificate (no Basic Auth) |
| **Client Cert Env Variable** | `TLS_CLIENT_CERT` |
| **Client Key Env Variable** | `TLS_CLIENT_KEY` |
| **Connection URL** | `{CSMS_WSS_ADDRESS}/{SECURITY_PROFILE_3_CP}` |

**Used in tests:** TC_A_04 (security_profile=3), TC_A_06 (security_profile=3), TC_A_07, TC_A_08, TC_A_11, TC_A_12, TC_A_13, TC_A_14, TC_A_19 (target when upgrading from SP2)

**CSMS requirements:**
- Must provide a valid server-side TLS certificate
- Must validate client certificate (CN = Charging Station serial number)
- Must reject invalid/unknown/expired client certificates
- Must use TLS 1.2 or above
- Must reject TLS connections below v1.2
- Must support required cipher suites (see TLS Requirements below)
- Must handle certificate renewal flows (TriggerMessage -> SignCertificate -> CertificateSigned)
- Must accept reconnection with renewed certificates
- No Basic Auth required

---

## Environment Variables

### Connection Endpoints

| Variable | Description | Example |
|---|---|---|
| `CSMS_ADDRESS` | WebSocket (WS) endpoint for SP1 connections | `ws://csms.example.com:8080` |
| `CSMS_WSS_ADDRESS` | Secure WebSocket (WSS) endpoint for SP2/SP3 connections | `wss://csms.example.com:8443` |

### Charging Point Identifiers

| Variable | Description |
|---|---|
| `BASIC_AUTH_CP` | Charging Station ID for SP1 (Basic Auth) |
| `SECURITY_PROFILE_2_CP` | Charging Station ID for SP2 (TLS + Basic Auth) |
| `SECURITY_PROFILE_3_CP` | Charging Station ID for SP3 (mTLS) |

### Credentials

| Variable | Description |
|---|---|
| `BASIC_AUTH_CP_PASSWORD` | Password for Basic Auth (used by SP1 and SP2 charging points) |

### TLS Certificates

| Variable | Description |
|---|---|
| `TLS_CA_CERT` | Path to CA certificate for verifying the CSMS server certificate |
| `TLS_CLIENT_CERT` | Path to valid client certificate (for SP3) |
| `TLS_CLIENT_KEY` | Path to valid client private key (for SP3) |
| `TLS_INVALID_CLIENT_CERT` | Path to invalid client certificate (for TC_A_08) |
| `TLS_INVALID_CLIENT_KEY` | Path to invalid client private key (for TC_A_08) |

### Timeouts

| Variable | Description | Default |
|---|---|---|
| `CSMS_ACTION_TIMEOUT` | Timeout (seconds) for waiting on CSMS-initiated actions | `30` |

---

## TLS Requirements

The CSMS must support TLS 1.2+ and the following cipher suites:

| Cipher Suite (IANA Name) | OpenSSL Name |
|---|---|
| TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 | ECDHE-ECDSA-AES128-GCM-SHA256 |
| TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 | ECDHE-ECDSA-AES256-GCM-SHA384 |
| TLS_RSA_WITH_AES_128_GCM_SHA256 | AES128-GCM-SHA256 |
| TLS_RSA_WITH_AES_256_GCM_SHA384 | AES256-GCM-SHA384 |

**Certificate requirements:**
- X.509 format, PEM-encoded
- Must include a serial number
- Server certificate CN must match the FQDN of the CSMS endpoint
- RSA/DSA keys: minimum 2048 bits
- ECC keys: minimum 224 bits
- TLS compression must be disabled

---

## Test-to-Charging-Point Matrix

| Test Case | Name | BASIC_AUTH_CP (SP1) | SECURITY_PROFILE_2_CP (SP2) | SECURITY_PROFILE_3_CP (SP3) |
|---|---|---|---|---|
| TC_A_01 | Basic Auth - Valid credentials | X | | |
| TC_A_02 | Basic Auth - Username != CS ID | X | | |
| TC_A_03 | Basic Auth - Invalid password | X | | |
| TC_A_04 | TLS server cert - Valid | | X | X |
| TC_A_06 | TLS server cert - TLS version too low | | X | X |
| TC_A_07 | TLS client cert - Valid | | | X |
| TC_A_08 | TLS client cert - Invalid | | | X |
| TC_A_09 | Update password - Accepted | X | | |
| TC_A_10 | Update password - Rejected | X | | |
| TC_A_11 | Update CS cert - CS Certificate | | | X |
| TC_A_12 | Update CS cert - V2G Certificate | | | X |
| TC_A_13 | Update CS cert - Combined Certificate | | | X |
| TC_A_14 | Update CS cert - Invalid certificate | | | X |
| TC_A_19 | Upgrade security profile | X | X | X |

---

## Test Prerequisites by Security Profile Support

| CSMS Capability | Required By |
|---|---|
| Supports Security Profile 1 and/or 2 | TC_A_01, TC_A_02, TC_A_03, TC_A_09, TC_A_10 |
| Supports Security Profile 2 and/or 3 | TC_A_04, TC_A_06 |
| Supports Security Profile 3 | TC_A_07, TC_A_08, TC_A_11, TC_A_13, TC_A_14 |
| Supports ISO 15118 | TC_A_12, TC_A_13 |
| Security profile initially set to 1 or 2 | TC_A_19 |
