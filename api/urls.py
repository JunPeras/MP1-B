from django.urls import path
from .views import (
    notes,
    note_detail,
    ActivityView,
    ActivityDetailView,
    SubtaskView,
    SubtaskDetailView,
    ActivitySubtasksView,
    health,
)
from .views_auth import (
    register_view,
    login_view,
    logout_view,
    profile_view,
    update_profile_view,
    check_limit_view,
)
from .views_today import (
    today_view,
    courses_list_view,
)

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    # Authentication endpoints
    path("auth/register/", register_view, name="register"),
    path("auth/login/", login_view, name="login"),
    path("auth/logout/", logout_view, name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/profile/", profile_view, name="profile"),
    path("auth/profile/update/", update_profile_view, name="update_profile"),
    path("auth/profile/check-limit/", check_limit_view, name="check_limit"),

    # Productivity endpoints
    path("today/", today_view, name="today"),
    path("courses/", courses_list_view, name="courses"),
    
    # Existing endpoints
    path("notes/", notes),
    path("notes/<int:note_id>/", note_detail),

    path("activities/", ActivityView.as_view()),
    path("activities/<int:pk>/", ActivityDetailView.as_view()),
    path("activities/<int:pk>/subtasks/", ActivitySubtasksView.as_view()),

    path("subtasks/", SubtaskView.as_view()),
    path("subtasks/<int:pk>/", SubtaskDetailView.as_view()),

    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("health/", health),
]