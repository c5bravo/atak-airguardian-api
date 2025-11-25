from celery import Celery
from app.config import settings

celery_app = Celery(
    "aircraft_tracker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.tasks.radar_task",
        "app.tasks.generater_task",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30,
    task_soft_time_limit=25,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "fetch-open_sky_aircraft-data": {
        "task": "app.tasks.radar_task.fetch_aircraft_data",
        "schedule": 30.0,
    },
    "fetch-generater-aircraft-data": {
        "task": "app.tasks.generater_task.fetch_generater_aircraft_data",
        "schedule": 30.0,
    },
}
