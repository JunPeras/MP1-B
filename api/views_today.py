from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Subtask, Activity
from .serializers import SubtaskSerializer, ActivitySerializer
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from django.db.models import Q

@extend_schema(
    summary="Get today's prioritized subtasks",
    parameters=[
        OpenApiParameter("days_ahead", OpenApiTypes.INT, description="Number of days to consider as 'Coming Up'", default=7),
        OpenApiParameter("course", OpenApiTypes.STR, description="Filter by activity course"),
        OpenApiParameter("activity_status", OpenApiTypes.STR, description="Filter by activity status"),
        OpenApiParameter("completed", OpenApiTypes.BOOL, description="Filter by subtask completion status")
    ],
    responses={200: OpenApiTypes.OBJECT}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_view(request):
    """
    Get subtasks grouped by: Overdue, Today, and Coming Up.
    Ordered by date (asc) and then by estimated effort (asc).
    """
    user = request.user
    today = timezone.now().date()
    
    # Parameters
    try:
        days_ahead = int(request.query_params.get('days_ahead', 7))
    except (ValueError, TypeError):
        days_ahead = 7
        
    course_filter = request.query_params.get('course')
    status_filter = request.query_params.get('activity_status')
    completed_filter = request.query_params.get('completed')

    # Base Queryset: filter by user and non-completed (unless specified)
    subtasks_qs = Subtask.objects.filter(activity__user=user)
    
    # Apply filters
    if course_filter:
        subtasks_qs = subtasks_qs.filter(activity__course__iexact=course_filter)
    
    if status_filter:
        subtasks_qs = subtasks_qs.filter(activity__status__iexact=status_filter)
        
    if completed_filter is not None:
        is_completed = completed_filter.lower() == 'true'
        subtasks_qs = subtasks_qs.filter(completed=is_completed)
    else:
        # Default: only non-completed
        subtasks_qs = subtasks_qs.filter(completed=False)

    # 1. OVERDUE: date < today
    overdue = subtasks_qs.filter(target_date__lt=today).order_by('target_date', 'estimated_hours')
    
    # 2. TODAY: date == today
    for_today = subtasks_qs.filter(target_date=today).order_by('estimated_hours')
    
    # 3. COMING UP: today < date <= today + days_ahead
    limit_date = today + timedelta(days=days_ahead)
    coming_up = subtasks_qs.filter(
        target_date__gt=today, 
        target_date__lte=limit_date
    ).order_by('target_date', 'estimated_hours')

    # Serialize
    overdue_data = SubtaskSerializer(overdue, many=True).data
    for_today_data = SubtaskSerializer(for_today, many=True).data
    coming_up_data = SubtaskSerializer(coming_up, many=True).data

    return Response({
        "summary": f"Prioridades del usuario ordenada por fecha y menor esfuerzo primero.",
        "groups": {
            "overdue": {
                "title": "Vencidas",
                "count": overdue.count(),
                "tasks": overdue_data
            },
            "today": {
                "title": "Para hoy",
                "count": for_today.count(),
                "tasks": for_today_data
            },
            "coming_up": {
                "title": f"Próximas ({days_ahead} días)",
                "count": coming_up.count(),
                "tasks": coming_up_data
            }
        },
        "total_count": overdue.count() + for_today.count() + coming_up.count()
    })

@extend_schema(
    summary="Get unique courses for the current user",
    responses={200: OpenApiTypes.STR}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def courses_list_view(request):
    """
    Get a list of all unique courses from the user's activities.
    Useful for filtering UI.
    """
    courses = Activity.objects.filter(user=request.user).values_list('course', flat=True).distinct()
    return Response(list(courses))
