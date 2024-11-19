import asyncio
from datetime import datetime
from typing import List, Dict

from ocpp.v201 import call, enums
from ocpp.v201 import ChargePoint
from ocpp.v201.call import TransactionEvent
from ocpp.v201.datatypes import IdTokenType, EventDataType, ComponentType, VariableAttributeType, VariableType
from ocpp.v201.enums import ConnectorStatusType, EventTriggerType
import logging

from urllib3 import request


def now_iso():
    return datetime.now().isoformat() + "Z"


class MockChargePoint(ChargePoint):

    async def start(self):
        try:
            await super().start()
        except asyncio.CancelledError:
            self._connection.close(reason="Normal closure")

    async def send_boot_notification(self):
        payload = call.BootNotification(
            charging_station={
                'model': 'CP Model 1.0',
                'vendor_name': 'tzi.app'
            },
            reason="PowerUp"
        )
        response = await self.call(payload)
        return response

    async def send_status_notification(self, connector_id, status):
        logging.info(f"Sending StatusNotification for connector {connector_id} with status {status}...")

        payload = call.StatusNotification(
            timestamp=now_iso(),
            connector_id=connector_id,
            evse_id=1,
            connector_status=status
        )

        logging.info("Received StatusNotification response.")
        return await self.call(payload)

    async def send_notify_event(self, data: List[EventDataType]):
        payload = call.NotifyEvent(generated_at=now_iso(), seq_no=0, event_data=data)
        return await self.call(payload)

    async def send_authorization_request(self, id_token, token_type,skip_schema_validation=False):
        payload = call.AuthorizePayload(id_token=dict(id_token=id_token, type=token_type))
        response = await self.call(payload, skip_schema_validation=skip_schema_validation)
        return response

    async def send_transaction_event_request(self, event: TransactionEvent):
        payload = call.TransactionEvent(event)
        response = await self.call(payload)
        return response
