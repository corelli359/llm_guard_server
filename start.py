from sanic import Sanic, response
from config.settings import Config
from services import create_routers
from sanic.log import logger
from utils.logging_config import LOGGING_CONFIG

def create_app() -> Sanic:
    app = Sanic("GuardrailsService", log_config=LOGGING_CONFIG)
    
    create_routers(app)
    
    # Load Config
    app.config.update(
        HOST=Config.HOST,
        PORT=Config.PORT,
        DEBUG=Config.DEBUG,
        AUTO_RELOAD = Config.AUTO_RELOAD
    )
    
    from tools.sensitive_tools import SensitiveAutomatonLoader
    from config.settings import SENSITIVE_DICT_PATH,SENSITIVE_DICT
    logger.info("begin to load global sensitive words")
    global_loader = SensitiveAutomatonLoader("global", SENSITIVE_DICT_PATH)
    global_loader.reload()
    SENSITIVE_DICT["global"] = global_loader
    logger.info("finish to load global sensitive words")
    
    @app.main_process_start
    async def start(app, loop):
        logger.info(f"!!!!!!Server starting on {app.config.HOST}:{app.config.PORT}")

    @app.route("/health")
    async def health_check(request):
        return response.json({"status": "ok"})

    return app

app = create_app()

if __name__ == "__main__":
    
    app.run(
        host=app.config.HOST, 
        port=app.config.PORT, 
        debug=app.config.DEBUG,
        auto_reload=app.config.AUTO_RELOAD
    )