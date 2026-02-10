# Charging Points Configuration - D (Local Authorization List Management) Test Suite

## Overview

All tests in the D test suite validate **CSMS** (Charging Station Management System) behavior for OCPP 2.0.1 Local Authorization List Management use cases. The tests simulate a mock Charging Point that connects to the CSMS under test.

---

## Charging Point Identity & Connection

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Charging Point ID** | `BASIC_AUTH_CP` | `CP_1` | The identity used to connect to the CSMS |
| **Password** | `BASIC_AUTH_CP_PASSWORD` | `0123456789123456` | Basic Auth password for CP_1 |
| **CSMS Address** | `CSMS_ADDRESS` | `ws://localhost:9000` | WebSocket endpoint of the CSMS |
| **Security Profile** | - | **1 (Basic Authentication)** | All D tests use HTTP Basic Auth over ws:// |
| **WebSocket Subprotocol** | - | `ocpp2.0.1` | OCPP 2.0.1 protocol |

### Boot Notification Parameters

| Field | Value |
|---|---|
| `chargingStation.model` | `CP Model 1.0` |
| `chargingStation.vendorName` | `tzi.app` |
| `reason` | `PowerUp` |

---

## Local Authorization List Configuration

| Parameter | Env Variable | Default Value | Description |
|---|---|---|---|
| **Local List Version** | `LOCAL_LIST_VERSION` | `1` | Version number the CS reports for GetLocalListVersion |

---

## Timeout Configuration

| Parameter | Env Variable | Default Value | Used By |
|---|---|---|---|
| **CSMS Action Timeout** | `CSMS_ACTION_TIMEOUT` | `30` (seconds) | All tests |

---

## CSMS Configuration Requirements Per Test

### Send Local Authorization List Tests (Use Case D01)

| Test | Name | CSMS Must Send | Update Type | List Content | Expected Response |
|---|---|---|---|---|---|
| **TC_D_01** | Full List | `SendLocalListRequest` | **Full** | Non-empty, all entries with idTokenInfo | Accepted |
| **TC_D_02** | Differential Update | `SendLocalListRequest` | **Differential** | Non-empty, versionNumber > CS version | Accepted |
| **TC_D_03** | Differential Remove | `SendLocalListRequest` | **Differential** | Entries with idToken only (no idTokenInfo) | Accepted |
| **TC_D_04** | Full with Empty List | `SendLocalListRequest` | **Full** | Empty (no entries) — clears CS list | Accepted |

### Get Local List Version Tests (Use Case D02)

| Test | Name | CSMS Must Send | CS Responds With | Notes |
|---|---|---|---|---|
| **TC_D_08** | Success | `GetLocalListVersionRequest` | versionNumber = `LOCAL_LIST_VERSION` (default: 1) | CSMS queries current list version |
| **TC_D_09** | No List Available | `GetLocalListVersionRequest` | versionNumber = **0** | Indicates no local list installed |

---

## Requirements & Validations Per Test

| Test | Requirements | Key Validations |
|---|---|---|
| **TC_D_01** | D01.FR.01, D01.FR.06, D01.FR.18 | updateType=Full, versionNumber > 0, list not empty, all entries have idTokenInfo |
| **TC_D_02** | D01.FR.01, D01.FR.06, D01.FR.18 | updateType=Differential, versionNumber > CS version, list not empty |
| **TC_D_03** | D01.FR.01, D01.FR.06, D01.FR.17, D01.FR.18 | updateType=Differential, versionNumber > CS version, entries have idToken but NO idTokenInfo |
| **TC_D_04** | D01.FR.01, D01.FR.06, D01.FR.18 | updateType=Full, localAuthorizationList is absent or empty |
| **TC_D_08** | N/a | CSMS sends GetLocalListVersionRequest, CS responds with configured version |
| **TC_D_09** | N/a | CSMS sends GetLocalListVersionRequest, CS responds with versionNumber=0 |

---

## Pre-Requisite States Per Test

| Test | Boot | Available | Local List Version |
|---|---|---|---|
| TC_D_01 | Yes | Yes | Configurable (default: 1) |
| TC_D_02 | Yes | Yes | Configurable (default: 1) |
| TC_D_03 | Yes | Yes | Configurable (default: 1) |
| TC_D_04 | Yes | Yes | Configurable (default: 1) |
| TC_D_08 | Yes | Yes | Configurable (default: 1) |
| TC_D_09 | Yes | Yes | **0** (no list installed) |

---

## CSMS Charging Point Setup Checklist

To run the full D test suite, the CSMS must have the following charging point configured:

### 1. Charging Point Registration

- **Charging Point ID:** `CP_1`
- **Password:** `0123456789123456`
- **Security Profile:** 1 (Basic Authentication over WebSocket)
- **Protocol:** OCPP 2.0.1

### 2. EVSE Configuration

- **EVSE 1** with **Connector 1** (at minimum)

### 3. Local Authorization List Capabilities the CSMS Must Support

| Capability | Required By Tests |
|---|---|
| Send `SendLocalListRequest` with updateType=Full and non-empty list | D01 |
| Send `SendLocalListRequest` with updateType=Differential and non-empty list | D02, D03 |
| Send `SendLocalListRequest` with updateType=Full and empty list | D04 |
| Send `SendLocalListRequest` with entries without idTokenInfo (removal) | D03 |
| Send `GetLocalListVersionRequest` | D08, D09 |
| Include idTokenInfo in all Full list entries | D01 |
| Use versionNumber > 0 in SendLocalListRequest | D01, D02, D03, D04 |
| Use versionNumber > CS current version for Differential updates | D02, D03 |

### 4. Environment Variables Summary

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# Local Authorization List
export LOCAL_LIST_VERSION="1"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"
```
