"""
数据加载器工厂
根据配置创建对应的数据加载器（FILE或DB）
"""
from config.data_source_config import get_data_source_config
from tools.data_tool.file_data_loader import FileDataLoader
from tools.db_tools.db_tool import DBConnectTool


class DataLoaderFactory:
    """数据加载器工厂

    根据配置自动创建对应的数据加载器
    """

    @staticmethod
    def create():
        """创建数据加载器

        Returns:
            FileDataLoader 或 DBConnectTool 实例
        """
        config = get_data_source_config()

        if config.is_file_mode():
            # 文件模式
            return FileDataLoader()
        else:
            # 数据库模式（需要传入connector，这里暂时返回None，后续在DataProvider中处理）
            return None

    @staticmethod
    def create_with_db_connector(db_connector):
        """创建数据加载器（数据库模式需要传入connector）

        Args:
            db_connector: DBConnector实例

        Returns:
            FileDataLoader 或 DBConnectTool 实例
        """
        config = get_data_source_config()

        if config.is_file_mode():
            # 文件模式
            return FileDataLoader()
        else:
            # 数据库模式
            return DBConnectTool(db_connector)
