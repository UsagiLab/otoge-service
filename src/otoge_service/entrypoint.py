import asyncio
import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from maimai_py import MaimaiPyError
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from otoge_service import sessions
from otoge_service.exceptions import LeporidException
from otoge_service.settings import get_settings

settings = get_settings()


class SuccessResponseMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)
        if request.url.path.endswith("/openapi.json"):
            return response
        if not 200 <= response.status_code < 300:
            return response
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type.lower():
            return response
        if hasattr(response, "body_iterator"):
            raw_body = b"".join([chunk async for chunk in response.body_iterator])  # type: ignore
        else:
            raw_body = getattr(response, "body", b"")
        if raw_body in (None, b""):
            data = None
        else:
            charset = getattr(response, "charset", "utf-8") or "utf-8"
            try:
                data = json.loads(raw_body.decode(charset))
            except (ValueError, UnicodeDecodeError):
                return response
        payload = {"code": 200, "node": "success", "detail": None, "data": data}
        headers = {k: v for k, v in response.headers.items() if k.lower() not in {"content-length", "content-type"}}
        wrapped_response = JSONResponse(payload, status_code=response.status_code, headers=headers)
        wrapped_response.background = response.background
        return wrapped_response


@asynccontextmanager
async def init_lifespan(asgi_app: FastAPI):
    asyncio.create_task(sessions.maimai_client.songs())
    await sessions.init_db()
    if settings.enable_developer_check:
        await sessions.init_developers()
    yield  # Above: Startup process Below: Shutdown process
    await sessions.async_engine.dispose()


def init_routes(asgi_app: FastAPI) -> None:
    from otoge_service.routes import router  # noqa: F401

    @asgi_app.get("/", include_in_schema=False)
    async def root():
        return {"message": "Welcome to Maimai Prober API. Visit /docs for API documentation."}

    asgi_app.include_router(router)


def init_exception_handlers(asgi_app: FastAPI) -> None:
    @asgi_app.exception_handler(MaimaiPyError)
    async def maimai_py_error_handler(request, exception: MaimaiPyError):
        return LeporidException.BAD_REQUEST.with_detail_ex("maimai-py-error", repr(exception)).as_response()

    @asgi_app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, error: RequestValidationError):
        details_list = []
        for err in error.errors():
            details_list.append({"message": str(err)})
        return LeporidException.VALIDATION_ERROR.with_detail(str(details_list)).as_response()

    @asgi_app.exception_handler(Exception)
    async def general_exception_handler(request, exception: Exception):
        return LeporidException.INTERNAL_SERVER_ERROR.with_detail(repr(exception)).as_response()

    @asgi_app.exception_handler(LeporidException)
    async def leporid_exception_handler(request, ex: LeporidException):
        return ex.as_response()


def init_middleware(asgi_app: FastAPI) -> None:
    asgi_app.add_middleware(SuccessResponseMiddleware)


def init_openapi(asgi_app: FastAPI) -> None:
    def custom_openapi():
        if asgi_app.openapi_schema:
            return asgi_app.openapi_schema

        openapi_schema = get_openapi(
            title=asgi_app.title,
            version=asgi_app.version,
            description=asgi_app.description,
            routes=asgi_app.routes,
        )

        components = openapi_schema.setdefault("components", {}).setdefault("schemas", {})
        components["LeporidResponse"] = {
            "title": "LeporidResponse",
            "type": "object",
            "properties": {
                "code": {"type": "integer", "example": 200},
                "node": {"type": "string", "example": "success"},
                "message": {"type": ["string", "null"], "example": None},
                "data": {"nullable": True},
            },
            "required": ["code", "node", "message", "data"],
        }

        for path_item in openapi_schema.get("paths", {}).values():
            for operation in path_item.values():
                for response in operation.get("responses", {}).values():
                    content = response.get("content")
                    if not content:
                        continue
                    json_content = content.get("application/json")
                    if not json_content:
                        continue
                    original_schema = json_content.get("schema") or {"nullable": True}
                    json_content["schema"] = {
                        "allOf": [
                            {"$ref": "#/components/schemas/LeporidResponse"},
                            {"type": "object", "properties": {"data": original_schema}},
                        ]
                    }

        if paths := openapi_schema.get("paths"):
            for _, method_item in paths.items():
                for _, param in method_item.items():
                    for key in list(param["responses"].keys()):
                        # Remove 4xx and 5xx responses from the OpenAPI schema
                        if key.startswith("4") or key.startswith("5"):
                            del param["responses"][key]

        asgi_app.openapi_schema = openapi_schema
        return asgi_app.openapi_schema

    asgi_app.openapi = custom_openapi


def init_api() -> FastAPI:
    """Create & initialize our app."""
    asgi_app = FastAPI(lifespan=init_lifespan)

    init_routes(asgi_app)
    init_exception_handlers(asgi_app)
    init_middleware(asgi_app)
    init_openapi(asgi_app)

    return asgi_app


asgi_app = init_api()


def main():
    uvicorn.run("otoge_service.entrypoint:asgi_app", port=settings.bind_port, host=settings.bind_host)


if __name__ == "__main__":
    main()
