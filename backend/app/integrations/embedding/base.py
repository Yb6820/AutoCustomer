"""Embedding Provider 基础实现。"""
from __future__ import annotations
from app.domain.ai.protocols import EmbeddingProvider
import httpx


class BaseEmbeddingProvider(EmbeddingProvider):
    """通用 OpenAI-compatible Embedding Provider。"""

    def __init__(self, endpoint: str, api_key: str = "", model: str = "bge-m3", dim: int = 1024):
        self._endpoint = endpoint.rstrip("/")
        self._api_key = api_key
        self.model = model
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self._endpoint}/embeddings",
                json={"model": self.model, "input": texts},
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()
            return [item["embedding"] for item in data["data"]]


class MockEmbeddingProvider(EmbeddingProvider):
    """Mock Embedding（测试用，返回固定维度随机向量）。"""

    def __init__(self, dim: int = 768):
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    async def embed(self, texts: list[str]) -> list[list[float]]:
        import random
        random.seed(42)
        return [[random.random() for _ in range(self._dim)] for _ in texts]