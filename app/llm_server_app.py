from sanic import Sanic, response
from config.settings import Config
from services import create_routers
from sanic.log import logger
from utils.logging_config import LOGGING_CONFIG
from db import DBConnector
from tools.db_tools import DBConnectTool
from tools.sensitive_tools import SensitiveAutomatonLoader
from config.settings import SENSITIVE_DICT_PATH, SENSITIVE_DICT
from tools.data_tool import DataProvider


def create_app() -> Sanic:
    app = Sanic("GuardrailsService", log_config=LOGGING_CONFIG)

    # Load Config
    app.config.update(
        HOST=Config.HOST,
        PORT=Config.PORT,
        DEBUG=Config.DEBUG,
        AUTO_RELOAD=Config.AUTO_RELOAD,
    )

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
            await data_provider.build_ac("global")

            logger.info("Data loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load data from DB: {e}")

    logger.info("begin to load global sensitive words")
    try:
        global_loader = SensitiveAutomatonLoader("global", SENSITIVE_DICT_PATH)
        global_loader.reload()
        SENSITIVE_DICT["global"] = global_loader
        logger.info("finish to load global sensitive words")
    except Exception as e:
        logger.error(f"Failed to load global sensitive words: {e}")

    @app.main_process_start
    async def start(app, loop):
        logger.info(f"!!!!!!Server starting on {app.config.HOST}:{app.config.PORT}")

    @app.route("/health")
    async def health_check(request):
        return response.json({"status": "ok"})

    return app
