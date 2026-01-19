from enum import Enum

class ErrorCode(str, Enum):
    """
    统一错误码定义
    """
    
    # ==========================
    # 4xx: 客户端/参数问题
    # ==========================
    INVALID_PARAM = "INVALID_PARAM"          # 通用参数错误
    VALIDATION_ERROR = "VALIDATION_ERROR"    # Pydantic 校验失败

    # HTTP 404: 资源未找到
    NOT_FOUND = "NOT_FOUND"

    # ==========================
    # 5xx: 服务端/业务逻辑问题
    # ==========================
    SYSTEM_ERROR = "SYSTEM_ERROR"            # 兜底系统错误
    DB_ERROR = "DB_ERROR"                    # 数据库连接或查询失败
    
    # 业务特有错误 (替换原有的硬编码字符串)
    MODEL_CONFIG_ERROR = "MODEL_CONFIG_ERROR" # 模型配置缺失
    RULE_ENGINE_ERROR = "RULE_ENGINE_ERROR"   # 规则引擎执行异常
    DATA_LOAD_ERROR = "DATA_LOAD_ERROR"       # 数据/词表加载失败
