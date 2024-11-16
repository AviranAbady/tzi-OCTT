import asyncio
from datetime import datetime

from ocpp.v201 import call, enums
from ocpp.v201 import ChargePoint
from ocpp.v201.datatypes import IdTokenType
from ocpp.v201.enums import ConnectorStatusType
import logging


class MockChargePoint(ChargePoint):

    async def start(self):
        try:
            await super().start()
        except asyncio.CancelledError:
            self._connection.close(reason="Normal closure")

    async def send_boot_notification(self):
        request = call.BootNotification(
            charging_station={
                'model': 'CP Model 1.0',
                'vendor_name': 'tzi.app'
            },
            reason="PowerUp"
        )
        response = await self.call(request)
        return response

    async def _send_connector_status(self, connector_id, status):
        logging.info(f"Sending StatusNotification for connector {connector_id} with status {status}...")

        request = call.StatusNotification(
            timestamp=datetime.now().isoformat() + "Z",
            connector_id=connector_id,
            evse_id=1,
            connector_status=status
        )
        logging.info("Received StatusNotification response.")
        return await self.call(request)

    async def send_status_notification(self):
        connectors_status = {
            1: ConnectorStatusType.available,
            2: ConnectorStatusType.occupied
        }

        response_count = 0
        for connector_id, status in connectors_status.items():
            await self._send_connector_status(connector_id, status)
            response_count += 1

        logging.info("Connected to central system.")
        return len(connectors_status) == response_count

    async def send_authorization_request(self, id_token, token_type):
        request = call.AuthorizePayload(id_token=dict(id_token=id_token, type=token_type))
        response = await self.call(request, skip_schema_validation=True)
        return response

