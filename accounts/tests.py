"""Tests for accounts (Sprint 1). Test case IDs match docs/10_test_plan.md."""

from django.test import TestCase
from django.urls import reverse

from complaints.models import Department

from .models import User

PASSWORD = "Campus-Pass-77"


def login_data(user_or_email, password=PASSWORD, login_type=None):
    """POST data for the login form; picks the matching tab unless told otherwise."""
    email = getattr(user_or_email, "email", user_or_email)
    if login_type is None:
        user = User.objects.filter(email=email.lower()).first()
        login_type = "student" if user is None or user.is_student() else "staff"
    return {"login_type": login_type, "username": email, "password": password}


def make_user(email, role=User.Role.STUDENT, **extra):
    if role == User.Role.STUDENT:
        extra.setdefault("student_id", email.split("@")[0])
    return User.objects.create_user(email, PASSWORD, full_name="Test User", role=role, **extra)


class UserModelTests(TestCase):
    """TC-01 to TC-04: rules on the User model (docs/05 §3)."""

    def setUp(self):
        self.department = Department.objects.create(name="IT Services", code="IT")

    def test_tc01_email_is_login_and_stored_in_lower_case(self):
        user = make_user("Mixed.Case@NorthSouth.edu")
        self.assertEqual(user.email, "mixed.case@northsouth.edu")
        self.assertEqual(User.USERNAME_FIELD, "email")
        field_names = [field.name for field in User._meta.get_fields()]
        for removed in ["username", "first_name", "last_name"]:
            self.assertNotIn(removed, field_names)

    def test_tc02_only_super_admin_gets_django_admin_flags(self):
        admin = make_user("admin@northsouth.edu", User.Role.DEPT_ADMIN, department=self.department)
        boss = make_user("boss@northsouth.edu", User.Role.SUPER_ADMIN)
        self.assertFalse(admin.is_staff or admin.is_superuser)
        self.assertTrue(boss.is_staff and boss.is_superuser)

    def test_tc03_blank_student_id_is_stored_as_null(self):
        a = make_user("a@northsouth.edu", User.Role.SUPER_ADMIN, student_id="")
        b = make_user("b@northsouth.edu", User.Role.DEPT_ADMIN, department=self.department, student_id="")
        self.assertIsNone(a.student_id)
        self.assertIsNone(b.student_id)  # two NULLs do not break the unique rule

    def test_tc04_suspend_reactivate_and_soft_delete_keep_is_active_in_sync(self):
        user = make_user("s@northsouth.edu")
        user.suspend()
        self.assertEqual((user.account_state, user.is_active), ("suspended", False))
        user.reactivate()
        self.assertEqual((user.account_state, user.is_active), ("active", True))
        user.soft_delete()
        self.assertEqual((user.account_state, user.is_active), ("deleted", False))
        self.assertTrue(User.objects.filter(pk=user.pk).exists())  # soft delete keeps the row


class InactiveAccountTests(TestCase):
    """VR-11: suspended and deleted accounts cannot log in (TC-05 to TC-07)."""

    def login(self, email):
        return self.client.post(reverse("accounts:login"), login_data(email))

    def test_tc05_suspended_account_sees_account_inactive(self):
        make_user("s@northsouth.edu").suspend()
        response = self.login("s@northsouth.edu")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Account inactive")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_tc06_deleted_account_sees_account_inactive(self):
        make_user("d@northsouth.edu").soft_delete()
        response = self.login("d@northsouth.edu")
        self.assertContains(response, "Account inactive")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_tc07_account_suspended_while_signed_in_is_signed_out(self):
        user = make_user("s@northsouth.edu")
        self.client.force_login(user)
        user.suspend()
        response = self.client.get(reverse("student:home"), follow=True)
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertContains(response, "Account inactive")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_tc08_wrong_password_shows_generic_error(self):
        make_user("s@northsouth.edu")
        response = self.client.post(
            reverse("accounts:login"), login_data("s@northsouth.edu", password="wrong")
        )
        self.assertNotContains(response, "Account inactive")
        self.assertNotIn("_auth_user_id", self.client.session)


