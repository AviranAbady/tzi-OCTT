""" Dummy Charging Station Management System (CSMS) implementation - Partial functionality """

import asyncio
import logging
import websockets
from datetime import datetime
import base64
import http
from ocpp.routing import on
from ocpp.v201 import ChargePoint
from ocpp.v201 import call_result
from ocpp.v201.enums import RegistrationStatusType, Action
from websockets import ConnectionClosedOK

from utils import now_iso

logging.basicConfig(level=logging.INFO)

VALID_USERNAME = "username"
VALID_PASSWORD = "password"


class ChargePointHandler(ChargePoint):

    @on(Action.boot_notification)
    async def on_boot_notification(self, charging_station, reason, **kwargs):
        return call_result.BootNotification(
            current_time=now_iso(),
            interval=10,
            status=RegistrationStatusType.accepted
        )

    @on(Action.status_notification)
    async def on_status_notification(self, connector_id, connector_status, **kwargs):
        logging.info(
            f"Received StatusNotification from {self.id} for connector {connector_id} with status {connector_status}.")
        return call_result.StatusNotification()


async def consume_message_and_echo(websocket):
    """Handle incoming messages and echo them back."""
    try:
        async for message in websocket:
            logging.info(f"Received message: {message}")
            await websocket.send(message)
            logging.info(f"Echoed message back: {message}")
    except websockets.exceptions.ConnectionClosed:
        logging.info("Client connection closed")
    except Exception as e:
        logging.error(f"Error handling message: {e}")


async def on_connect(websocket, path):
    """ For every new charge point that connects, create a ChargePoint
    instance and start listening for messages.
    """
    try:
        requested_protocols = websocket.request_headers['Sec-WebSocket-Protocol']
    except KeyError:
        logging.info("Client hasn't requested any Sub protocol. Closing Connection")
        return await websocket.close()

    if websocket.subprotocol:
        logging.info("Protocols Matched: %s", websocket.subprotocol)
        # DEBUG ONLY
        # await consume_message_and_echo(websocket)
    else:
        logging.warning('Protocols Mismatched | Expected %s Requested  %s | Closing connection',
                        websocket.available_subprotocols,
                        requested_protocols)
        return await websocket.close()

    charge_point_id = path.strip('/')
    cp = ChargePointHandler(charge_point_id, websocket)

    try:
        await cp.start()
    except ConnectionClosedOK:
        logging.info(f'Charging station {charge_point_id} - connection closed')


async def process_request(path, request_headers):
    """Intercept the HTTP request to extract and validate headers."""
    auth_header = request_headers.get('Authorization')
    if auth_header is None:
        logging.warning("No Authorization header received.")
        return _unauthorized_response()

    # Validate the Authorization header
    if not auth_header.startswith('Basic '):
        logging.warning("Invalid Authorization header format.")
        return _unauthorized_response()

    # Decode credentials
    encoded_credentials = auth_header.split(' ', 1)[1]
    try:
        decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
        username, password = decoded_credentials.split(':', 1)
    except (base64.binascii.Error, UnicodeDecodeError, ValueError) as e:
        logging.error(f"Error decoding credentials: {e}")
        return _unauthorized_response()

    # Check credentials
    if username == VALID_USERNAME and password == VALID_PASSWORD:
        logging.info(f"Authorized user '{username}'.")
        return  # None means proceed with the handshake
    else:
        logging.warning(f"Invalid credentials for user '{username}'.")
        return _unauthorized_response()


def _unauthorized_response():
    """Construct a 401 Unauthorized response."""
    return (
        http.HTTPStatus.UNAUTHORIZED,
        [('WWW-Authenticate', 'Basic realm="Access to CSMS"')],
        b'HTTP 401 Unauthorized\n'
    )


async def main():
    server = await websockets.serve(
        on_connect,
        '0.0.0.0',
        9000,
        process_request=process_request,
        subprotocols=['ocpp2.0.1']
    )
    logging.info("WebSocket Server Started")
    await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
