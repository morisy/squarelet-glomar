# Standard Library
import json

# Django
from django.db.models import Count, Q, Sum

# Third Party
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, viewsets
from rest_framework.response import Response

# Squarelet
from squarelet.glomar.api.filters import (
    EmailReceiptFilter,
    EmailSendFilter,
    EventAttendanceFilter,
    EventFilter,
    GlomarOrganizationFilter,
    GlomarUserFilter,
    ResearchContractFilter,
    ResearchProjectFilter,
    WorkLogFilter,
)
from squarelet.glomar.api.permissions import HasGlomarPermission
from squarelet.glomar.api.serializers import (
    EmailReceiptSerializer,
    EmailSendSerializer,
    EventAttendanceSerializer,
    EventSerializer,
    GlomarOrganizationDetailSerializer,
    GlomarOrganizationListSerializer,
    GlomarUserDetailSerializer,
    GlomarUserListSerializer,
    MailingListSerializer,
    ResearchContractSerializer,
    ResearchProjectSerializer,
    WorkLogSerializer,
)
from squarelet.glomar.models import (
    EmailReceipt,
    EmailSend,
    Event,
    EventAttendance,
    MailingList,
    ResearchContract,
    ResearchProject,
    WorkLog,
)
from squarelet.glomar.views import _get_billing_context, _get_login_chart_context
from squarelet.organizations.models import Organization
from squarelet.users.models import User


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EventFilter
    search_fields = ["name"]
    ordering_fields = ["date", "name"]

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


class EventAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventAttendanceSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = EventAttendanceFilter

    def get_queryset(self):
        return EventAttendance.objects.select_related("event", "user")


class MailingListViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MailingListSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name"]

    def get_queryset(self):
        return MailingList.objects.annotate(
            send_count=Count("email_sends"),
            total_recipients=Count("email_sends__receipts"),
        )


class EmailSendViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmailSendSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = EmailSendFilter
    search_fields = ["title"]
    ordering_fields = ["date", "title"]

    def get_queryset(self):
        return EmailSend.objects.select_related("mailing_list").annotate(
            recipient_count=Count("receipts"),
            total_opens=Sum("receipts__opens"),
            total_clicks=Sum("receipts__clicks"),
        )


class EmailReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EmailReceiptSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmailReceiptFilter

    def get_queryset(self):
        return EmailReceipt.objects.select_related("email_send", "user")


class ResearchContractViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResearchContractSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ResearchContractFilter
    search_fields = ["title", "organization__name"]
    ordering_fields = ["start_date", "end_date", "title"]

    def get_queryset(self):
        return ResearchContract.objects.select_related("organization").annotate(
            hours_used=Sum("projects__work_logs__hours"),
            project_count=Count("projects"),
        )


class ResearchProjectViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ResearchProjectSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = ResearchProjectFilter
    search_fields = ["title"]
    ordering_fields = ["created_at", "title", "allotted_hours"]

    def get_queryset(self):
        return ResearchProject.objects.select_related(
            "contract", "contract__organization"
        ).annotate(hours_used=Sum("work_logs__hours"))


class WorkLogViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = WorkLogSerializer
    permission_classes = (HasGlomarPermission,)
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = WorkLogFilter
    ordering_fields = ["work_date", "hours"]

    def get_queryset(self):
        return WorkLog.objects.select_related("project", "user")


class GlomarUserDetailViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Composite user detail endpoint mirroring GlomarUserDetailView."""

    permission_classes = (HasGlomarPermission,)
    lookup_field = "username"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = GlomarUserFilter
    search_fields = ["username", "name", "email"]
    ordering_fields = ["username", "created_at", "last_login"]

    def get_serializer_class(self):
        if self.action == "list":
            return GlomarUserListSerializer
        return GlomarUserDetailSerializer

    def get_queryset(self):
        return User.objects.select_related(
            "individual_organization", "individual_organization___plan"
        )

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        ind_org = user.individual_organization

        # Memberships (non-individual orgs)
        memberships = (
            user.memberships.filter(organization__individual=False)
            .select_related("organization", "organization___plan")
            .order_by("organization__name")
        )
        membership_data = [
            {
                "organization_name": m.organization.name,
                "organization_slug": m.organization.slug,
                "admin": m.admin,
                # pylint: disable=protected-access
                "plan_name": getattr(m.organization._plan, "name", "Free"),
            }
            for m in memberships
        ]

        # Billing
        billing = _get_billing_context([ind_org.id])

        # Login activity
        login_ctx = _get_login_chart_context(user)
        login_activity = json.loads(login_ctx["login_chart_json"])

        # Event attendances
        event_attendances = (
            EventAttendance.objects.filter(user=user)
            .select_related("event")
            .order_by("-event__date")
        )

        # Email receipts
        email_receipts = (
            EmailReceipt.objects.filter(user=user)
            .select_related("email_send", "email_send__mailing_list")
            .order_by("-email_send__date")
        )

        data = {
            "username": user.username,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login,
            "source": user.source,
            "is_staff": user.is_staff,
            "is_active": user.is_active,
            "city": ind_org.city,
            "state": ind_org.state,
            "country": ind_org.country,
            # pylint: disable=protected-access
            "individual_plan": getattr(ind_org._plan, "name", "Free"),
            "verified_journalist": user.verified_journalist(),
            "verified_emails": user.get_verified_emails(),
            "mfa_enabled": user.has_mfa_enabled,
            "billing": billing,
            "login_activity": login_activity,
            "memberships": membership_data,
            "event_attendances": event_attendances,
            "email_receipts": email_receipts,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)


class GlomarOrganizationDetailViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Composite organization detail endpoint mirroring
    GlomarOrganizationDetailView."""

    permission_classes = (HasGlomarPermission,)
    lookup_field = "slug"
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_class = GlomarOrganizationFilter
    search_fields = ["name", "slug"]
    ordering_fields = ["name", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return GlomarOrganizationListSerializer
        return GlomarOrganizationDetailSerializer

    def get_queryset(self):
        qs = Organization.objects.filter(individual=False).select_related("_plan")
        return qs

    def retrieve(self, request, *args, **kwargs):  # pylint: disable=too-many-locals
        org = self.get_object()

        # Subscriptions
        subscriptions = org.subscriptions.select_related("plan")
        subscription_data = [
            {
                "plan_name": s.plan.name if s.plan else "Free",
                "update_on": s.update_on,
                "cancelled": s.cancelled,
            }
            for s in subscriptions
        ]

        # Members
        memberships = org.memberships.select_related("user").order_by(
            "-admin", "user__username"
        )

        # Billing
        billing = _get_billing_context([org.id])

        # Login activity (all members)
        member_ids = list(org.memberships.values_list("user_id", flat=True))
        login_ctx = _get_login_chart_context(user_ids=member_ids)
        login_activity = json.loads(login_ctx["login_chart_json"])

        # Event attendances for all org members
        event_attendances = (
            EventAttendance.objects.filter(user_id__in=member_ids)
            .select_related("event", "user")
            .order_by("-event__date")
        )

        # Email receipts for all org members
        email_receipts = (
            EmailReceipt.objects.filter(user_id__in=member_ids)
            .select_related("email_send", "email_send__mailing_list", "user")
            .order_by("-email_send__date")
        )

        # Research contracts
        contracts = org.research_contracts.annotate(
            hours_used=Sum("projects__work_logs__hours"),
            project_count=Count("projects"),
        )
        active_contracts = contracts.filter(status=ResearchContract.ACTIVE)
        total_hours = active_contracts.aggregate(total=Sum("total_hours"))["total"] or 0
        hours_used = active_contracts.aggregate(used=Sum("hours_used"))["used"] or 0
        research = {
            "total_hours": total_hours,
            "hours_used": hours_used,
            "hours_remaining": total_hours - hours_used,
            "usage_pct": round(hours_used / total_hours * 100) if total_hours else 0,
            "contracts": ResearchContractSerializer(contracts, many=True).data,
        }

        data = {
            "name": org.name,
            "slug": org.slug,
            "created_at": org.created_at,
            "updated_at": org.updated_at,
            "city": org.city,
            "state": org.state,
            "country": org.country,
            "max_users": org.max_users,
            "private": org.private,
            "verified_journalist": org.verified_journalist,
            "plan": getattr(
                org._plan, "name", "Free"  # pylint: disable=protected-access
            ),
            "subscriptions": subscription_data,
            "billing": billing,
            "login_activity": login_activity,
            "memberships": memberships,
            "event_attendances": event_attendances,
            "email_receipts": email_receipts,
            "research": research,
        }

        serializer = self.get_serializer(data)
        return Response(serializer.data)
