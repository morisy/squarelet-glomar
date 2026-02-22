# Standard Library
import random
import uuid
from datetime import date, timedelta
from decimal import Decimal

# Django
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

# Squarelet
from squarelet.organizations.models import Membership, Organization
from squarelet.organizations.models.payment import Charge, Customer, Plan, Subscription

ORG_NAMES = [
    "The Bayside Courier",
    "Millbrook Gazette",
    "The Harrington Herald",
    "Coastal Plains Tribune",
    "The Westfield Examiner",
    "Dunmore Daily Register",
    "The Ironwood Sentinel",
    "Lakehaven Press",
    "The Crestwood Observer",
    "Fairfield Evening Post",
    "The Northgate Chronicle",
    "Riverton Independent",
    "The Ashby Dispatch",
    "Clearwater Times-Picayune",
    "The Elmwood Ledger",
    "Sandstone Record",
    "The Holloway Report",
    "Greenvale Sun",
    "The Portsmith Inquirer",
    "Maplewood Free Press",
    "The Ridgeline Journal",
    "Harborview Star",
    "The Calloway Beacon",
    "Stonehaven Weekly",
    "The Pendleton Globe",
    "Ferndale Current",
    "The Brackton Review",
    "Silverwood Bulletin",
    "The Oakdale Clarion",
    "Cliffside Monitor",
    "The Burnham Standard",
    "Valley Ridge Advocate",
    "The Whitmore Express",
    "Tidewater Mirror",
    "The Colton Pilot",
    "Marshfield Examiner",
    "The Dunbar Signal",
    "Pineview Correspondent",
    "The Alton Transcript",
    "Redwood Falls Dispatch",
    "The Garrison Weekly",
    "Bellmoor Citizen",
    "The Fenwick Report",
    "Copperhead Creek Courier",
    "The Sutton Intelligencer",
    "Wrenfield Evening News",
    "The Halcyon Times",
    "Birchwood Register",
    "The Dalton Perspective",
    "Lakemont Public Press",
]

US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

CHARGE_DESCRIPTIONS = [
    "Monthly subscription",
    "Additional user seats",
    "Research desk access",
    "Document processing fee",
    "API access overage",
    "Premium support add-on",
    "Annual renewal",
    "Setup fee",
    "Training session",
    "Data export fee",
]


class Command(BaseCommand):
    help = "Seed 50 test news organizations with varied plans and fake charges"

    def add_arguments(self, parser):
        parser.add_argument(
            "--teardown",
            action="store_true",
            help="Remove all seeded test organizations instead of creating them",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["teardown"]:
            self.teardown()
            return

        self.seed()

    def teardown(self):
        slugs = []
        for name in ORG_NAMES:
            from django.utils.text import slugify

            slugs.append(slugify(name))

        count, details = Organization.objects.filter(
            slug__in=slugs, individual=False
        ).delete()
        self.stderr.write(self.style.SUCCESS(f"Deleted {count} objects: {details}"))

    def seed(self):
        random.seed(42)

        # Get group-eligible plans
        group_plans = list(
            Plan.objects.filter(for_groups=True).order_by("base_price")
        )
        if not group_plans:
            self.stderr.write(
                self.style.ERROR("No group plans found. Run migrations first.")
            )
            return

        self.stderr.write(
            f"Using {len(group_plans)} plans: "
            + ", ".join(p.name for p in group_plans)
        )

        created = 0
        skipped = 0

        for name in ORG_NAMES:
            from django.utils.text import slugify

            slug = slugify(name)

            if Organization.objects.filter(slug=slug).exists():
                self.stderr.write(f"  Skipping {name} (already exists)")
                skipped += 1
                continue

            # Pick a random plan
            plan = random.choice(group_plans)

            # Vary max_users based on plan tier
            max_users = random.choice([5, 10, 15, 20, 25, 50])

            # Random US state
            state = random.choice(US_STATES)

            org = Organization.objects.create(
                name=name,
                slug=slug,
                individual=False,
                private=False,
                verified_journalist=True,
                max_users=max_users,
                state=state,
                country="US",
            )

            # Create customer record (required for billing)
            Customer.objects.create(organization=org)

            # Create subscription with the chosen plan
            update_on = date.today() + timedelta(days=random.randint(1, 30))
            Subscription.objects.create(
                organization=org,
                plan=plan,
                update_on=update_on,
            )

            # Create random fake charges (1-8 per org)
            num_charges = random.randint(1, 8)
            for _ in range(num_charges):
                days_ago = random.randint(1, 365)
                charge_date = timezone.now() - timedelta(days=days_ago)
                amount = random.choice(
                    [1700, 3400, 4000, 6800, 10000, 13800, 20000, 27500, 32000]
                )

                Charge.objects.create(
                    organization=org,
                    amount=amount,
                    fee_amount=0,
                    charge_id=f"ch_test_{uuid.uuid4().hex[:24]}",
                    description=random.choice(CHARGE_DESCRIPTIONS),
                    created_at=charge_date,
                )

            self.stderr.write(
                f"  Created {name} "
                f"(plan={plan.name}, users={max_users}, "
                f"charges={num_charges}, state={state})"
            )
            created += 1

        self.stderr.write(
            self.style.SUCCESS(
                f"\nDone: {created} created, {skipped} skipped"
            )
        )
