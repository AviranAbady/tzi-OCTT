# OCPP CSMS Test Suite

Python (`pytest`) implementation of OCTT scenarios for CSMS (Central System Management System) verification against OCPP 2.0.1.
Based on `OCPP 2.0.1 Specification, Edition 4 (2025-12-03)`.

## Project Structure

```
├── A/                     # Test blocks (Section A test cases)
├── B/ ...                 # Test blocks (Section B test cases)
├── reusable_states/       # Shared preconditions and reusable scenario states
├── schema/                # JSON schema assets used by tests
├── conftest.py            # Pytest fixtures and shared setup
├── tzi_charge_point.py    # Mock charge point used by the tests
├── csms.py                # Minimal in-memory CSMS for local validation
├── utils.py               # Shared helpers (auth, ids, timestamps, etc.)
├── pytest.ini             # Default environment and pytest settings
└── requirements.txt       # Python dependencies
```

## Implemented Coverage

Current implemented CSMS tests:

- `A` Security: 14
- `B` Provisioning: 22
- `C` Authorization: 16
- `D` Local Authorization List Management: 6
- `E` Transactions: 27
- `F` Remote Control: 15
- `G` Availability: 10
- `H` Reservation: 9
- `I` Tariff and Cost: 2
- `J` Meter Values: 9
- `K` Smart Charging: 32
- `L` Firmware Management: 19
- `M` Certificate Management: 18
- `N` Diagnostics: 30
- `O` Display Message: 21
- `P` Data Transfer: 2

**Total implemented tests: 252**

## Test Artifacts

- Test files follow `test_tc_<section>_<id>_csms.py` naming.
- Mermaid sequence diagrams are included for many blocks (for example all `K` Smart Charging tests).
- Reusable states are in `reusable_states/` and are used by multiple scenarios to keep setup consistent.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Default environment is defined in `pytest.ini` and can be overridden with shell env vars. See the full environment variables reference in [`ChargingPointsConfig.md`](ChargingPointsConfig.md).

## Charge Points Configuration

To run the test suite, you need to register **3 charging points** in your CSMS:

| # | Charging Point | Security Profile | Transport | Used By |
|---|----------------|-----------------|-----------|---------|
| 1 | `BASIC_AUTH_CP` (default: `CP_1`) | 1 (Basic Auth) | WS | All test blocks (A-P) |
| 2 | `SECURITY_PROFILE_2_CP` | 2 (TLS + Basic Auth) | WSS | Block A only |
| 3 | `SECURITY_PROFILE_3_CP` | 3 (mTLS) | WSS | Block A only |

### CSMS Setup

1. **Register charging points** with the IDs, security profiles, and passwords listed above.
2. **Configure EVSE topology** on `BASIC_AUTH_CP`: EVSE 1 with Connector 1 (type `cType2`), and EVSE 2 with Connector 1 for Master Pass tests (TC_C_47, TC_C_49).
3. **Configure ID tokens** in your CSMS:
   - `VALID_ID_TOKEN` (default `100000C01`, type `Central`) - status: **Accepted**
   - `INVALID_ID_TOKEN` (default `100000C02`, type `Cash`) - status: **Invalid/Unknown**
   - `BLOCKED_ID_TOKEN` - status: **Blocked** (for Block C)
   - `EXPIRED_ID_TOKEN` - status: **Expired** (for Block C)
   - `MASTERPASS_ID_TOKEN` - status: **Accepted**, with `MASTERPASS_GROUP_ID` (for Block C)
4. **Configure TLS** (for Block A): valid server-side TLS certificates, client certificate validation for SP3, TLS 1.2+.
5. **Configure tariff** (for Block I): energy-based tariff with running cost updates during charging.

### Minimal Environment Variables

```bash
# Connection
export CSMS_ADDRESS="ws://localhost:9000"

# Charging Point
export BASIC_AUTH_CP="CP_1"
export BASIC_AUTH_CP_PASSWORD="0123456789123456"

# Hardware
export CONFIGURED_EVSE_ID="1"
export CONFIGURED_CONNECTOR_ID="1"

# ID Tokens
export VALID_ID_TOKEN="100000C01"
export VALID_ID_TOKEN_TYPE="Central"

# Timeouts
export CSMS_ACTION_TIMEOUT="30"
export TRANSACTION_DURATION="5"
```

For the complete environment variables template and detailed per-block requirements, see [`ChargingPointsConfig.md`](ChargingPointsConfig.md).

## Running Tests

Run one block:

```bash
pytest -v -p no:warnings ./K
```

Run a specific test:

```bash
pytest -v -p no:warnings ./K/test_tc_k_01_csms.py
```

Run full suite:

```bash
pytest -v -p no:warnings
```

Collect-only (fast sanity check):

```bash
pytest --collect-only -q
```

## Local CSMS playground

[csms.py](csms.py) provides a minimal in-memory CSMS to help validate test behavior locally. It is not intended for production use.
currently supporting the `A B C D E` testcases.
```
pytest -v -p no:warnings ./A ./B ./C ./D ./E

============== 88 passed in 143.02s (0:02:23) ==============
```

## Contributing

Contributions are welcome via pull requests.

## Authors

[tzi.app](https://www.tzi.app)

## License

[MIT](https://choosealicense.com/licenses/mit/)
