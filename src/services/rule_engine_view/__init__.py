from sanic import Blueprint, Sanic
from .view import RuleEngineInputHandler, AirRuleEngineInputHandler

rule_engine_router = Blueprint("rule_engine_routes", url_prefix="/api/input/instance/rule", strict_slashes=False)

air_router = Blueprint("rule_engine_air_routes", url_prefix="api/rule")


def create_rule_engine_router(app: Sanic) -> Blueprint:
    rule_engine_router.add_route(RuleEngineInputHandler.as_view(), '/run')

    return rule_engine_router


def create_rule_engin_air_router(app: Sanic) -> Blueprint:
    air_router.add_route(AirRuleEngineInputHandler.as_view(), '/v1/ZHAISPXXLLMSAFE01')
    return air_router
