class AppException(Exception):
    """Base class for application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
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
        error_code: str = "BAD_REQUEST",
        data: dict | None = None,
    ):
        super().__init__(message, 400, error_code, data)


class UnauthorizedError(AppException):
    def __init__(
        self,
        message: str = "Unauthorized",
        error_code: str = "UNAUTHORIZED",
        data: dict | None = None,
    ):
        super().__init__(message, 401, error_code, data)


class ForbiddenError(AppException):
    def __init__(
        self,
        message: str = "Forbidden",
        error_code: str = "FORBIDDEN",
        data: dict | None = None,
    ):
        super().__init__(message, 403, error_code, data)


class NotFoundError(AppException):
    def __init__(
        self,
        message: str = "Not Found",
        error_code: str = "NOT_FOUND",
        data: dict | None = None,
    ):
        super().__init__(message, 404, error_code, data)


class ValidationError(AppException):
    def __init__(
        self,
        message: str = "Validation Error",
        error_code: str = "VALIDATION_ERROR",
        data: dict | None = None,
    ):
        super().__init__(message, 422, error_code, data)


class InternalServerError(AppException):
    def __init__(
        self,
        message: str = "Internal Server Error",
        error_code: str = "INTERNAL_ERROR",
        data: dict | None = None,
    ):
        super().__init__(message, 500, error_code, data)
