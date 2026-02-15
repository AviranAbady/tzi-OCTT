# Charging Points Configuration - Test Set C (Authorization)

## Overview

> **Scope Notice:** This configuration is intended only for the `tzi-OCTT` OCPP 2.0.1 test suite and is not intended for production or general-purpose CSMS deployments.

Test set C requires **1 charging point** configured in the CSMS using Security Profile 1 (Basic Auth over WS). These tests focus on authorization scenarios and require multiple ID tokens in various states (valid, invalid, blocked, expired), GroupId configuration, Master Pass tokens, and ISO 15118 contract certificate data.

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
| **EVSEs** | EVSE 1 (all tests), EVSE 2 (TC_C_47, TC_C_49) |
| **Connectors** | Connector 1 on each EVSE |

**Used in tests:** All 16 tests (TC_C_02 through TC_C_52)

**CSMS requirements:**
- Must handle AuthorizeRequest and respond with correct authorization status
- Must support various ID token statuses: Accepted, Invalid, Unknown, Blocked, Expired
- Must support GroupId in IdTokenInfo responses
- Must support MasterPass GroupId for stopping transactions
- Must support ClearCache operations
- Must support ISO 15118 contract certificate authorization with OCSP validation
- Must support at least 2 EVSEs for Master Pass tests (TC_C_47, TC_C_49)

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
| `VALID_ID_TOKEN` | Primary valid ID token value | TC_C_08, TC_C_39, TC_C_40, TC_C_43, TC_C_47, TC_C_48, TC_C_49, TC_C_50, TC_C_51, TC_C_52 |
| `VALID_ID_TOKEN_TYPE` | Type of the primary valid ID token (e.g., `Central`, `eMAID`) | Same as above |
| `VALID_ID_TOKEN_2` | Second valid ID token (same GroupId as primary) | TC_C_39, TC_C_40, TC_C_43, TC_C_47, TC_C_49 |
| `VALID_ID_TOKEN_TYPE_2` | Type of the second valid ID token | Same as above |

### Invalid / Blocked / Expired ID Tokens

| Variable | Description | Used By |
|---|---|---|
| `INVALID_ID_TOKEN` | Invalid ID token value (not recognized by CSMS) | TC_C_02, TC_C_20 |
| `INVALID_ID_TOKEN_TYPE` | Type of the invalid ID token | TC_C_02, TC_C_20 |
| `BLOCKED_ID_TOKEN` | Blocked ID token value | TC_C_06 |
| `BLOCKED_ID_TOKEN_TYPE` | Type of the blocked ID token | TC_C_06 |
| `EXPIRED_ID_TOKEN` | Expired ID token value | TC_C_07 |
| `EXPIRED_ID_TOKEN_TYPE` | Type of the expired ID token | TC_C_07 |

### GroupId Configuration

| Variable | Description | Used By |
|---|---|---|
| `GROUP_ID` | Shared GroupId for `VALID_ID_TOKEN` and `VALID_ID_TOKEN_2` | TC_C_39, TC_C_40, TC_C_43 |

### Master Pass Configuration

| Variable | Description | Used By |
|---|---|---|
| `MASTERPASS_ID_TOKEN` | Master Pass ID token value | TC_C_47, TC_C_48, TC_C_49 |
| `MASTERPASS_ID_TOKEN_TYPE` | Type of the Master Pass ID token | TC_C_47, TC_C_48, TC_C_49 |
| `MASTERPASS_GROUP_ID` | MasterPass group identifier value | TC_C_47, TC_C_48, TC_C_49 |

### ISO 15118 Contract Certificates

| Variable | Description | Used By |
|---|---|---|
| `ISO15118_CERT_HASH_DATA_FILE` | Path to JSON file with OCSP request data for valid certificate chain | TC_C_50 |
| `ISO15118_REVOKED_CERT_HASH_DATA_FILE` | Path to JSON file with OCSP request data for revoked certificate chain | TC_C_51 |
| `CONTRACT_CERT_FILE` | Path to PEM-encoded contract certificate (with OCSP responder URL in AIA extension) | TC_C_52 |

### Timeouts

| Variable | Description | Default |
|---|---|---|
| `CSMS_ACTION_TIMEOUT` | Timeout (seconds) for waiting on CSMS-initiated actions | `30` |

---

## ID Token Configuration in CSMS

The CSMS must have the following ID tokens configured:

| Token | CSMS Status | GroupId | Notes |
|---|---|---|---|
| `VALID_ID_TOKEN` | **Accepted** | `GROUP_ID` | Primary valid token; also used as eMAID for ISO 15118 tests |
| `VALID_ID_TOKEN_2` | **Accepted** | `GROUP_ID` (same as above) | Second valid token for GroupId tests |
| `INVALID_ID_TOKEN` | **Invalid** or **Unknown** | - | Must not be recognized as valid |
| `BLOCKED_ID_TOKEN` | **Blocked** or **Invalid** | - | Must be explicitly blocked |
| `EXPIRED_ID_TOKEN` | **Expired** or **Invalid** | - | Must be marked as expired |
| `MASTERPASS_ID_TOKEN` | **Accepted** | `MASTERPASS_GROUP_ID` | Master Pass token for stopping transactions |

