from django.urls import path
from .views import (
    notes,
    note_detail,
    ActivityView,
    ActivityDetailView,
    SubtaskView,
    SubtaskDetailView,
    ActivitySubtasksView,
    health,
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
