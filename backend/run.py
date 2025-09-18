#!/usr/bin/env python3
"""
Скрипт для запуска Novelsia Backend API.
"""

import uvicorn
from config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    ) 