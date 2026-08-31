"""通用响应模型。"""
from __future__ import annotations
from typing import Any, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: T | None = None
    request_id: str = ""


class PaginatedResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = "ok"
    data: PaginatedData[T]
    request_id: str = ""


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int