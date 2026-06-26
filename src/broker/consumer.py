import asyncio
from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import AbstractIncomingMessage
from src.utility.email_sender import send_email
import json
from src.core.settings import settings


async def on_message(message: AbstractIncomingMessage) -> None:
    async with message.process():
        data = json.loads(message.body.decode())

        await send_email(
            to=data["email"],
            subject="Verification Code",
            body=data["code"]
        )
        print(f"Email успешно отправлен на: {data['email']}")


async def main():
    connection = await connect_robust(settings.rabbitmq_url)

    async with connection:
        channel = await connection.channel()

        exchange = await channel.declare_exchange(
            "email", ExchangeType.DIRECT
        )

        queue = await channel.declare_queue("email", durable=True)
        await queue.bind(exchange, routing_key="email")

        # ВАЖНО: Передаем функцию on_message в метод consume
        await queue.consume(on_message)

        print("Жду сообщения...")
        # Бесконечный цикл, чтобы процесс не завершался сразу
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())