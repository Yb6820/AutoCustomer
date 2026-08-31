"""分片策略单元测试。"""
from app.domain.kb.chunking import FixedSizeChunking


class TestFixedSizeChunking:
    def test_split_small_text(self):
        strategy = FixedSizeChunking()
        chunks = strategy.split("hello world", chunk_size=100)
        assert len(chunks) == 1
        assert chunks[0].content == "hello world"

    def test_split_large_text(self):
        strategy = FixedSizeChunking()
        text = "a" * 300
        chunks = strategy.split(text, chunk_size=100, overlap=20)
        assert len(chunks) >= 3