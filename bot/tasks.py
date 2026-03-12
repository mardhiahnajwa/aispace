from celery import shared_task


@shared_task
def add(x, y):
    """Simple example task: returns the sum of two numbers."""
    return x + y


@shared_task
def log_message(message):
    """Example periodic task: logs a message (replace with real logic)."""
    print(f"[Celery] {message}")
