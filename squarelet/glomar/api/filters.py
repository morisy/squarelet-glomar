# Third Party
import django_filters

# Squarelet
from squarelet.glomar.models import (
    EmailReceipt,
    EmailSend,
    Event,
    EventAttendance,
    ResearchContract,
    ResearchProject,
    WorkLog,
)
from squarelet.organizations.models import Organization
from squarelet.users.models import User


class EventFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["format"]


class EventAttendanceFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username")

    class Meta:
        model = EventAttendance
        fields = ["event", "user"]


class EmailSendFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = EmailSend
        fields = ["mailing_list"]


class EmailReceiptFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username")

    class Meta:
        model = EmailReceipt
        fields = ["email_send", "user"]


class ResearchContractFilter(django_filters.FilterSet):
    organization = django_filters.NumberFilter(field_name="organization_id")

    class Meta:
        model = ResearchContract
        fields = ["status", "organization"]


class ResearchProjectFilter(django_filters.FilterSet):
    contract = django_filters.NumberFilter(field_name="contract_id")

    class Meta:
        model = ResearchProject
        fields = ["contract", "status", "size"]


class GlomarUserFilter(django_filters.FilterSet):
    is_staff = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()
    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = User
        fields = ["source", "is_staff", "is_active"]


class GlomarOrganizationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    private = django_filters.BooleanFilter()
    verified_journalist = django_filters.BooleanFilter()
    created_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Organization
        fields = ["name", "private", "verified_journalist", "state", "country"]


class WorkLogFilter(django_filters.FilterSet):
    project = django_filters.NumberFilter(field_name="project_id")
    user = django_filters.CharFilter(field_name="user__username")
    date_from = django_filters.DateFilter(field_name="work_date", lookup_expr="gte")
    date_to = django_filters.DateFilter(field_name="work_date", lookup_expr="lte")

    class Meta:
        model = WorkLog
        fields = ["project", "user"]
