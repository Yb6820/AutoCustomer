"""Celery 应用工厂。"""
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "autocustomer",
    broker=settings.redis.celery_broker,
    backend=settings.redis.celery_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_queue="default",
    task_routes={
        "app.workers.tasks.*": {"queue": "default"},
        "app.workers.tasks.embed_chunk": {"queue": "embedding"},
        "app.workers.tasks.index_chunk": {"queue": "index"},
    },
    beat_schedule={
        "reconcile-milvus": {
            "task": "app.workers.tasks.reconcile_milvus",
            "schedule": 3600.0,  # 每小时
        },
        "stat-daily-rollup": {
            "task": "app.workers.tasks.stat_daily_rollup",
            "schedule": 3600.0,
        },
    },
)