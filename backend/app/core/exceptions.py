import traceback
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

logger = structlog.get_logger(__name__)


class AppException(Exception):
    def __init__(self, message: str = "Bad Request", code: int = 400, status_code: int = 400) -> None:
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Not Found", code: int = 404) -> None:
        super().__init__(message=message, code=code, status_code=404)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Unauthorized", code: int = 401) -> None:
        super().__init__(message=message, code=code, status_code=401)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Forbidden", code: int = 403) -> None:
        super().__init__(message=message, code=code, status_code=403)


class ConflictException(AppException):
    def __init__(self, message: str = "Conflict", code: int = 409) -> None:
        super().__init__(message=message, code=code, status_code=409)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation Error", code: int = 400) -> None:
        super().__init__(message=message, code=code, status_code=400)


class ServiceUnavailableException(AppException):
    def __init__(self, message: str = "Service Unavailable", code: int = 503) -> None:
        super().__init__(message=message, code=code, status_code=503)


class DomainError:
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.code,
                "message": exc.message,
                "request_id": _get_request_id(request),
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": 422,
                "message": "Validation Error",
                "request_id": _get_request_id(request),
                "detail": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            request_id=_get_request_id(request),
            exception_type=type(exc).__name__,
            traceback=traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "message": "Internal Server Error",
                "request_id": _get_request_id(request),
            },
        )