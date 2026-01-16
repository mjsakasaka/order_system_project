from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .core.config import settings
from .core.middleware import TraceIdMiddleware
from .core.errors import AppError, ErrorCode

import app.models


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # Middleware：trace_id + request log
    app.add_middleware(TraceIdMiddleware)

    # 业务异常统一返回（可断言 error_code）
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        trace_id = getattr(request.state, "trace_id", None)
        return JSONResponse(
            status_code=exc.http_status,
            content={
                "trace_id": trace_id,
                "error_code": exc.error_code,
                "message": exc.message,
                "details": exc.details or {},
            },
        )

    # FastAPI/Starlette 默认 HTTPException（也统一成我们的格式）
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        trace_id = getattr(request.state, "trace_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "trace_id": trace_id,
                "error_code": ErrorCode.VALIDATION_ERROR
                if 400 <= exc.status_code < 500
                else ErrorCode.INTERNAL_ERROR,
                "message": exc.detail,
                "details": {},
            },
        )

    # 未捕获异常：统一输出（避免前端/测试拿不到一致结构）
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        trace_id = getattr(request.state, "trace_id", None)
        return JSONResponse(
            status_code=500,
            content={
                "trace_id": trace_id,
                "error_code": ErrorCode.INTERNAL_ERROR,
                "message": "Internal server error",
                "details": {},
            },
        )

    # Health check
    @app.get("/health")
    async def health():
        return {"status": "ok", "env": settings.ENV}
    


    from .db.session import debug_db_info

    @app.get("/debug/db")
    async def debug_db():
        return debug_db_info()
    

    from .db.session import engine
    from .db.base import Base

    @app.on_event("startup")
    async def on_startup():
        Base.metadata.create_all(bind=engine)

    from .api.v1.router import router as v1_router
    app.include_router(v1_router)


    return app


app = create_app()
