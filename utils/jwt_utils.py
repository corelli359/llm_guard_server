import jwt
import time
from config import Config


def generate_jwt(salt: str = None, expire_seconds: int = 3600) -> str:
    """
    生成 JWT token

    Args:
        salt: JWT 密钥，如果不提供则使用配置中的 JWT_SALT
        expire_seconds: 过期时间（秒），默认 1 小时

    Returns:
        JWT token 字符串
    """
    if salt is None:
        salt = Config.JWT_SALT

    if not salt:
        raise ValueError("JWT_SALT is not configured")

    # 生成 payload
    payload = {
        "iat": int(time.time()),  # 签发时间
        "exp": int(time.time()) + expire_seconds,  # 过期时间
        "app_id": Config.X_APP_ID,  # 可选：将 app_id 也放入 payload
    }

    # 生成 JWT
    token = jwt.encode(payload, salt, algorithm="HS256")

    return token
