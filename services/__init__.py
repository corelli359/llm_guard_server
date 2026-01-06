from sanic import Sanic
from .sensitive_view import create_sensitive_router
from .guard_view import create_guard_router
from .rule_engine_view import create_rule_engine_router
from .db_service import create_db_router


def create_routers(app: Sanic):
    sensitive_router = create_sensitive_router(app)
    guard_router = create_guard_router(app)
    rule_engine_router = create_rule_engine_router(app)
    db_router = create_db_router(app)
    app.blueprint([sensitive_router, guard_router, rule_engine_router, db_router])
