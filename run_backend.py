"""
Quick start script for running the backend server.
"""

import uvicorn
from backend.config import get_app_config

if __name__ == "__main__":
    config = get_app_config()
    
    print("=" * 60)
    print("Starting Conversational AI System - Phase 1")
    print("=" * 60)
    print(f"Server: http://{config.HOST}:{config.PORT}")
    print(f"Health check: http://{config.HOST}:{config.PORT}/health")
    print(f"API docs: http://{config.HOST}:{config.PORT}/docs")
    print("=" * 60)
    
    uvicorn.run(
        "backend.main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True,
        log_level=config.LOG_LEVEL.lower()
    )
