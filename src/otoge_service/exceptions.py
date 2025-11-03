from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import ClassVar

from fastapi.responses import JSONResponse


@dataclass(frozen=True)
class LeporidException(RuntimeError):
    message: str
    http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR

    NOT_FOUND: ClassVar["LeporidException"]
    ALREADY_EXISTS: ClassVar["LeporidException"]
    INVALID_CREDENTIALS: ClassVar["LeporidException"]
    VALIDATION_ERROR: ClassVar["LeporidException"]
    EXPIRED_CREDENTIALS: ClassVar["LeporidException"]
    FORBIDDEN: ClassVar["LeporidException"]
    BAD_REQUEST: ClassVar["LeporidException"]
    INTERNAL_SERVER_ERROR: ClassVar["LeporidException"]

    def msg(self, message: str) -> "LeporidException":
        return LeporidException(http_status=self.http_status, message=message)

    def as_response(self) -> JSONResponse:
        return JSONResponse(
            {
                "code": int(self.http_status),
                "message": self.message,
                "data": None,
            },
            status_code=self.http_status,
        )


LeporidException.NOT_FOUND = LeporidException("资源不存在", http_status=HTTPStatus.NOT_FOUND)
LeporidException.ALREADY_EXISTS = LeporidException("资源已存在", http_status=HTTPStatus.CONFLICT)
LeporidException.INVALID_CREDENTIALS = LeporidException("无效的凭据", http_status=HTTPStatus.UNAUTHORIZED)
LeporidException.VALIDATION_ERROR = LeporidException("验证错误", http_status=HTTPStatus.BAD_REQUEST)
LeporidException.EXPIRED_CREDENTIALS = LeporidException("凭据已过期", http_status=HTTPStatus.UNAUTHORIZED)
LeporidException.FORBIDDEN = LeporidException("没有权限执行该操作", http_status=HTTPStatus.FORBIDDEN)
LeporidException.BAD_REQUEST = LeporidException("错误的请求", http_status=HTTPStatus.BAD_REQUEST)
LeporidException.INTERNAL_SERVER_ERROR = LeporidException("内部错误", http_status=HTTPStatus.INTERNAL_SERVER_ERROR)
