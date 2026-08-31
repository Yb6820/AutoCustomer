"""命中阈值策略单元测试。"""
from app.domain.ai.hit_policy import HitThresholdPolicy


class TestHitPolicy:
    def test_hit_above_threshold(self):
        policy = HitThresholdPolicy(0.78)
        result = policy.evaluate([0.85, 0.70], [1, 2])
        assert result.hit is True
        assert result.score == 0.85

    def test_below_threshold(self):
        policy = HitThresholdPolicy(0.78)
        result = policy.evaluate([0.50, 0.30], [1, 2])
        assert result.hit is False

    def test_empty_scores(self):
        policy = HitThresholdPolicy(0.78)
        result = policy.evaluate([], [])
        assert result.hit is False
        assert result.score == 0.0