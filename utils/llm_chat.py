import threading
import httpx
from typing import Dict, Optional
from langchain_openai import ChatOpenAI
from config import MODEL_CONFIGS, Config
from models import VllmType
from .jwt_utils import generate_jwt


class AuthHTTPClient(httpx.AsyncClient):
    """自定义 HTTP 客户端，每次请求前动态添加认证 headers"""

    async def send(self, request, *args, **kwargs):
        """重写 send 方法，在发送请求前添加认证 headers"""
        try:
            # 每次请求前生成新的 JWT
            token = generate_jwt()
            request.headers["Authorization"] = f"Bearer {token}"
            request.headers["x-app-id"] = Config.X_APP_ID
        except Exception as e:
            print(f"[ERROR] Failed to generate JWT: {e}")
            raise

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

        # 使用自定义的 AuthHTTPClient
        self.shared_client = AuthHTTPClient(
            limits=limits,
            timeout=httpx.Timeout(60.0, connect=10.0),
            follow_redirects=True,
        )

        # 模型实例缓存池
        self._model_instances: Dict[str, ChatOpenAI] = {}

        self._initialized = True
        print("LLMManager 核心服务已初始化（支持动态 JWT 认证）")

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
                        raise ValueError(f"MODEL_CONFIG_NOT_FOUND_ERROR: {model_type}")

                    print(f"初始化模型接入: {model_type.value} ...")
                    llm = ChatOpenAI(
                        model=config["model_name"],
                        temperature=config["temperature"],
                        api_key=config["api_key"],
                        base_url=config["base_url"],
                        max_retries=config.get("max_retries", 3),
                        http_async_client=self.shared_client,  # 使用自定义客户端
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
