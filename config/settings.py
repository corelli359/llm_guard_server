from typing import Dict, Any
import os

SENSITIVE_DICT_PATH: str = (
    "/Users/weipeng/Desktop/PY_WORK_SPACE/LangTaste/agent_dev_gemini/security/llm_guard_server/assets/sensitive_words_lines.txt"
)
# SENSITIVE_DICT_PATH:str = './assets/sensitive_words_lines.txt'
SENSITIVE_DICT = {}
SENSITIVE_CUSTOMIZE_DICT = {}
SENSITIVE_CUSTOMIZE_PATH = {
    "999999": "/Users/weipeng/Desktop/PY_WORK_SPACE/LangTaste/agent_dev_gemini/security/llm_guard_server/assets/999999.txt"
}


SENSITIVE_WHITE_DICT = {}
SENSITIVE_CUSTOMIZE_WHITE_PATH = {
    "999999": "/Users/weipeng/Desktop/PY_WORK_SPACE/LangTaste/agent_dev_gemini/security/llm_guard_server/assets/999999-w.txt"
}

RULE_CUSTOMIZE_DICT = {}


CUSTOMIZE_RULE_VIP_BLACK_WORDS_DICT = {}
CUSTOMIZE_RULE_VIP_BLACK_WORDS_PATH = {
    "999999": "/Users/weipeng/Desktop/PY_WORK_SPACE/LangTaste/agent_dev_gemini/security/llm_guard_server/assets/999999-vip-black.txt"
}

CUSTOMIZE_RULE_VIP_BLACK_RULE_DICT: Dict[str, Dict[str, Any]] = {}
CUSTOMIZE_RULE_VIP_BLACK_RULE_PATH = {}


CUSTOMIZE_RULE_VIP_WHITE_WORDS_DICT = {}
CUSTOMIZE_RULE_VIP_WHITE_WORDS_PATH = {
    "999999": "/Users/weipeng/Desktop/PY_WORK_SPACE/LangTaste/agent_dev_gemini/security/llm_guard_server/assets/999999-vip-black.txt"
}

CUSTOMIZE_RULE_VIP_WHITE_RULE_DICT = {}
CUSTOMIZE_RULE_VIP_WHITE_RULE_PATH = {}


CUSTOMIZE_RULE_DICT_SAMPLE = {"999999": {"A-1-controversial": 0}}


class Config:
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = False
    AUTO_RELOAD = True
