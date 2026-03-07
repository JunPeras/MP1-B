import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Note
from .models import Subtask, Activity
from rest_framework import generics, status
from .models import User
from .serializers import ActivitySerializer, SubtaskSerializer
from django.http import JsonResponse
from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

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


class ActivityView(generics.ListCreateAPIView):
    serializer_class = ActivitySerializer

    def get_queryset(self):
        """
        Retorna solo actividades que pertenecen al usuario autenticado.
        """
        return Activity.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": list(serializer.errors.values())[0][0],
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Usamos el usuario autenticado en lugar del demo
        serializer.save(user=request.user)

        return Response({
            "success": True,
            "message": "Actividad creada correctamente",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ActivitySerializer

    def get_queryset(self):
        """
        Retorna solo actividades que pertenecen al usuario autenticado.
        """
        return Activity.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Actividad eliminada correctamente"
        }, status=status.HTTP_200_OK)
    

class ActivitySubtasksView(APIView):

    def get(self, request, pk):
        # Aseguramos que la actividad pertenece al usuario
        activity = get_object_or_404(Activity, id=pk, user=request.user)

        subtasks = activity.subtasks.all()
        serializer = SubtaskSerializer(subtasks, many=True)

        return Response({
            "success": True,
            "activity_id": activity.id,
            "subtasks": serializer.data
        }, status=status.HTTP_200_OK)
    

class SubtaskView(generics.ListCreateAPIView):
    serializer_class = SubtaskSerializer

    def get_queryset(self):
        """
        Retorna solo subtareas cuyas actividades pertenecen al usuario autenticado.
        """
        return Subtask.objects.filter(activity__user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid subtask data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Verificar que la actividad pertenece al usuario antes de crear la subtarea
        activity_id = request.data.get('activity')
        get_object_or_404(Activity, id=activity_id, user=request.user)

        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Subtask created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)


class SubtaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SubtaskSerializer

    def get_queryset(self):
        """
        Retorna solo subtareas cuyas actividades pertenecen al usuario autenticado.
        """
        return Subtask.objects.filter(activity__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Subtask eliminada correctamente"
        }, status=status.HTTP_200_OK)