class RegistrationTests(TestCase):
    """VR-13: registration needs an unused @northsouth.edu email (TC-09 to TC-13)."""

    def register(self, **overrides):
        data = {
            "full_name": "New Student",
            "student_id": "2311111042",
            "email": "new.student@northsouth.edu",
            "phone": "",
            "password1": PASSWORD,
            "password2": PASSWORD,
        }
        data.update(overrides)
        return self.client.post(reverse("accounts:register"), data)

    def test_tc09_valid_registration_creates_signed_in_student(self):
        response = self.register()
        self.assertRedirects(response, reverse("student:home"))
        user = User.objects.get(email="new.student@northsouth.edu")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_tc10_non_nsu_email_is_rejected(self):
        response = self.register(email="someone@gmail.com")
        self.assertContains(response, "Use your @northsouth.edu email address.")
        self.assertFalse(User.objects.exists())

    def test_tc11_lookalike_domain_is_rejected(self):
        self.register(email="someone@northsouth.edu.fake.com")
        self.assertFalse(User.objects.exists())

    def test_tc12_registered_email_is_rejected_in_any_case(self):
        make_user("taken@northsouth.edu")
        response = self.register(email="TAKEN@northsouth.edu")
        self.assertContains(response, "An account with this email already exists.")
        self.assertEqual(User.objects.count(), 1)

    def test_tc13_student_id_is_required_and_unique(self):
        self.register(student_id="")
        self.assertFalse(User.objects.exists())
        make_user("first@northsouth.edu", student_id="2311111042")
        self.register()
        self.assertEqual(User.objects.count(), 1)

    def test_tc14_registration_cannot_create_an_admin(self):
        self.register(role=User.Role.SUPER_ADMIN)
        self.assertEqual(User.objects.get().role, User.Role.STUDENT)


