"""通用工具函数。"""
from __future__ import annotations
from typing import Optional


def mask_sensitive(text: str, keep_prefix: int = 3, keep_suffix: int = 2) -> str:
    """脱敏：保留前 n 后 m 字符，中间用 *** 替换。"""
    if len(text) <= keep_prefix + keep_suffix:
        return "*" * len(text)
    return text[:keep_prefix] + "***" + text[-keep_suffix:]


def hash_content(content: str) -> str:
    """SHA-256 哈希。"""
    import hashlib
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def build_ticket_no(prefix: str = "T", count: int = 1) -> str:
    """生成工单编号。"""
    from datetime import datetime
    date_str = datetime.utcnow().strftime("%Y%m%d")
    return f"{prefix}{date_str}-{count:04d}"