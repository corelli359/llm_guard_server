from models import VllmType

MODEL_CONFIGS = {
    VllmType.SAFE_MODEL: {
        "base_url": "https://api.deepseek.com",
        "api_key": "",
        "model_name": "deepseek-chat",
        "temperature": 0.0,
    }
}