class RoleRedirectTests(TestCase):
    """P-01 role redirect and server-side role checks (TC-15 to TC-19)."""

    def setUp(self):
        department = Department.objects.create(name="Facilities Management", code="FAC")
        self.student = make_user("student@northsouth.edu")
        self.dept_admin = make_user("fac@northsouth.edu", User.Role.DEPT_ADMIN, department=department)
        self.super_admin = make_user("boss@northsouth.edu", User.Role.SUPER_ADMIN)

    def login(self, user):
        return self.client.post(reverse("accounts:login"), login_data(user))

    def test_tc15_each_role_lands_on_its_home(self):
        cases = [
            (self.student, "student:home"),
            (self.dept_admin, "console:dashboard"),
            (self.super_admin, "console:dashboard"),
        ]
        for user, home in cases:
            with self.subTest(role=user.role):
                self.assertRedirects(self.login(user), reverse(home))
                self.client.logout()

    def test_tc16_signed_in_user_visiting_login_goes_home(self):
        self.client.force_login(self.dept_admin)
        self.assertRedirects(self.client.get(reverse("accounts:login")), reverse("console:dashboard"))

    def test_tc17_anonymous_user_is_sent_to_login(self):
        for name in ["student:home", "console:dashboard", "accounts:profile"]:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertRedirects(response, f"{reverse('accounts:login')}?next={reverse(name)}")

    def test_tc18_wrong_role_gets_403(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("console:dashboard")).status_code, 403)
        self.client.force_login(self.dept_admin)
        self.assertEqual(self.client.get(reverse("student:home")).status_code, 403)
        self.client.force_login(self.super_admin)
        self.assertEqual(self.client.get(reverse("student:home")).status_code, 403)

    def test_tc27_root_url_sends_each_user_to_the_right_place(self):
        login = reverse("accounts:login")
        self.assertRedirects(self.client.get("/", follow=True), login)
        cases = [
            (self.student, "student:home"),
            (self.dept_admin, "console:dashboard"),
            (self.super_admin, "console:dashboard"),
        ]
        for user, home in cases:
            with self.subTest(role=user.role):
                self.client.force_login(user)
                self.assertRedirects(self.client.get("/", follow=True), reverse(home))

    def test_tc19_logout_needs_post_and_signs_out(self):
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(reverse("accounts:logout")).status_code, 405)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class ProfileTests(TestCase):
    """C-15: edit name and phone, change password (TC-20 to TC-22)."""

    def setUp(self):
        self.user = make_user("student@northsouth.edu")
        self.client.force_login(self.user)

    def test_tc20_profile_saves_name_and_phone_only(self):
        response = self.client.post(
            reverse("accounts:profile"),
            {"full_name": "Renamed", "phone": "01700000000", "email": "other@northsouth.edu"},
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual((self.user.full_name, self.user.phone), ("Renamed", "01700000000"))
        self.assertEqual(self.user.email, "student@northsouth.edu")

    def test_tc21_password_change_keeps_user_signed_in(self):
        new = "Another-Pass-88"
        response = self.client.post(
            reverse("accounts:password_change"),
            {"old_password": PASSWORD, "new_password1": new, "new_password2": new},
        )
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new))
        self.assertEqual(self.client.get(reverse("accounts:profile")).status_code, 200)

    def test_tc26_failed_profile_save_keeps_saved_name_in_top_bar(self):
        # A valid new name with an invalid phone (over 20 characters): the save fails.
        response = self.client.post(
            reverse("accounts:profile"), {"full_name": "Unsaved Name", "phone": "1" * 25}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user"].full_name, "Test User")  # top bar
        self.assertContains(response, "at most 20 characters")
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Test User")

    def test_tc22_wrong_old_password_is_rejected(self):
        response = self.client.post(
            reverse("accounts:password_change"),
            {"old_password": "wrong", "new_password1": "Another-Pass-88", "new_password2": "Another-Pass-88"},
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(PASSWORD))


class LoginTypeTests(TestCase):
    """VR-15: the Student/Staff tab must match the account role (TC-30 to TC-34)."""

    def setUp(self):
        department = Department.objects.create(name="Security", code="SEC")
        self.student = make_user("student@northsouth.edu")
        self.dept_admin = make_user("sec@northsouth.edu", User.Role.DEPT_ADMIN, department=department)
        self.super_admin = make_user("boss@northsouth.edu", User.Role.SUPER_ADMIN)

    def post(self, user, login_type):
        return self.client.post(reverse("accounts:login"), login_data(user, login_type=login_type))

    def assert_refused(self, response, message):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, message)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_tc30_login_page_has_both_tabs_student_by_default(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(
            response,
            '<input type="radio" name="login_type" value="student" id="id_login_type_0" required checked>',
            html=True,
        )
        self.assertContains(response, "Use your @northsouth.edu student email.")
        self.assertContains(response, "For department coordinators and administrators.")
        self.assertContains(response, "Staff accounts are created by the Super Admin.")
        self.assertContains(response, reverse("accounts:register"))

    def test_tc31_student_on_staff_tab_is_refused(self):
        self.assert_refused(
            self.post(self.student, "staff"), "This is a student account. Please use the Student tab."
        )

    def test_tc32_staff_on_student_tab_is_refused(self):
        for user in [self.dept_admin, self.super_admin]:
            with self.subTest(role=user.role):
                self.assert_refused(
                    self.post(user, "student"), "This is a staff account. Please use the Staff tab."
                )

    def test_tc33_inactive_account_on_wrong_tab_sees_account_inactive_first(self):
        self.student.suspend()
        self.dept_admin.soft_delete()
        for user, wrong_tab in [(self.student, "staff"), (self.dept_admin, "student")]:
            with self.subTest(role=user.role):
                response = self.post(user, wrong_tab)
                self.assert_refused(response, "Account inactive")
                self.assertNotContains(response, "Please use the")

    def test_tc34_missing_or_unknown_login_type_is_refused(self):
        for login_type in ["", "admin"]:
            with self.subTest(login_type=login_type):
                response = self.post(self.student, login_type)
                self.assertEqual(response.status_code, 200)
                self.assertNotIn("_auth_user_id", self.client.session)


class ErrorPageTests(TestCase):
    """I-34: friendly error pages that use base.html (TC-28, TC-29). Tests run with DEBUG off."""

    def test_tc28_403_page_explains_and_links_home(self):
        self.client.force_login(make_user("student@northsouth.edu"))
        response = self.client.get(reverse("console:dashboard"))
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, "403.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, "Back to your home", status_code=403)

    def test_tc29_404_page_explains_and_links_home(self):
        response = self.client.get("/no-such-page/")
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, "404.html")
        self.assertContains(response, "Page not found", status_code=404)
        self.assertContains(response, 'href="/"', status_code=404)
