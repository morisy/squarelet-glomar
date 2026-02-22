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


class ResearchContract(models.Model):
    """A contract allotting research hours to an organization."""

    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (COMPLETED, "Completed"),
        (EXPIRED, "Expired"),
    ]

    organization = models.ForeignKey(
        "organizations.Organization",
        related_name="research_contracts",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    total_hours = models.DecimalField(max_digits=7, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    notes = models.TextField(blank=True)
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    class Meta:
        ordering = ("-start_date",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("glomar:contract_detail", kwargs={"pk": self.pk})


class ResearchProject(models.Model):
    """A project that consumes hours from a research contract."""

    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    SIZE_CHOICES = [
        (SMALL, "Small (up to 25 hrs)"),
        (MEDIUM, "Medium (up to 50 hrs)"),
        (LARGE, "Large (custom)"),
    ]
    SIZE_HOUR_DEFAULTS = {SMALL: 25, MEDIUM: 50}

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (OPEN, "Open"),
        (IN_PROGRESS, "In Progress"),
        (COMPLETED, "Completed"),
        (CANCELLED, "Cancelled"),
    ]

    contract = models.ForeignKey(
        ResearchContract, related_name="projects", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    allotted_hours = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    description = models.TextField(blank=True)
    created_at = AutoCreatedField()
    updated_at = AutoLastModifiedField()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("glomar:project_detail", kwargs={"pk": self.pk})


class WorkLog(models.Model):
    """A log entry of hours worked on a research project."""

    project = models.ForeignKey(
        ResearchProject, related_name="work_logs", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="research_work_logs",
        on_delete=models.CASCADE,
    )
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    work_date = models.DateField()
    created_at = AutoCreatedField()

    class Meta:
        ordering = ("-work_date",)

    def __str__(self):
        return f"{self.user} — {self.hours}h on {self.work_date}"
