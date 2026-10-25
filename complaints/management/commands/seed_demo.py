"""Demo data for development and demos (docs/05 §7).

    python manage.py seed_demo

Safe to run again: records are matched by department code, category name and
email, so nothing is duplicated, and demo passwords are reset each run.

Sprint 1 seeds departments, categories and accounts. Complaints in every status
are added in Sprints 2 and 3, as their models and actions are built.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from complaints.models import Category, Department

# One shared password for every demo account (local development only).
DEMO_PASSWORD = "unifix-demo-2026"

# (code, name, [(category name, requires_attachment), ...])  docs/05 §7
DEPARTMENTS = [
    ("FAC", "Facilities Management", [
        ("Air conditioning", True), ("Electrical", True), ("Furniture", True), ("Plumbing", True),
    ]),
    ("IT", "IT Services", [
        ("Projector & AV", False), ("Network", False), ("Lab computers", False),
    ]),
    ("HK", "Housekeeping", [
        ("Cleanliness", True), ("Waste & bins", False),
    ]),
    ("SEC", "Security", [
        ("Lost access card", False), ("Safety hazard", True),
    ]),
]

SUPER_ADMIN = ("superadmin@northsouth.edu", "Tanvir Ahmed")

# (department code, email, full name)
DEPT_ADMINS = [
    ("FAC", "fac.admin@northsouth.edu", "Nusrat Karim"),
    ("IT", "it.admin@northsouth.edu", "Farhan Kabir"),
    ("HK", "hk.admin@northsouth.edu", "Shirin Akter"),
    ("SEC", "sec.admin@northsouth.edu", "Imran Hossain"),
]

# (email, full name, student ID)
STUDENTS = [
    ("rafiq.hasan@northsouth.edu", "Rafiq Hasan", "2112345642"),
    ("ayesha.rahman@northsouth.edu", "Ayesha Rahman", "2113456042"),
    ("tahmid.islam@northsouth.edu", "Tahmid Islam", "2121234042"),
    ("nabila.chowdhury@northsouth.edu", "Nabila Chowdhury", "2122345042"),
    ("sakib.hossain@northsouth.edu", "Sakib Hossain", "2131234642"),
    ("mithila.das@northsouth.edu", "Mithila Das", "2132345642"),
    ("arif.mahmud@northsouth.edu", "Arif Mahmud", "2211234042"),
    ("farzana.akter@northsouth.edu", "Farzana Akter", "2212345042"),
    ("zubair.ahmed@northsouth.edu", "Zubair Ahmed", "2221234642"),
    ("priya.saha@northsouth.edu", "Priya Saha", "2222345642"),
]


class Command(BaseCommand):
    help = "Create or update demo departments, categories and user accounts."

    @transaction.atomic
    def handle(self, *args, **options):
        departments = {}
        for code, name, categories in DEPARTMENTS:
            department, _ = Department.objects.update_or_create(
                code=code, defaults={"name": name, "is_active": True}
            )
            departments[code] = department
            for category_name, requires_attachment in categories:
                Category.objects.update_or_create(
                    department=department,
                    name=category_name,
                    defaults={"requires_attachment": requires_attachment, "is_active": True},
                )

        email, full_name = SUPER_ADMIN
        self.make_user(email, full_name, User.Role.SUPER_ADMIN)
        for code, email, full_name in DEPT_ADMINS:
            self.make_user(email, full_name, User.Role.DEPT_ADMIN, department=departments[code])
        for email, full_name, student_id in STUDENTS:
            self.make_user(email, full_name, User.Role.STUDENT, student_id=student_id)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Department.objects.count()} departments, {Category.objects.count()} categories "
            f"and {User.objects.count()} users. Demo password: {DEMO_PASSWORD}"
        ))

    def make_user(self, email, full_name, role, department=None, student_id=None):
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={
                "full_name": full_name,
                "role": role,
                "department": department,
                "student_id": student_id,
                "account_state": User.AccountState.ACTIVE,
            },
        )
        user.set_password(DEMO_PASSWORD)
        user.save()
        return user
