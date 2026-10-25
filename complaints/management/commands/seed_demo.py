"""Demo data for development and demos (docs/05 §7).

    python manage.py seed_demo

Safe to run again: records are matched by department code, category name and
email, and complaints by reporter and title, so nothing is duplicated; demo
passwords are reset each run.

Sprint 1 seeds departments, categories and accounts. Sprint 2 adds complaints
in every status (docs/05 §7). Each one is created with Complaint.submit(), so
files, history and notifications are real; the later steps are written to
match docs/03 §4, because the Sprint 3 action methods do not exist yet. All
times are counted back from today, so overdue examples stay overdue.
"""

import struct
import zlib
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from complaints.models import Category, Complaint, ComplaintUpdate, Department, Support
from notifications.models import Notification

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

# Demo complaints (Sprint 2), one dict each:
#   reporter (email prefix), category, building, room, title, description,
#   files: sample files to attach ("photo" or "pdf"),
#   steps: (action, days ago, actor, note, extra) after the submission, where
#          actor is "admin" (the department's admin), "super" or "reporter",
#          and extra holds verify's priority and due date (days from today),
#   supporters: (email prefix, days ago).
# Between them they show every status, an overdue and a reopened complaint,
# and duplicate matches for the S-02 demo (NAC 512 projector, SAC 304 AC).
COMPLAINTS = [
    {
        "reporter": "rafiq.hasan", "category": "Projector & AV", "building": "nac", "room": "512",
        "title": "Projector shows no signal",
        "description": "The projector in NAC 512 shows 'No signal' with every laptop. The HDMI cable looks damaged near the plug.",
        "submitted": 9, "files": ["photo"],
        "steps": [
            ("start_review", 8.8, "admin", "", {}),
            ("verify", 8.5, "admin", "", {"priority": "high", "due": 2}),
            ("start_work", 6, "admin", "Replacing the HDMI cable and checking the input board.", {}),
            ("resolve", 1, "admin", "HDMI cable replaced and tested with two laptops.", {}),
        ],
        "supporters": [("ayesha.rahman", 8), ("tahmid.islam", 7)],
    },
    {
        "reporter": "rafiq.hasan", "category": "Air conditioning", "building": "sac", "room": "304",
        "title": "AC leaking water onto desks",
        "description": "Water has been dripping from the AC unit above the back row since Monday. Desks underneath are wet.",
        "submitted": 12, "files": ["photo"],
        "steps": [
            ("start_review", 11.8, "admin", "", {}),
            ("verify", 11.5, "admin", "", {"priority": "high", "due": -2}),
            ("start_work", 9, "admin", "Technician booked; drain pipe needs a replacement part.", {}),
        ],
        "supporters": [("nabila.chowdhury", 11), ("sakib.hossain", 10), ("mithila.das", 9)],
    },
    {
        "reporter": "rafiq.hasan", "category": "Furniture", "building": "nac", "room": "208",
        "title": "Broken chair armrest",
        "description": "The armrest of the third chair in the front row is loose and has a sharp edge.",
        "submitted": 3, "files": ["photo"],
        "steps": [("start_review", 2, "admin", "", {})],
    },
    {
        "reporter": "rafiq.hasan", "category": "Network", "building": "library", "room": "L3",
        "title": "Library 3rd floor Wi-Fi drops",
        "description": "Wi-Fi on the third floor of the library disconnects every few minutes, mostly near the study carrels.",
        "submitted": 5, "files": [],
        "steps": [
            ("start_review", 4.8, "admin", "", {}),
            ("verify", 4.5, "admin", "", {"priority": "medium", "due": 4}),
            ("note", 3, "admin", "A replacement access point has been ordered.", {}),
            ("note", 2.9, "admin", "Vendor confirms delivery on Thursday.", {"internal": True}),
        ],
    },
    {
        "reporter": "rafiq.hasan", "category": "Plumbing", "building": "sac", "room": "2F washroom",
        "title": "Washroom tap not closing",
        "description": "The left tap in the second-floor men's washroom keeps running after it is closed.",
        "submitted": 20, "files": ["photo"],
        "steps": [
            ("start_review", 19.8, "admin", "", {}),
            ("verify", 19.5, "admin", "", {"priority": "low", "due": -14}),
            ("start_work", 18, "admin", "", {}),
            ("resolve", 15, "admin", "Tap cartridge replaced.", {}),
            ("close", 14, "reporter", "", {}),
        ],
    },
    {
        "reporter": "rafiq.hasan", "category": "Lab computers", "building": "nac", "room": "712",
        "title": "Lab PC 14 won't boot",
        "description": "PC 14 in the NAC 712 lab stops at a black screen after the university logo.",
        "submitted": 0.1, "files": [],
        "steps": [],
    },
    {
        "reporter": "ayesha.rahman", "category": "Electrical", "building": "nac", "room": "301",
        "title": "Flickering lights in NAC 301",
        "description": "Two tube lights near the whiteboard flicker all through class, which makes the board hard to read.",
        "submitted": 18, "files": ["photo"],
        "steps": [
            ("start_review", 17.8, "admin", "", {}),
            ("verify", 17.5, "admin", "", {"priority": "medium", "due": -3}),
            ("start_work", 15, "admin", "", {}),
            ("resolve", 10, "admin", "Replaced both starters.", {}),
            ("reopen", 8, "reporter", "Still flickering after two days.", {}),
        ],
        "supporters": [("rafiq.hasan", 16)],
    },
    {
        "reporter": "tahmid.islam", "category": "Cleanliness", "building": "plaza", "room": "",
        "title": "Litter around the plaza benches",
        "description": "Food wrappers are left around the plaza benches every afternoon.",
        "submitted": 6, "files": ["photo"],
        "steps": [
            ("start_review", 5.8, "admin", "", {}),
            ("reject", 5.5, "admin", "The plaza is cleaned on a fixed schedule; this is not a fault report.", {}),
        ],
    },
    {
        "reporter": "nabila.chowdhury", "category": "Waste & bins", "building": "sac", "room": "",
        "title": "Bins not emptied on SAC ground floor",
        "description": "The bins near the SAC ground-floor stairs were full all morning.",
        "submitted": 4, "files": [],
        "steps": [("withdraw", 3.9, "reporter", "", {})],
    },
    {
        "reporter": "sakib.hossain", "category": "Lost access card", "building": "admin_building", "room": "",
        "title": "Access card not working at the admin building",
        "description": "My access card is refused at the admin building gate since yesterday.",
        "submitted": 1, "files": [],
        "steps": [],
    },
    {
        "reporter": "mithila.das", "category": "Safety hazard", "building": "library", "room": "Stairs B",
        "title": "Loose handrail on library stairs",
        "description": "The handrail on staircase B between the first and second floor moves when you lean on it.",
        "submitted": 2, "files": ["photo", "pdf"],
        "steps": [
            ("start_review", 1.9, "admin", "", {}),
            ("verify", 1.8, "admin", "", {"priority": "high", "due": 1}),
            ("note", 1, "super", "Security has taped off the staircase until it is fixed.", {}),
        ],
        "supporters": [("rafiq.hasan", 1.5)],
    },
    {
        "reporter": "farzana.akter", "category": "Projector & AV", "building": "nac", "room": "512",
        "title": "Projector remote missing",
        "description": "The projector remote in NAC 512 is missing, so the input cannot be switched.",
        "submitted": 2, "files": [],
        "steps": [],
    },
    {
        "reporter": "zubair.ahmed", "category": "Electrical", "building": "sac", "room": "210",
        "title": "Power socket sparks",
        "description": "The wall socket next to the door sparks when a charger is plugged in.",
        "submitted": 30, "files": ["photo"],
        "steps": [
            ("start_review", 29.8, "admin", "", {}),
            ("verify", 29.5, "admin", "", {"priority": "high", "due": -27}),
            ("start_work", 29, "admin", "", {}),
            ("resolve", 28, "admin", "Socket replaced; the circuit was checked.", {}),
            ("close", 27, "reporter", "", {}),
        ],
    },
    {
        "reporter": "priya.saha", "category": "Network", "building": "nac", "room": "",
        "title": "Wi-Fi login page not loading in NAC",
        "description": "The Wi-Fi login page times out on most floors of NAC.",
        "submitted": 4, "files": [],
        "steps": [
            ("start_review", 3.8, "admin", "", {}),
            ("verify", 3.5, "admin", "", {"priority": "medium", "due": 3}),
            ("start_work", 2, "admin", "", {}),
        ],
    },
]

