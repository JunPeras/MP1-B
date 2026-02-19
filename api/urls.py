from django.urls import path

from .views import note_detail, notes

urlpatterns = [
    path("notes/", notes),
    path("notes/<int:note_id>/", note_detail),
]
