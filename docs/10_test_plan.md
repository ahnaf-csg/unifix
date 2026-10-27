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

## 2. Coverage by Rule (Sprints 1 and 2)

| Rule / feature | Test cases |
|---|---|
| C-01 email login, custom User | TC-01, TC-15 |
| C-16 Django admin access (Super Admin only); complaints read-only (Sprint 2) | TC-02, TC-61 |
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
| Seed data (`05` §7) | TC-23 to TC-25, TC-49 |
| *Sprint 2:* C-02 submission and C-04 routing | TC-36, TC-37, TC-40, TC-53 |
| VR-07 file type, content, size, count; files kept intact and cleaned up | TC-38, TC-47, TC-48, TC-54 |
| VR-08 required attachment | TC-39, TC-54 |
| Duplicate rule and two-step S-02 (`03` §6) | TC-41, TC-50 to TC-53 |
| C-03 Me too, VR-09 | TC-42, TC-43, TC-55 |
| VR-01 limited view, actor names, 404; VR-02 groundwork | TC-45, TC-46, TC-52, TC-56, TC-57 |
| NFR-03 private files | TC-58 |
| Computed values (`03` §5) | TC-44 |
| S-01, S-03 (and VR-14 groundwork) | TC-59, TC-60 |
| *Sprint 3:* CR-13 optional gender, avatars; VR-16 | TC-62, TC-63 |
| Workflow methods, history and notifications (`03` §4) | TC-64, TC-68 to TC-73 |
| VR-02 own department; Super Admin on any department | TC-66 |
| VR-03 allowed transitions | TC-65 |
| VR-04 (reject reason, resolve note) | TC-68 |
| VR-05 priority and future due date | TC-67 |
| C-07 proof photo, file clean-up | TC-69, TC-70 |
| `allowed_actions(user)` and hints, `can_add_note()` | TC-74 |
| C-11 notifications list, mark all read, bell count; S-01 latest notifications | TC-75, TC-76 |
| C-10 Withdraw on S-04 | TC-77 |
| A-02 queue: VR-02 scope, filters, search, sort, overdue flag | TC-78 |
| A-03: VR-02 access, VR-16 neutral avatar, history; action bar; actions by POST; console files (NFR-03) | TC-79 to TC-82 |

## 3. Test Cases

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

### Sprint 2

