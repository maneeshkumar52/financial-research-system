import json
import structlog
from typing import Callable, Dict, Any

logger = structlog.get_logger(__name__)

class ServiceBusHelper:
    """Service Bus wrapper with LOCAL_MODE in-process fallback."""

    def __init__(self, connection_string: str) -> None:
        self.connection_string = connection_string
        self._local_queues: Dict[str, list] = {}

    async def publish(self, queue_name: str, message_dict: Dict[str, Any]) -> str:
        if not self.connection_string:
            if queue_name not in self._local_queues:
                self._local_queues[queue_name] = []
            self._local_queues[queue_name].append(message_dict)
            logger.info("local_queue_publish", queue=queue_name)
            return f"local-{id(message_dict)}"
        try:
            from azure.servicebus.aio import ServiceBusClient
            from azure.servicebus import ServiceBusMessage
            async with ServiceBusClient.from_connection_string(self.connection_string) as client:
                async with client.get_queue_sender(queue_name=queue_name) as sender:
                    await sender.send_messages(ServiceBusMessage(json.dumps(message_dict)))
            return f"sent-{queue_name}"
        except Exception as exc:
            logger.error("service_bus_publish_failed", error=str(exc))
            raise

    async def subscribe(self, queue_name: str, handler_fn: Callable, max_wait: int = 180) -> None:
        if not self.connection_string:
            for msg in self._local_queues.get(queue_name, []):
                await handler_fn(msg)
            self._local_queues[queue_name] = []
            return
        try:
            from azure.servicebus.aio import ServiceBusClient
            async with ServiceBusClient.from_connection_string(self.connection_string) as client:
                async with client.get_queue_receiver(queue_name=queue_name, max_wait_time=max_wait) as receiver:
                    async for msg in receiver:
                        try:
                            await handler_fn(json.loads(str(msg)))
                            await receiver.complete_message(msg)
                        except Exception as exc:
                            await receiver.dead_letter_message(msg, reason=str(exc))
        except Exception as exc:
            logger.error("service_bus_subscribe_failed", error=str(exc))
