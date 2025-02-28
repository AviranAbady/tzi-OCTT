import asyncio
from typing import List
import logging

from ocpp.v201 import call
from ocpp.v201 import ChargePoint
from ocpp.v201.datatypes import EventDataType, StatusInfoType
from ocpp.v201.call import TransactionEvent, ClearCache

from utils import now_iso


class MockChargePoint(ChargePoint):
    seq_no = 0
    notify_event_sent = False

    def next_seq_no(self):
        self.seq_no += 1
        return self.seq_no

    def get_notify_event_type(self):
        if self.notify_event_sent:
            return 'Updated'

        self.notify_event_sent = True
        return 'Started'

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
        payload = call.NotifyEvent(generated_at=now_iso(), seq_no=1231230, event_data=data)
        return await self.call(payload)

    async def send_authorization_request(self, id_token, token_type, skip_schema_validation=False):
        payload = call.AuthorizePayload(id_token=dict(id_token=id_token, type=token_type))
        response = await self.call(payload, skip_schema_validation=skip_schema_validation)
        return response

    async def send_transaction_event_request(self, event: TransactionEvent):
        response = await self.call(event)
        return response

    async def send_clear_cache_request(self, req: ClearCache) -> StatusInfoType:
        response = await self.call(req)
        return response
