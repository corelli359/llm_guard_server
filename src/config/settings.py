from typing import Dict, Any
import os


class Config:
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = False
    AUTO_RELOAD = True
    WORKER = 1

    # LLM 网关认证配置
    JWT_SALT = os.getenv("JWT_SALT", "")
    X_APP_ID = os.getenv("X_APP_ID", "")
