from django.utils import timezone

from rest_framework import serializers

from .models import Activity, Subtask

DATE_INPUT_FORMATS = [
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d-%m-%Y %H:%M",
    "%d/%m/%Y %H:%M",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S.%f",
    "%Y-%m-%dT%H:%M:%SZ",
]


class SubtaskSerializer(serializers.ModelSerializer):
    activity_title = serializers.CharField(source="activity.title", read_only=True)
    status = serializers.ChoiceField(
        choices=[
            Subtask.STATUS_PENDING,
            Subtask.STATUS_COMPLETED,
            Subtask.STATUS_POSTPONED,
        ],
        default=Subtask.STATUS_PENDING,
        required=False,
    )
    note = serializers.CharField(required=False, allow_blank=True, allow_null=True, default="")
    completed = serializers.BooleanField(required=False)
    target_date = serializers.DateField(
        input_formats=DATE_INPUT_FORMATS,
        error_messages={
            "invalid": "Fecha con formato erróneo. Use YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY o formato ISO con hora (YYYY-MM-DDTHH:MM)."
        },
    )

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
            "status",
            "note",
            "completed",
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

    def validate_status(self, value):
        valid_statuses = {
            Subtask.STATUS_PENDING,
            Subtask.STATUS_COMPLETED,
            Subtask.STATUS_POSTPONED,
        }
        if value not in valid_statuses:
            raise serializers.ValidationError(
                "Estado inválido. Use pending, completed o postponed."
            )
        return value

    def validate(self, attrs):
        # Normalize null notes coming from frontend optional fields.
        if attrs.get("note") is None:
            attrs["note"] = ""

        # Keep backward compatibility when older clients send `completed` only.
        if "status" not in attrs and "completed" in attrs:
            attrs["status"] = (
                Subtask.STATUS_COMPLETED if attrs["completed"] else Subtask.STATUS_PENDING
            )
        if "status" in attrs and "completed" not in attrs:
            attrs["completed"] = attrs["status"] == Subtask.STATUS_COMPLETED
        return attrs


class InlineSubtaskSerializer(serializers.Serializer):
    """
    Serializer ligero para validar subtareas que vienen dentro del payload
    de creación de actividad (sin campo 'activity', que aún no existe).
    """

    name = serializers.CharField(max_length=255)
    target_date = serializers.DateField(
        input_formats=DATE_INPUT_FORMATS,
        error_messages={
            "invalid": "Fecha con formato erróneo. Use YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY o formato ISO con hora (YYYY-MM-DDTHH:MM)."
        },
    )
    estimated_hours = serializers.DecimalField(max_digits=4, decimal_places=1)
    status = serializers.ChoiceField(
        choices=[
            Subtask.STATUS_PENDING,
            Subtask.STATUS_COMPLETED,
            Subtask.STATUS_POSTPONED,
        ],
        default=Subtask.STATUS_PENDING,
        required=False,
    )
    note = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre no puede estar vacío.")
        return value

    def validate_estimated_hours(self, value):
        if value <= 0:
            raise serializers.ValidationError("Las horas estimadas deben ser mayores que 0.")
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
            "subtasks",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
            "status",
        ]

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Debe especificar un nombre para la actividad")
        return value

    def validate_due_date(self, value):
        # Asegurar que la fecha/hora límite sea futura.
        if value < timezone.now():
            raise serializers.ValidationError(
                "No puedes planificar una fecha de estudio anterior a la actual"
            )
        return value
