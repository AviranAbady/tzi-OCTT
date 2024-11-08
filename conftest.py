import os

import pytest_asyncio
import websockets
from websockets import InvalidStatusCode
from dataclasses import dataclass

CSMS_ADDRESS = os.environ.get('CSMS_ADDRESS', None)

@dataclass
class MockConnection:
    open: bool
    status_code: int

@pytest_asyncio.fixture
async def connection(request):
    if not CSMS_ADDRESS:
        raise Exception("CSMS_ADDRESS NOT SET - check pytest.ini")
    cp_name, headers = request.param
    try:
        ws = await websockets.connect(uri=f'{CSMS_ADDRESS}/{cp_name}',
                                      subprotocols=['ocpp2.0.1'],
                                      extra_headers=headers)
    except InvalidStatusCode as e:
        yield MockConnection(open=False, status_code=e.status_code)
        return


    yield ws

    await ws.close()
