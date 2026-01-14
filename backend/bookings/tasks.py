from celery import shared_task
from bookings.services.cleanup import release_expired_seats

@shared_task
def task_release_expired_seats():
    """
    Celery entry point.
    Runs every 1 minute via Celery Beat.
    """
    count = release_expired_seats()
    return f"Released {count} seats"