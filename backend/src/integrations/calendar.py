"""
VoiceFlow AI — Calendar Integration
Google Calendar and Zoom meeting creation.
"""

import logging
from datetime import datetime
from typing import Optional

import httpx

from src.core.config import settings

logger = logging.getLogger(__name__)


async def create_google_calendar_event(
    access_token: str,
    title: str,
    description: str,
    start_time: datetime,
    duration_minutes: int = 30,
    attendee_email: Optional[str] = None,
) -> Optional[dict]:
    """Create a Google Calendar event with optional Google Meet link."""
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

    end_time = start_time.replace(
        minute=start_time.minute + duration_minutes
    )

    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "conferenceData": {
            "createRequest": {"requestId": f"vf-{int(start_time.timestamp())}"},
        },
    }

    if attendee_email:
        event["attendees"] = [{"email": attendee_email}]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=event,
                headers=headers,
                params={"conferenceDataVersion": 1},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            meet_link = ""
            if "conferenceData" in data:
                entry_points = data["conferenceData"].get("entryPoints", [])
                for ep in entry_points:
                    if ep.get("entryPointType") == "video":
                        meet_link = ep.get("uri", "")
                        break

            logger.info("✅ Calendar event created: %s", data.get("htmlLink"))
            return {
                "event_id": data.get("id"),
                "html_link": data.get("htmlLink"),
                "meet_link": meet_link,
            }
    except Exception as e:
        logger.error("❌ Calendar event creation failed: %s", e)
        return None


async def create_zoom_meeting(
    access_token: str,
    topic: str,
    start_time: datetime,
    duration_minutes: int = 30,
) -> Optional[dict]:
    """Create a Zoom meeting."""
    url = "https://api.zoom.us/v2/users/me/meetings"

    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "duration": duration_minutes,
        "timezone": "Asia/Kolkata",
        "settings": {
            "join_before_host": True,
            "waiting_room": False,
        },
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            logger.info("✅ Zoom meeting created: %s", data.get("join_url"))
            return {
                "meeting_id": data.get("id"),
                "join_url": data.get("join_url"),
                "start_url": data.get("start_url"),
                "password": data.get("password"),
            }
    except Exception as e:
        logger.error("❌ Zoom meeting creation failed: %s", e)
        return None
