from __future__ import annotations

from dataclasses import dataclass
from http import HTTPStatus
from typing import ClassVar

from fastapi.responses import JSONResponse


@dataclass(frozen=True)
class LeporidException(RuntimeError):
    node: str
    message: str | None = None
    http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR

    NOT_FOUND: ClassVar["LeporidException"]
    ALREADY_EXISTS: ClassVar["LeporidException"]
    INVALID_CREDENTIALS: ClassVar["LeporidException"]
    VALIDATION_ERROR: ClassVar["LeporidException"]
    EXPIRED_CREDENTIALS: ClassVar["LeporidException"]
    FORBIDDEN: ClassVar["LeporidException"]
    BAD_REQUEST: ClassVar["LeporidException"]
    INTERNAL_SERVER_ERROR: ClassVar["LeporidException"]

    def with_node(self, code: str) -> "LeporidException":
        return LeporidException(node=code, http_status=self.http_status)

    def with_detail(self, message: str) -> "LeporidException":
        return LeporidException(node=self.node, http_status=self.http_status, message=message)

    def with_detail_ex(self, node: str, message: str) -> "LeporidException":
        return LeporidException(node=node, http_status=self.http_status, message=message)

    def as_response(self) -> JSONResponse:
        return JSONResponse(
            {
                "code": int(self.http_status),
                "node": self.node,
                "message": self.message,
                "data": None,
            },
            status_code=self.http_status,
        )


LeporidException.NOT_FOUND = LeporidException("not-found", http_status=HTTPStatus.NOT_FOUND)
LeporidException.ALREADY_EXISTS = LeporidException("already-exists", http_status=HTTPStatus.CONFLICT)
LeporidException.INVALID_CREDENTIALS = LeporidException("invalid-credentials", http_status=HTTPStatus.UNAUTHORIZED)
LeporidException.VALIDATION_ERROR = LeporidException("validation-error", http_status=HTTPStatus.BAD_REQUEST)
LeporidException.EXPIRED_CREDENTIALS = LeporidException("expired-credentials", http_status=HTTPStatus.UNAUTHORIZED)
LeporidException.FORBIDDEN = LeporidException("forbidden", http_status=HTTPStatus.FORBIDDEN)
LeporidException.BAD_REQUEST = LeporidException("bad-request", http_status=HTTPStatus.BAD_REQUEST)
LeporidException.INTERNAL_SERVER_ERROR = LeporidException("internal-server-error", http_status=HTTPStatus.INTERNAL_SERVER_ERROR)
