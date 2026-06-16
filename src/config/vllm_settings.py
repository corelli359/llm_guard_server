import os
from models import VllmType

MODEL_CONFIGS = {
    VllmType.INTENT_MODEL: {
        "base_url": os.getenv("INTENT_MODEL_BASE_URL", ""),
        "api_key": os.getenv("INTENT_MODEL_API_KEY", ""),
        "model_name": os.getenv("INTENT_MODEL_NAME", "deepseek-chat"),
        "temperature": float(os.getenv("INTENT_MODEL_TEMPERATURE", "0.0")),
    },
    VllmType.SAFE_MODEL: {
        "base_url": os.getenv("SAFE_MODEL_BASE_URL", "http://127.0.0.1:8000/v1"),
        "api_key": os.getenv("SAFE_MODEL_API_KEY", "EMPTY"),
        "model_name": os.getenv("SAFE_MODEL_NAME", "Qwen/Qwen3Guard-Gen-8B"),
        "temperature": float(os.getenv("SAFE_MODEL_TEMPERATURE", "0.0")),
    }
}
