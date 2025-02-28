"""
Test case name      Clear Authorization Data in Authorization Cache - Accepted
Test case Id        TC_C_37_CSMS
Use case Id(s)      C11
Requirement(s)      N/a
System under test   CSMS

Description         This test case covers how the Charging Station autonomously stores a record of previously presented
                    identifiers that have been successfully authorized by the CSMS in the Authorization Cache. (Successfully
                    meaning: a response received on a message containing an IdToken)
                    Purpose To verify if the CSMS is able to request the Charging Station to clear all identifiers from the Authorization
                    Cache according to the mechanism as described in the OCPP specification.

Prerequisite(s)     N/a

Before (Preparations)
    Configuration State:    N/a
    Memory State:           N/a
    Reusable State(s):      N/a

Test scenario
1. The CSMS sends a ClearCacheRequest
2. The OCTT responds with a ClearCacheResponse with status Accepted
"""

import asyncio
import pytest
import os

from ocpp.v201 import call
from ocpp.v201.enums import ClearCacheStatusType
from mock_charge_point import MockChargePoint
from utils import get_basic_auth_headers, validate_schema

BASIC_AUTH_CP = os.environ['BASIC_AUTH_CP']
BASIC_AUTH_CP_PASSWORD = os.environ['BASIC_AUTH_CP_PASSWORD']


@pytest.mark.asyncio
@pytest.mark.parametrize("connection", [(BASIC_AUTH_CP, get_basic_auth_headers(BASIC_AUTH_CP, BASIC_AUTH_CP_PASSWORD))],
                         indirect=True)
async def test_tc_c_37(connection):
    assert connection.open
    cp = MockChargePoint(BASIC_AUTH_CP, connection)

    start_task = asyncio.create_task(cp.start())

    request = call.ClearCache()
    response = await cp.send_clear_cache_request(request)

    assert response is not None
    assert validate_schema(data=response, schema_file_name='../schema/ClearCacheResponse.json')
    assert response.status == ClearCacheStatusType.accepted

    start_task.cancel()
