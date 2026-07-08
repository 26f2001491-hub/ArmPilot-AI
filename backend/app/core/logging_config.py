import logging.config
import os

from app.core.config import Settings


def setup_logging(settings: Settings) -> None:
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": settings.LOG_LEVEL,
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "default",
                    "level": settings.LOG_LEVEL,
                    "filename": os.path.join(settings.LOG_DIR, "app.log"),
                    "maxBytes": 5 * 1024 * 1024,
                    "backupCount": 3,
                },
            },
            "root": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
            },
        }
    )
