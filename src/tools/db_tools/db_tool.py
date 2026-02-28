from contextlib import asynccontextmanager
from typing import List, Dict
from unittest import result
from db import RuleDataLoaderDAO, DBConnector
from models import RuleScenarioPolicy
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from models import DECISION_MAPPING, DecisionClassifyEnum


class DBConnectTool:
    def __init__(self, connector: DBConnector) -> None:
        self.dao: RuleDataLoaderDAO | None = None
        self.connector = connector

        self._session_factory = None

    @property
    def session_factory(self):
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                bind=self.connector.conn,
                class_=AsyncSession,
                expire_on_commit=False,
                autoflush=False,
            )
        return self._session_factory

    @asynccontextmanager
    async def get_dao(self):
        # 调用 self.session_factory (会自动触发上面的懒加载逻辑)
        async with self.session_factory() as session:
            dao = RuleDataLoaderDAO(session)
            try:
                yield dao
            except Exception as e:
                raise e

    async def load_global_rules(self):
        async with self.get_dao() as dao:
            results = await dao.get_all_global_defaults()
        return {
            f"{item.tag_code}-{item.extra_condition}": DECISION_MAPPING[
                item.strategy.strip()
            ]
            for item in results
        }

    async def load_global_words(self):
        async with self.get_dao() as dao:
            result = await dao.get_all_global_keywords()
        return result

    async def load_all_custom_words(self):
        async with self.get_dao() as dao:
            results = await dao.get_all_scenario_keywords()
        return results

    async def load_custom_words(self, app_id: str):
        async with self.get_dao() as dao:
            result = await dao.get_scenario_keywords_by_appid(app_id)
        black_list = []
        white_list = []
        for row in result:
            if row.category == 1:
                black_list.append(row)
            else:
                white_list.append(row)
        return black_list, white_list

    async def load_all_custom_rules(self):
        async with self.get_dao() as dao:
            results = await dao.get_all_scenario_rules()
        return results

    async def load_all_vip(self):
        async with self.get_dao() as dao:
            results = await dao.load_all_vip()
        return results

    async def load_custom_rule(self, app_id: str):
        async with self.get_dao() as dao:
            results: List[RuleScenarioPolicy] = await dao.get_scenario_rule_by_appid(
                app_id
            )
        return {
            f"{row.match_value}-{row.extra_condition}": DECISION_MAPPING[
                row.strategy.upper()
            ]
            for row in results
        }

    async def load_vip_scenario_by_app_id(self, app_id: str):
        async with self.get_dao() as dao:
            result = await dao.get_vip_scenario_by_appid(app_id)

        vip_black_words = []
        vip_white_words = []
        vip_black_rules: Dict[str, DecisionClassifyEnum] = {}
        vip_white_rules: Dict[str, DecisionClassifyEnum] = {}

        for row in result:
            if row.match_type == "words" and row.strategy == "block":
                vip_black_words.append(row.match_value)
            elif row.match_type == "words" and row.strategy == "pass":
                vip_white_words.append(row.match_value)
            elif row.match_type == "rule" and row.strategy == "block":
                vip_black_rules.update(
                    {
                        f"{row.match_value}-{row.extra_condition}": DECISION_MAPPING[
                            row.strategy.upper()
                        ]
                    }
                )
            elif row.match_type == "rule" and row.strategy == "pass":
                vip_white_rules.update(
                    {
                        f"{row.match_value}-{row.extra_condition}": DECISION_MAPPING[
                            row.strategy.upper()
                        ]
                    }
                )
        return vip_black_words, vip_black_rules, vip_white_words, vip_white_rules
