"""
数据源配置管理模块
支持环境变量覆盖，优先级：环境变量 > 配置文件 > 默认值
"""
import os
from typing import Literal
from pydantic import BaseSettings, Field


class DataSourceConfig(BaseSettings):
    """数据源配置

    环境变量示例：
        export DATA_SOURCE_MODE=FILE
        export DATA_SOURCE_FILE_BASE_PATH=/nas/llm_guard_data
        export DATA_SOURCE_FILE_USE_CACHE=true
    """

    # 数据源模式：FILE 或 DB
    mode: Literal["FILE", "DB"] = Field(
        default="DB",
        description="数据源模式：FILE=文件存储，DB=数据库存储"
    )

    # 文件模式配置
    file_base_path: str = Field(
        default="data",
        description="文件存储的基础路径"
    )

    file_use_cache: bool = Field(
        default=True,
        description="是否启用文件缓存"
    )

    file_cache_ttl: int = Field(
        default=3600,
        description="文件缓存过期时间（秒）"
    )

    # 数据库模式配置（从现有配置读取）
    db_url: str = Field(
        default="",
        description="数据库连接URL"
    )

    class Config:
        env_prefix = "DATA_SOURCE_"  # 环境变量前缀
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"

    def is_file_mode(self) -> bool:
        """是否为文件模式"""
        return self.mode.upper() == "FILE"

    def is_db_mode(self) -> bool:
        """是否为数据库模式"""
        return self.mode.upper() == "DB"

    def get_file_path(self, filename: str) -> str:
        """获取完整的文件路径"""
        return os.path.join(self.file_base_path, filename)


# 全局配置实例（单例）
_config_instance = None


def get_data_source_config() -> DataSourceConfig:
    """获取数据源配置实例（单例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = DataSourceConfig()
    return _config_instance
