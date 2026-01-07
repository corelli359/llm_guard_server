from collections import defaultdict
from typing import Dict, List
from utils import SingleTon, run_in_async
from tools.db_tools import DBConnectTool
from .ac_tool import SensitiveAutomatonLoaderByDB
import asyncio
from .ac_tool import CustomAcContainer, CustomVipContainer
from models import DecisionClassifyEnum, RuleGlobalDefaults
from sanic.log import logger

_APP_LOCKS: Dict[str, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


async def get_lock_by_app_id(app_id: str) -> asyncio.Lock:
    if app_id not in _APP_LOCKS:
        async with _GLOBAL_LOCK:
            if app_id not in _APP_LOCKS:
                _APP_LOCKS[app_id] = asyncio.Lock()
    return _APP_LOCKS[app_id]


DECISION_MAPPING: dict = {
    "BLOCK": DecisionClassifyEnum.REJECT,
    "PASS": DecisionClassifyEnum.PASS,
    "REWRITE": DecisionClassifyEnum.REWRITE,
    "REVIEW": DecisionClassifyEnum.MANUAL,
}


class DataProvider(metaclass=SingleTon):
    def __init__(self, db_tool: DBConnectTool) -> None:
        self.db_tool = db_tool
        self._global_ac: SensitiveAutomatonLoaderByDB | None = None

        self._custom_ac: Dict[str, CustomAcContainer] = {}

        self._vip: Dict[str, CustomVipContainer] = {}

        self._app_super_rules: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._global_rules: Dict[str, DecisionClassifyEnum] = {}

    @property
    def global_rules(self):
        return self._global_rules

    @global_rules.setter
    def global_rules(self, rules):
        self._global_rules = rules

    @property
    def custom_vip(self):
        return self._vip

    @custom_vip.setter
    def custom_vip(self, vip):
        self._vip = vip

    @property
    def custom_ac(self):
        return self._custom_ac

    @custom_ac.setter
    def custom_ac(self, ac):
        self._custom_ac = ac

    @property
    def global_ac(self):
        return self._global_ac

    @global_ac.setter
    def global_ac(self, ac):
        self._global_ac = ac

    async def build_rule(self):
        if not self.global_rules:
            try:
                results: List[RuleGlobalDefaults] = (
                    await self.db_tool.load_global_rules()
                )
                if results:
                    self.global_rules = {
                        f"{item.tag_code}-{item.extra_condition}": DECISION_MAPPING[
                            item.strategy.strip()
                        ]
                        for item in results
                    }
            except Exception as e:
                logger.error(f"{str(e)}")

    async def build_ac(self, ac_type: str, app_id: str = ""):

        match ac_type:
            case "global":
                data = await self.db_tool.load_global_words()
                self.global_ac = SensitiveAutomatonLoaderByDB()
                await run_in_async(self.global_ac.load_keywords, data)
            case "customize":
                app_id_lock: asyncio.Lock = await get_lock_by_app_id(app_id)
                async with app_id_lock:
                    if app_id and app_id not in self.custom_ac:
                        black_list, white_list = await self.db_tool.load_custom_words(
                            app_id
                        )
                        ac_container = CustomAcContainer()

                        if black_list:
                            ac = SensitiveAutomatonLoaderByDB()
                            await run_in_async(ac.load_keywords, black_list)
                            ac_container.black_ac = ac
                        if white_list:
                            ac_container.white_ac = set([_.keyword for _ in white_list])
                        ac_container.loaded = True
                        self.custom_ac[app_id] = ac_container

            case "vip":
                app_id_lock: asyncio.Lock = await get_lock_by_app_id(app_id)
                async with app_id_lock:
                    if app_id and app_id not in self.custom_vip:
                        (
                            vip_black_words,
                            vip_black_rules,
                            vip_white_words,
                            vip_white_rules,
                        ) = await self.db_tool.load_scenario_by_app_id(app_id)
                        vip_container = CustomVipContainer()
                        if vip_black_words:
                            ac = SensitiveAutomatonLoaderByDB()
                            await run_in_async(ac.load_keywords, vip_black_words)
                            vip_container.black_ac = ac
                        if vip_black_rules:
                            vip_container.black_rule = set(vip_black_rules)
                        if vip_white_rules:
                            vip_container.white_rule = set(vip_white_rules)
                        if vip_white_words:
                            ac = SensitiveAutomatonLoaderByDB()
                            await run_in_async(ac.load_keywords, vip_black_words)
                            vip_container.white_ac = ac
                        vip_container.loaded = True
                        self.custom_vip[app_id] = vip_container
            case _:
                raise Exception("NO_MATCHED_AC_TYPE_ERROR")
