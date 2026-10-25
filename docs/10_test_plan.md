# 10. Test Plan

How UniFix is tested, and which automated test covers which rule. Updated every sprint.

## 1. Approach

| Level | What | How |
|---|---|---|
| Unit | Model rules (`User.save()`, `clean()`, state methods) | Django `TestCase`, no browser |
| Integration | Views, forms, permissions, redirects | Django test `Client` posting real forms |
| Command | `seed_demo` | `call_command()` |
| Manual | Every page for every role, desktop and phone width | `runserver` with seed data, checklist in §4 |

Rules:

- Every validation rule (VR-xx) has at least one automated test before its sprint is done.
- Test methods are named `test_tcNN_<what>` so failures map to this file.
- Run everything with `python manage.py test`; all tests must pass before a pull request.
- Tests use Django's fast MD5 password hasher (set in `unifix/settings.py` only when running `manage.py test`, I-33). The Sprint 1 suite runs in under a second.

## 2. Coverage by Rule (Sprint 1)

| Rule / feature | Test cases |
|---|---|
| C-01 email login, custom User | TC-01, TC-15 |
| C-16 Django admin access (Super Admin only) | TC-02 |
| `student_id` stored as NULL | TC-03 |
| VR-11 suspended and deleted accounts cannot log in | TC-04 to TC-08 |
| VR-13 registration with an unused `@northsouth.edu` email | TC-09 to TC-14 |
| P-01 role redirect; `/` routes by role | TC-15, TC-16, TC-27 |
| Server-side role checks (VR-02 groundwork) | TC-17, TC-18 |
| Logout | TC-19 |
| C-15 profile and password change | TC-20 to TC-22, TC-26 |
| Friendly 403 and 404 pages (I-34) | TC-28, TC-29 |
| VR-15 login type must match the role (CR-10) | TC-30 to TC-34 |
| P-01 email field type | TC-35 |
| Seed data (`05` §7) | TC-23 to TC-25 |

## 3. Test Cases (Sprint 1)

