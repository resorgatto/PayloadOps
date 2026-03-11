"""
SEAM — Development Settings
"""

from config.settings.base import *  # noqa: F401, F403

DEBUG = True

CORS_ALLOW_ALL_ORIGINS = True

# Django Extensions
SHELL_PLUS_IMPORTS = [
    "from apps.accounts.models import User",
    "from apps.workspaces.models import Workspace, WorkspaceMembership",
    "from apps.workflows.models import Workflow, Trigger, Action, Credential",
    "from apps.observability.models import ExecutionLog",
]

# Celery — use eager mode for easier local debugging (optional)
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "apps.engine": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
