"""Конфигурация логгирования."""

import json
import logging
import logging.config

from app.config import settings


def setup_logger() -> None:
    """Установка конфигурации логгирования."""
    level = settings.logger.logger_level
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'class': 'logging.Formatter',
                'format': (
                    json.dumps(
                        {
                            'time': '%(asctime)s',
                            'level': '%(levelname)s',
                            'logger': '%(name)s',
                            'message': '%(message)s',
                        }
                    )
                ),
                'datefmt': '%Y-%m-%d %H:%M:%S %z',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': level,
                'formatter': 'detailed',
            }
        },
        'loggers': {
            '': {'level': level, 'handlers': ['console'], 'propagate': False},
            'app': {'level': level, 'handlers': ['console'], 'propagate': False},
        },
    }
    logging.config.dictConfig(log_config)
