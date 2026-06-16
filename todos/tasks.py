import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_todo_notification(todo_id):
    """Async task: simulate notifying someone a todo was created."""
    from .models import Todo

    try:
        todo = Todo.objects.get(pk=todo_id)
    except Todo.DoesNotExist:
        logger.warning("send_todo_notification: todo %s gone", todo_id)
        return None

    # Stand-in for email/push/etc.
    logger.info("Notification: new todo #%s '%s'", todo.id, todo.title)
    return f"notified for todo {todo.id}"


@shared_task
def delete_old_completed_todos(days=30):
    """Periodic task: purge completed todos older than `days`."""
    from .models import Todo

    cutoff = timezone.now() - timedelta(days=days)
    qs = Todo.objects.filter(completed=True, updated_at__lt=cutoff)
    count = qs.count()
    qs.delete()
    logger.info("delete_old_completed_todos: removed %s todos", count)
    return count


@shared_task
def count_todos():
    """Periodic task: log current todo counts."""
    from .models import Todo

    total = Todo.objects.count()
    done = Todo.objects.filter(completed=True).count()
    logger.info("count_todos: %s total, %s completed", total, done)
    return {"total": total, "completed": done}
