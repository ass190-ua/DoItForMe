from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.response import error_response


class AppException(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def _json_error(
    *, code: str, message: str, status_code: int, details: dict[str, Any] | None = None
) -> JSONResponse:
    payload, response_status = error_response(
        code=code,
        message=message,
        details=details,
        status_code=status_code,
    )
    return JSONResponse(status_code=response_status, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
        return _json_error(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            details=exc.details,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors_clean = [
            {
                "loc": list(err.get("loc", [])),
                "msg": str(err.get("msg", "")),
                "type": str(err.get("type", "")),
            }
            for err in exc.errors()
        ]
        return _json_error(
            code="VALIDATION_ERROR",
            message="Request validation failed",
            status_code=422,
            details={"errors": errors_clean},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(_: Request, __: Exception) -> JSONResponse:
        return _json_error(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            status_code=500,
        )