| ID | File | Checks | Expected |
|---|---|---|---|
| TC-01 | `accounts/tests.py` | Create a user with a mixed-case email | Stored in lower case; `email` is the login field; no `username`, `first_name`, `last_name` |
| TC-02 | `accounts/tests.py` | Create a Dept Admin and a Super Admin | Only the Super Admin has `is_staff` and `is_superuser` |
| TC-03 | `accounts/tests.py` | Two admins with a blank student ID | Both stored as NULL; no unique clash |
| TC-04 | `accounts/tests.py` | `suspend()`, `reactivate()`, `soft_delete()` | `account_state` and `is_active` change together; row is kept |
| TC-05 | `accounts/tests.py` | Log in as a suspended user (VR-11) | Page shows "Account inactive"; not signed in |
| TC-06 | `accounts/tests.py` | Log in as a deleted user (VR-11) | Page shows "Account inactive"; not signed in |
| TC-07 | `accounts/tests.py` | Suspend a user who is already signed in (VR-11) | Next request signs them out and shows "Account inactive" |
| TC-08 | `accounts/tests.py` | Wrong password | Generic error, not "Account inactive" |
| TC-09 | `accounts/tests.py` | Register with valid details (VR-13) | Student created, signed in, sent to S-01 |
| TC-10 | `accounts/tests.py` | Register with a non-NSU email (VR-13) | Error; no account |
| TC-11 | `accounts/tests.py` | Register with `@northsouth.edu.fake.com` (VR-13) | Error; no account |
| TC-12 | `accounts/tests.py` | Register an email already used, in different case (VR-13) | Error; no second account |
| TC-13 | `accounts/tests.py` | Register with a blank or duplicate student ID | Error; no account |
| TC-14 | `accounts/tests.py` | Post `role=super_admin` to the register form | Account is still a student |
| TC-15 | `accounts/tests.py` | Log in as each role (P-01) | Student → S-01; Dept Admin and Super Admin → A-01 |
| TC-16 | `accounts/tests.py` | Signed-in user opens the login page | Redirected to their home |
| TC-17 | `accounts/tests.py` | Anonymous user opens S-01, A-01, S-06 | Redirected to login with `?next=` |
| TC-18 | `accounts/tests.py` | Student opens A-01; admins open S-01 | 403 Forbidden |
| TC-19 | `accounts/tests.py` | Logout by GET, then by POST | GET refused (405); POST signs out |
| TC-20 | `accounts/tests.py` | Save the profile form with an extra `email` field (C-15) | Name and phone change; email does not |
| TC-21 | `accounts/tests.py` | Change password (C-15) | New password works; user stays signed in |
| TC-22 | `accounts/tests.py` | Change password with a wrong old password | Error; password unchanged |
| TC-23 | `complaints/tests.py` | Run `seed_demo` | 4 departments, 11 categories, 1 Super Admin, 1 Dept Admin per department, 10 students |
| TC-24 | `complaints/tests.py` | Run `seed_demo` twice | No duplicates |
| TC-25 | `complaints/tests.py` | Log in with a seeded student | Login succeeds with the demo password |
| TC-26 | `accounts/tests.py` | Save the profile with a valid new name and an invalid phone (I-31) | Error shown; the top bar still shows the saved name; nothing saved |
| TC-27 | `accounts/tests.py` | Open `/` signed out, and as each role (I-35) | Login page; student → S-01; Dept Admin and Super Admin → A-01 |
| TC-28 | `accounts/tests.py` | Student opens A-01 (I-34) | 403 with `403.html` inside `base.html` and a "Back to your home" link |
| TC-29 | `accounts/tests.py` | Open a URL that does not exist (I-34) | 404 with `404.html` and a link to `/` |
| TC-30 | `accounts/tests.py` | Open the login page (CR-10) | Student tab checked by default; both hints, the staff note and the register link are in the page |
| TC-31 | `accounts/tests.py` | Student logs in on the Staff tab (VR-15) | Refused: "This is a student account. Please use the Student tab." |
| TC-32 | `accounts/tests.py` | Dept Admin and Super Admin log in on the Student tab (VR-15) | Refused: "This is a staff account. Please use the Staff tab." |
| TC-33 | `accounts/tests.py` | Suspended student on the Staff tab; deleted admin on the Student tab (VR-11, VR-15) | "Account inactive", not the tab message |
| TC-34 | `accounts/tests.py` | Log in with a missing or unknown `login_type` | Not signed in |
| TC-35 | `accounts/tests.py` | Open the login page | The email field is `type="email"` |

## 4. Manual Checklist (each sprint)

Run `python manage.py seed_demo` and `python manage.py runserver`, then for each demo role (student, Dept Admin, Super Admin):

1. Log in on the matching tab; the correct home page opens. Log in on the wrong tab; the message names the right tab (VR-15).
   Keyboard only: Tab reaches the login type tabs, arrow keys switch them, the focused tab has an outline.
2. Every enabled sidebar link opens without an error; disabled links show the sprint they arrive in.
3. Opening another role's page gives 403.
4. Profile: save name and phone; change password; log out.
5. Top bar: NSU logo and UniFix wordmark centred together as one unit on one centre line, left zone empty, tools right. Check at 1440, 1280, 1024 and 900 px: the tools never overlap the centre group.
6. Repeat at phone width (375 px): no horizontal page scroll, search shows as an icon, sidebar scrolls sideways.
7. Error pages: open another role's page (403) and a missing URL (404). The 404 page only shows with `DEBUG=False`; run `python manage.py runserver --insecure` so the CSS still loads, then set `DEBUG=True` again.
8. Super Admin only: `/django-admin/` opens and lists users, departments and categories.

## 5. Planned for Later Sprints

| Sprint | Rules to cover |
|---|---|
| 2 | VR-01 (limited view, role/department actor names, 404 for others, private files), VR-07 (type, content match, 15 MB, 5 files), VR-08, VR-09 (own, twice, not open), duplicate rule and two-step S-02 (`03` §6), C-04 routing, `submit()` history and notifications, `can_view_complaint()`, S-01 and S-03 lists and filters, Sprint 2 seed data. Test cases TC-36 onwards are added here with the code. |
| 3 | VR-02, VR-03, VR-04, VR-05, VR-06 |
| 4 | VR-10, VR-12, VR-14 |
