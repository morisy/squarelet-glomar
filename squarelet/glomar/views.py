# Standard Library
import json
from collections import defaultdict
from datetime import date

# Django
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

# Squarelet
from squarelet.organizations.models import Organization
from squarelet.organizations.models.payment import Charge
from squarelet.users.models import LoginLog, User

from .forms import (
    AttendanceForm,
    EmailSendForm,
    EventForm,
    MailingListForm,
    ReceiptForm,
)
from .models import EmailReceipt, EmailSend, Event, EventAttendance, MailingList


def _get_billing_context(org_ids):
    """Compute lifetime spend and monthly charges for the last 12 months."""
    charges = Charge.objects.filter(organization_id__in=org_ids)

    lifetime_cents = charges.aggregate(total=Sum("amount"))["total"] or 0

    # Monthly charges for the last 12 months
    today = timezone.now().date()
    months = []
    for i in range(11, -1, -1):
        # Walk backwards 11..0 months from current month
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        month_start = timezone.make_aware(timezone.datetime(y, m, 1))
        if m == 12:
            month_end = timezone.make_aware(timezone.datetime(y + 1, 1, 1))
        else:
            month_end = timezone.make_aware(timezone.datetime(y, m + 1, 1))
        total = (
            charges.filter(
                created_at__gte=month_start, created_at__lt=month_end
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )
        months.append(
            {
                "label": date(y, m, 1).strftime("%b %Y"),
                "short_label": date(y, m, 1).strftime("%b"),
                "amount_cents": total,
                "amount_display": f"${total / 100:,.2f}",
            }
        )

    max_amount = max((m["amount_cents"] for m in months), default=1) or 1
    for m in months:
        m["bar_pct"] = round(m["amount_cents"] / max_amount * 100)

    return {
        "lifetime_spend": f"${lifetime_cents / 100:,.2f}",
        "monthly_charges": months,
    }


def _month_boundaries():
    """Return list of 12 (month_start, month_end, label, short_label) tuples."""
    today = timezone.now().date()
    result = []
    for i in range(11, -1, -1):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        month_start = timezone.make_aware(timezone.datetime(y, m, 1))
        if m == 12:
            month_end = timezone.make_aware(timezone.datetime(y + 1, 1, 1))
        else:
            month_end = timezone.make_aware(timezone.datetime(y, m + 1, 1))
        result.append((month_start, month_end, y, m))
    return result


def _get_login_chart_context(user=None, user_ids=None):
    """Compute monthly login counts per service for the last 12 months."""
    if user_ids is not None:
        logins = LoginLog.objects.filter(user_id__in=user_ids)
    else:
        logins = LoginLog.objects.filter(user=user)
    boundaries = _month_boundaries()

    # Get all logins in the 12-month window at once
    window_start = boundaries[0][0]
    window_end = boundaries[-1][1]
    monthly_data = (
        logins.filter(created_at__gte=window_start, created_at__lt=window_end)
        .values("client__name", "created_at__year", "created_at__month")
        .annotate(count=Count("id"))
    )

    # Build lookup: (year, month, service) -> count
    lookup = defaultdict(int)
    services = set()
    for row in monthly_data:
        key = (row["created_at__year"], row["created_at__month"], row["client__name"])
        lookup[key] = row["count"]
        services.add(row["client__name"])

    services = sorted(services)

    # Build chart data: list of months, each with per-service counts
    labels = []
    series = {s: [] for s in services}
    for month_start, month_end, y, m in boundaries:
        labels.append(date(y, m, 1).strftime("%b"))
        for s in services:
            series[s].append(lookup[(y, m, s)])

    return {
        "login_chart_json": json.dumps({"labels": labels, "series": series}),
    }


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restrict access to users with the view_glomar permission"""

    def test_func(self):
        return self.request.user.has_perm("glomar.view_glomar")


class GlomarDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "glomar/dashboard.html"


class GlomarUserDetailView(StaffRequiredMixin, DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "glomar/user_detail.html"
    context_object_name = "target_user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        ind_org = user.individual_organization

        # Location from the individual organization
        context["city"] = ind_org.city
        context["state"] = ind_org.state
        context["country"] = ind_org.country

        # Individual plan (subscription on the individual org)
        context["individual_plan"] = ind_org._plan

        # Verification
        context["verified_journalist"] = user.verified_journalist()
        context["verified_emails"] = user.get_verified_emails()

        # Org memberships (non-individual orgs)
        memberships = (
            user.memberships.filter(organization__individual=False)
            .select_related("organization", "organization___plan")
            .order_by("organization__name")
        )
        # Attach plan_name since templates can't access _plan
        for m in memberships:
            m.plan_name = getattr(m.organization._plan, "name", "Free")
        context["memberships"] = memberships

        # Billing: charges on the individual org
        context.update(_get_billing_context([ind_org.id]))

        # Service logins chart
        context.update(_get_login_chart_context(user))

        # Event attendances
        context["event_attendances"] = (
            EventAttendance.objects.filter(user=user)
            .select_related("event")
            .order_by("-event__date")
        )

        # Email receipts
        context["email_receipts"] = (
            EmailReceipt.objects.filter(user=user)
            .select_related("email_send", "email_send__mailing_list")
            .order_by("-email_send__date")
        )

        return context


class GlomarOrganizationDetailView(StaffRequiredMixin, DetailView):
    model = Organization
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = "glomar/organization_detail.html"
    context_object_name = "org"

    def get_queryset(self):
        return Organization.objects.filter(individual=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        org = self.object

        context["plan"] = org._plan
        context["verified_journalist"] = org.verified_journalist

        # Subscriptions
        subscriptions = org.subscriptions.select_related("plan")
        # Attach plan_name since templates can't access _plan
        for s in subscriptions:
            s.plan_name = s.plan.name if s.plan else "Free"
        context["subscriptions"] = subscriptions

        # Members sorted admins-first, then by username
        memberships = org.memberships.select_related("user").order_by(
            "-admin", "user__username"
        )
        context["memberships"] = memberships

        # Billing: charges on this org
        context.update(_get_billing_context([org.id]))

        # Service logins chart (all members' logins)
        member_ids = list(org.memberships.values_list("user_id", flat=True))
        context.update(_get_login_chart_context(user_ids=member_ids))

        # Event attendances for all org members
        context["event_attendances"] = (
            EventAttendance.objects.filter(user_id__in=member_ids)
            .select_related("event", "user")
            .order_by("-event__date")
        )

        # Email receipts for all org members
        context["email_receipts"] = (
            EmailReceipt.objects.filter(user_id__in=member_ids)
            .select_related("email_send", "email_send__mailing_list", "user")
            .order_by("-email_send__date")
        )

        return context


# --- Event views ---


class EventListView(StaffRequiredMixin, ListView):
    model = Event
    template_name = "glomar/event_list.html"
    context_object_name = "events"

    def get_queryset(self):
        return Event.objects.annotate(
            registered_count=Count(
                "attendances",
                filter=Q(attendances__status=EventAttendance.REGISTERED),
            ),
            attended_count=Count(
                "attendances",
                filter=Q(attendances__status=EventAttendance.ATTENDED),
            ),
            total_count=Count("attendances"),
        )


class EventDetailView(StaffRequiredMixin, DetailView):
    model = Event
    template_name = "glomar/event_detail.html"
    context_object_name = "event"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendances"] = self.object.attendances.select_related(
            "user"
        ).order_by("user__username")
        context["status_choices"] = EventAttendance.STATUS_CHOICES
        return context


class EventCreateView(StaffRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = "glomar/event_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class EventUpdateView(StaffRequiredMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = "glomar/event_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class AttendanceUpdateView(StaffRequiredMixin, View):
    """Handle adding/removing attendees and updating attendance status."""

    def post(self, request, pk):
        event = get_object_or_404(Event, pk=pk)
        form = AttendanceForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]

            if action == "add" and form.cleaned_data.get("username"):
                username = form.cleaned_data["username"]
                try:
                    user = User.objects.get(username=username)
                    EventAttendance.objects.get_or_create(event=event, user=user)
                except User.DoesNotExist:
                    pass

            elif action == "update_status" and form.cleaned_data.get("attendance_id"):
                attendance_id = form.cleaned_data["attendance_id"]
                status = form.cleaned_data.get("status", "")
                if status in dict(EventAttendance.STATUS_CHOICES):
                    EventAttendance.objects.filter(
                        id=attendance_id, event=event
                    ).update(status=status)

            elif action == "remove" and form.cleaned_data.get("attendance_id"):
                EventAttendance.objects.filter(
                    id=form.cleaned_data["attendance_id"], event=event
                ).delete()

        return redirect("glomar:event_detail", pk=event.pk)


# --- Mailing List views ---


class MailingListListView(StaffRequiredMixin, ListView):
    model = MailingList
    template_name = "glomar/mailing_list_list.html"
    context_object_name = "mailing_lists"

    def get_queryset(self):
        return MailingList.objects.annotate(
            send_count=Count("email_sends"),
            total_recipients=Count("email_sends__receipts"),
        )


class MailingListDetailView(StaffRequiredMixin, DetailView):
    model = MailingList
    template_name = "glomar/mailing_list_detail.html"
    context_object_name = "mailing_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["email_sends"] = self.object.email_sends.annotate(
            recipient_count=Count("receipts"),
            total_opens=Sum("receipts__opens"),
            total_clicks=Sum("receipts__clicks"),
        )
        return context


class MailingListCreateView(StaffRequiredMixin, CreateView):
    model = MailingList
    form_class = MailingListForm
    template_name = "glomar/mailing_list_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class MailingListUpdateView(StaffRequiredMixin, UpdateView):
    model = MailingList
    form_class = MailingListForm
    template_name = "glomar/mailing_list_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


# --- Email Send views ---


class EmailSendListView(StaffRequiredMixin, ListView):
    model = EmailSend
    template_name = "glomar/email_send_list.html"
    context_object_name = "email_sends"

    def get_queryset(self):
        return EmailSend.objects.select_related("mailing_list").annotate(
            recipient_count=Count("receipts"),
            total_opens=Sum("receipts__opens"),
            total_clicks=Sum("receipts__clicks"),
        )


class EmailSendDetailView(StaffRequiredMixin, DetailView):
    model = EmailSend
    template_name = "glomar/email_send_detail.html"
    context_object_name = "email_send"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["receipts"] = self.object.receipts.select_related("user").order_by(
            "user__username"
        )
        return context


class EmailSendCreateView(StaffRequiredMixin, CreateView):
    model = EmailSend
    form_class = EmailSendForm
    template_name = "glomar/email_send_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class EmailSendUpdateView(StaffRequiredMixin, UpdateView):
    model = EmailSend
    form_class = EmailSendForm
    template_name = "glomar/email_send_form.html"

    def get_success_url(self):
        return self.object.get_absolute_url()


class ReceiptUpdateView(StaffRequiredMixin, View):
    """Handle adding/removing recipients and updating opens/clicks."""

    def post(self, request, pk):
        email_send = get_object_or_404(EmailSend, pk=pk)
        form = ReceiptForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data["action"]

            if action == "add" and form.cleaned_data.get("username"):
                username = form.cleaned_data["username"]
                try:
                    user = User.objects.get(username=username)
                    EmailReceipt.objects.get_or_create(email_send=email_send, user=user)
                except User.DoesNotExist:
                    pass

            elif action == "update" and form.cleaned_data.get("receipt_id"):
                receipt_id = form.cleaned_data["receipt_id"]
                updates = {}
                if form.cleaned_data.get("opens") is not None:
                    updates["opens"] = form.cleaned_data["opens"]
                if form.cleaned_data.get("clicks") is not None:
                    updates["clicks"] = form.cleaned_data["clicks"]
                if updates:
                    EmailReceipt.objects.filter(
                        id=receipt_id, email_send=email_send
                    ).update(**updates)

            elif action == "remove" and form.cleaned_data.get("receipt_id"):
                EmailReceipt.objects.filter(
                    id=form.cleaned_data["receipt_id"], email_send=email_send
                ).delete()

        return redirect("glomar:email_send_detail", pk=email_send.pk)
