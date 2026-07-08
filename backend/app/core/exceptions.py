from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.core.logger import get_logger

logger = get_logger(__name__)


class AppException(Exception):
    status_code: int = status.HTTP_400_BAD_REQUEST
    code: str = "app_error"

    def __init__(self, detail: str, code: str | None = None, status_code: int | None = None):
        self.detail = detail
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail)


class NotFoundError(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class UnauthorizedError(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "unauthorized"


class ConflictError(AppException):
    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "code": exc.code},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "internal_error"},
    )


def register_exception_handlers(app) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
