from django.urls import path

from .views import (
    ActivityDetailView,
    ActivitySubtasksView,
    ActivityView,
    SubtaskDetailView,
    SubtaskView,
    health,
    note_detail,
    notes,
)

urlpatterns = [
    path("notes/", notes),
    path("notes/<int:note_id>/", note_detail),
    path("activities/", ActivityView.as_view()),
    path("activities/<int:pk>/", ActivityDetailView.as_view()),
    path("activities/<int:pk>/subtasks/", ActivitySubtasksView.as_view()),
    path("subtasks/", SubtaskView.as_view()),
    path("subtasks/<int:pk>/", SubtaskDetailView.as_view()),
    path("health/", health),
]
