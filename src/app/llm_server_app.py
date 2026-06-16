from sanic.log import logger
from services import create_routers
from utils.logging_config import LOGGING_CONFIG, setup_async_logging, stop_async_logging
from db import DBConnector
from tools.db_tools import DBConnectTool
from tools.data_tool.data_loader_factory import DataLoaderFactory
from tools.data_tool import DataProvider, DataInitPromise
from .middleware import setup_audit_middleware
import logging
from config.data_source_config import get_data_source_config, DataSourceConfig
from sanic import Sanic, response


def create_app() -> Sanic:
    app = Sanic("GuardrailsService", log_config=LOGGING_CONFIG)

    # Setup async logging with QueueHandler
    log_queue = setup_async_logging()

    # Replace audit logger handler with QueueHandler for async logging
    audit_logger = logging.getLogger("audit")
    audit_logger.handlers.clear()
    queue_handler = logging.handlers.QueueHandler(log_queue)
    audit_logger.addHandler(queue_handler)
    audit_logger.setLevel(logging.INFO)

    setup_audit_middleware(app)

    data_source_config: DataSourceConfig = get_data_source_config()
    logger.info(f"Data source : {data_source_config}")
    if data_source_config and data_source_config.is_db_mode():
        db_client = DBConnector()
        db_client.init_db(app)
        db_tool = DBConnectTool(db_client)
        app.ctx.db_tool = db_tool
        data_loader = db_tool
        logger.info("Using DATABASE mode for data storage")
    else:
        data_loader = DataLoaderFactory.create()
        app.ctx.db_tool = None  # 兼容性
        logger.info(
            f"Using FILE mode for data storage: {data_source_config.file_base_path}"
        )

    data_provider = DataProvider(data_loader)

    create_routers(app)

    # Use lifecycle event to load data after DB is connected
    @app.after_server_start
    async def load_data(app):
        try:
            logger.info("Loading data from DB...")
            data_promise = DataInitPromise()
            data_promise.flow()
            await data_promise.run(data_provider)

            logger.info("Data loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load data from DB: {e}")

    logger.info("begin to load global sensitive words")

    @app.route("/health")
    async def health_check(request):
        logger.info("health check")
        return response.json({"status": "ok"})

    @app.main_process_start
    async def start(app):
        logger.info(f"!!!!!!Server starting ")

    from cron.cron_task import setup_scheduled_tasks
    setup_scheduled_tasks(app)

    @app.before_server_stop
    async def cleanup(app):
        logger.info("Stopping async logging...")
        stop_async_logging()

    return app
