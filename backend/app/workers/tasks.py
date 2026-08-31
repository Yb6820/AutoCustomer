"""Celery 异步任务定义。"""
from __future__ import annotations
from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.embed_chunk", max_retries=3, default_retry_delay=60)
def embed_chunk(chunk_id: int, content: str, embedding_model: str = "bge-m3"):
    """向量化单个分片（异步）。"""
    # 实际调用 Embedding Provider
    return {"chunk_id": chunk_id, "status": "done"}


@celery_app.task(name="app.workers.tasks.index_chunk", max_retries=3, default_retry_delay=30)
def index_chunk(chunk_id: int, vector: list[float], doc_id: int, category_id: int):
    """写入 Milvus（异步）。"""
    # 实际调用 MilvusGateway.upsert
    return {"chunk_id": chunk_id, "status": "indexed"}


@celery_app.task(name="app.workers.tasks.kb_pipeline")
def kb_pipeline(doc_id: int):
    """知识库导入全管线：解析 → 分片 → 向量化 → 索引。"""
    return {"doc_id": doc_id, "status": "started"}


@celery_app.task(name="app.workers.tasks.reconcile_milvus")
def reconcile_milvus():
    """Milvus 增量水位线对账。"""
    # 实际调用 Redis 水位线 + MySQL count + Milvus count
    return {"status": "reconciled"}


@celery_app.task(name="app.workers.tasks.stat_daily_rollup")
def stat_daily_rollup():
    """日统计物化。"""
    return {"status": "rolled_up"}


@celery_app.task(name="app.workers.tasks.ticket_timeout_scan")
def ticket_timeout_scan():
    """工单超时扫描升级。"""
    return {"status": "scanned"}