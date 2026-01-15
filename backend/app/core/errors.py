from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AppError(Exception):
    """统一业务异常：可测、可断言、可带 error_code."""
    error_code: str
    message: str
    http_status: int = 400
    details: Optional[Dict[str, Any]] = None


# 建议先定义一批常用 error_code（后面写用例/断言很舒服）
class ErrorCode:
    AUTH_INVALID_TOKEN = "AUTH_INVALID_TOKEN"
    AUTH_FORBIDDEN = "AUTH_FORBIDDEN"

    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
    ORDER_STATE_INVALID = "ORDER_STATE_INVALID"

    STOCK_INSUFFICIENT = "STOCK_INSUFFICIENT"
    PRICE_INVALID_DISCOUNT = "PRICE_INVALID_DISCOUNT"

    VALIDATION_ERROR = "VALIDATION_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
