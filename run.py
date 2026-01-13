#!/usr/bin/env python3
"""
Startup script for the FastAPI blog backend.
This script reads configuration from .env and starts the server accordingly.
"""
import uvicorn
from src.config import config

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=config.SERVER_PORT,
        reload=True,
        log_level="info"
    )
