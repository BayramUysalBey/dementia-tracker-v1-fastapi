from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, SecretStr
import os
from app.core.settings import settings


conf = ConnectionConfig(
    MAIL_USERNAME = settings.MAIL_USERNAME,
    MAIL_PASSWORD = SecretStr(settings.MAIL_PASSWORD),
    MAIL_FROM = settings.MAIL_FROM,
    MAIL_SERVER = settings.MAIL_SERVER,
    MAIL_PORT = settings.MAIL_PORT,
    MAIL_STARTTLS = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = settings.USE_CREDENTIALS,
    VALIDATE_CERTS = settings.VALIDATE_CERTS
)

class EmailService:
    def __init__(self):
        self.fastmail = FastMail(conf)

    async def send_monthly_report(self, recipient_email: EmailStr, report_title: str, pdf_file_path:str):
       
        message = MessageSchema(
            subject=f"Your Monthly Report: {report_title}",
            recipients=[recipient_email], #type: ignore
            body=f"Transcript of patient and caregiver's notes for one month.",
            subtype=MessageType.html,
            attachments=[pdf_file_path]
        )
        
        await self.fastmail.send_message(message)
        print(f"Email successfully sent to {recipient_email}")