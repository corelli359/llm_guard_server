from collections import defaultdict
from typing import Optional, Dict
from utils import SingleTon, run_in_async
import ahocorasick
from tools.db_tools import DBConnectTool
from tools.sensitive_tools import SensitiveAutomatonLoaderByDB
import asyncio

_APP_LOCKS: Dict[str, asyncio.Lock] = {}
_GLOBAL_LOCK = asyncio.Lock()


async def get_lock_by_app_id(app_id: str) -> asyncio.Lock:
    if app_id not in _APP_LOCKS:
        async with _GLOBAL_LOCK:
            if app_id not in _APP_LOCKS:
                _APP_LOCKS[app_id] = asyncio.Lock()
    return _APP_LOCKS[app_id]


class DataProvider(metaclass=SingleTon):
    def __init__(self, db_tool: DBConnectTool) -> None:
        self.db_tool = db_tool
        self._global_ac: Optional[ahocorasick.Automaton] = None

        self._custom_ac: Dict[str, ahocorasick.Automaton] = {}

        self._super_ac: Dict[str, ahocorasick.Automaton] = {}

        self._app_super_rules: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._global_rules: Dict[str, str] = {}

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

    async def build_ac(self, ac_type: str, app_id: str = ""):
        match ac_type:
            case "global":
                data = await self.db_tool.load_global_words()
                ac = SensitiveAutomatonLoaderByDB()
                self.global_ac = await run_in_async(ac.load_keywords, data)
            case "customize":
                app_id_lock: asyncio.Lock = await get_lock_by_app_id(app_id)
                async with app_id_lock:
                    if app_id and app_id not in self.custom_ac:
                        data = await self.db_tool.load_custom_words(app_id)
                        ac = SensitiveAutomatonLoaderByDB()
                        self.custom_ac[app_id] = await run_in_async(
                            ac.load_keywords, data
                        )
            case "vip":
                pass
            case _:
                raise Exception("NO_MATCHED_AC_TYPE_ERROR")
