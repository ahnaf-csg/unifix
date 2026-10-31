# 11. User Stories

User stories for the three roles, with acceptance criteria linked to the rules in `02_requirements.md` (VR-xx), the use cases in `06_diagram_blueprint.md` (UC-xx) and the screens in `04_screens.md`. Names follow `05_data_dictionary.md`.

**Format.** *As a <role>, I want <goal>, so that <benefit>.* Each acceptance criterion (AC) is a checkable statement; a criterion that enforces a rule names it. Stable IDs `US-xx` follow the rule in `00_README.md` §3: never reused, removed stories are marked *(removed)*.

**Status.** `v0.2` = built in Sprint 1, `v0.3` = Sprint 2, `v0.4` = Sprint 3 (tags on `main`). `S4` / `S5` = planned for Sprint 4 / Sprint 5. *Partial* = some criteria built, the rest planned (named in the story).

**Scope.** Core features only (C-01 to C-18). Optional features (OP-xx) get stories when they are picked for a sprint.

## 1. Story-to-Sprint Map

| ID | Role | Story (short) | Feature | Use case | Screens | Status |
|---|---|---|---|---|---|---|
| US-01 | All | Log in on the right tab | C-01 | UC-02 | P-01 | v0.2 |
| US-02 | All | Manage my profile and password | C-15 | UC-22 | S-06, A-07 | v0.2 (gender and avatar v0.4) |
| US-03 | All | See my notifications | C-11 | UC-21 | S-05, A-06, top bar | v0.4 |
| US-04 | All | Search within what I may see | C-18 | UC-23 | S-03, A-02, top bar | Partial: list search v0.3/v0.4; top bar S5 |
| US-05 | Student | Register with my NSU email | C-01 | UC-01 | P-02 | v0.2 |
| US-06 | Student | Check for similar issues first | C-03 | UC-04 | S-02 | v0.3 |
| US-07 | Student | Support an existing issue ("Me too") | C-03 | UC-05 | S-02, S-04 | v0.3 |
| US-08 | Student | Submit a complaint with evidence | C-02, C-04 | UC-03 | S-02 | v0.3 |
| US-09 | Student | Track my complaints | C-08, C-14 | UC-06 | S-01, S-03, S-04 | v0.3 |
| US-10 | Student | Withdraw a complaint before review | C-10 | UC-10 | S-04 | v0.4 |
| US-11 | Student | Confirm a fix | C-09 | UC-07 | S-01, S-04 | S4 |
| US-12 | Student | Reopen an unfixed issue | C-09 | UC-08 | S-01, S-04 | S4 |
| US-13 | Student | Rate the resolution | C-17 | UC-09 | S-01, S-04 | S4 |
| US-14 | Dept Admin | Work through my department's queue | C-05 | UC-11 | A-02 | v0.4 |
| US-15 | Dept Admin | Start reviewing a complaint | C-05 | UC-11 | A-03 | v0.4 |
| US-16 | Dept Admin | Verify with priority and due date | C-06 | UC-12 | A-03 | v0.4 |
| US-17 | Dept Admin | Reject an invalid complaint | C-05 | UC-13 | A-03 | v0.4 |
| US-18 | Dept Admin | Start work | C-05 | UC-14 | A-03 | v0.4 |
| US-19 | Dept Admin | Resolve with proof | C-07 | UC-15 | A-03 | v0.4 |
| US-20 | Dept Admin | Add public or internal notes | C-08 | UC-16 | A-03 | v0.4 |
| US-21 | Dept Admin | Open evidence files safely | C-02 | UC-11 | A-03 | v0.4 |
| US-22 | Dept Admin | See my department at a glance | C-14 | – | A-01 | S4 (cards, tables); S5 (charts) |
| US-23 | Dept Admin | View student records | C-12 | UC-17 | A-04, A-05 | S4 |
| US-24 | Super Admin | Act on any department's complaint | C-13 | UC-11 to UC-16 | A-02, A-03 | v0.4 |
| US-25 | Super Admin | Reassign a misrouted complaint | C-13 | UC-19 | A-03 | S4 |
| US-26 | Super Admin | Manage user accounts | C-12 | UC-18 | SA-02, SA-03, A-05 | S4 |
| US-27 | Super Admin | View campus-wide reports | C-14 | UC-20 | SA-01 | S5 |
| US-28 | Super Admin | Configure departments and categories | C-16 | – | Django admin | v0.2 |

