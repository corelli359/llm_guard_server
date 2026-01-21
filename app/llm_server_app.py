from sanic import Sanic, response
from services import create_routers
from sanic.log import logger
from utils.logging_config import LOGGING_CONFIG, setup_async_logging, stop_async_logging
from db import DBConnector
from tools.db_tools import DBConnectTool
from tools.sensitive_tools import SensitiveAutomatonLoader
# from config.settings import SENSITIVE_DICT_PATH, SENSITIVE_DICT
from tools.data_tool import DataProvider, DataInitPromise
from utils.error_handler import setup_exception_handlers
from .middleware import setup_audit_middleware
import logging



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
    # setup_exception_handlers(app)

    # # Load Config
    # app.config.update(
    #     HOST=Config.HOST,
    #     PORT=Config.PORT,
    #     DEBUG=Config.DEBUG,
    #     AUTO_RELOAD=Config.AUTO_RELOAD,
    # )

    # Initialize DB and Tools
    db_client = DBConnector()
    db_client.init_db(app)
    # app.ctx.db_client = db_client

    db_tool = DBConnectTool(db_client)
    app.ctx.db_tool = db_tool

    data_provider = DataProvider(app.ctx.db_tool)

    create_routers(app)

    # Use lifecycle event to load data after DB is connected
    @app.after_server_start
    async def load_data(app, loop):
        try:
            logger.info("Loading data from DB...")
            # await app.ctx.db_tool.load_data_from_db()
            data_promise = DataInitPromise()
            data_promise.flow()
            await data_promise.run(data_provider)

            logger.info("Data loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load data from DB: {e}")

    logger.info("begin to load global sensitive words")
    # try:
    #     global_loader = SensitiveAutomatonLoader("global", SENSITIVE_DICT_PATH)
    #     global_loader.reload()
    #     SENSITIVE_DICT["global"] = global_loader
    #     logger.info("finish to load global sensitive words")
    # except Exception as e:
    #     logger.error(f"Failed to load global sensitive words: {e}")

    @app.route("/health")
    async def health_check(request):
        return response.json({"status": "ok"})

    @app.main_process_start
    async def start(app, loop):
        logger.info(f"!!!!!!Server starting ")

    @app.before_server_stop
    async def cleanup(app, loop):
        logger.info("Stopping async logging...")
        stop_async_logging()

    return app
