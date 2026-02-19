from django.urls import path
from .views import notes, note_detail, ActivityCreateView, health



urlpatterns = [
    path("notes/", notes),
    path("notes/<int:note_id>/", note_detail),
    path("activities/", ActivityCreateView.as_view(), name="activity-create"),
    path("health/", health),
]
