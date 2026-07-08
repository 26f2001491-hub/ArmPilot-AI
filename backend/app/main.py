from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.events import lifespan
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import setup_logging
from app.core.middleware import RequestLoggingMiddleware

settings = get_settings()
setup_logging(settings)


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(application)
    application.include_router(api_router)

    return application


app = create_app()
