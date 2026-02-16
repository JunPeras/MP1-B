from django.urls import path
from .views import notes, note_detail


urlpatterns = [
    path("notes/", notes),
    path("notes/<int:note_id>/", note_detail),
]
