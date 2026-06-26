import json

from aio_pika import connect_robust, Message, ExchangeType, DeliveryMode
from src.core.settings import settings

async def email_sender(data: dict):
    connection = await connect_robust(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "email", ExchangeType.DIRECT
        )
        message_body = json.dumps(data).encode("utf-8")
        message = Message(body=message_body, delivery_mode=DeliveryMode.PERSISTENT)
        await exchange.publish(message, routing_key="email")


