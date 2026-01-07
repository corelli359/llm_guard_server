from contextlib import asynccontextmanager
from typing import List
from db import RuleDataLoaderDAO, DBConnector
from sanic import Sanic
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


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
        return results

    async def load_global_words(self):
        async with self.get_dao() as dao:
            result = await dao.get_all_global_keywords()
        return result

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

    async def load_scenario_by_app_id(self, app_id: str):
        async with self.get_dao() as dao:
            result = await dao.get_scenario_by_appid(app_id)

        vip_black_words = []
        vip_white_words = []
        vip_black_rules: List[str] = []
        vip_white_rules = []

        for row in result:
            if row.match_type == "words" and row.strategy == "block":
                vip_black_words.append(row.match_value)
            elif row.match_type == "words" and row.strategy == "pass":
                vip_white_words.append(row.match_value)
            elif row.match_type == "rule" and row.strategy == "block":
                vip_black_rules.append(row.match_value)
            elif row.match_type == "rule" and row.strategy == "pass":
                vip_white_rules.append(row.match_value)
        return vip_black_words, vip_black_rules, vip_white_words, vip_white_rules
