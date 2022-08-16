from django.urls import path

from .views import (
    AgentListAPIView,
    GetProfileAPIView,
    TopAgentsListAPIView,
    UpdateProfileAPIView,
)

urlpatterns = [
    path("me/", GetProfileAPIView.as_view(), name="get_profile"),
    path(
        "update/<str:username>/", UpdateProfileAPIView.as_view(), name="update_profile"
    ),
    path("agents/all/", AgentListAPIView.as_view(), name="get_all_agents"),
    path("agents/top/", TopAgentsListAPIView.as_view(), name="get_top_agents"),
]
