# Third Party
from rest_framework import serializers

# Squarelet
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
from squarelet.organizations.models import Organization
from squarelet.users.models import User


class EventSerializer(serializers.ModelSerializer):
    registered_count = serializers.IntegerField(read_only=True)
    attended_count = serializers.IntegerField(read_only=True)
    total_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Event
        fields = (
            "id",
            "name",
            "date",
            "time",
            "format",
            "description",
            "created_at",
            "updated_at",
            "registered_count",
            "attended_count",
            "total_count",
        )


class EventAttendanceSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)
    event_name = serializers.CharField(source="event.name", read_only=True)

    class Meta:
        model = EventAttendance
        fields = ("id", "event", "event_name", "user", "status", "created_at")


class MailingListSerializer(serializers.ModelSerializer):
    send_count = serializers.IntegerField(read_only=True)
    total_recipients = serializers.IntegerField(read_only=True)

    class Meta:
        model = MailingList
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "updated_at",
            "send_count",
            "total_recipients",
        )


class EmailSendSerializer(serializers.ModelSerializer):
    mailing_list_name = serializers.CharField(
        source="mailing_list.name", read_only=True, default=None
    )
    recipient_count = serializers.IntegerField(read_only=True)
    total_opens = serializers.IntegerField(read_only=True)
    total_clicks = serializers.IntegerField(read_only=True)

    class Meta:
        model = EmailSend
        fields = (
            "id",
            "title",
            "mailing_list",
            "mailing_list_name",
            "date",
            "time",
            "created_at",
            "updated_at",
            "recipient_count",
            "total_opens",
            "total_clicks",
        )


class EmailReceiptSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = EmailReceipt
        fields = ("id", "email_send", "user", "opens", "clicks", "created_at")


class ResearchContractSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    hours_used = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    project_count = serializers.IntegerField(read_only=True)
    hours_remaining = serializers.SerializerMethodField()
    usage_pct = serializers.SerializerMethodField()

    class Meta:
        model = ResearchContract
        fields = (
            "id",
            "organization",
            "organization_name",
            "title",
            "total_hours",
            "start_date",
            "end_date",
            "status",
            "notes",
            "created_at",
            "updated_at",
            "hours_used",
            "project_count",
            "hours_remaining",
            "usage_pct",
        )

    def get_hours_remaining(self, obj):
        used = obj.hours_used or 0
        return obj.total_hours - used

    def get_usage_pct(self, obj):
        if not obj.total_hours:
            return 0
        used = obj.hours_used or 0
        return round(used / obj.total_hours * 100)


class ResearchProjectSerializer(serializers.ModelSerializer):
    hours_used = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    hours_remaining = serializers.SerializerMethodField()
    usage_pct = serializers.SerializerMethodField()

    class Meta:
        model = ResearchProject
        fields = (
            "id",
            "contract",
            "title",
            "size",
            "allotted_hours",
            "status",
            "description",
            "created_at",
            "updated_at",
            "hours_used",
            "hours_remaining",
            "usage_pct",
        )

    def get_hours_remaining(self, obj):
        used = obj.hours_used or 0
        return obj.allotted_hours - used

    def get_usage_pct(self, obj):
        if not obj.allotted_hours:
            return 0
        used = obj.hours_used or 0
        return round(used / obj.allotted_hours * 100)


class WorkLogSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = WorkLog
        fields = (
            "id",
            "project",
            "user",
            "hours",
            "description",
            "work_date",
            "created_at",
        )
        read_only_fields = ("created_at",)


# --- Lightweight list serializers ---


class GlomarUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "name",
            "email",
            "source",
            "is_staff",
            "is_active",
            "created_at",
            "updated_at",
            "last_login",
        )


class GlomarOrganizationListSerializer(serializers.ModelSerializer):
    plan = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            "name",
            "slug",
            "created_at",
            "updated_at",
            "city",
            "state",
            "country",
            "max_users",
            "private",
            "verified_journalist",
            "plan",
        )

    def get_plan(self, obj):
        # pylint: disable=protected-access
        return getattr(obj._plan, "name", "Free")


