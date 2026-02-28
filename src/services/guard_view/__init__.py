
from sanic import Blueprint, Sanic
from .view import GuardHandler

sensitive_router = Blueprint("guard_routes", url_prefix="/api/input/instance/guard")


def create_guard_router(app:Sanic) -> Blueprint:
    sensitive_router.add_route(GuardHandler.as_view(),'/run')
    return sensitive_router


