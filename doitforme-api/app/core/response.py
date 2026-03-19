from typing import Any

from app.schemas.common import ErrorDetails, ErrorResponse, SuccessResponse


def success_response(data: Any, status_code: int = 200) -> tuple[dict[str, Any], int]:
    payload = SuccessResponse(data=data).model_dump(mode="json")
    return payload, status_code


def error_response(
    *,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int = 400,
) -> tuple[dict[str, Any], int]:
    payload = ErrorResponse(
        error=ErrorDetails(code=code, message=message, details=details)
    ).model_dump(mode="json")
    return payload, status_code
