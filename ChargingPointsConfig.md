# Master Charging Points Configuration (OCPP 2.0.1)

## Overview



This root document consolidates the suite-specific configuration files under `2.0.1/*/ChargingPointsConfig.md` and aligns them with the current repository defaults from `pytest.ini` and `2.0.1/config.json`.

Use this file as the single reference when running all suites `A` through `P`.

---

## Charging Point IDs Used by Tests

### Security Profile 1 (WS + Basic Auth)

| Variable | Default Value | Used By |
|---|---|---|
| `BASIC_AUTH_CP_A` | `CP_A_SP1` | Suite A (SP1 flows) |
| `BASIC_AUTH_CP_B` | `CP_B` | Suite B |
| `BASIC_AUTH_CP_C` | `CP_C` | Suite C |
| `BASIC_AUTH_CP_D` | `CP_D` | Suite D |
| `BASIC_AUTH_CP_E` | `CP_E` | Suite E |
| `BASIC_AUTH_CP_F` | `CP_F` | Suite F |
| `BASIC_AUTH_CP_G` | `CP_G` | Suite G |
| `BASIC_AUTH_CP` | `CP_1` | Suites H, I, J, K, L, M, N, O, P (and shared fallback in helpers) |

### Security Profiles 2 and 3 (WSS)

| Variable | Default Value | Profile | Used By |
|---|---|---|---|
| `SECURITY_PROFILE_2_CP_A` | `CP_A_SP2` | 2 (TLS + Basic Auth) | Suite A |
| `SECURITY_PROFILE_3_CP_A` | `CP_A_SP3` | 3 (mTLS) | Suite A |

Notes:
- `pytest.ini` still contains `SECURITY_PROFILE_2_CP` and `SECURITY_PROFILE_3_CP` for compatibility, but current suite A test files use the `_A` variants.
- You can map multiple variables to the same physical CS registration if your setup allows it, but distinct IDs reduce cross-suite state bleed.

---

## Connection and Authentication

| Variable | Default | Notes |
|---|---|---|
| `CSMS_ADDRESS` | `ws://localhost:9000` | WS endpoint for profile 1 tests |
| `CSMS_WSS_ADDRESS` | `wss://localhost:8082` | WSS endpoint for profile 2/3 tests |
| `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for SP1/SP2 charging points |
| `NEW_BASIC_AUTH_PASSWORD` | `new_password_12345678` | Used by suite A password update flows |
| `CSMS_ACTION_TIMEOUT` | `30` | Timeout waiting for CSMS-initiated actions |

---

## Hardware and Connector Configuration

| Variable | Default | Used By |
|---|---|---|
| `CONFIGURED_EVSE_ID` | `1` | B, C, E, F, G, H, I, J, K, L, N, O, P |
| `CONFIGURED_CONNECTOR_ID` | `1` | All suites except A |
| `CONFIGURED_NUMBER_OF_EVSES` | `1` | H (`TC_H_14`) |
| `CONFIGURED_CONNECTOR_TYPE` | `cType2` | H (`TC_H_15`) |
| `CONFIGURED_NUMBER_PHASES` | `3` | K smart charging scenarios |

---

## ID Token and Authorization Configuration

### Core Tokens

| Variable | Default | Used By |
|---|---|---|
| `VALID_ID_TOKEN` | `100000C01` | B, C, E, F, G, H, I, J, K, L, N |
| `VALID_ID_TOKEN_TYPE` | `Central` | Same as above |
| `VALID_ID_TOKEN_2` | `100000C39B` | C group-id/master-pass scenarios |
| `VALID_ID_TOKEN_TYPE_2` | `Central` | C |
| `INVALID_ID_TOKEN` | `100000C02` | C, E |
| `INVALID_ID_TOKEN_TYPE` | `Cash` | C, E |
| `BLOCKED_ID_TOKEN` | `100000C06` | C |
| `BLOCKED_ID_TOKEN_TYPE` | `Central` | C |
| `EXPIRED_ID_TOKEN` | `100000C07` | C |
| `EXPIRED_ID_TOKEN_TYPE` | `Central` | C |

### Group / Master Pass

| Variable | Default | Used By |
|---|---|---|
| `GROUP_ID` | `GROUP001` | C, H |
| `MASTERPASS_ID_TOKEN` | `MASTERC47` | C |
| `MASTERPASS_ID_TOKEN_TYPE` | `Central` | C |
| `MASTERPASS_GROUP_ID` | `GROUP001` | C |

### Display Message (Suite O)

| Variable | Default | Used By |
|---|---|---|
| `VALID_IDTOKEN_IDTOKEN` | `100000C01` | O transaction-bound display message tests |
| `VALID_IDTOKEN_TYPE` | `Central` | O |

### Local Auth List

| Variable | Default | Used By |
|---|---|---|
| `LOCAL_LIST_VERSION` | `1` | D, N |
| `LOCAL_AUTH_LIST_ID_TOKEN` | `D001001` | D (test-data setup) |
| `LOCAL_AUTH_LIST_ID_TOKEN_TYPE` | `Central` | D |
| `LOCAL_AUTH_LIST_ID_TOKEN_2` | `D001002` | D |
| `LOCAL_AUTH_LIST_ID_TOKEN_TYPE_2` | `Central` | D |

---

## Metering and Timing

| Variable | Default | Used By |
|---|---|---|
| `TRANSACTION_DURATION` | `5` | E, F, G, H, J, L |
| `SAMPLED_METER_VALUES_INTERVAL` | `1` | I, J |
| `CLOCK_ALIGNED_METER_VALUES_INTERVAL` | `1` | J |
| `TX_ENDED_METER_VALUES_INTERVAL` | `1` | J |

---

## Network Profile and Data Transfer

### Network Profile (Suite B)

| Variable | Default |
|---|---|
| `CONFIGURED_CONFIGURATION_SLOT` | `1` |
| `CONFIGURED_MESSAGE_TIMEOUT` | `30` |
| `CONFIGURED_OCPP_CSMS_URL` | `wss://localhost:8082` |
| `CONFIGURED_OCPP_INTERFACE` | `Wired0` |
| `CONFIGURED_SECURITY_PROFILE` | `2` |