# --- Composite detail serializers ---


class MembershipSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Inline serializer for org memberships on a user detail."""

    organization_name = serializers.CharField()
    organization_slug = serializers.CharField()
    admin = serializers.BooleanField()
    plan_name = serializers.CharField()


class OrgMemberSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Inline serializer for members on an org detail."""

    username = serializers.CharField(source="user.username")
    admin = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class UserEventAttendanceSerializer(
    serializers.Serializer
):  # pylint: disable=abstract-method
    """Event attendance for user/org detail endpoints."""

    id = serializers.IntegerField()
    event_id = serializers.IntegerField(source="event.id")
    event_name = serializers.CharField(source="event.name")
    event_date = serializers.DateField(source="event.date")
    event_format = serializers.CharField(source="event.format")
    status = serializers.CharField()
    username = serializers.CharField(source="user.username", default=None)


class UserEmailReceiptSerializer(
    serializers.Serializer
):  # pylint: disable=abstract-method
    """Email receipt for user/org detail endpoints."""

    id = serializers.IntegerField()
    email_send_id = serializers.IntegerField(source="email_send.id")
    email_send_title = serializers.CharField(source="email_send.title")
    email_send_date = serializers.DateField(source="email_send.date")
    mailing_list_name = serializers.CharField(
        source="email_send.mailing_list.name", default=None
    )
    opens = serializers.IntegerField()
    clicks = serializers.IntegerField()
    username = serializers.CharField(source="user.username", default=None)


class SubscriptionSerializer(serializers.Serializer):  # pylint: disable=abstract-method
    """Inline serializer for subscriptions on an org detail."""

    plan_name = serializers.CharField()
    update_on = serializers.DateField()
    cancelled = serializers.BooleanField()


class ResearchSummarySerializer(
    serializers.Serializer
):  # pylint: disable=abstract-method
    """Summary of active research contracts for an org."""

    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    hours_used = serializers.DecimalField(max_digits=10, decimal_places=2)
    hours_remaining = serializers.DecimalField(max_digits=10, decimal_places=2)
    usage_pct = serializers.IntegerField()


class GlomarUserDetailSerializer(
    serializers.Serializer
):  # pylint: disable=abstract-method
    """Composite serializer for the user detail API endpoint."""

    # Basic user fields
    username = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    last_login = serializers.DateTimeField()
    source = serializers.CharField()
    is_staff = serializers.BooleanField()
    is_active = serializers.BooleanField()

    # Location from individual org
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()

    # Plan & verification
    individual_plan = serializers.CharField()
    verified_journalist = serializers.BooleanField()
    verified_emails = serializers.ListField(child=serializers.CharField())
    mfa_enabled = serializers.BooleanField()

    # Nested sections
    billing = serializers.DictField()
    login_activity = serializers.DictField()
    memberships = MembershipSerializer(many=True)
    event_attendances = UserEventAttendanceSerializer(many=True)
    email_receipts = UserEmailReceiptSerializer(many=True)


class GlomarOrganizationDetailSerializer(
    serializers.Serializer
):  # pylint: disable=abstract-method
    """Composite serializer for the organization detail API endpoint."""

    # Basic org fields
    name = serializers.CharField()
    slug = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    max_users = serializers.IntegerField()
    private = serializers.BooleanField()
    verified_journalist = serializers.BooleanField()

    # Plan & subscriptions
    plan = serializers.CharField()
    subscriptions = SubscriptionSerializer(many=True)

    # Nested sections
    billing = serializers.DictField()
    login_activity = serializers.DictField()
    memberships = OrgMemberSerializer(many=True)
    event_attendances = UserEventAttendanceSerializer(many=True)
    email_receipts = UserEmailReceiptSerializer(many=True)

    # Research
    research = serializers.DictField()
