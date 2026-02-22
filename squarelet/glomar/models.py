# Django
from django.conf import settings
from django.db import models
from django.urls import reverse

# Squarelet
from squarelet.core.fields import AutoCreatedField, AutoLastModifiedField


class Event(models.Model):
    """A trackable event in the Glomar CRM."""

    VIRTUAL = "virtual"
    IN_PERSON = "in_person"
    FORMAT_CHOICES = [
        ("", "—"),
        (VIRTUAL, "Virtual"),
        (IN_PERSON, "In Person"),
    ]

    name = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    format = models.CharField(
        max_length=20, choices=FORMAT_CHOICES, blank=True, default=""
    )
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

    UNKNOWN = ""
    REGISTERED = "registered"
    ATTENDED = "attended"
    NO_SHOW = "no_show"
    STATUS_CHOICES = [
        (UNKNOWN, "—"),
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=UNKNOWN)
    created_at = AutoCreatedField()

    class Meta:
        unique_together = ("event", "user")
        ordering = ("user__username",)

    def __str__(self):
        return f"{self.user} — {self.event} ({self.get_status_display()})"


class MailingList(models.Model):
    """A named mailing list that groups related email sends."""

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("glomar:mailing_list_detail", kwargs={"pk": self.pk})


class EmailSend(models.Model):
    """A single email campaign/blast."""

    title = models.CharField(max_length=255)
    mailing_list = models.ForeignKey(
        MailingList,
        related_name="email_sends",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    class Meta:
        ordering = ("-date",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("glomar:email_send_detail", kwargs={"pk": self.pk})


class EmailReceipt(models.Model):
    """Per-user tracking for an email send."""

    email_send = models.ForeignKey(
        EmailSend, related_name="receipts", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="email_receipts",
        on_delete=models.CASCADE,
    )
    opens = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    created_at = AutoCreatedField()

    class Meta:
        unique_together = ("email_send", "user")
        ordering = ("user__username",)

    def __str__(self):
        return (
            f"{self.user} — {self.email_send}"
            f" ({self.opens} opens, {self.clicks} clicks)"
        )
