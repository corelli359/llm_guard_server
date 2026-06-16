from typing import Any, List, Sequence
from sqlalchemy.engine import Row
from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from models import (
    GlobalKeywords,
    ScenarioKeywords,
    RuleScenarioPolicy,
    RuleGlobalDefaults,
    MetaTags,
    AuditLogDetail
)
import uuid
import datetime
import asyncio
from sqlalchemy import func


class RuleDataLoaderDAO:
    """
    数据访问对象：专门负责从数据库拉取规则引擎所需的配置数据
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_global_keywords(self) -> Sequence[Row]:
        """全量加载：通用敏感词"""
        stmt = select(
            GlobalKeywords.keyword,
            GlobalKeywords.tag_code
        ).where(GlobalKeywords.is_active == True)
        result = await self.session.execute(stmt)
        return result.all()

    async def get_all_scenario_keywords(self) -> Sequence[Row]:
        """全量加载：场景自定义敏感词"""
        stmt = select(
            ScenarioKeywords.scenario_id,
            ScenarioKeywords.keyword,
            ScenarioKeywords.exemptions,
            ScenarioKeywords.tag_code,
            ScenarioKeywords.category,
            ScenarioKeywords.risk_level,
            ScenarioKeywords.rule_mode,
        ).where(
            ScenarioKeywords.is_active == True
        )
        result = await self.session.execute(stmt)
        return result.all()
        # return list(result.scalars().all())
        # return list(result.scalars().all())

    async def get_scenario_keywords_by_appid(
            self, app_id: str
    ) -> List[ScenarioKeywords]:
        """全量加载：场景自定义敏感词"""
        stmt = select(ScenarioKeywords).where(
            ScenarioKeywords.is_active == True, ScenarioKeywords.scenario_id == app_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_scenario_keywords_only_by_appid(
            self, app_id: str
    ) -> List[ScenarioKeywords]:
        """全量加载：场景自定义敏感词"""
        stmt = select(ScenarioKeywords).where(
            ScenarioKeywords.is_active == True,
            ScenarioKeywords.scenario_id == app_id,
            ScenarioKeywords.rule_mode == 0
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_scenario_rules(self) -> Sequence[Row]:
        # 定义拼接列
        rule = func.concat(
            RuleScenarioPolicy.match_value,
            "-",
            func.coalesce(RuleScenarioPolicy.extra_condition, ""),
        ).label(
            "rule_key"
        )  # 起个别名，方便后面引用
        stmt = select(
            RuleScenarioPolicy.scenario_id,
            # RuleScenarioPolicy.match_value,
            # RuleScenarioPolicy.extra_condition,
            rule,
            RuleScenarioPolicy.strategy,
        ).where(
            RuleScenarioPolicy.is_active == True,
            RuleScenarioPolicy.rule_mode == 1,
            RuleScenarioPolicy.match_type == "TAG",
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def load_all_vip_keywords(self):
        stmt = select(
            ScenarioKeywords.scenario_id,
            ScenarioKeywords.keyword,
            ScenarioKeywords.tag_code,
            ScenarioKeywords.category,
            ScenarioKeywords.risk_level,
        ).where(
            ScenarioKeywords.is_active == True,
            ScenarioKeywords.rule_mode == 1,
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def load_vip_keywords_by_app_id(self, app_id):
        stmt = select(ScenarioKeywords).where(
            ScenarioKeywords.is_active == True,
            ScenarioKeywords.rule_mode == 1,
            ScenarioKeywords.scenario_id == app_id,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def load_all_vip(self):
        stmt = select(
            RuleScenarioPolicy.scenario_id,
            RuleScenarioPolicy.match_value,
            RuleScenarioPolicy.extra_condition,
            RuleScenarioPolicy.strategy,
            RuleScenarioPolicy.match_type
        ).where(
            RuleScenarioPolicy.is_active == True,
            RuleScenarioPolicy.rule_mode == 0,
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_scenario_rule_by_appid(self, app_id: str):
        stmt = select(RuleScenarioPolicy).where(
            RuleScenarioPolicy.is_active == True,
            RuleScenarioPolicy.scenario_id == app_id,
            RuleScenarioPolicy.rule_mode == 1,
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_vip_scenario_by_appid(self, app_id: str) -> List[RuleScenarioPolicy]:
        stmt = select(RuleScenarioPolicy).where(
            RuleScenarioPolicy.is_active == True,
            RuleScenarioPolicy.scenario_id == app_id,
            RuleScenarioPolicy.rule_mode == 0,
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

    async def get_all_scenario_ids(self) -> List[str]:
        """全量加载：场景列表"""
        stmt = select(ScenarioKeywords.scenario_id).where(ScenarioKeywords.is_active == True).distinct()
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_global_keywords_cnt(self):
        stmt = (
            select(func.count()).select_from(GlobalKeywords).where(GlobalKeywords.is_active == True)
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_global_keywords_by_limit(self, page_no: int = 1, page_size: int = 200):
        offset = (page_no - 1) * page_size
        stmt = select(
            GlobalKeywords.keyword,
            GlobalKeywords.tag_code
        ).where(
            GlobalKeywords.is_active == True
        ).order_by(GlobalKeywords.id).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        return list(result.all())

    async def get_global_rules_cnt(self):
        """全量加载：通用兜底规则"""
        stmt = (
            select(func.count()).select_from(RuleGlobalDefaults).where(RuleGlobalDefaults.is_active == True)
        )
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_global_rules_by_limit(self, page_no: int = 1, page_size: int = 200):
        offset = (page_no - 1) * page_size
        stmt = select(
            RuleGlobalDefaults.tag_code,
            RuleGlobalDefaults.extra_condition,
            RuleGlobalDefaults.strategy
        ).where(
            RuleGlobalDefaults.is_active == True
        ).order_by(RuleGlobalDefaults.id).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        return list(result.all())


class AuditLogDataLoaderDAO:
    """
    数据访问对象：专门负责从数据库拉取规则引擎所需的配置数据
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_audit_log(self, record):
        """全量加载：通用敏感词"""
        try:
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            auto_fields = {
                "id": str(uuid.uuid4()),
                "log_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "created_at": now_str,
                "updated_at": now_str
            }
            full_record = {**auto_fields, **record}
            stmt = insert(AuditLogDetail).values(**full_record)
            await self.session.execute(stmt)
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e
