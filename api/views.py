import json

from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction

from .models import Note
from .models import Subtask, Activity
from rest_framework import generics, status
from .models import User
from .serializers import ActivitySerializer, SubtaskSerializer, InlineSubtaskSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import checkDailyLimit, check_subtasks_daily_limits

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
        # Extraer subtareas del payload antes de validar la actividad
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        subtasks_data = data.pop("subtasks", None)

        serializer = self.get_serializer(data=data)

        if not serializer.is_valid():
            return Response({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": list(serializer.errors.values())[0][0],
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Validar subtareas si las hay
        if subtasks_data:
            # Validar cada subtarea individualmente con SubtaskSerializer
            subtask_errors = []
            validated_subtasks = []
            for idx, st in enumerate(subtasks_data):
                st_serializer = InlineSubtaskSerializer(data=st)
                if not st_serializer.is_valid():
                    subtask_errors.append({
                        "subtask_index": idx,
                        "subtask_name": st.get("name", f"Subtarea {idx + 1}"),
                        "errors": st_serializer.errors,
                    })
                else:
                    validated_subtasks.append(st_serializer.validated_data)

            if subtask_errors:
                return Response({
                    "success": False,
                    "error_code": "SUBTASK_VALIDATION_ERROR",
                    "message": "Algunas subtareas tienen errores de validación.",
                    "details": {"subtask_errors": subtask_errors}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verificar límites diarios de horas
            conflicts = check_subtasks_daily_limits(
                request.user, validated_subtasks
            )
            if conflicts:
                return Response({
                    "success": False,
                    "error_code": "DAILY_LIMIT_EXCEEDED",
                    "message": "Algunas subtareas exceden el límite diario de horas.",
                    "details": {"conflicts": conflicts}
                }, status=status.HTTP_400_BAD_REQUEST)

            # Crear actividad + subtareas atómicamente
            with transaction.atomic():
                activity = serializer.save(user=request.user)
                for st_data in validated_subtasks:
                    Subtask.objects.create(activity=activity, **st_data)
        else:
            # Sin subtareas: crear solo la actividad
            serializer.save(user=request.user)

        return Response({
            "success": True,
            "message": "Actividad creada correctamente",
            "data": ActivitySerializer(
                serializer.instance
            ).data
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

        serializer.is_valid(raise_exception=True)

        # Verificar que la actividad pertenece al usuario
        activity_id = serializer.validated_data.get("activity").id
        get_object_or_404(Activity, id=activity_id, user=request.user)

        # Obtener datos validados
        date = serializer.validated_data["target_date"]
        hours = serializer.validated_data["estimated_hours"]

        # Verificar limite diario
        is_valid, total, limit, conflicting_activities = checkDailyLimit(request.user, date, hours)
        if not is_valid:
            return Response({
                "success": False,
                "error_code": "DAILY_LIMIT_EXCEEDED",
                "message": "Has excedido el límite diario de horas.",
                "details": {
                    "date": str(date),
                    "requested_hours": float(hours),
                    "total_hours_day": total,
                    "limit": limit,
                    "conflicting_activities": conflicting_activities
                }
            }, status=status.HTTP_400_BAD_REQUEST)

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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Si se esta intentando completar la tarea, permitimos el cambio sin validar horas
        is_completing = serializer.validated_data.get("completed") is True
        
        # Solo validamos el limite si se esta cambiando la fecha o las horas,
        # o si la tarea NO se esta marcando como completada.
        changing_schedule = "target_date" in serializer.validated_data or "estimated_hours" in serializer.validated_data

        if not is_completing and changing_schedule:
            date = serializer.validated_data.get("target_date", instance.target_date)
            hours = serializer.validated_data.get("estimated_hours", instance.estimated_hours)

            # Verificar limite diario
            is_valid, total, limit, conflicting_activities = checkDailyLimit(
                request.user, date, hours, exclude_subtask_id=instance.id
            )
            
            if not is_valid:
                return Response({
                    "success": False,
                    "error_code": "DAILY_LIMIT_EXCEEDED",
                    "message": "Has excedido el límite diario de horas.",
                    "details": {
                        "date": str(date),
                        "requested_hours": float(hours),
                        "total_hours_day": total,
                        "limit": limit,
                        "conflicting_activities": conflicting_activities
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Subtask updated successfully",
            "data": serializer.data
        })

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({
            "success": True,
            "message": "Subtask eliminada correctamente"
        }, status=status.HTTP_200_OK)
    


