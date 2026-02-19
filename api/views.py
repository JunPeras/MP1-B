import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from .models import Note
from .models import Activity
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import ActivitySerializer
from django.http import JsonResponse
from django.db import connection
from django.shortcuts import get_object_or_404

def _note_to_dict(n: Note):
    return {
        "id": n.id,
        "title": n.title,
        "content": n.content,
        "created_at": n.created_at.isoformat(),
    }


@csrf_exempt
def notes(request):
    if request.method == "GET":
        qs = Note.objects.order_by("-id")[:50]
        return JsonResponse([_note_to_dict(n) for n in qs], safe=False)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        title = data.get("title")

        if not title:
            return JsonResponse({"error": "Falta 'title'."}, status=400)

        n = Note.objects.create(
            title=title,
            content=data.get("content", ""),
        )
        return JsonResponse(_note_to_dict(n), status=201)

    return HttpResponseNotAllowed(["GET", "POST"])


@csrf_exempt
def note_detail(request, note_id: int):
    try:
        n = Note.objects.get(id=note_id)
    except Note.DoesNotExist:
        return JsonResponse({"error": "No encontrado."}, status=404)

    if request.method == "GET":
        return JsonResponse(_note_to_dict(n))

    if request.method == "PUT":
        data = json.loads(request.body or "{}")

        if "title" in data:
            n.title = data["title"]

        if "content" in data:
            n.content = data["content"]

        n.save()
        return JsonResponse(_note_to_dict(n))

    if request.method == "DELETE":
        n.delete()
        return JsonResponse({"ok": True})

    return HttpResponseNotAllowed(["GET", "PUT", "DELETE"])

class ActivityCreateView(generics.CreateAPIView):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer

    def perform_create(self, serializer):
        demo_user = get_object_or_404(User, username="demo")
        serializer.save(user=demo_user)


def health(request):
    try:
        connection.ensure_connection()
        db_status = "ok"
    except Exception:
        db_status = "error"

    return JsonResponse({
        "status": "ok",
        "database": db_status
    })



