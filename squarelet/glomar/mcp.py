# Third Party
from mcp_server import ModelQueryToolset

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


class UserQuery(ModelQueryToolset):
    model = User
    fields = [
        "username",
        "name",
        "email",
        "source",
        "is_staff",
        "is_active",
        "created_at",
        "updated_at",
        "last_login",
    ]
    extra_instructions = (
        "Use this collection to look up user accounts. "
        "Sensitive fields like password hashes and tokens are excluded."
    )


class OrganizationQuery(ModelQueryToolset):
    model = Organization
    fields = [
        "name",
        "slug",
        "created_at",
        "updated_at",
        "city",
        "state",
        "country",
        "individual",
        "private",
        "verified_journalist",
        "max_users",
        "payment_failed",
    ]
    extra_instructions = (
        "Use this collection to look up organizations (excludes individual/personal orgs). "
        "Use $lookup on 'users' to see members."
    )

    def get_queryset(self):
        return super().get_queryset().filter(individual=False)


class EventQuery(ModelQueryToolset):
    model = Event


class EventAttendanceQuery(ModelQueryToolset):
    model = EventAttendance


class MailingListQuery(ModelQueryToolset):
    model = MailingList


class EmailSendQuery(ModelQueryToolset):
    model = EmailSend


class EmailReceiptQuery(ModelQueryToolset):
    model = EmailReceipt


class ResearchContractQuery(ModelQueryToolset):
    model = ResearchContract


class ResearchProjectQuery(ModelQueryToolset):
    model = ResearchProject


class WorkLogQuery(ModelQueryToolset):
    model = WorkLog
