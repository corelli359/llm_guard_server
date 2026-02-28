"""
配置视图路由
"""
from sanic import Blueprint
from .view import ConfigDataSourceHandler


def create_config_router(app):
    """创建配置路由"""
    config_bp = Blueprint("config", url_prefix="/api/config")

    # 注册数据源配置查看接口
    config_bp.add_route(
        ConfigDataSourceHandler.as_view(),
        "/data-source",
        name="data_source_config"
    )

    return config_bp