### Data Transfer (Suite P)

| Variable | Default |
|---|---|
| `CONFIGURED_VENDOR_ID` | `tzi.app` |
| `CONFIGURED_MESSAGE_ID` | `TestMessage` |

---

## Certificate and Security Assets

### TLS / mTLS (Suite A)

| Variable | Default Path |
|---|---|
| `TLS_CA_CERT` | `certs/ca.pem` |
| `TLS_CLIENT_CERT` | `certs/client.pem` |
| `TLS_CLIENT_KEY` | `certs/client.key` |
| `TLS_INVALID_CLIENT_CERT` | `certs/invalid_client.pem` |
| `TLS_INVALID_CLIENT_KEY` | `certs/invalid_client.key` |

### ISO 15118 Contract Certificate Inputs (Suite C)

| Variable | Default Path |
|---|---|
| `ISO15118_CERT_HASH_DATA_FILE` | `certs/iso15118_cert_hash_data.json` |
| `ISO15118_REVOKED_CERT_HASH_DATA_FILE` | `certs/iso15118_revoked_cert_hash_data.json` |
| `CONTRACT_CERT_FILE` | `certs/contract_cert.pem` |
| `CONTRACT_CERT_EMAID` | `DE-TZI-C12345-A` |

---

## CSMS Simulator Configuration Model

`2.0.1/csms.py` loads configuration from `2.0.1/config.json` at startup.

Implications:
- The CSMS simulator itself should be configured through `2.0.1/config.json`.
- The test harness (`pytest`) still uses environment variables from `pytest.ini` to parameterize simulated charging points and assertions.
- Keep `pytest.ini` and `2.0.1/config.json` aligned for shared values (IDs, ports, token defaults, EVSE/connectors, and timeouts).

---

## Block-to-Configuration Summary

| Block | Primary CP Variables | Additional Required Configuration |
|---|---|---|
| A | `BASIC_AUTH_CP_A`, `SECURITY_PROFILE_2_CP_A`, `SECURITY_PROFILE_3_CP_A` | TLS cert paths, password update support |
| B | `BASIC_AUTH_CP_B` | Network profile keys, EVSE/connector, valid token |
| C | `BASIC_AUTH_CP_C` | valid/invalid/blocked/expired tokens, group/master-pass, ISO15118 files |
| D | `BASIC_AUTH_CP_D` | local authorization list version/tokens |
| E | `BASIC_AUTH_CP_E` | transaction timing, valid/invalid tokens |
| F | `BASIC_AUTH_CP_F` | transaction timing, valid token |
| G | `BASIC_AUTH_CP_G` | transaction timing, valid token |
| H | `BASIC_AUTH_CP` | reservations, group ID, connector type, EVSE count |
| I | `BASIC_AUTH_CP` | sampled meter values interval |
| J | `BASIC_AUTH_CP` | sampled/clock-aligned/ended meter intervals |
| K | `BASIC_AUTH_CP` | smart charging params including phases |
| L | `BASIC_AUTH_CP` | firmware flow prerequisites, transaction timing |
| M | `BASIC_AUTH_CP` | certificate management capabilities |
| N | `BASIC_AUTH_CP` | monitoring/logging flows, local list version |
| O | `BASIC_AUTH_CP` | display message flows and `VALID_IDTOKEN_*` |
| P | `BASIC_AUTH_CP` | data transfer vendor/message identifiers |

---

## Minimum Registration Checklist

For a clean full run of `2.0.1/A` through `2.0.1/P`, register:

1. SP1 charging points for `CP_A_SP1`, `CP_B`, `CP_C`, `CP_D`, `CP_E`, `CP_F`, `CP_G`, `CP_1`.
2. SP2 charging point for `CP_A_SP2`.
3. SP3 charging point for `CP_A_SP3`.
4. Basic Auth password matching `BASIC_AUTH_CP_PASSWORD`.
5. EVSE/connector topology matching `CONFIGURED_EVSE_ID` and `CONFIGURED_CONNECTOR_ID` (plus extra EVSE behavior required by specific C/H scenarios).

