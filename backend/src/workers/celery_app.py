"""
VoiceFlow AI — Celery Application
Background task queue with Redis broker.
"""

from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "voiceflow",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=300,
    task_time_limit=600,
    beat_schedule={
        "cleanup-stale-conversations": {
            "task": "src.workers.tasks.cleanup_stale_conversations",
            "schedule": 3600.0,  # Every hour
        },
        "aggregate-daily-analytics": {
            "task": "src.workers.tasks.aggregate_daily_analytics",
            "schedule": 86400.0,  # Every 24 hours
        },
    },
)

celery_app.autodiscover_tasks(["src.workers"])
