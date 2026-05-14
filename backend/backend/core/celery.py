import os

from celery import Celery


# =========================================================
# DJANGO SETTINGS
# =========================================================

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'core.settings'
)


# =========================================================
# CREATE CELERY APP
# =========================================================

app = Celery('core')


# =========================================================
# LOAD DJANGO SETTINGS
# =========================================================

app.config_from_object(
    'django.conf:settings',
    namespace='CELERY'
)


# =========================================================
# AUTO DISCOVER TASKS
# =========================================================

app.autodiscover_tasks()