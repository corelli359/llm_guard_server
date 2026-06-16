from sanic.log import logger
from sanic import json
from models import AirRequestData
import time

rule_engine_air_public_params = [
    "appId", "trCode", "trVersion", "trToken", "requestId", "timestamp", "data"
]

rule_engine_air_data_params = [
    "api_key",
]


def is_valid_rule_engine_air_params(body):
    for p in rule_engine_air_public_params:
        if not hasattr(body, p):
            logger.info(f"rule_engine_air_public_params not found:{p}")
            return False

    data = body.data
    for p in rule_engine_air_data_params:
        if not hasattr(data, p):
            logger.info(f"rule_engine_air_data_params not found:{p}")
            return False
    return True


def make_result(body: AirRequestData, response_id, return_type, additional_message="", data=None):
    if data is None:
        data = {}
    if additional_message!= '':
        msg = return_type[1] + '. ' + additional_message
    else:
        msg = return_type[1]

    ret = {
        'appId': body.appId,
        'trCode': body.trCode,
        'trVersion': body.trVersion,
        'resCode': return_type[0],
        'resMessage': msg,
        'responseId': response_id,
        'timestamp': int(time.time() * 1000),
        'data': data
    }

    return json(ret, 200)
