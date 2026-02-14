import os
import pytest_asyncio
import websockets
from websockets import InvalidStatusCode
from dataclasses import dataclass
import time

CSMS_ADDRESS = os.environ['CSMS_ADDRESS']

@dataclass
class MockConnection:
    open: bool
    status_code: int

@pytest_asyncio.fixture
async def connection(request):
    cp_name, headers = request.param
    try:
        uri = f'{CSMS_ADDRESS}/{cp_name}'
        ws = await websockets.connect(uri=uri,
                                      subprotocols=['ocpp2.0.1'],
                                      extra_headers=headers)
    except InvalidStatusCode as e:
        yield MockConnection(open=False, status_code=e.status_code)
        return

    # Some delay is required by some CSMS prior to being able to handle data sent
    time.sleep(0.5)
    yield ws

    await ws.close()
