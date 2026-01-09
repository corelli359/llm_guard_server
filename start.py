from app.llm_server_app import create_app
from config import Config

app = create_app()

if __name__ == "__main__":

    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG,
        auto_reload=Config.AUTO_RELOAD,
        workers=Config.WORKER
    )
