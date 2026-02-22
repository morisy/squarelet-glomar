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
    # Mailing Lists
    path(
        "mailing-lists/",
        views.MailingListListView.as_view(),
        name="mailing_list_list",
    ),
    path(
        "mailing-lists/create/",
        views.MailingListCreateView.as_view(),
        name="mailing_list_create",
    ),
    path(
        "mailing-lists/<int:pk>/",
        views.MailingListDetailView.as_view(),
        name="mailing_list_detail",
    ),
    path(
        "mailing-lists/<int:pk>/edit/",
        views.MailingListUpdateView.as_view(),
        name="mailing_list_update",
    ),
    # Email Sends
    path(
        "email-sends/",
        views.EmailSendListView.as_view(),
        name="email_send_list",
    ),
    path(
        "email-sends/create/",
        views.EmailSendCreateView.as_view(),
        name="email_send_create",
    ),
    path(
        "email-sends/<int:pk>/",
        views.EmailSendDetailView.as_view(),
        name="email_send_detail",
    ),
    path(
        "email-sends/<int:pk>/edit/",
        views.EmailSendUpdateView.as_view(),
        name="email_send_update",
    ),
    path(
        "email-sends/<int:pk>/receipt/",
        views.ReceiptUpdateView.as_view(),
        name="email_receipt",
    ),
]
