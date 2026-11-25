from celery import Celery

from app.config import get_settings

settings = get_settings()
celery_app = Celery("secretsanta", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_always_eager = settings.app_env != "production"


@celery_app.task
def ping() -> str:
    return "ok"
