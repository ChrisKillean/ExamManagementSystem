from django.urls import path

from .views import DisplayUserTeams, TeamOverview

app_name = "teams"

urlpatterns = [
    path('my-teams/', DisplayUserTeams.as_view(), name='my-teams'),
    path('team-overview/<int:pk>/', TeamOverview.as_view(), name='team-page'),
]
