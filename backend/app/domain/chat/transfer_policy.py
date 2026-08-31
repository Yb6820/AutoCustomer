"""转人工策略。"""
from dataclasses import dataclass
from enum import Enum


class TransferReason(Enum):
    BELOW_THRESHOLD = "below_threshold"      # 检索分数低于阈值
    USER_REQUEST = "user_request"             # 用户主动要求转人工
    MODEL_FAILURE = "model_failure"           # LLM 调用失败
    SENSITIVE_TOPIC = "sensitive_topic"       # 命中敏感词


@dataclass
class TransferDecision:
    should_transfer: bool
    reason: TransferReason | None = None
    message: str = ""


class TransferPolicy:
    """转人工判定策略。"""

    def __init__(self, score_threshold: float = 0.78):
        self.score_threshold = score_threshold

    def evaluate(self, max_score: float, user_text: str = "", model_error: bool = False) -> TransferDecision:
        if model_error:
            return TransferDecision(True, TransferReason.MODEL_FAILURE, "AI 服务暂时不可用，已为您转接人工客服")

        if self._is_user_request(user_text):
            return TransferDecision(True, TransferReason.USER_REQUEST, "已为您转接人工客服")

        if max_score < self.score_threshold:
            return TransferDecision(True, TransferReason.BELOW_THRESHOLD, "抱歉，我暂时无法回答您的问题，已为您转接人工客服")

        return TransferDecision(False)

    @staticmethod
    def _is_user_request(text: str) -> bool:
        keywords = ["转人工", "人工客服", "找人工", "转接人工", "人工服务", "找客服"]
        return any(kw in text.lower() for kw in keywords)