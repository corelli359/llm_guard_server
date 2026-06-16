import asyncio
import orjson
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from config.db_config import DATABASE_URL

from models.db_meta import (
    GlobalKeywords,
    MetaTags,
    ScenarioKeywords,
    RuleGlobalDefaults,
    RuleScenarioPolicy
)



async def export_all_data(output_dir:str="data"):
    os.makedirs(output_dir, exist_ok=True)

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        print("1.导出 global_keywords")
        stmt = select(GlobalKeywords).where(GlobalKeywords.is_active==True)
        result = await session.execute(stmt)
        keywords = result.scalars().all()
        data = [
            {
                "id": k.id,
                "keyword": k.keyword,
                "tag_code": k.tag_code,
                "risk_level":k.risk_level,
                "is_active": k.is_active,
            } for k in keywords
        ]
        with open(os.path.join(output_dir, "global_keywords.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        print(f"一共导出{len(data)}条记录")

        print("2.导出 meta_tags")
        stmt = select(MetaTags).where(MetaTags.is_active==True)
        result = await session.execute(stmt)
        tags = result.scalars().all()
        data = [
            {
                "id": k.id,
                "tag_code": k.tag_code,
                "tag_name": k.tag_name,
                "parent_code":k.parent_code,
                "level": k.level,
                "is_active": k.is_active,
            } for k in tags
        ]
        with open(os.path.join(output_dir, "meta_tags.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        print(f"一共导出{len(data)}条记录")

        print("3.导出 scenario_keywords")
        stmt = select(ScenarioKeywords).where(ScenarioKeywords.is_active == True)
        result = await session.execute(stmt)
        scenario_keywords = result.scalars().all()
        data = [
            {
                "id": k.id,
                "scenario_id": k.scenario_id,
                "keyword": k.keyword,
                "tag_code": k.tag_code,
                "risk_level": k.risk_level,
                "is_active": k.is_active,
                "category": k.category
            } for k in scenario_keywords
        ]
        with open(os.path.join(output_dir, "scenario_keywords.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        print(f"一共导出{len(data)}条记录")

        print("4.导出 scenario_policies")
        stmt = select(RuleScenarioPolicy).where(RuleScenarioPolicy.is_active == True)
        result = await session.execute(stmt)
        policies = result.scalars().all()
        data = [
            {
                "id": k.id,
                "acenario_id": k.scenario_id,
                "match_type": k.match_type,
                "match_value": k.match_value,
                "rule_mode": k.rule_mode,
                "extra_condition": k.extra_condition,
                "strategy": k.strategy,
                "is_active": k.is_active,
            } for k in policies
        ]
        with open(os.path.join(output_dir, "scenario_policies.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        print(f"一共导出{len(data)}条记录")

        print("5.导出 global_defaults")
        stmt = select(RuleGlobalDefaults).where(RuleGlobalDefaults.is_active == True)
        result = await session.execute(stmt)
        global_defaults = result.scalars().all()
        data = [
            {
                "id": k.id,
                "tag_code": k.tag_code,
                "extra_condition": k.extra_condition,
                "strategy": k.strategy,
                "is_active": k.is_active,
            } for k in global_defaults
        ]
        with open(os.path.join(output_dir, "global_defaults.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

        print(f"一共导出{len(data)}条记录")

    await engine.dispose()

    print(f"所有数据导出到:{output_dir}/")


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    asyncio.run(export_all_data(output_dir))
