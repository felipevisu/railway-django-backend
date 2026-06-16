from celery.result import AsyncResult
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from config.celery import app as celery_app

from .models import Todo
from .serializers import TodoSerializer
from .tasks import count_todos, delete_old_completed_todos, send_todo_notification

# Tasks allowed to be enqueued over HTTP. Whitelist — never trust a raw task
# name from a request.
ENQUEUEABLE_TASKS = {
    "send_todo_notification": send_todo_notification,
    "count_todos": count_todos,
    "delete_old_completed_todos": delete_old_completed_todos,
}


class TodoViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for todo items."""

    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def perform_create(self, serializer):
        todo = serializer.save()
        # Fire async task; returns immediately, worker processes it.
        send_todo_notification.delay(todo.id)


class EnqueueTaskView(APIView):
    """POST a job into the Celery queue.

    Body:
        {"task": "count_todos", "args": [], "kwargs": {}}
    Returns the task id; poll TaskStatusView for the result.
    """

    def post(self, request):
        name = request.data.get("task")
        task = ENQUEUEABLE_TASKS.get(name)
        if task is None:
            return Response(
                {"detail": f"unknown task. allowed: {sorted(ENQUEUEABLE_TASKS)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        args = request.data.get("args", [])
        kwargs = request.data.get("kwargs", {})
        if not isinstance(args, list) or not isinstance(kwargs, dict):
            return Response(
                {"detail": "args must be a list, kwargs must be an object"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = task.apply_async(args=args, kwargs=kwargs)
        return Response(
            {"task_id": result.id, "status": result.status},
            status=status.HTTP_202_ACCEPTED,
        )


class TaskStatusView(APIView):
    """GET the state/result of a queued task by id."""

    def get(self, request, task_id):
        result = AsyncResult(task_id, app=celery_app)
        body = {"task_id": task_id, "status": result.status}
        if result.ready():
            if result.successful():
                body["result"] = result.result
            else:
                body["error"] = str(result.result)
        return Response(body)
