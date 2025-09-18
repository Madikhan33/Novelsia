"""
Middleware для логирования запросов.
"""

import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def log_request(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Request: {request.method} {request.url} - {duration:.2f}s")
        return response



    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Request: {request.method} {request.url} - {duration:.2f}s")
        return response
    
    
    