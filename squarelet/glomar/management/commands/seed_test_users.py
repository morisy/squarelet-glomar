# Standard Library
import random

# Django
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

# Third Party
from allauth.account.models import EmailAddress

# Squarelet
from squarelet.organizations.models import Membership, Organization
from squarelet.users.models import User

USER_NAMES = [
    "Adrienne Colquhoun",
    "Marcus Thibodeau",
    "Priya Nambiar",
    "Felix Ostrowski",
    "Celeste Drummond",
    "Jerome Wakefield",
    "Ingrid Halvorsen",
    "Darnell Pitcher",
    "Yolanda Esperanza",
    "Tobias Fennell",
    "Simone Achterberg",
    "Kwame Asante",
    "Bridget Czarnecki",
    "Rafael Solorzano",
    "Nadia Petrossian",
    "Clive Abernethy",
    "Fatima Oduya",
    "Spencer Hollenbeck",
    "Miriam Goldstein",
    "Alejandro Villanueva",
    "Tamsin Brackley",
    "Obinna Eze",
    "Harriet Swanwick",
    "Colin Murchie",
    "Yuki Tanigawa",
    "Desmond Farquhar",
    "Lena Brożek",
    "Antoine Clervaux",
    "Khadija Moussa",
    "Warren Thistlethwaite",
    "Svetlana Borisenko",
    "Emmett Galloway",
    "Pilar Montserrat",
    "Reginald Ashby",
    "Fumiko Nakashima",
    "Cormac Drennan",
    "Zahara Okonkwo",
    "Phoebe Nightingale",
    "Silas Drummond",
    "Ananya Krishnaswamy",
    "Bertrand Lefeuvre",
    "Winona Blackthorne",
    "Idris Mensah",
    "Georgina Tully",
    "Pavel Horváček",
    "Solange Belafonte",
    "Hugh Cavendish",
    "Rosamund Fitch",
    "Tendai Mokoena",
    "Lars Lindqvist",
    "Marisela Gutierrez",
    "Alistair Dunbar",
    "Chiamaka Obi",
    "Fletcher Whitmore",
    "Seraphina Kowalczyk",
    "Vaughn Eddington",
    "Adaeze Nwosu",
    "Casimir Przybylski",
    "Leonora Esterhuysen",
    "Declan Finneran",
    "Imani Nakagawa",
    "Rutherford Crane",
    "Blessing Adeleke",
    "Isadora Pembrook",
    "Nikolai Voloshyn",
    "Celestine Abara",
    "Angus MacPherson",
    "Rosaline Svensson",
    "Tarquin Featherstone",
    "Abena Asiedu",
    "Matteo Scarpelli",
    "Wren Hollingsworth",
    "Chukwuemeka Nzinga",
    "Cordelia Bancroft",
    "Dmitri Shevchenko",
    "Patience Acheampong",
    "Leopold Hartmann",
    "Seun Adeyemi",
    "Imogen Bellweather",
    "Thaddeus Burrell",
    "Keiko Yamamoto",
    "Orla Flanagan",
    "Emmanuel Ouattara",
    "Constance Whitfield",
    "Reuben Achterberg",
    "Nneka Okwu",
    "Percival Sotheby",
    "Linnea Björklund",
    "Chidi Okonkwo",
    "Maeve Callister",
    "Bashir Rahimi",
    "Theodora Blackwell",
    "Søren Holmberg",
    "Adaora Uzoma",
    "Winston Fairfax",
    "Zara Hussain",
    "Crispin Wollstonecraft",
    "Ebony Marchetti",
    "Tadashi Fujimoto",
    "Genevieve Beaumont",
    "Kofi Dartey",
    "Sibyl Ravenswood",
    "Aloysius Brennan",
    "Chidinma Eze",
    "Frederica Llewellyn",
    "Tunde Oladele",
    "Marguerite Delacroix",
    "Stellan Axelsson",
    "Nkechi Obiora",
    "Bertram Foxley",
    "Amara Diallo",
    "Clifton Ashworth",
    "Vesna Kovačević",
    "Lemuel Granger",
    "Chisom Ugwu",
    "Arabella Fforbes",
    "Yusuf Kamara",
    "Octavia Pemberton",
    "Rasmus Kjaergaard",
    "Adunola Fashola",
    "Sebastian Wierzbicki",
    "Zinnia Moreau",
    "Ekundayo Bello",
    "Lavinia Stanhope",
    "Miroslav Dragić",
    "Chiamaka Igwe",
    "Rupert Wyndham",
    "Shirin Nazari",
    "Emeka Okafor",
    "Clarissa Whitmore",
    "Gunnar Thorvaldsen",
    "Adisa Ogunleye",
    "Millicent Foxbourne",
    "Cyprian Koslowski",
    "Fatou Dieng",
    "Aldous Pembroke",
    "Yewande Adesanya",
    "Cornelius Blackwood",
    "Leila Mansouri",
    "Prosper Nkemdirim",
    "Eugenia Stafford",
    "Seamus Callaghan",
    "Zora Nkosi",
    "Edmund Whitacre",
    "Blessing Nwobi",
    "Horatio Cartwright",
    "Abiodun Salami",
    "Portia Langford",
    "Eriko Hayashi",
    "Theron Caldecott",
    "Akosua Mensah",
    "Godfrey Tremayne",
    "Halima Jibril",
    "Reginald Bottomley",
    "Saoirse Donnelly",
    "Uzoma Nwoye",
    "Wilhelmina Thorpe",
    "Chukwudi Ikenna",
    "Barnabas Whitcomb",
    "Adaeze Obi",
    "Florian Bruckner",
    "Abimbola Adeyemo",
    "Lavinia Crumpet",
    "Kwabena Owusu",
    "Millicent Ravenswood",
    "Tomiwa Adeleke",
    "Caspian Holloway",
    "Sunniva Østergaard",
    "Rotimi Fashola",
    "Eugenie Cholmondeley",
    "Stanisław Wojciechowski",
    "Nkechi Uzoma",
    "Barnaby Featherington",
    "Aissatou Balde",
    "Reginald Foxley",
    "Chibueze Nwosu",
    "Edwina Grimshaw",
    "Olumide Adebayo",
    "Celestine Fournier",
    "Torbjørn Halvorsen",
    "Amina Camara",
    "Cornelius Hartley",
    "Onyinye Okeke",
    "Jasper Coldwell",
    "Wanjiru Kariuki",
    "Peregrine Ashby",
    "Chinenye Obasi",
    "Aldrich Pembrook",
    "Mariam Traoré",
    "Sixtus Worthington",
    "Adaeze Nwoye",
    "Mortimer Blackthorn",
    "Uchenna Okonkwo",
    "Arabella Stonehouse",
    "Dakarai Moyo",
    "Ignatius Fairweather",
    "Oluwakemi Adegoke",
    "Clementine Ravenswood",
    "Chibuzo Obi",
    "Reginald Stanhope",
]

