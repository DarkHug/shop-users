import aiosmtplib
from email.message import EmailMessage

from src.core.settings import settings


async def send_email(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.sender_email
    msg["To"] = to
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_server,
        port=settings.smtp_port,
        username=settings.sender_email,
        password=settings.sender_password,
        start_tls=True
    )