| ID | File | Checks | Expected |
|---|---|---|---|
| TC-36 | `complaints/tests.py` | Submit two complaints | Tracking IDs are `UF-` + zero-padded primary key |
| TC-37 | `complaints/tests.py` | Submit with a JPG and a PDF (C-02, C-04) | Status `submitted`; department from the category; one `submitted` history row; two attachments with detected types and random names under `complaints/<tracking_id>/`; only that department's admin notified |
| TC-38 | `complaints/tests.py` | Files: `.gif`, a PDF renamed `.jpg`, 15 MB + 1 byte, 6 files, one bad file in a batch (VR-07) | Each refused with a message; nothing saved |
| TC-39 | `complaints/tests.py` | Category with `requires_attachment` and no file; with a file; category without the flag (VR-08) | Refused; accepted; accepted |
| TC-40 | `complaints/tests.py` | Submit as a Dept Admin; submit to an inactive category | Both refused |
| TC-41 | `complaints/tests.py` | `find_duplicates()` with rooms "L 3"/"l3", another room, building, category, a closed match and a blank room (`03` §6) | Only open matches with the same category, building and normalised room; a blank room matches on building |
| TC-42 | `complaints/tests.py` | Another student presses Me too (C-03) | `Support` row, `support` history row, `updated_at` bumped; students affected = 2 |
| TC-43 | `complaints/tests.py` | Me too on own complaint, twice, as an admin, on a rejected complaint (VR-09) | All refused; one supporter |
| TC-44 | `complaints/tests.py` | `location`, `status_badge_class`, `is_overdue` per status, `can_reopen` at 7 and 8 days (`03` §5) | "NAC 512"; `badge-under-review`; overdue only for verified, in progress, reopened; reopen allowed up to 7 days |
| TC-45 | `complaints/tests.py` | `can_view_complaint()` for reporter, supporter, stranger, own-department admin, other admin, Super Admin (VR-01, VR-02) | True, True, False, True, False, True |
| TC-46 | `complaints/tests.py` | `get_complaint_for_user()` and `has_full_view()` | 404 for a stranger, another department and an unknown ID; full view for the reporter and own-department admin, not for a supporter |
| TC-47 | `complaints/tests.py` | Run the VR-07 check twice on a file, then submit it | Stored bytes equal the uploaded bytes (the check rewinds the file) |
| TC-48 | `complaints/tests.py` | Submit with two files and force an error after they are written | No complaint in the database and no new files on disk |
| TC-49 | `complaints/tests.py` | Run `seed_demo`, then again (`05` §7) | Complaints in all 9 statuses, an overdue and a reopened one, supporters; each history starts with `submitted` at `created_at`, is in time order and ends at the current status; VR-08 holds; the second run adds no complaints, files or notifications |
| TC-50 | `complaints/tests.py` | Open S-02 step 1 with one category deactivated | Categories grouped by department (`<optgroup>`); the inactive one is missing; "Check for similar issues" |
| TC-51 | `complaints/tests.py` | Check a location with no open matches | Step 2 opens with the location as hidden fields and a Change link; nothing saved |
| TC-52 | `complaints/tests.py` | Check a location with matches: another student's, own (room "5 12" vs "512"), one already supported | Me too only on the other student's; "You reported this", "You support this"; no description or reporter name (VR-01); Continue link |
| TC-53 | `complaints/tests.py` | Submit step 2 while an open match exists | Complaint created and S-04 opens; the duplicate check is not repeated |
| TC-54 | `complaints/tests.py` | Submit with a renamed PDF, 6 files, no file for a required category, a category deactivated between the steps | Form errors (VR-07, VR-08); back to step 1 for the deactivated category; nothing saved |
| TC-55 | `complaints/tests.py` | Me too by GET, by POST, twice, on own complaint; post an unbuilt action | 405; supported and S-04 opens; "already support"; "your own complaint"; 404 |
| TC-56 | `complaints/tests.py` | Reporter opens S-04 with a public and an internal note | Description, file link and public note shown; internal note hidden; admin shown as "IT Services"; no person's name |
| TC-57 | `complaints/tests.py` | Supporter, stranger and Dept Admin open S-04 | Limited view (no description, files or reporter name; "Reporter" label); 404; 403 |
| TC-58 | `complaints/tests.py` | Open a file as reporter, supporter, stranger, signed out; open its `/media/` path | 200 with the right type and bytes; 404; 404; login redirect; 404 (NFR-03) |
| TC-59 | `complaints/tests.py` | S-03 with own, supported and someone else's complaints; status filter; search by room and tracking ID | Own and supported (labelled) only; filter and `?q=` work; another student's ID finds nothing (VR-14) |
| TC-60 | `complaints/tests.py` | S-01 with one open, one resolved and one supported complaint | Cards 1, 1, 0, 1; recent complaints; New complaint and My complaints links enabled |
| TC-61 | `complaints/tests.py` | Super Admin opens a complaint and the complaint list in `/django-admin/` (C-16, I-53) | 200; attachment shown as text; no Save or Delete button; a delete POST is refused (403) |

### Sprint 3

