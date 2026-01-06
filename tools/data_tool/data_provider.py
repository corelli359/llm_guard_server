from collections import defaultdict
from typing import Optional, Dict
from utils import SingleTon, run_in_async
import ahocorasick
from tools.db_tools import DBConnectTool
from tools.sensitive_tools import SensitiveAutomatonLoaderByDB


class DataProvider(metaclass=SingleTon):
    def __init__(self, db_tool: DBConnectTool) -> None:
        self.db_tool = db_tool
        self._global_ac: Optional[ahocorasick.Automaton] = None

        self._custom_ac: Dict[str, ahocorasick.Automaton] = {}

        self._super_ac: Dict[str, ahocorasick.Automaton] = {}

        self._app_super_rules: Dict[str, Dict[str, str]] = defaultdict(dict)
        self._global_rules: Dict[str, str] = {}

        self.all_data = None

    # async def build(self):
    #     self.all_data = await self.db_tool.load_data_from_db()

    @property
    def global_ac(self):
        return self._global_ac

    @global_ac.setter
    def global_ac(self, ac):
        self._global_ac = ac

    async def build_ac(self, ac_type: str):
        match ac_type:
            case "global":
                data = await self.db_tool.load_global_words()
                ac = SensitiveAutomatonLoaderByDB()
                self.global_ac = await run_in_async(ac.load_keywords, data)
            case "customize":
                pass
            case "vip":
                pass
            case _:
                raise Exception("NO_MATCHED_AC_TYPE_ERROR")
