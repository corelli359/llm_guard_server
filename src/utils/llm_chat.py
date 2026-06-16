import threading
import httpx
import os
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from config import MODEL_CONFIGS
from models import VllmType
from .jwt_download import generate_agent_token
from sanic.log import logger

APP_ID = os.getenv("X_APP_ID", "")


# def add_auth_headers(request: httpx.Request):
#     request.headers['Authorization'] = generate_agent_token()
#     request.headers['x-app-id'] = APP_ID


class AuthHttpClient(httpx.AsyncClient):
    async def send(self, request, *args, **kwargs):
        try:
            token = generate_agent_token()
            request.headers['Authorization'] = token
            # request.headers['Authorization'] = f"Bearer {token}"
            request.headers['x-app-id'] = APP_ID
        except Exception as e:
            logger.exception(f"authhttpclient exception:{e}, APP_ID:{APP_ID}")
        return await super().send(request, *args, **kwargs)


class LLMManager:
    _instance = None
    _lock = threading.Lock()  # 线程锁，防止多线程并发初始化时创建多个实例

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # 双重检查锁 (Double-Checked Locking)
                if not cls._instance:
                    cls._instance = super(LLMManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, "_initialized") and self._initialized:
            return

        limits = httpx.Limits(max_keepalive_connections=20, max_connections=150)

        self.shared_client = AuthHttpClient(
            limits=limits,
            timeout=httpx.Timeout(5.0, connect=5.0),
            # event_hooks={"request": [add_auth_headers]}
        )

        # 模型实例缓存池
        self._model_instances: Dict[str, ChatOpenAI] = {}

        self._initialized = True
        print("LLMManager 核心服务已初始化")

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def get_model(self, model_type: VllmType) -> ChatOpenAI:
        if model_type not in self._model_instances:
            with self._lock:
                if model_type not in self._model_instances:
                    config = MODEL_CONFIGS.get(model_type)
                    if not config:
                        logger.error(f"MODEL_CONFIG_NOT_FOUND_ERROR: {model_type}")
                        raise ValueError(f"MODEL_CONFIG_NOT_FOUND_ERROR: {model_type}")

                    llm = ChatOpenAI(
                        model=config["model_name"],
                        temperature=config["temperature"],
                        api_key=config["api_key"],
                        base_url=config["base_url"],
                        max_retries=config.get("max_retries", 3),
                        http_async_client=self.shared_client,
                    )
                    self._model_instances[model_type] = llm
        return self._model_instances[model_type]

    async def close(self):
        """显式关闭连接池"""
        if self.shared_client and not self.shared_client.is_closed:
            await self.shared_client.aclose()
            print("LMManager 连接池已释放")

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
