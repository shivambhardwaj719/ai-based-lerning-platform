"""Email service using FastAPI-Mail with Jinja2 templates."""
from __future__ import annotations

import structlog
from jinja2 import Environment, FileSystemLoader

from core.config import settings

log = structlog.get_logger()

_fast_mail = None


def _get_fast_mail():
    global _fast_mail
    if _fast_mail is None:
        if not settings.SMTP_HOST:
            return None
        from fastapi_mail import ConnectionConfig, FastMail
        mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USERNAME or "",
            MAIL_PASSWORD=settings.SMTP_PASSWORD or "",
            MAIL_FROM=settings.SMTP_FROM_EMAIL,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_FROM_NAME=settings.SMTP_FROM_NAME,
            MAIL_STARTTLS=settings.SMTP_TLS,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=bool(settings.SMTP_USERNAME),
        )
        _fast_mail = FastMail(mail_config)
    return _fast_mail


class EmailService:
    async def send_template(self, to: str, subject: str, template: str, context: dict) -> None:
        fast_mail = _get_fast_mail()
        if fast_mail is None:
            log.warning("Email not sent — SMTP not configured", to=to, subject=subject)
            return
        try:
            from fastapi_mail import MessageSchema, MessageType
            html = self._render_template(template, context)
            message = MessageSchema(
                subject=subject,
                recipients=[to],
                body=html,
                subtype=MessageType.html,
            )
            await fast_mail.send_message(message)
            log.info("Email sent", to=to, subject=subject)
        except Exception as e:
            log.error("Failed to send email", to=to, error=str(e))

    def _render_template(self, template_name: str, context: dict) -> str:
        env = Environment(loader=FileSystemLoader("templates/email"))
        template = env.get_template(f"{template_name}.html")
        return template.render(**context)


async def send_email_verification(email: str, token: str) -> None:
    service = EmailService()
    verify_url = f"{settings.CORS_ORIGINS[0]}/verify-email?token={token}"
    await service.send_template(
        to=email,
        subject="Verify your email - AI Learning Platform",
        template="verify_email",
        context={"verify_url": verify_url, "platform_name": settings.APP_NAME},
    )


async def send_password_reset_email(email: str, token: str) -> None:
    service = EmailService()
    reset_url = f"{settings.CORS_ORIGINS[0]}/reset-password?token={token}"
    await service.send_template(
        to=email,
        subject="Reset your password - AI Learning Platform",
        template="password_reset",
        context={"reset_url": reset_url, "platform_name": settings.APP_NAME},
    )


async def send_otp_email(email: str, otp: str) -> None:
    service = EmailService()
    await service.send_template(
        to=email,
        subject="Your verification code - AI Learning Platform",
        template="otp",
        context={"otp": otp, "platform_name": settings.APP_NAME},
    )
