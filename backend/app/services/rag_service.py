"""RAG 编排服务 —— 检索增强生成核心管线。"""
from __future__ import annotations
import json
import time
from typing import AsyncIterator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.ai.hit_policy import HitThresholdPolicy
from app.domain.ai.protocols import EmbeddingProvider, LLMProvider, RerankProvider, VectorStore
from app.domain.chat.transfer_policy import TransferPolicy
from app.repositories.chat_repo import SessionRepository, MessageRepository, RetrievalLogRepository
from app.repositories.kb_repo import ChunkRepository


class RAGService:
    """RAG 编排：检索 → 重排 → 判定 → 生成 → 日志。"""

    def __init__(
        self,
        session: AsyncSession,
        embedding: EmbeddingProvider,
        vector_store: VectorStore,
        reranker: RerankProvider | None = None,
        llm: LLMProvider | None = None,
        score_threshold: float = 0.78,
    ):
        self.session = session
        self.embedding = embedding
        self.vector_store = vector_store
        self.reranker = reranker
        self.llm = llm
        self.hit_policy = HitThresholdPolicy(score_threshold)
        self.transfer_policy = TransferPolicy(score_threshold)
        self.chunk_repo = ChunkRepository(session)
        self.msg_repo = MessageRepository(session)
        self.retrieval_repo = RetrievalLogRepository(session)

    async def retrieve(self, query: str, top_k: int = 20) -> list[dict]:
        """向量检索 + 可选重排。"""
        vectors = await self.embedding.embed([query])
        results = await self.vector_store.search(vectors[0], top_k=top_k, filter_expr="status == 1")

        topk_scores = [{"chunk_id": r.chunk_id, "score": round(r.score, 4)} for r in results]

        if self.reranker and results:
            docs = [r.content for r in results]
            reranked = await self.reranker.rerank(query, docs, top_n=5)
            indices = [i for i, _ in reranked]
            topk_scores = [topk_scores[i] for i in indices if i < len(topk_scores)]
            topk_scores = topk_scores[:5]

        return topk_scores

    async def generate(
        self,
        session_id: int,
        query: str,
        model: str = "",
        stream: bool = False,
    ) -> dict | AsyncIterator[str]:
        """完整 RAG 管线（非流式返回 dict，流式返回 AsyncIterator）。"""
        start = time.time()

        # 1. 检索
        topk_scores = await self.retrieve(query)
        max_score = max((s["score"] for s in topk_scores), default=0.0)
        chunk_ids = [s["chunk_id"] for s in topk_scores]

        # 2. 命中判定
        hit_result = self.hit_policy.evaluate(
            [s["score"] for s in topk_scores], chunk_ids
        )

        # 3. 保存用户消息
        user_msg = await self.msg_repo.add(
            type(self).__name__ is not None and None or None  # placeholder
        )
        from app.models.chat import ChatMessage
        user_msg = ChatMessage(session_id=session_id, role="user", content=query, msg_type="text")
        await self.msg_repo.add(user_msg)

        # 4. 检索日志
        await self.retrieval_repo.add(
            type(self).__name__ is not None and None or None
        )

        # 5. 生成回答或转人工
        if hit_result.hit and self.llm:
            # 获取分片内容构建上下文
            chunks = []
            for cid in chunk_ids[:5]:
                chunk = await self.chunk_repo.get_by_id(cid)
                if chunk:
                    chunks.append(chunk.content)
            context = "\n\n---\n\n".join(chunks)

            system_prompt = "你是电商客服助手。根据以下知识库内容回答用户问题。如果知识库中没有相关信息，请诚实告知。\n\n知识库：\n" + context
            answer = await self.llm.generate(query, system_prompt=system_prompt)

            assistant_msg = ChatMessage(
                session_id=session_id,
                role="assistant",
                content=answer,
                msg_type="text",
                retrieval_ids=json.dumps(chunk_ids),
                latency_ms=int((time.time() - start) * 1000),
            )
            await self.msg_repo.add(assistant_msg)

            return {
                "hit": True,
                "answer": answer,
                "chunk_ids": chunk_ids,
                "score": hit_result.score,
                "latency_ms": int((time.time() - start) * 1000),
            }
        else:
            # 未命中 → 转人工
            transfer = self.transfer_policy.evaluate(max_score)
            from app.services.chat_service import ChatService
            chat_svc = ChatService(self.session)
            await chat_svc.transfer_to_human(session_id, transfer.reason.value if transfer.reason else "unknown")

            return {
                "hit": False,
                "answer": transfer.message,
                "transfer": True,
                "reason": transfer.reason.value if transfer.reason else "unknown",
                "latency_ms": int((time.time() - start) * 1000),
            }

    async def stream_generate(self, session_id: int, query: str) -> AsyncIterator[str]:
        """流式 RAG 生成（SSE 数据源）。"""
        # 简化版：先做检索，再流式生成
        topk_scores = await self.retrieve(query)
        max_score = max((s["score"] for s in topk_scores), default=0.0)
        chunk_ids = [s["chunk_id"] for s in topk_scores]

        hit_result = self.hit_policy.evaluate([s["score"] for s in topk_scores], chunk_ids)

        if hit_result.hit and self.llm:
            chunks = []
            for cid in chunk_ids[:5]:
                chunk = await self.chunk_repo.get_by_id(cid)
                if chunk:
                    chunks.append(chunk.content)
            context = "\n\n---\n\n".join(chunks)
            system_prompt = "你是电商客服助手。根据以下知识库内容回答用户问题。\n\n知识库：\n" + context

            full = ""
            async for token in self.llm.stream(query, system_prompt=system_prompt):
                full += token
                yield token
            yield json.dumps({"chunk_ids": chunk_ids, "score": hit_result.score})
        else:
            transfer = self.transfer_policy.evaluate(max_score)
            yield json.dumps({"transfer": True, "reason": transfer.reason.value if transfer.reason else "unknown", "message": transfer.message})