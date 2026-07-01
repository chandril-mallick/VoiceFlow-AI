"""
VoiceFlow AI — Webhook Dispatcher
Sends outgoing webhooks for lead, conversation, and appointment events.
"""

import hashlib
import hmac
import json
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


async def dispatch_webhook(
    url: str,
    event: str,
    payload: dict,
    secret: Optional[str] = None,
) -> bool:
    """
    Dispatch an outgoing webhook.

    Args:
        url: Webhook endpoint URL.
        event: Event type (e.g., 'lead.created', 'conversation.completed').
        payload: Event payload data.
        secret: HMAC secret for signature verification.
    """
    body = json.dumps({"event": event, "data": payload}, default=str)

    headers = {
        "Content-Type": "application/json",
        "X-VoiceFlow-Event": event,
    }

    # HMAC signature if secret is provided
    if secret:
        signature = hmac.new(
            secret.encode(), body.encode(), hashlib.sha256
        ).hexdigest()
        headers["X-VoiceFlow-Signature"] = f"sha256={signature}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, content=body, headers=headers, timeout=10
            )
            success = 200 <= response.status_code < 300
            if success:
                logger.info("✅ Webhook delivered: %s → %s", event, url)
            else:
                logger.warning("⚠️ Webhook returned %d: %s → %s", response.status_code, event, url)
            return success
    except Exception as e:
        logger.error("❌ Webhook failed: %s → %s: %s", event, url, e)
        return False


# Standard webhook events
WEBHOOK_EVENTS = [
    "lead.created",
    "lead.updated",
    "lead.qualified",
    "conversation.started",
    "conversation.completed",
    "appointment.booked",
    "appointment.cancelled",
    "document.processed",
]
