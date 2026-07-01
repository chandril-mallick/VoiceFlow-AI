"""
VoiceFlow AI — Integration Modules
Email, WhatsApp, Calendar, Webhooks, and Notification integrations.
"""

# ── Email ──

import logging
from typing import Optional

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template

from src.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    to: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None,
) -> bool:
    """Send an email via SMTP."""
    if not settings.smtp_user:
        logger.warning("SMTP not configured, skipping email to %s", to)
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = settings.smtp_from_email
        msg["To"] = to
        msg["Subject"] = subject

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
        )
        logger.info("✅ Email sent to %s: %s", to, subject)
        return True

    except Exception as e:
        logger.error("❌ Email failed to %s: %s", to, e)
        return False


MEETING_EMAIL_TEMPLATE = """
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #6366f1;">Meeting Confirmed — {{ company_name }}</h2>
  <p>Hi {{ customer_name }},</p>
  <p>Thank you for your interest! Your meeting has been scheduled:</p>
  <div style="background: #f3f4f6; padding: 16px; border-radius: 8px; margin: 16px 0;">
    <p><strong>📅 Date:</strong> {{ meeting_date }}</p>
    <p><strong>⏰ Time:</strong> {{ meeting_time }}</p>
    <p><strong>⏱️ Duration:</strong> {{ duration }} minutes</p>
    {% if meeting_link %}
    <p><strong>🔗 Meeting Link:</strong> <a href="{{ meeting_link }}">{{ meeting_link }}</a></p>
    {% endif %}
  </div>
  <p>Looking forward to speaking with you!</p>
  <p>Best regards,<br>{{ company_name }} Team</p>
</body>
</html>
"""


async def send_meeting_confirmation(
    to: str,
    customer_name: str,
    company_name: str,
    meeting_date: str,
    meeting_time: str,
    duration: int = 30,
    meeting_link: str = "",
) -> bool:
    """Send a meeting confirmation email."""
    template = Template(MEETING_EMAIL_TEMPLATE)
    html = template.render(
        customer_name=customer_name,
        company_name=company_name,
        meeting_date=meeting_date,
        meeting_time=meeting_time,
        duration=duration,
        meeting_link=meeting_link,
    )
    return await send_email(to, f"Meeting Confirmed — {company_name}", html)
