"""领域层 Protocol 接口（依赖倒置核心）。L4 基础设施层实现这些协议。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class EmbeddingResult:
    chunk_id: int
    vector: list[float]


@dataclass
class RetrieveResult:
    chunk_id: int
    score: float
    content: str = ""
    meta: dict | None = None


class LLMProvider(ABC):
    """大模型 Provider 协议。"""

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        ...

    @abstractmethod
    async def stream(self, prompt: str, system_prompt: str = "", **kwargs) -> AsyncIterator[str]:
        ...


class EmbeddingProvider(ABC):
    """向量化 Provider 协议。"""

    @abstractmethod
    async def embed(self, texts: list[str]) -> list[list[float]]:
        ...

    @property
    @abstractmethod
    def dim(self) -> int:
        ...


class RerankProvider(ABC):
    """重排序 Provider 协议。"""

    @abstractmethod
    async def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[tuple[int, float]]:
        """返回 [(原始索引, 分数), ...] 按分数降序。"""
        ...


class VectorStore(ABC):
    """向量存储 Protocol（Milvus 实现）。"""

    @abstractmethod
    async def search(self, vector: list[float], top_k: int = 20, filter_expr: str = "") -> list[RetrieveResult]:
        ...

    @abstractmethod
    async def upsert(self, chunk_id: int, vector: list[float], doc_id: int, category_id: int, status: int) -> None:
        ...

    @abstractmethod
    async def delete_by_doc_id(self, doc_id: int) -> None:
        ...

    @abstractmethod
    async def count(self, filter_expr: str = "") -> int:
        ...