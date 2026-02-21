# Django
from django.urls import path

from . import views

app_name = "glomar"

urlpatterns = [
    path("", views.GlomarDashboardView.as_view(), name="dashboard"),
    path(
        "users/<slug:username>/",
        views.GlomarUserDetailView.as_view(),
        name="user_detail",
    ),
    path(
        "organizations/<slug:slug>/",
        views.GlomarOrganizationDetailView.as_view(),
        name="organization_detail",
    ),
    path("events/", views.EventListView.as_view(), name="event_list"),
    path("events/create/", views.EventCreateView.as_view(), name="event_create"),
    path("events/<int:pk>/", views.EventDetailView.as_view(), name="event_detail"),
    path(
        "events/<int:pk>/edit/",
        views.EventUpdateView.as_view(),
        name="event_update",
    ),
    path(
        "events/<int:pk>/attendance/",
        views.AttendanceUpdateView.as_view(),
        name="event_attendance",
    ),
]
