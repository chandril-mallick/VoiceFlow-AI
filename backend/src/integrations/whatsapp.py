"""
VoiceFlow AI — WhatsApp Integration
WhatsApp Business API message sending.
"""

import logging

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


async def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send a WhatsApp text message via the Business API."""
    if not settings.whatsapp_access_token or not settings.whatsapp_phone_number_id:
        logger.warning("WhatsApp not configured, skipping message to %s", phone)
        return False

    url = f"{settings.whatsapp_api_url}/{settings.whatsapp_phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message},
    }

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("✅ WhatsApp message sent to %s", phone)
            return True
    except Exception as e:
        logger.error("❌ WhatsApp failed to %s: %s", phone, e)
        return False


async def send_whatsapp_template(phone: str, template_name: str, parameters: list[str]) -> bool:
    """Send a WhatsApp template message."""
    if not settings.whatsapp_access_token:
        return False

    url = f"{settings.whatsapp_api_url}/{settings.whatsapp_phone_number_id}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "en"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": p} for p in parameters
                    ],
                }
            ],
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error("WhatsApp template send failed: %s", e)
        return False
