"""文档分片策略。"""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    index: int
    token_count: int
    meta: dict | None = None


class ChunkingStrategy(ABC):
    """分片策略抽象。"""

    @abstractmethod
    def split(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[Chunk]:
        ...


class FixedSizeChunking(ChunkingStrategy):
    """固定大小分片（按字符数，后续可升级语义分片）。"""

    def split(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[Chunk]:
        chunks = []
        start = 0
        idx = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            content = text[start:end]
            chunks.append(Chunk(
                content=content,
                index=idx,
                token_count=len(content) // 2,  # 粗略估算，实际由 Embedding 模型决定
            ))
            idx += 1
            start = end - overlap if end < len(text) else len(text)
        return chunks