**Count:** 28 stories; 21 built (v0.2 to v0.4, US-04 partly), 7 planned (S4/S5).

## 2. All Roles

### US-01 Log in on the right tab · v0.2
*As a user of any role, I want to log in on the Student or Staff tab, so that I land on the home page for my role.*

- AC1: Student tab accepts only `student` accounts; Staff tab accepts only `dept_admin` and `super_admin`. A mismatch is refused with "This is a staff account. Please use the Staff tab." or "This is a student account. Please use the Student tab." (VR-15)
- AC2: Suspended or deleted accounts see "Account inactive" before any tab check (VR-11).
- AC3: After login a student opens S-01 and an admin opens A-01.
- AC4: After an error the form keeps the chosen tab.

Code: `accounts/forms.py`, `accounts/views.py`, `templates/accounts/login.html`.

### US-02 Manage my profile and password · v0.2, gender and avatar v0.4
*As a user, I want to edit my details and change my password, so that my account stays correct and secure.*

- AC1: Name, phone and optional gender are editable; email is read-only.
- AC2: Change password requires the current password; the user stays logged in afterwards.
- AC3: My own avatar matches my gender only in my top bar and on my profile; `other` and `prefer_not_to_say` show the neutral avatar (VR-16).
- AC4: No other user, admin page, report or filter shows or uses my gender (VR-16).

Code: `accounts/views.py`, `accounts/forms.py`, `templates/accounts/profile.html`, `templates/partials/avatar.html`.

### US-03 See my notifications · v0.4
*As a user, I want to be told when something happens to my complaints, so that I don't have to keep checking.*

- AC1: The bell shows my unread count on every page; with none, no number.
- AC2: The notifications page lists my own notifications, newest first, unread highlighted; each opens its complaint (S-04 for students, A-03 for admins).
- AC3: Opening the list marks nothing as read; **Mark all as read** appears only when something is unread and works by POST only.
- AC4: The reporter is notified of every status change and public note; a Reject notification includes the reason; a Resolved notification says to confirm or reopen by the date 7 days after resolution (`03` §4).
- AC5: Department admins are notified of new and withdrawn complaints in their department (reopened, closed, rated and reassigned-in follow with US-11 to US-13 and US-25).
- AC6: The person who performed an action is never notified about it.

Code: `notifications/models.py`, `notifications/views.py`, `notifications/context_processors.py`, `templates/notifications/list.html`.

### US-04 Search within what I may see · Partial (list search v0.3/v0.4; top bar S5)
*As a user, I want to search by tracking ID or keywords, so that I can find a complaint quickly.*

- AC1: Student search (S-03) matches tracking ID, title and room, within own and supported complaints only. *(v0.3)*
- AC2: Admin queue search (A-02) matches tracking ID, title, room, reporter name, student ID and email, within the admin's scope; first or last name alone is enough ("contains" matching). *(v0.4)*
- AC3: Results never include records outside the user's scope; out-of-scope searches return no results, not an error (VR-14, VR-01, VR-02).
- AC4: The top-bar search sends each role to its own list page with `?q=`; an exact tracking ID the user may see opens that complaint directly. *(S5)*
- AC5: Admins can also find students (A-04) and the Super Admin users (SA-02). *(S5)*

## 3. Student

### US-05 Register with my NSU email · v0.2
*As a student, I want to create an account with my NSU email, so that I can report campus issues.*

- AC1: Email must end in `@northsouth.edu` and not be registered already (VR-13).
- AC2: Full name, student ID, phone and password (twice) are required; gender is optional with "Prefer not to say" preselected (VR-16).
- AC3: The account is created with role `student`; staff accounts cannot be created here.

