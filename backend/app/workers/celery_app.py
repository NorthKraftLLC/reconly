"""Celery application configuration."""

from celery import Celery

celery_app = Celery("tasks")
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
celery_app.conf.timezone = "UTC"
celery_app.conf.task_acks_late = True
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.broker_url = "redis://localhost:6379/1"
celery_app.conf.result_backend = "redis://localhost:6379/1"
celery_app.autodiscover_tasks(["app.tasks"])
