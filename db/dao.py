from typing import List

from whatthepatch import apply_diff
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from models import (
    GlobalKeywords,
    ScenarioKeywords,
    RuleScenarioPolicy,
    RuleGlobalDefaults,
    MetaTags,
)
import asyncio


class RuleDataLoaderDAO:
    """
    数据访问对象：专门负责从数据库拉取规则引擎所需的配置数据
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_global_keywords(self) -> List[GlobalKeywords]:
        """全量加载：通用敏感词"""
        stmt = select(GlobalKeywords).where(GlobalKeywords.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_scenario_keywords(self) -> List[ScenarioKeywords]:
        """全量加载：场景自定义敏感词"""
        stmt = select(ScenarioKeywords).where(ScenarioKeywords.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_scenario_keywords_by_appid(
        self, app_id: str
    ) -> List[ScenarioKeywords]:
        """全量加载：场景自定义敏感词"""
        stmt = select(ScenarioKeywords).where(
            ScenarioKeywords.is_active == True, ScenarioKeywords.scenario_id == app_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_scenario_by_appid(self, app_id: str) -> List[RuleScenarioPolicy]:
        stmt = select(RuleScenarioPolicy).where(
            RuleScenarioPolicy.is_active == True,
            RuleScenarioPolicy.scenario_id == app_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_scenario_policies(self) -> List[RuleScenarioPolicy]:
        """全量加载：场景策略（超黑/超白/规则覆盖）"""
        stmt = select(RuleScenarioPolicy).where(RuleScenarioPolicy.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_global_defaults(self) -> List[RuleGlobalDefaults]:
        """全量加载：通用兜底规则"""
        stmt = select(RuleGlobalDefaults).where(RuleGlobalDefaults.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_tags(self) -> List[MetaTags]:
        """全量加载：标签元数据"""
        stmt = select(MetaTags).where(MetaTags.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def fetch_full_data_package(self) -> dict:
        """
        组合查询：一次性获取所有需要的数据
        返回一个字典，供 Service 层直接构建缓存
        """
        # 并发执行所有查询以提高初始化速度

        # 这里的顺序要和返回值的组装对应
        results = await asyncio.gather(
            self.get_all_global_keywords(),
            self.get_all_scenario_keywords(),
            self.get_all_scenario_policies(),
            self.get_all_global_defaults(),
        )

        return {
            "global_keywords": results[0],
            "scenario_keywords": results[1],
            "scenario_policies": results[2],
            "global_defaults": results[3],
        }
