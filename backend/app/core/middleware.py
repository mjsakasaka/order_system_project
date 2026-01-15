import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings


class TraceIdMiddleware(BaseHTTPMiddleware):
    """
    - 从请求头读取 trace_id（默认 X-Trace-Id），没有则生成
    - 存到 request.state.trace_id
    - 写回响应头，保证每个响应可追踪
    """

    async def dispatch(self, request: Request, call_next):
        trace_header = settings.TRACE_HEADER_NAME
        trace_id = request.headers.get(trace_header) or str(uuid.uuid4())
        request.state.trace_id = trace_id

        start = time.time()
        try:
            response: Response = await call_next(request)
        except Exception:
            # 让全局 exception handler 处理，但 trace_id 已经在 request.state 里
            raise
        finally:
            duration_ms = int((time.time() - start) * 1000)

            # 最小可观测性日志：你后面可以换成 structured logging
            # 现在先用 print 也行（面试可说：已预留 trace_id 与请求耗时）
            print(
                f'trace_id={trace_id} method={request.method} path="{request.url.path}" '
                f"duration_ms={duration_ms}"
            )

        response.headers[trace_header] = trace_id
        return response