Code: `accounts/forms.py`, `accounts/views.py`, `templates/accounts/register.html`.

### US-06 Check for similar issues first · v0.3
*As a student, I want to see whether my issue is already reported, so that I don't file a duplicate.*

- AC1: Step 1 asks only for category, building and room; **Check for similar issues** saves nothing.
- AC2: Matches are open complaints with the same category, building and room (room compared case-insensitively, spaces ignored) (`03` §6).
- AC3: Matches show the limited summary only: no description, reporter or files (VR-01).
- AC4: My own matches say "You reported this" and ones I support say "You support this", with no Me too button (VR-09).
- AC5: With no matches, step 2 opens directly.

Code: `Complaint.find_duplicates()` in `complaints/models.py`, `complaints/views.py`, `templates/student/complaint_form.html`.

### US-07 Support an existing issue ("Me too") · v0.3
*As a student, I want to add my support to an existing complaint, so that the department sees how many students are affected.*

- AC1: **Me too** adds me as a supporter and increases students affected by one.
- AC2: I cannot support my own complaint, support twice, or support a complaint that is not open (VR-09).
- AC3: Afterwards I see the complaint in the limited view, with no action buttons (VR-01), and it appears in My complaints labelled "Supported".

Code: `Complaint.support()`, `student:complaint_action` (`support`).

### US-08 Submit a complaint with evidence · v0.3
*As a student, I want to describe the issue and attach photos, videos or PDFs, so that the department can verify it.*

- AC1: Title, category, building and description are required; the server re-checks the carried-over category and location on Submit.
- AC2: Files: JPG, JPEG, PNG, WEBP, MP4, MOV or PDF only, at most 15 MB each and 5 per complaint; the real file type must match the extension (VR-07). A refused file keeps my typed text.
- AC3: Categories marked `requires_attachment` need at least one file (VR-08).
- AC4: On success I get a tracking ID (`UF-xxxx`); the department is copied from the category (C-04); its admins are notified; I land on S-04.

Code: `Complaint.submit()`, `check_attachment_file()`, `complaints/forms.py`, `templates/student/complaint_form.html`.

### US-09 Track my complaints · v0.3
*As a student, I want to see the status and history of my complaints, so that I know what is happening.*

- AC1: Home (S-01) shows cards: Open, Awaiting your confirmation, Closed, Issues you supported; plus recent complaints (latest notifications added in v0.4).
- AC2: My complaints (S-03) lists reported and supported complaints with status filter and search.
- AC3: My own complaints show in full; supported ones in the limited view (VR-01).
- AC4: Timeline entries name the actor by role or department ("Reporter", "You", "Facilities Management", "A student supported this"), never a person's name (VR-01); internal notes never appear.
- AC5: A complaint I may not see shows "not found" (404).
- AC6: Files open only through a permission-checked view, never from `/media/` (NFR-03).

Code: `complaints/views.py`, `templates/student/home.html`, `complaint_list.html`, `complaint_detail.html`.

### US-10 Withdraw a complaint before review · v0.4
*As a student, I want to cancel a complaint I filed by mistake, so that the department doesn't waste time on it.*

- AC1: **Withdraw** appears only on my own complaints while Submitted (VR-03).
- AC2: It asks for confirmation ("This cannot be undone.") and works by POST only.
- AC3: Status becomes Withdrawn (final); department admins are notified.

Code: `Complaint.withdraw()`, `student:complaint_action` (`withdraw`).

### US-11 Confirm a fix · S4
*As a student, I want to confirm that the issue is fixed, so that the complaint is closed.*

- AC1: **Confirm fix** appears on my own Resolved complaints and in "Needs your action" on S-01 (VR-03).
- AC2: Status becomes Closed; department admins are notified.

### US-12 Reopen an unfixed issue · S4
*As a student, I want to reopen a complaint if the problem persists, so that the department works on it again.*

