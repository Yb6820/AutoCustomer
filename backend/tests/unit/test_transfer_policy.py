"""转人工策略单元测试。"""
from app.domain.chat.transfer_policy import TransferPolicy, TransferReason


class TestTransferPolicy:
    def test_hit_above_threshold(self):
        policy = TransferPolicy(score_threshold=0.78)
        decision = policy.evaluate(max_score=0.85)
        assert decision.should_transfer is False

    def test_below_threshold_transfers(self):
        policy = TransferPolicy(score_threshold=0.78)
        decision = policy.evaluate(max_score=0.50)
        assert decision.should_transfer is True
        assert decision.reason == TransferReason.BELOW_THRESHOLD

    def test_user_request_transfers(self):
        policy = TransferPolicy(score_threshold=0.78)
        decision = policy.evaluate(max_score=0.90, user_text="转人工")
        assert decision.should_transfer is True
        assert decision.reason == TransferReason.USER_REQUEST

    def test_model_error_transfers(self):
        policy = TransferPolicy(score_threshold=0.78)
        decision = policy.evaluate(max_score=0.90, model_error=True)
        assert decision.should_transfer is True
        assert decision.reason == TransferReason.MODEL_FAILURE