# Same org names as seed_test_orgs for cross-referencing
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

DEFAULT_PASSWORD = "test-password-2026"


def make_username(full_name):
    """Generate a username like 'acolquhoun' from 'Adrienne Colquhoun'."""
    parts = full_name.strip().split()
    first = parts[0]
    last = parts[-1]
    base = slugify(f"{first[0]}{last}")
    return base


class Command(BaseCommand):
    help = "Seed test users and assign them to test organizations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--teardown",
            action="store_true",
            help="Remove all seeded test users",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["teardown"]:
            self.teardown()
            return

        self.seed()

    def teardown(self):
        usernames = []
        for name in USER_NAMES:
            usernames.append(make_username(name))

        # Delete users (cascades to memberships, email addresses, individual orgs)
        users = User.objects.filter(username__in=usernames)
        # Also delete their individual organizations
        individual_org_ids = list(
            users.values_list("individual_organization_id", flat=True)
        )
        count, details = users.delete()
        self.stderr.write(f"Deleted {count} user-related objects: {details}")

        org_count, org_details = Organization.objects.filter(
            uuid__in=individual_org_ids
        ).delete()
        self.stderr.write(
            f"Deleted {org_count} individual org objects: {org_details}"
        )
        self.stderr.write(self.style.SUCCESS("Teardown complete"))

    def seed(self):
        random.seed(99)

        # Load all test organizations
        org_slugs = [slugify(name) for name in ORG_NAMES]
        orgs = list(
            Organization.objects.filter(slug__in=org_slugs, individual=False)
        )
        if not orgs:
            self.stderr.write(
                self.style.ERROR(
                    "No test organizations found. Run seed_test_orgs first."
                )
            )
            return

        self.stderr.write(f"Found {len(orgs)} test organizations")

        # Track which orgs have admins assigned
        orgs_with_admin = set()
        # Track memberships to create
        memberships_to_create = []

        # Create all users first
        created_users = []
        skipped = 0

        for full_name in USER_NAMES:
            username = make_username(full_name)
            email = f"{username}@example.com"

            if User.objects.filter(username=username).exists():
                self.stderr.write(f"  Skipping {full_name} ({username}, already exists)")
                created_users.append(User.objects.get(username=username))
                skipped += 1
                continue

            user = User.objects.create_user(
                username=username,
                email=email,
                password=DEFAULT_PASSWORD,
                name=full_name,
            )

            EmailAddress.objects.create(
                user=user,
                email=email,
                primary=True,
                verified=True,
            )

            created_users.append(user)
            self.stderr.write(f"  Created user: {full_name} ({username})")

        # Assign users to organizations
        # Strategy:
        # 1. First pass: assign one admin per org (round-robin from user list)
        # 2. Second pass: assign remaining users to 1-3 random orgs as members
        # 3. Some users get assigned to multiple orgs

        shuffled_users = list(created_users)
        random.shuffle(shuffled_users)

        # First pass: guarantee every org has at least one admin
        admin_pool = list(shuffled_users)
        for org in orgs:
            # Check if org already has an admin membership
            if Membership.objects.filter(organization=org, admin=True).exists():
                orgs_with_admin.add(org.pk)
                continue

            if not admin_pool:
                # Recycle from the full list if we run out
                admin_pool = list(shuffled_users)
                random.shuffle(admin_pool)

            admin_user = admin_pool.pop(0)

            if not Membership.objects.filter(
                user=admin_user, organization=org
            ).exists():
                Membership.objects.create(
                    user=admin_user, organization=org, admin=True
                )
                orgs_with_admin.add(org.pk)
                self.stderr.write(
                    f"    Admin: {admin_user.name} -> {org.name}"
                )

        # Second pass: assign each user to 1-3 random orgs as members
        for user in created_users:
            num_orgs = random.choices([1, 2, 3], weights=[50, 35, 15])[0]
            target_orgs = random.sample(orgs, min(num_orgs, len(orgs)))

            for org in target_orgs:
                if Membership.objects.filter(user=user, organization=org).exists():
                    continue

                Membership.objects.create(
                    user=user, organization=org, admin=False
                )
                self.stderr.write(
                    f"    Member: {user.name} -> {org.name}"
                )

        # Summary
        total_memberships = Membership.objects.filter(
            organization__slug__in=org_slugs
        ).count()
        admin_count = Membership.objects.filter(
            organization__slug__in=org_slugs, admin=True
        ).count()
        orgs_without_admin = (
            Organization.objects.filter(slug__in=org_slugs)
            .exclude(memberships__admin=True)
            .count()
        )

        self.stderr.write(
            self.style.SUCCESS(
                f"\nDone: {len(created_users) - skipped} users created, "
                f"{skipped} skipped\n"
                f"Total memberships: {total_memberships} "
                f"({admin_count} admins)\n"
                f"Orgs without admin: {orgs_without_admin}"
            )
        )
