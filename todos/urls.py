from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import EnqueueTaskView, TaskStatusView, TodoViewSet

router = DefaultRouter()
router.register(r"todos", TodoViewSet, basename="todo")

urlpatterns = router.urls + [
    path("tasks/", EnqueueTaskView.as_view(), name="enqueue-task"),
    path("tasks/<str:task_id>/", TaskStatusView.as_view(), name="task-status"),
]
