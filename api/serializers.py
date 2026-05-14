from rest_framework import serializers
from .models import Subtask, Activity
from django.utils import timezone


class SubtaskSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source='activity.title', read_only=True)

    class Meta:
        model = Subtask
        fields = [
            "id",
            "activity",
            "activity_title",
            "name",
            "target_date",
            "estimated_hours",
            "created_at",
            "completed"
        ]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_estimated_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Las horas estimadas deben ser mayores que 0.")
        return value

    def validate_target_date(self, value):
        # DRF ya valida formato, esto es para mensaje claro
        if not value:
            raise serializers.ValidationError("La fecha objetivo es obligatoria.")

        if value < timezone.localdate():
            raise serializers.ValidationError(
                "La fecha de la subtarea no puede ser anterior a hoy."
            )
        return value


class InlineSubtaskSerializer(serializers.Serializer):
    """
    Serializer ligero para validar subtareas que vienen dentro del payload
    de creación de actividad (sin campo 'activity', que aún no existe).
    """
    name = serializers.CharField(max_length=255)
    target_date = serializers.DateField()
    estimated_hours = serializers.DecimalField(max_digits=4, decimal_places=1)

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_estimated_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Las horas estimadas deben ser mayores que 0."
            )
        return value

    def validate_target_date(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError(
                "La fecha de la subtarea no puede ser anterior a hoy."
            )
        return value
    
class ActivitySerializer(serializers.ModelSerializer):
    subtasks = SubtaskSerializer(many=True, required=False)

    class Meta:
        model = Activity
        fields = [
            "id",
            "user",
            "title",
            "type",
            "course",
            "due_date",
            "event_date",
            "created_at",
            "status",
            "subtasks"
        ]
        
        read_only_fields = [
            "id",
            "user",
            "created_at",
            "status",
        ]

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Debe especificar un nombre para la actividad"
            )
        return value

    def validate_due_date(self, value):
        # Asegurar que la fecha/hora límite sea futura.
        if value < timezone.now():
            raise serializers.ValidationError(
                "No puedes planificar una fecha de estudio anterior a la actual"
            )
        return value
    