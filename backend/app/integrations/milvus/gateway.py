"""Milvus Gateway - 向量存储实现。"""
from __future__ import annotations
from app.domain.ai.protocols import VectorStore, RetrieveResult


class MilvusGateway(VectorStore):
    """Milvus 向量存储网关（生产实现）。"""

    def __init__(self, host: str = "localhost", port: int = 19530, db_name: str = "autocustomer"):
        self.host = host
        self.port = port
        self.db_name = db_name
        self._collection_name = "kb_chunk_vec"

    async def _get_collection(self):
        """延迟导入 pymilvus，避免强依赖。"""
        from pymilvus import connections, Collection
        connections.connect(host=self.host, port=self.port, db_name=self.db_name)
        return Collection(self._collection_name)

    async def search(self, vector: list[float], top_k: int = 20, filter_expr: str = "") -> list[RetrieveResult]:
        col = await self._get_collection()
        col.load()
        search_params = {"metric_type": "COSINE", "params": {"ef": 64}}
        results = col.search(
            data=[vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            expr=filter_expr or None,
            output_fields=["chunk_id", "doc_id", "category_id"],
        )
        return [
            RetrieveResult(
                chunk_id=int(hit.entity.get("chunk_id")),
                score=float(hit.distance),
            )
            for hit in results[0]
        ]

    async def upsert(self, chunk_id: int, vector: list[float], doc_id: int, category_id: int, status: int) -> None:
        col = await self._get_collection()
        col.insert([
            [chunk_id],
            [doc_id],
            [category_id],
            [vector],
            [status],
            [0],  # created_at
        ])

    async def delete_by_doc_id(self, doc_id: int) -> None:
        col = await self._get_collection()
        col.delete(f"doc_id == {doc_id}")

    async def count(self, filter_expr: str = "") -> int:
        col = await self._get_collection()
        col.load()
        if filter_expr:
            return len(col.query(expr=filter_expr, output_fields=["chunk_id"]))
        return col.num_entities


class MockVectorStore(VectorStore):
    """Mock 向量存储（测试用）。"""

    def __init__(self):
        self._store: dict[int, list[float]] = {}
        self._meta: dict[int, dict] = {}

    async def search(self, vector: list[float], top_k: int = 20, filter_expr: str = "") -> list[RetrieveResult]:
        import math
        def cosine(a, b):
            dot = sum(x*y for x,y in zip(a,b))
            na = math.sqrt(sum(x*x for x in a))
            nb = math.sqrt(sum(x*x for x in b))
            return dot/(na*nb) if na*nb else 0
        scores = [(cid, cosine(vector, v)) for cid, v in self._store.items()]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [RetrieveResult(chunk_id=cid, score=s) for cid, s in scores[:top_k]]

    async def upsert(self, chunk_id: int, vector: list[float], doc_id: int, category_id: int, status: int) -> None:
        self._store[chunk_id] = vector
        self._meta[chunk_id] = {"doc_id": doc_id, "category_id": category_id, "status": status}

    async def delete_by_doc_id(self, doc_id: int) -> None:
        to_delete = [cid for cid, m in self._meta.items() if m.get("doc_id") == doc_id]
        for cid in to_delete:
            self._store.pop(cid, None)
            self._meta.pop(cid, None)

    async def count(self, filter_expr: str = "") -> int:
        return len(self._store)