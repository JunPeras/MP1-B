from django.urls import path
from .views import (
    notes,
    note_detail,
    ActivityCreateView,
    ActivityUpdateView,
    SubtaskCreateView,
    SubtaskUpdateView,
    health,
)


urlpatterns = [
    path("notes/", notes),
    path("notes/<int:note_id>/", note_detail),

    path("activities/", ActivityCreateView.as_view(), name="activity-create"),
    path("activities/<int:activity_id>/", ActivityUpdateView.as_view()),

    path("subtasks/", SubtaskCreateView.as_view(), name="subtask-create"),
    path("subtasks/<int:subtask_id>/", SubtaskUpdateView.as_view()),
    
    path("health/", health),
]
