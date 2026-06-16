# encoding:utf-8
# author: corelli
import jwt
import time
import os

AGENT_SALT = os.getenv("JWT_SALT", "")
APP_ID = os.getenv("X_APP_ID", "")
_cached_token: str | None = None
_token_expire_time: float = 0.0


def generate_agent_token() -> str:
    global _cached_token, _token_expire_time
    now = time.time()
    if _cached_token is not None and now < _token_expire_time - 100:
        return _cached_token

    ttl = 3600
    if not AGENT_SALT:
        return ""
    payload = {
        'appid': APP_ID,  # 主题，可以是用户名或其他唯一标识符
        'exp': int(time.time()) + ttl  # 过期秒数
    }
    jwt_token = jwt.encode(payload, AGENT_SALT, algorithm='HS256')  # 签名算法
    _cached_token = jwt_token
    _token_expire_time = now + ttl
    return jwt_token
