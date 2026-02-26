from rest_framework import serializers
from .models import Subtask, Activity
from datetime import date

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ["id", "title", "type", "course", "due_date", "created_at"]

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Debe especificar un nombre para la actividad"
            )
        return value

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError(
                "No puedes planificar una fecha de estudio anterior a la actual"
            )
        return value
    

class SubtaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subtask
        fields = ["id", "activity", "name", "target_date", "estimated_hours", "created_at"]

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
        return value