| ID | File | Checks | Expected |
|---|---|---|---|
| TC-62 | `accounts/tests.py` | Register without and with gender; change it on the profile (CR-13) | Default `prefer_not_to_say`; `female` stored and own avatar shown in top bar and profile; `other` → neutral avatar |
| TC-63 | `accounts/tests.py` | Super Admin opens the user list and a user in `/django-admin/` (VR-16) | 200; no gender anywhere |
| TC-64 | `complaints/tests.py` | Start review → Verify → Start work → Resolve (C-05 to C-08) | Status, priority, due date, `verified_at`, `resolved_at` set; one history row each with from/to status and note; reporter gets "UF-… is now <status>", and on resolve "UF-… was resolved. Please confirm or reopen by <date>" (`03` §4); the acting admin gets nothing |
| TC-65 | `complaints/tests.py` | Every action from every status (VR-03) | Only the `03` §2 transitions succeed; others raise an error and write nothing |
| TC-66 | `complaints/tests.py` | Other department's admin, reporter and stranger act; Super Admin acts (VR-02, C-13) | Refused (actions and notes); Super Admin allowed on any department |
| TC-67 | `complaints/tests.py` | Verify with a bad priority, no due date, today, yesterday; then tomorrow (VR-05) | Refused; accepted |
| TC-68 | `complaints/tests.py` | Reject with a blank reason, then with one; resolve with a blank note (VR-04) | Refused; rejected with the trimmed reason; reporter gets "UF-… was rejected: <reason>", a long reason shortened with "…" to 255 characters while history keeps it in full; refused |
| TC-69 | `complaints/tests.py` | Resolve with a PDF, a PDF renamed `.jpg`, an MP4, then a JPG, on a complaint with 5 evidence files (C-07) | Refused; the JPG is stored as `proof_of_fix` by the admin under `complaints/<tracking_id>/` |
| TC-70 | `complaints/tests.py` | Resolve with a photo while notifications fail | Status, `resolved_at` and history unchanged; no attachment row; no new file on disk |
| TC-71 | `complaints/tests.py` | Start work on a reopened complaint past its due date (`03` §7) | In progress; due date kept; still overdue |
| TC-72 | `complaints/tests.py` | Withdraw by another student, admin, Super Admin, then the reporter; withdraw while Under review (C-10) | Refused; withdrawn, history row, only the active department admin notified; refused |
| TC-73 | `complaints/tests.py` | Public and internal note on a Resolved complaint; blank note; note on Closed, Rejected, Withdrawn | Both stored with `is_internal`; only the public note notifies the reporter; refused |
| TC-74 | `complaints/tests.py` | `allowed_actions()` on each status, for own admin, Super Admin, other admin, student; `can_add_note()` | Enabled buttons match `03` §2; hints "Available after …", "Done", "Not available: complaint is …"; empty for others |
| TC-75 | `complaints/tests.py` | Reporter and IT admin open S-05/A-06; mark all read by GET, then POST | Own notifications only, newest first, links to S-04 (student) or A-03 (admin), unread highlighted; bell "2 unread"; opening reads nothing; GET 405; POST marks only own as read |
| TC-76 | `complaints/tests.py` | S-01 with six notifications | The 5 newest, with a link to S-05 |
| TC-77 | `complaints/tests.py` | Withdraw on S-04 as supporter, stranger, reporter (GET and POST); a complaint under review | No button and refused; 404; 405 then withdrawn with a message and no button; no button |
| TC-78 | `complaints/tests.py` | A-02 as IT admin, FAC admin, Super Admin with each filter, search and sort; as a student | Open complaints of the own department by default, soonest due first, no due date last; filters, `?q=` (name, email) and `department` (Super Admin only) work; overdue row flagged; another department's ID finds nothing; student 403 |
| TC-79 | `complaints/tests.py` | A-03 for own admin, other admin, student, Super Admin; reporter with gender female | 200, 404, 403, 200; reporter card with counts, neutral avatar, no gender, disabled A-05 link; history with names, Me too grouped, internal note marked |
| TC-80 | `complaints/tests.py` | Action bar on Submitted, Under review, Closed | Start review as a plain button; forms only for enabled actions; hints; all five "Not available" and no Add note on Closed |
| TC-81 | `complaints/tests.py` | POST each action as own admin; other admin; `reassign`; GET; verify while Submitted; bad due date; blank reason; PDF proof; valid resolve with photo; internal note | Redirect to A-03 with a message; 404; 404; 405; 400 with the error shown; 400 with the form open; 400; 400; resolved with a `console:attachment` link; internal note stored |
| TC-82 | `complaints/tests.py` | Open an evidence file through `console:attachment` as own admin, Super Admin, other admin, student | 200 with the bytes and `Cache-Control: private`; 200; 404; 403 |

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
8. Super Admin only: `/django-admin/` opens and lists users, departments and categories (and, from Sprint 2, read-only complaints and notifications).

From Sprint 2, as a student (`rafiq.hasan@northsouth.edu`):

9. S-01 cards and recent complaints match the seed; New complaint and My complaints are enabled in the sidebar.
10. S-02: Projector & AV, NAC, 512 → a match with Me too; Air conditioning, SAC, 304 → "You reported this". Continue → step 2 shows the location read-only with Change. A PDF renamed `.jpg` is refused with the text kept; a valid file submits and opens S-04.
11. Me too on a match → the limited view (no description, files or names; "Reporter" and department labels).
12. S-03: status filter and search by tracking ID, title or room.
13. Open another student's complaint by URL (e.g. `UF-0008`) → 404. Open a file's `/media/...` path → 404.
14. Repeat 9–12 at 375 px: no sideways page scroll; tables scroll inside their cards.

## 5. Planned for Later Sprints

| Sprint | Rules to cover |
|---|---|
| 2 | VR-01 (limited view, role/department actor names, 404 for others, private files), VR-07 (type, content match, 15 MB, 5 files), VR-08, VR-09 (own, twice, not open), duplicate rule and two-step S-02 (`03` §6), C-04 routing, `submit()` history and notifications, `can_view_complaint()`, S-01 and S-03 lists and filters, Sprint 2 seed data. Test cases TC-36 onwards are added here with the code. |
| 3 | VR-02, VR-03, VR-04 (reject reason, resolve note), VR-05, VR-16; workflow methods and their history and notifications (`03` §4), `allowed_actions(user)`, A-02 filters and search, A-03 action bar, console files, notifications list and bell, S-04 Withdraw, seed on the real methods. Test cases TC-62 onwards are added here with the code. |
| 4 | VR-04 (reopen reason), VR-06, VR-10, VR-12, VR-14 |
