from collections import defaultdict
from decimal import Decimal

from django.db.models import Sum

from .models import Subtask


def checkDailyLimit(user, date, new_hours=0, exclude_subtask_id=None):
    """
    Verifica si agregar o actualizar una subtarea con 'new_hours' excede el limite.
    Retorna (es_valido, total_actual, limite, actividades_en_conflicto)
    """
    limit = user.daily_hour_limit
    
    # Obtener todas las subtareas del dia, agrupadas por actividad
    # Excluimos subtareas que ya esten marcadas como completadas
    # y subtareas de actividades que esten marcadas como completadas
    qs = Subtask.objects.filter(
        activity__user=user, 
        target_date=date,
        completed=False
    ).exclude(activity__status="completed")

    if exclude_subtask_id:
        qs = qs.exclude(id=exclude_subtask_id)

    # Agrupar por actividad para saber de donde vienen las horas
    activities_qs = (
        qs.values('activity__id', 'activity__title')
        .annotate(total=Sum('estimated_hours'))
        .order_by('-total')
    )

    db_total = sum(item['total'] for item in activities_qs)
    projected_total = db_total + Decimal(str(new_hours))

    if projected_total > limit:
        # Si hay exceso, devolvemos info de que otras actividades estan ocupando el dia
        other_activities = [
            {
                'id': item['activity__id'],
                'title': item['activity__title'],
                'hours': float(item['total'])
            }
            for item in activities_qs
        ]
        return False, float(projected_total), float(limit), other_activities

    return True, float(projected_total), float(limit), []


def check_subtasks_daily_limits(user, subtasks_data):
    """
    Valida que las subtareas enviadas no excedan el límite diario de horas.
    Retorna lista de conflictos con detalle de otras actividades.
    """
    limit = user.daily_hour_limit

    # 1. Agrupar payload por fecha
    payload_hours_by_date = defaultdict(Decimal)
    for subtask in subtasks_data:
        date = subtask["target_date"]
        payload_hours_by_date[date] += Decimal(str(subtask["estimated_hours"]))

    dates = list(payload_hours_by_date.keys())
    
    # 2. Buscar horas de OTRAS actividades en esas fechas (SOLO PENDIENTES)
    db_activities_qs = (
        Subtask.objects
        .filter(activity__user=user, target_date__in=dates, completed=False)
        .exclude(activity__status="completed")
        .values('target_date', 'activity__id', 'activity__title')
        .annotate(total=Sum('estimated_hours'))
    )

    db_info_by_date = defaultdict(list)
    db_total_by_date = defaultdict(Decimal)

    for row in db_activities_qs:
        date = row['target_date']
        db_info_by_date[date].append({
            'id': row['activity__id'],
            'title': row['activity__title'],
            'hours': float(row['total'])
        })
        db_total_by_date[date] += row['total']

    # 3. Validar
    conflicts = []
    for idx, subtask in enumerate(subtasks_data):
        date = subtask["target_date"]
        hours_in_payload = payload_hours_by_date[date]
        hours_in_db = db_total_by_date.get(date, Decimal("0"))
        
        if (hours_in_payload + hours_in_db) > limit:
            conflicts.append({
                "subtask_index": idx,
                "subtask_name": subtask.get("name", f"Subtarea {idx + 1}"),
                "target_date": str(date),
                "hours_requested_total_day": float(hours_in_payload),
                "hours_already_scheduled": float(hours_in_db),
                "limit": float(limit),
                "conflicting_activities": db_info_by_date.get(date, [])
            })

    return conflicts