---

## ISO 15118 Certificate Hash Data File Format

The `ISO15118_CERT_HASH_DATA_FILE` and `ISO15118_REVOKED_CERT_HASH_DATA_FILE` must be JSON files with the following structure:

```json
[
  {
    "hash_algorithm": "SHA256",
    "issuer_name_hash": "<base64-encoded>",
    "issuer_key_hash": "<base64-encoded>",
    "serial_number": "1A2B3C4D",
    "responder_url": "http://ocsp.example.com"
  }
]
```

The `responder_url` must point to an OCTT-controlled OCSP service. For the valid file, the OCSP service returns "valid". For the revoked file, it returns "revoked".

---

## Test-to-Charging-Point Matrix

All tests use the single **BASIC_AUTH_CP** charging point.

| Test Case | Name | Category | ID Tokens Used | Multi-EVSE |
|---|---|---|---|---|
| TC_C_02 | Local start - Authorization Invalid/Unknown | Direct Auth | INVALID_ID_TOKEN | |
| TC_C_06 | Local start - Authorization Blocked | Direct Auth | BLOCKED_ID_TOKEN | |
| TC_C_07 | Local start - Authorization Expired | Direct Auth | EXPIRED_ID_TOKEN | |
| TC_C_08 | Auth through cache - Accepted | Auth Cache | VALID_ID_TOKEN | |
| TC_C_20 | Auth through cache - Invalid | Auth Cache | INVALID_ID_TOKEN | |
| TC_C_37 | Clear Authorization Cache - Accepted | Clear Cache | - | |
| TC_C_38 | Clear Authorization Cache - Rejected | Clear Cache | - | |
| TC_C_39 | Authorization by GroupId - Success | GroupId | VALID_ID_TOKEN, VALID_ID_TOKEN_2, GROUP_ID | |
| TC_C_40 | Auth by GroupId - Local Auth List | GroupId | VALID_ID_TOKEN, VALID_ID_TOKEN_2, GROUP_ID | |
| TC_C_43 | Auth by GroupId - Invalid with Local Auth List | GroupId | VALID_ID_TOKEN, VALID_ID_TOKEN_2, GROUP_ID | |
| TC_C_47 | Master Pass - With UI - All transactions | Master Pass | VALID_ID_TOKEN, VALID_ID_TOKEN_2, MASTERPASS_* | X (EVSE 1+2) |
| TC_C_48 | Master Pass - With UI - Specific transaction | Master Pass | VALID_ID_TOKEN, MASTERPASS_* | |
| TC_C_49 | Master Pass - Without UI | Master Pass | VALID_ID_TOKEN, VALID_ID_TOKEN_2, MASTERPASS_* | X (EVSE 1+2) |
| TC_C_50 | ISO 15118 - Local validation - Accepted | ISO 15118 | VALID_ID_TOKEN (eMAID), ISO15118_CERT_HASH_DATA_FILE | |
| TC_C_51 | ISO 15118 - Local validation - Rejected | ISO 15118 | VALID_ID_TOKEN (eMAID), ISO15118_REVOKED_CERT_HASH_DATA_FILE | |
| TC_C_52 | ISO 15118 - Central validation - Accepted | ISO 15118 | VALID_ID_TOKEN (eMAID), CONTRACT_CERT_FILE | |

---

## Test Categories

### Direct Authorization (3 tests)
- **TC_C_02**: CSMS responds Invalid/Unknown for unrecognized ID token
- **TC_C_06**: CSMS responds Blocked/Invalid for blocked ID token
- **TC_C_07**: CSMS responds Expired/Invalid for expired ID token

### Authorization Cache (2 tests)
- **TC_C_08**: CSMS accepts cached valid token via TransactionEvent (no AuthorizeRequest)
- **TC_C_20**: CSMS rejects cached invalid token via TransactionEvent

### Clear Cache (2 tests)
- **TC_C_37**: CSMS sends ClearCacheRequest, CS responds Accepted
- **TC_C_38**: CSMS sends ClearCacheRequest, CS responds Rejected

### GroupId Authorization (3 tests)
- **TC_C_39**: Two tokens with same GroupId can start/stop same transaction
- **TC_C_40**: Same as TC_C_39 but tokens are in Local Authorization List
- **TC_C_43**: GroupId authorization with tokens in Local Authorization List (full flow with Authorize + stop)

### Master Pass (3 tests)
- **TC_C_47**: Master Pass with UI stops all transactions on all EVSEs (requires 2 EVSEs)
- **TC_C_48**: Master Pass with UI stops specific transaction on one EVSE
- **TC_C_49**: Master Pass without UI stops all transactions (requires 2 EVSEs)

### ISO 15118 Contract Certificates (3 tests)
- **TC_C_50**: CSMS validates valid contract certificate via OCSP (local hash data provided)
- **TC_C_51**: CSMS rejects revoked contract certificate via OCSP (local hash data provided)
- **TC_C_52**: CSMS validates valid contract certificate via OCSP (CSMS computes hash from certificate)
