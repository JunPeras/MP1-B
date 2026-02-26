import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Note
from .models import Subtask, Activity
from rest_framework import generics, status
from django.contrib.auth.models import User
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

class ActivityCreateView(APIView):

    def post(self, request):
        serializer = ActivitySerializer(data=request.data)

        if serializer.is_valid():
            demo_user = get_object_or_404(User, username="demo")
            serializer.save(user=demo_user)

            return Response({
                "success": True,
                "message": "Actividad creada correctamente",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response({
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": list(serializer.errors.values())[0][0],
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
class ActivityUpdateView(APIView):

    def put(self, request, activity_id):
        activity = get_object_or_404(Activity, id=activity_id)
        serializer = ActivitySerializer(activity, data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": list(serializer.errors.values())[0][0],
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "success": True,
            "message": "Actividad actualizada correctamente",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def patch(self, request, activity_id):
        activity = get_object_or_404(Activity, id=activity_id)
        serializer = ActivitySerializer(activity, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": list(serializer.errors.values())[0][0],
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "success": True,
            "message": "Actividad actualizada correctamente",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
    def delete(self, request, activity_id):
        activity = get_object_or_404(Activity, id=activity_id)
        activity.delete()

        return Response({
            "success": True,
            "message": "Actividad eliminada correctamente"
        }, status=status.HTTP_200_OK)    

class SubtaskCreateView(generics.CreateAPIView):
    queryset = Subtask.objects.all()
    serializer_class = SubtaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid subtask data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)

        return Response({
            "success": True,
            "message": "Subtask created successfully",
            "data": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request, subtask_id):
        subtask = get_object_or_404(Subtask, id=subtask_id)
        subtask.delete()

        return Response({
            "success": True,
            "message": "Subtask eliminada correctamente"
        }, status=status.HTTP_200_OK)
    
class SubtaskUpdateView(APIView):

    def put(self, request, subtask_id):
        subtask = get_object_or_404(Subtask, id=subtask_id)
        serializer = SubtaskSerializer(subtask, data=request.data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid subtask data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "success": True,
            "message": "Subtask updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def patch(self, request, subtask_id):
        subtask = get_object_or_404(Subtask, id=subtask_id)
        serializer = SubtaskSerializer(subtask, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid subtask data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "success": True,
            "message": "Subtask updated successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)    

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



