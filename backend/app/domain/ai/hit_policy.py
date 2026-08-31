"""命中阈值判定策略。"""
from dataclasses import dataclass


@dataclass
class HitResult:
    hit: bool
    score: float
    threshold: float
    chunk_ids: list[int]
    top_scores: list[float]


class HitThresholdPolicy:
    """检索命中判定。"""

    def __init__(self, threshold: float = 0.78):
        self.threshold = threshold

    def evaluate(self, scores: list[float], chunk_ids: list[int]) -> HitResult:
        if not scores:
            return HitResult(hit=False, score=0.0, threshold=self.threshold, chunk_ids=[], top_scores=[])
        max_score = max(scores)
        return HitResult(
            hit=max_score >= self.threshold,
            score=max_score,
            threshold=self.threshold,
            chunk_ids=chunk_ids,
            top_scores=scores,
        )