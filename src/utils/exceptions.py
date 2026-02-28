from .error_codes import ErrorCode


class AppException(Exception):
    """Base class for application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = ErrorCode.SYSTEM_ERROR,
        data: dict | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.data = data


class BadRequestError(AppException):
    def __init__(
        self,
        message: str = "Bad Request",
        error_code: str = ErrorCode.INVALID_PARAM,
        data: dict | None = None,
    ):
        super().__init__(message, 400, error_code, data)


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Not Found",
        error_code: str = ErrorCode.NOT_FOUND,
        data: dict | None = None,
    ):
        super().__init__(message, 404, error_code, data)


class ValidationError(AppException):
    def __init__(
        self,
        message: str = "Validation Error",
        error_code: str = ErrorCode.VALIDATION_ERROR,
        data: dict | None = None,
    ):
        super().__init__(message, 422, error_code, data)


class InternalServerError(AppException):
    def __init__(
        self,
        message: str = "Internal Server Error",
        error_code: str = ErrorCode.SYSTEM_ERROR,
        data: dict | None = None,
    ):
        super().__init__(message, 500, error_code, data)
