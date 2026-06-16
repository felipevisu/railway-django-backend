from rest_framework import viewsets

from .models import Todo
from .serializers import TodoSerializer
from .tasks import send_todo_notification


class TodoViewSet(viewsets.ModelViewSet):
    """CRUD endpoints for todo items."""

    queryset = Todo.objects.all()
    serializer_class = TodoSerializer

    def perform_create(self, serializer):
        todo = serializer.save()
        # Fire async task; returns immediately, worker processes it.
        send_todo_notification.delay(todo.id)
