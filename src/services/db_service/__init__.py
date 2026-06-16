from sanic import Blueprint, Sanic
from .view import DBHandle, ReloadDataView

sensitive_router = Blueprint("db_routes", url_prefix="/api/input/instance/db")
reload_router = Blueprint("reload_routes", url_prefix="/api/data")


def create_db_router(app: Sanic):
    sensitive_router.add_route(DBHandle.as_view(app.ctx.db_tool), '/run')
    reload_router.add_route(ReloadDataView.as_view(), "/reload")
    return sensitive_router, reload_router
