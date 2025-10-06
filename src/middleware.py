from fastapi import FastAPI, Request, Response
import time
from typing import Callable, Awaitable
import logging
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = logging.getLogger('uvicorn.access')
logger.disabled = True


def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def custom_logging(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start_time = time.time()
        method = request.method
        url = str(request.url)

        print(f"[Request] {method} {url} - Start")

        response = await call_next(request)

        process_time = time.time() - start_time
        status_code = response.status_code

        print(
            f"[Response] {method} {url} - Status: {status_code} - Time: {process_time:.4f}s")

        return response

    app.add_middleware(CORSMiddleware,
                       allow_origins=["*"],
                       allow_methods=["*"],
                       allow_headers=["*"],
                       allow_credentials=False,
                       )

    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=["localhost", "127.0.0.1"]
                       )
