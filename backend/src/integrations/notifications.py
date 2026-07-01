"""
VoiceFlow AI — Notification Integration
Slack and Discord webhook notifications.
"""

import logging

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


async def send_slack_notification(message: str, channel: str = "") -> bool:
    """Send a notification to Slack via webhook."""
    webhook_url = settings.slack_webhook_url
    if not webhook_url:
        return False

    payload = {"text": message}
    if channel:
        payload["channel"] = channel

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10)
            return response.status_code == 200
    except Exception as e:
        logger.error("Slack notification failed: %s", e)
        return False


async def send_discord_notification(message: str, embed: dict = None) -> bool:
    """Send a notification to Discord via webhook."""
    webhook_url = settings.discord_webhook_url
    if not webhook_url:
        return False

    payload = {"content": message}
    if embed:
        payload["embeds"] = [embed]

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=payload, timeout=10)
            return response.status_code in (200, 204)
    except Exception as e:
        logger.error("Discord notification failed: %s", e)
        return False


async def notify_new_lead(lead_name: str, company: str, score: int) -> None:
    """Send notifications about a new qualified lead."""
    message = (
        f"🎯 *New Lead!*\n"
        f"• Name: {lead_name}\n"
        f"• Company: {company}\n"
        f"• Score: {score}/100"
    )
    await send_slack_notification(message)
    await send_discord_notification(message)


async def notify_meeting_booked(lead_name: str, meeting_time: str) -> None:
    """Send notifications about a booked meeting."""
    message = (
        f"📅 *Meeting Booked!*\n"
        f"• Lead: {lead_name}\n"
        f"• Time: {meeting_time}"
    )
    await send_slack_notification(message)
    await send_discord_notification(message)
