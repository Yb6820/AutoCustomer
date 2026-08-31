"""Rerank Provider 基础实现。"""
from __future__ import annotations
from app.domain.ai.protocols import RerankProvider
import httpx


class BaseReranker(RerankProvider):
    """通用 Rerank Provider（BGE-Reranker 兼容）。"""

    def __init__(self, endpoint: str, api_key: str = "", model: str = "bge-reranker-v2-m3"):
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        self.model = model

    async def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[tuple[int, float]]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{self.endpoint}/rerank",
                json={"model": self.model, "query": query, "documents": documents, "top_n": top_n},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return [(item["index"], item["relevance_score"]) for item in data.get("results", [])]


class MockReranker(RerankProvider):
    """Mock Reranker（测试用，返回原始顺序）。"""

    async def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[tuple[int, float]]:
        return [(i, 1.0 - i * 0.01) for i in range(min(top_n, len(documents)))]