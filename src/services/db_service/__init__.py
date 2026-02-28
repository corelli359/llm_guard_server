
from sanic import Blueprint, Sanic
from .view import DBHandle

sensitive_router = Blueprint("db_routes", url_prefix="/api/input/instance/db")


def create_db_router(app:Sanic) -> Blueprint:
    sensitive_router.add_route(DBHandle.as_view(app.ctx.db_tool),'/run')
    return sensitive_router


