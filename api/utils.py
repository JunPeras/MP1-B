from django.db.models import Sum
from .models import Subtask


def checkDailyLimit(user, date, new_hours=0):

    total_hours = (
        Subtask.objects
        .filter(activity__user=user, target_date=date)
        .aggregate(total=Sum("estimated_hours"))
        .get("total") or 0
    )

    total_hours += new_hours

    if total_hours > user.daily_hour_limit:
        return False

    return True