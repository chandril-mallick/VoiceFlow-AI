"""
VoiceFlow AI — Celery Background Tasks
Document processing, email sending, webhook dispatch, and analytics.
"""

import asyncio
import logging

from src.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in Celery sync context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="src.workers.tasks.process_document")
def process_document_task(file_path: str, file_type: str, tenant_id: str, document_id: str):
    """Process an uploaded document for RAG indexing."""
    from src.rag.ingestion import process_document
    from src.core.database import get_db_context
    from src.models.knowledge import KnowledgeDocument, ProcessingStatus
    from sqlalchemy import select
    from uuid import UUID

    async def _process():
        result = await process_document(file_path, file_type, tenant_id)

        async with get_db_context() as db:
            doc_result = await db.execute(
                select(KnowledgeDocument).where(KnowledgeDocument.id == UUID(document_id))
            )
            doc = doc_result.scalar_one_or_none()
            if doc:
                doc.chunk_count = result["chunk_count"]
                doc.qdrant_collection = result["collection_name"]
                doc.processing_status = ProcessingStatus.COMPLETED
                await db.commit()

        return result

    try:
        return run_async(_process())
    except Exception as e:
        logger.error("Document processing failed: %s", e)
        raise


@celery_app.task(name="src.workers.tasks.send_email_task")
def send_email_task(to: str, subject: str, body_html: str):
    """Send an email in the background."""
    from src.integrations.email import send_email
    return run_async(send_email(to, subject, body_html))


@celery_app.task(name="src.workers.tasks.send_whatsapp_task")
def send_whatsapp_task(phone: str, message: str):
    """Send a WhatsApp message in the background."""
    from src.integrations.whatsapp import send_whatsapp_message
    return run_async(send_whatsapp_message(phone, message))


@celery_app.task(name="src.workers.tasks.dispatch_webhook_task")
def dispatch_webhook_task(url: str, event: str, payload: dict, secret: str = None):
    """Dispatch a webhook in the background."""
    from src.integrations.webhook import dispatch_webhook
    return run_async(dispatch_webhook(url, event, payload, secret))


@celery_app.task(name="src.workers.tasks.cleanup_stale_conversations")
def cleanup_stale_conversations():
    """Mark stale active conversations as abandoned."""
    logger.info("Running stale conversation cleanup...")
    # Implementation: find conversations active for > 1 hour and mark as abandoned


@celery_app.task(name="src.workers.tasks.aggregate_daily_analytics")
def aggregate_daily_analytics():
    """Aggregate daily analytics for all tenants."""
    logger.info("Running daily analytics aggregation...")
    # Implementation: compute daily stats and store in analytics table