- AC1: **Reopen** is allowed only within 7 days of `resolved_at` (VR-06) and requires a reason (VR-04).
- AC2: Status becomes Reopened; department admins are notified; the complaint returns to their queue.

### US-13 Rate the resolution · S4
*As a student, I want to rate how my complaint was handled, so that departments get feedback.*

- AC1: Only the reporter, only once, only when Closed (VR-10).
- AC2: 1 to 5 stars with an optional comment; department admins are notified.
- AC3: Ratings feed the average rating on A-01 and SA-01.

## 4. Department Admin

### US-14 Work through my department's queue · v0.4
*As a department admin, I want a filtered list of my department's complaints, so that I can see what needs attention first.*

- AC1: Only my department's complaints appear (VR-02).
- AC2: Default view: open statuses, soonest due date first (no due date last); option to sort by most recently updated.
- AC3: Filters by status, category, priority and overdue combine with search (US-04).
- AC4: Overdue rows are flagged (`03` §5).
- AC5: Each row opens A-03.

Code: `console/views.py`, `templates/console/queue.html`.

### US-15 Start reviewing a complaint · v0.4
*As a department admin, I want to mark a complaint as under review, so that the student and other admins know it is being checked.*

- AC1: The action bar shows Start review, Verify, Reject, Start work, Mark resolved in that order; only buttons valid for the current status are enabled, and disabled ones show a hint ("Done", "Available after <step>", "Not available: complaint is <status>") (VR-03).
- AC2: Start review posts straight away (Submitted → Under review); the student is notified.
- AC3: An action that is no longer valid (e.g. another admin acted first in another tab) is refused by the server with a message above the action bar, and no history row is added (VR-03).
- AC4: Another department's complaint opened by URL shows "not found" (VR-02).

Code: `Complaint.allowed_actions(user)`, `Complaint.start_review()`, `console:complaint_action`, `templates/console/complaint_detail.html`.

### US-16 Verify with priority and due date · v0.4
*As a department admin, I want to verify a valid complaint with a priority and due date, so that the work is planned and tracked.*

- AC1: Priority (Low, Medium, High) and a due date later than today are required (VR-05); otherwise the form reopens with errors and nothing changes.
- AC2: Under review → Verified; the student is notified and sees the due date.
- AC3: After the due date, an unfinished complaint counts as overdue (`03` §5).

Code: `Complaint.verify()`, `console/forms.py`.

### US-17 Reject an invalid complaint · v0.4
*As a department admin, I want to reject invalid or out-of-scope complaints with a reason, so that the student understands why.*

- AC1: A reason is required (VR-04); Under review → Rejected (final).
- AC2: The student's notification includes the reason.

Code: `Complaint.reject()`.

### US-18 Start work · v0.4
*As a department admin, I want to mark that work has started, so that the student sees progress.*

- AC1: Allowed from Verified or Reopened only (VR-03); an optional note is recorded.
- AC2: Status becomes In progress; the student is notified.

Code: `Complaint.start_work()`.

### US-19 Resolve with proof · v0.4
*As a department admin, I want to mark a complaint resolved with a note and a photo, so that the student can check the fix.*

- AC1: A resolution note is required (VR-04); a proof-of-fix photo is optional (JPG, JPEG, PNG or WEBP, 15 MB, real type checked as in VR-07).
- AC2: In progress → Resolved; `resolved_at` is set.
- AC3: The student is notified with the confirm-or-reopen-by date (resolution + 7 days) and sees the photo under "Proof of fix" on S-04.

Code: `Complaint.resolve()`, `check_proof_file()`.

### US-20 Add public or internal notes · v0.4
*As a department admin, I want to add notes, so that I can update the student or leave information for other admins.*

- AC1: Notes can be added on open statuses and Resolved, not on Closed, Rejected or Withdrawn (`03` §2).
- AC2: A public note appears on the student's timeline and notifies the student.
- AC3: An internal note is visible to admins only and notifies nobody (VR-01).

Code: `Complaint.add_note()`, `Complaint.can_add_note(user)`.

