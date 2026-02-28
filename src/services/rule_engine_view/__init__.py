from sanic import Blueprint, Sanic
from .view import RuleEngineInputHandler

rule_engine_router = Blueprint("rule_engine_routes", url_prefix="/api/input/instance/rule")


def create_rule_engine_router(app:Sanic) -> Blueprint:
    rule_engine_router.add_route(RuleEngineInputHandler.as_view(),'/run')
    return rule_engine_router