# action → resulting status (docs/05 action mapping); "note" keeps the status.
STEP_STATUS = {
    "start_review": Complaint.Status.UNDER_REVIEW,
    "verify": Complaint.Status.VERIFIED,
    "reject": Complaint.Status.REJECTED,
    "start_work": Complaint.Status.IN_PROGRESS,
    "resolve": Complaint.Status.RESOLVED,
    "close": Complaint.Status.CLOSED,
    "reopen": Complaint.Status.REOPENED,
    "withdraw": Complaint.Status.WITHDRAWN,
}


def sample_png(red, green, blue, width=160, height=120):
    """A small one-colour PNG, built by hand so the seed needs no image library."""

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data))

    rows = b"".join(b"\x00" + bytes([red, green, blue]) * width for _ in range(height))
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)  # 8-bit RGB
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def sample_pdf(text):
    """A one-page PDF with one line of text."""
    stream = f"BT /F1 14 Tf 72 720 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = b"%PDF-1.4\n"
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    pdf += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(objects) + 1, xref)
    return pdf


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

        created = sum(self.seed_complaint(spec) for spec in COMPLAINTS)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {Department.objects.count()} departments, {Category.objects.count()} categories, "
            f"{User.objects.count()} users and {created} new complaints "
            f"({Complaint.objects.count()} in total). Demo password: {DEMO_PASSWORD}"
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

    # --- Complaints (Sprint 2) ---------------------------------------------

    def seed_complaint(self, spec):
        """Create one demo complaint with its history; skip it if it exists. Returns 1 or 0."""
        reporter = User.objects.get(email=f"{spec['reporter']}@northsouth.edu")
        if Complaint.objects.filter(reporter=reporter, title=spec["title"]).exists():
            return 0
        now = timezone.now()
        files = [
            SimpleUploadedFile(f"photo_{number}.png", sample_png(70 + 40 * number, 110, 160))
            if kind == "photo"
            else SimpleUploadedFile(f"report_{number}.pdf", sample_pdf(spec["title"]))
            for number, kind in enumerate(spec["files"], start=1)
        ]
        complaint = Complaint.submit(
            reporter=reporter,
            category=Category.objects.get(name=spec["category"]),
            building=spec["building"],
            room=spec["room"],
            title=spec["title"],
            description=spec["description"],
            files=files,
        )
        # submit() stamped everything "now": move it back to the submission day.
        submitted_at = now - timedelta(days=spec["submitted"])
        Complaint.objects.filter(pk=complaint.pk).update(created_at=submitted_at, updated_at=submitted_at)
        complaint.updates.update(created_at=submitted_at)
        complaint.attachments.update(uploaded_at=submitted_at)
        complaint.notifications.update(created_at=submitted_at)
        complaint.refresh_from_db()

        # Steps and "Me too" presses, replayed oldest first so statuses build up in order.
        events = [(step[1], "step", step) for step in spec["steps"]]
        events += [(days, "support", email) for email, days in spec.get("supporters", [])]
        for days, kind, item in sorted(events, key=lambda event: -event[0]):  # oldest first
            when = now - timedelta(days=days)
            if kind == "support":
                self.add_support(complaint, item, when)
            else:
                self.add_step(complaint, item, when)
        return 1

    def add_support(self, complaint, email_prefix, when):
        student = User.objects.get(email=f"{email_prefix}@northsouth.edu")
        support = Support.objects.create(complaint=complaint, student=student)
        Support.objects.filter(pk=support.pk).update(created_at=when)
        update = complaint.updates.create(
            actor=student,
            action=ComplaintUpdate.Action.SUPPORT,
            from_status=complaint.status,
            to_status=complaint.status,
        )
        ComplaintUpdate.objects.filter(pk=update.pk).update(created_at=when)
        Complaint.objects.filter(pk=complaint.pk).update(updated_at=when)

    def add_step(self, complaint, step, when):
        """Write one workflow step as docs/03 §4 describes it (Sprint 3 replaces this with the real methods)."""
        action, _, actor_key, note, extra = step
        actor = {
            "admin": User.objects.filter(role=User.Role.DEPT_ADMIN, department=complaint.department).first(),
            "super": User.objects.get(role=User.Role.SUPER_ADMIN, email=SUPER_ADMIN[0]),
            "reporter": complaint.reporter,
        }[actor_key]
        from_status = complaint.status
        to_status = STEP_STATUS.get(action, from_status)
        complaint.status = to_status
        if action == "verify":
            complaint.priority = extra["priority"]
            complaint.due_date = timezone.localdate() + timedelta(days=extra["due"])
            complaint.verified_at = when
        elif action == "resolve":
            complaint.resolved_at = when
        elif action == "close":
            complaint.closed_at = when
        elif action == "reopen":
            complaint.reopen_count += 1
        Complaint.objects.filter(pk=complaint.pk).update(
            status=complaint.status,
            priority=complaint.priority,
            due_date=complaint.due_date,
            verified_at=complaint.verified_at,
            resolved_at=complaint.resolved_at,
            closed_at=complaint.closed_at,
            reopen_count=complaint.reopen_count,
            updated_at=when,
        )
        is_internal = extra.get("internal", False)
        update = complaint.updates.create(
            actor=actor,
            action=action,
            from_status=from_status,
            to_status=to_status,
            note=note,
            is_internal=is_internal,
        )
        ComplaintUpdate.objects.filter(pk=update.pk).update(created_at=when)

        # Notifications as in docs/03 §4.
        tracking_id = complaint.tracking_id
        if action in ("start_review", "verify", "reject", "start_work", "resolve"):
            self.notify([complaint.reporter], complaint, Notification.Event.STATUS_CHANGED,
                        f"{tracking_id} is now {complaint.get_status_display()}", when)
        elif action == "note" and not is_internal:
            self.notify([complaint.reporter], complaint, Notification.Event.NOTE_ADDED,
                        f"New note on {tracking_id}", when)
        elif action in ("close", "reopen"):
            admins = User.objects.filter(role=User.Role.DEPT_ADMIN, department=complaint.department)
            if action == "close":
                self.notify(admins, complaint, Notification.Event.STATUS_CHANGED,
                            f"{tracking_id} was closed by the student", when)
            else:
                self.notify(admins, complaint, Notification.Event.REOPENED, f"{tracking_id} was reopened", when)

    def notify(self, recipients, complaint, event, message, when):
        for recipient in recipients:
            notification = Notification.objects.create(
                recipient=recipient, complaint=complaint, event=event, message=message
            )
            Notification.objects.filter(pk=notification.pk).update(created_at=when)