### US-21 Open evidence files safely · v0.4
*As a department admin, I want to open a complaint's evidence, so that I can verify it without exposing files to others.*

- AC1: Evidence and proof files open through `console:attachment`, which checks permission first (NFR-03).
- AC2: Files of another department's complaint return "not found" (VR-02).

### US-22 See my department at a glance · S4 (cards, tables), S5 (charts)
*As a department admin, I want a dashboard of my department's workload, so that I can spot overdue and popular issues.*

- AC1: Cards: New, In progress, Overdue, Resolved this week, Average rating. *(S4)*
- AC2: Tables: Overdue (by due date), Due in next 3 days, Most supported. *(S4)*
- AC3: Each card or row opens A-02 filtered, or A-03. *(S4)*
- AC4: Charts: by status, by category, weekly trend for the last 8 weeks; static, no animation. *(S5)*
- AC5: Super Admin sees the same page for all departments; no gender anywhere (VR-16).

Until S4 the page is a placeholder showing the real department and category table (the Update 1 package shows a labelled shell with placeholder cards).

### US-23 View student records · S4
*As a department admin, I want to see a student's complaint history, so that I can spot repeated or invalid reports.*

- AC1: Dept Admin sees only students who filed in their department, read-only (VR-02, VR-14); Super Admin sees all.
- AC2: Student detail shows profile fields, account state, joined date, complaint history and ratings given; no gender (VR-16).
- AC3: The reporter card on A-03 links here.

## 5. Super Admin

### US-24 Act on any department's complaint · v0.4
*As the super admin, I want to use every action on any complaint, so that I can step in when a department is stuck.*

- AC1: A-02 shows all departments, with a department filter.
- AC2: Every action in US-15 to US-20 works on every department's complaint, with the same transition rules (VR-03).

### US-25 Reassign a misrouted complaint · S4
*As the super admin, I want to move a complaint to the right department, so that it reaches the people who can fix it.*

- AC1: Only the Super Admin (VR-12), only while Submitted or Under review; a new department and a reason are required.
- AC2: The complaint returns to Submitted in the new department; the student and the new department's admins are notified.

### US-26 Manage user accounts · S4
*As the super admin, I want to add admins and edit, suspend or delete accounts, so that only the right people have access.*

- AC1: Only the Super Admin can edit, suspend, reactivate or delete users (VR-12).
- AC2: Add admin sets name, email, phone, role and department.
- AC3: Delete is soft and asks for confirmation; suspended and deleted accounts cannot log in (VR-11).
- AC4: The users list filters by role, department and account state.

### US-27 View campus-wide reports · S5
*As the super admin, I want campus-wide reports, so that I can compare departments and find problem locations.*

- AC1: Cards: Total open, Overdue, Average resolution time (days), Average rating, Active students (and suspended count).
- AC2: Tables: Department scorecard, Hotspot locations (building + room, with top category), Recently suspended users.
- AC3: Charts: by department, monthly trend (submitted vs resolved), average resolution time per department; date-range filter.
- AC4: Metrics follow the definitions in `02` §4; no gender anywhere (VR-16).

### US-28 Configure departments and categories · v0.2
*As the super admin, I want to manage departments and categories, so that complaints are routed correctly.*

- AC1: Departments and categories are managed in the Django admin panel; each category belongs to one department and can require an attachment.
- AC2: Complaints are read-only in the Django admin panel; status changes happen only through the workflow actions.

Code: `complaints/admin.py`, `accounts/admin.py`.

## 6. Coverage Check

| Check | Result |
|---|---|
| Every core feature C-01 to C-18 has at least one story | Yes |
| Every use case UC-01 to UC-23 has a story | Yes (UC-04 → US-06; UC-11 to UC-16 → US-14 to US-20) |
| Every rule VR-01 to VR-16 appears in at least one AC | Yes |
| Stories shown in Update 1 (`v0.3-sprint2` + A-01 shell) | US-01, US-02, US-05 to US-09, US-28; US-04 AC1. Updates 2–4 are set after the instructor's feedback |
