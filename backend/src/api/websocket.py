"""
VoiceFlow AI — WebSocket Voice Endpoint
Real-time voice streaming via WebSocket for browser-based conversations.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.database import get_db
from src.core.security import decode_token
from src.ai.voice.pipeline import VoicePipeline

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

# Active voice sessions
_active_sessions: dict[str, VoicePipeline] = {}


@router.websocket("/ws/voice")
async def voice_websocket(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time voice conversations.

    Protocol:
    1. Client connects with JWT token as query param
    2. Client sends JSON control messages or binary audio frames
    3. Server responds with JSON metadata + binary audio

    Control messages (JSON):
    - {"type": "start", "config": {...}} — Start a new conversation
    - {"type": "stop"} — End the conversation
    - {"type": "interrupt"} — Interrupt current response

    Audio frames (binary):
    - Raw PCM 16-bit audio at 16kHz
    """
    # ── Authenticate ──
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    tenant_id = payload.get("tenant_id", "")
    user_id = payload.get("sub", "")

    await websocket.accept()
    session_id = str(uuid4())
    pipeline: Optional[VoicePipeline] = None

    logger.info("🎙️ WebSocket connected: session=%s, user=%s", session_id, user_id)

    try:
        while True:
            # Receive message (could be text/JSON or binary audio)
            message = await websocket.receive()

            if "text" in message:
                # JSON control message
                data = json.loads(message["text"])
                msg_type = data.get("type", "")

                if msg_type == "start":
                    # Start a new conversation
                    config = data.get("config", {})
                    pipeline = VoicePipeline(
                        tenant_id=tenant_id,
                        company_name=config.get("company_name", "Our Company"),
                        services=config.get("services", []),
                        agent_name=config.get("agent_name", "AI Assistant"),
                        company_context=config.get("company_context", ""),
                        custom_prompts=config.get("custom_prompts", {}),
                        initial_language=config.get("language", "en"),
                    )
                    _active_sessions[session_id] = pipeline

                    # Send initial greeting
                    greeting = await pipeline.start_conversation()

                    await websocket.send_json({
                        "type": "greeting",
                        "session_id": session_id,
                        "text": greeting["text"],
                        "language": greeting["language"],
                        "stage": greeting["stage"],
                    })

                    # Send greeting audio
                    if greeting.get("audio"):
                        await websocket.send_bytes(greeting["audio"])

                elif msg_type == "stop":
                    # End conversation
                    if pipeline:
                        summary = pipeline.conversation_summary
                        await websocket.send_json({
                            "type": "ended",
                            "summary": summary,
                        })
                        _active_sessions.pop(session_id, None)
                    break

                elif msg_type == "interrupt":
                    # Acknowledge interruption
                    await websocket.send_json({"type": "interrupted"})

                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "text_input":
                    # Text-based input (for testing without audio)
                    if pipeline:
                        user_text = data.get("text", "")
                        response_text = await pipeline.agent.respond(user_text)
                        response_audio = pipeline.tts.synthesize(
                            response_text, pipeline.current_language
                        )

                        await websocket.send_json({
                            "type": "response",
                            "user_text": user_text,
                            "text": response_text,
                            "language": pipeline.current_language,
                            "stage": pipeline.agent.current_stage,
                            "is_ended": pipeline.agent.is_ended,
                        })

                        if response_audio:
                            await websocket.send_bytes(response_audio)

            elif "bytes" in message:
                # Binary audio frame
                if not pipeline:
                    await websocket.send_json({
                        "type": "error",
                        "message": "No active session. Send a 'start' message first.",
                    })
                    continue

                audio_bytes = message["bytes"]

                # Process audio through the pipeline
                result = await pipeline.process_audio(audio_bytes)

                if result.get("is_silence"):
                    continue

                # Send text response metadata
                await websocket.send_json({
                    "type": "response",
                    "user_text": result.get("user_text", ""),
                    "text": result["text"],
                    "language": result["language"],
                    "language_confidence": result.get("language_confidence", 0),
                    "stage": result["stage"],
                    "is_ended": result.get("is_ended", False),
                    "turn_count": result.get("turn_count", 0),
                })

                # Send audio response
                if result.get("audio"):
                    await websocket.send_bytes(result["audio"])

                # End if conversation is done
                if result.get("is_ended"):
                    summary = pipeline.conversation_summary
                    await websocket.send_json({
                        "type": "ended",
                        "summary": summary,
                    })
                    _active_sessions.pop(session_id, None)
                    break

    except WebSocketDisconnect:
        logger.info("🔌 WebSocket disconnected: session=%s", session_id)
    except Exception as e:
        logger.error("WebSocket error: %s", e, exc_info=True)
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        _active_sessions.pop(session_id, None)
        logger.info("🧹 Session cleaned up: %s", session_id)
