"""
数据导出工具
从数据库导出数据到JSON文件
"""
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
    RuleScenarioPolicy,
    RuleGlobalDefaults,
)


async def export_all_data(output_dir: str = "data"):
    """导出所有数据到JSON文件

    Args:
        output_dir: 输出目录
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 初始化数据库连接
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
    )

    # 创建会话工厂
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        print("开始导出数据...")

        # 1. 导出全局关键词
        print("导出 global_keywords...")
        stmt = select(GlobalKeywords).where(GlobalKeywords.is_active == True)
        result = await session.execute(stmt)
        keywords = result.scalars().all()
        data = [
            {
                "id": k.id,
                "keyword": k.keyword,
                "tag_code": k.tag_code,
                "risk_level": k.risk_level,
                "is_active": k.is_active,
            }
            for k in keywords
        ]
        with open(os.path.join(output_dir, "global_keywords.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        print(f"  ✓ 导出 {len(data)} 条记录")

        # 2. 导出元数据标签
        print("导出 meta_tags...")
        stmt = select(MetaTags).where(MetaTags.is_active == True)
        result = await session.execute(stmt)
        tags = result.scalars().all()
        data = [
            {
                "id": t.id,
                "tag_code": t.tag_code,
                "tag_name": t.tag_name,
                "parent_code": t.parent_code,
                "level": t.level,
                "is_active": t.is_active,
            }
            for t in tags
        ]
        with open(os.path.join(output_dir, "meta_tags.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        print(f"  ✓ 导出 {len(data)} 条记录")

        # 3. 导出场景关键词
        print("导出 scenario_keywords...")
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
                "category": k.category,
            }
            for k in scenario_keywords
        ]
        with open(os.path.join(output_dir, "scenario_keywords.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        print(f"  ✓ 导出 {len(data)} 条记录")

        # 4. 导出场景策略
        print("导出 scenario_policies...")
        stmt = select(RuleScenarioPolicy).where(RuleScenarioPolicy.is_active == True)
        result = await session.execute(stmt)
        policies = result.scalars().all()
        data = [
            {
                "id": p.id,
                "scenario_id": p.scenario_id,
                "match_type": p.match_type,
                "match_value": p.match_value,
                "rule_mode": p.rule_mode,
                "extra_condition": p.extra_condition,
                "strategy": p.strategy,
                "is_active": p.is_active,
            }
            for p in policies
        ]
        with open(os.path.join(output_dir, "scenario_policies.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        print(f"  ✓ 导出 {len(data)} 条记录")

        # 5. 导出全局默认策略
        print("导出 global_defaults...")
        stmt = select(RuleGlobalDefaults).where(RuleGlobalDefaults.is_active == True)
        result = await session.execute(stmt)
        defaults = result.scalars().all()
        data = [
            {
                "id": d.id,
                "tag_code": d.tag_code,
                "extra_condition": d.extra_condition,
                "strategy": d.strategy,
                "is_active": d.is_active,
            }
            for d in defaults
        ]
        with open(os.path.join(output_dir, "global_defaults.json"), "wb") as f:
            f.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))
        print(f"  ✓ 导出 {len(data)} 条记录")

    # 关闭数据库连接
    await engine.dispose()

    print(f"\n✓ 所有数据已导出到: {output_dir}/")
    print("\n下一步：")
    print("1. 设置环境变量: export DATA_SOURCE_MODE=FILE")
    print(f"2. 设置数据路径: export DATA_SOURCE_FILE_BASE_PATH={output_dir}")
    print("3. 重启服务: bash start.sh")


if __name__ == "__main__":
    import sys

    output_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
    asyncio.run(export_all_data(output_dir))
