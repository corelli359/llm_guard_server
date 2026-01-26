"""
配置查看API视图
提供查看当前数据源配置的接口
"""
from sanic import Request
from sanic.response import json as json_response
from sanic.views import HTTPMethodView
from config.data_source_config import get_data_source_config
from db.connect import db_connector
import os


class ConfigDataSourceHandler(HTTPMethodView):
    """数据源配置查看接口

    GET /api/config/data-source
    """

    async def get(self, request: Request):
        """获取当前数据源配置信息"""
        config = get_data_source_config()

        response_data = {
            "mode": config.mode,
            "config": {}
        }

        if config.is_file_mode():
            # 文件模式配置
            response_data["config"] = {
                "base_path": config.file_base_path,
                "use_cache": config.file_use_cache,
                "cache_ttl": config.file_cache_ttl,
                "files_status": await self._check_files_status(config.file_base_path)
            }
        else:
            # 数据库模式配置
            db_connected = False
            try:
                await db_connector.ping()
                db_connected = True
            except Exception:
                pass

            response_data["config"] = {
                "db_url": config.db_url if config.db_url else "from db_config",
                "connected": db_connected
            }

        return json_response(response_data, 200)

    async def _check_files_status(self, base_path: str) -> dict:
        """检查数据文件状态"""
        required_files = [
            "global_keywords.json",
            "meta_tags.json",
            "scenario_keywords.json",
            "scenario_policies.json",
            "global_defaults.json"
        ]

        files_status = {}
        for filename in required_files:
            file_path = os.path.join(base_path, filename)
            exists = os.path.exists(file_path)
            size = os.path.getsize(file_path) if exists else 0

            files_status[filename] = {
                "exists": exists,
                "size_bytes": size,
                "path": file_path
            }

        return files_status
