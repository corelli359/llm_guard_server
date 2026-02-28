from sanic import Sanic, Request, json
from sanic.log import logger
from sanic.exceptions import SanicException
from .exceptions import AppException

def setup_exception_handlers(app: Sanic):
    @app.exception(AppException)
    async def handle_app_exception(request: Request, exception: AppException):
        logger.error(f"AppException: {exception.message}", exc_info=True)
        return json({
            "error": {
                "code": exception.error_code,
                "message": exception.message,
                "data": exception.data
            }
        }, status=exception.status_code)

    @app.exception(SanicException)
    async def handle_sanic_exception(request: Request, exception: SanicException):
        logger.error(f"SanicException: {exception}", exc_info=True)
        return json({
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exception),
                "data": None
            }
        }, status=exception.status_code)

    @app.exception(Exception)
    async def handle_generic_exception(request: Request, exception: Exception):
        logger.error(f"Unhandled Exception: {exception}", exc_info=True)
        return json({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "data": str(exception) if app.config.DEBUG else None
            }
        }, status=500)
