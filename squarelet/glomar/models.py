# Django
from django.conf import settings
from django.db import models
from django.urls import reverse

# Squarelet
from squarelet.core.fields import AutoCreatedField, AutoLastModifiedField


class Event(models.Model):
    """A trackable event in the Glomar CRM."""

    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    class Meta:
        ordering = ("-date",)
        permissions = (("view_glomar", "Can access Glomar CRM"),)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("glomar:event_detail", kwargs={"pk": self.pk})


class EventAttendance(models.Model):
    """Tracks a user's attendance status for an event."""

    REGISTERED = "registered"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    STATUS_CHOICES = [
        (REGISTERED, "Registered"),
        (ATTENDED, "Attended"),
        (NO_SHOW, "No-show"),
    ]

    event = models.ForeignKey(
        Event, related_name="attendances", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="event_attendances",
        on_delete=models.CASCADE,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=REGISTERED
    )
    created_at = AutoCreatedField()

    class Meta:
        unique_together = ("event", "user")
        ordering = ("user__username",)

    def __str__(self):
        return f"{self.user} — {self.event} ({self.get_status_display()})"
