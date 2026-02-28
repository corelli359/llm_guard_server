
from sanic import Blueprint, Sanic
from .view import SensitiveHandler

sensitive_router = Blueprint("sensitive_routes", url_prefix="/api/input/instance/sensitive")


def create_sensitive_router(app:Sanic) -> Blueprint:
    sensitive_router.add_route(SensitiveHandler.as_view(),'/run')
    return sensitive_router


