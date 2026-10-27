# 04. Screen Inventory

18 screens. Each lists what it shows, its buttons, and which data it reads (R) or writes (W). URL and template names follow `05_data_dictionary.md`.

**Layout:** every signed-in page uses `base.html` (with `partials/topbar.html`, `partials/sidebar.html`, `partials/messages.html`): a white top bar and a role-specific navy left sidebar.

**Top bar** (CR-11), three zones, vertically aligned:

| Zone | Contents |
|---|---|
| Left (`topbar-left`) | Empty on desktop; kept for layout balance and for a future mobile menu button |
| Centre (`topbar-center`) | One centred unit: NSU logo (`static/img/nsu_logo.png`, 36 px high, alt text "North South University") beside the UniFix wordmark ("UniFix", subtitle "NSU Campus Services" for students and signed-out pages, "Admin Console" for admins), vertically aligned |
| Right (`topbar-right`, signed-in pages only) | Search, notification bell with unread count, user menu (avatar, name, role, Log out) |

- Login (P-01) and Register (P-02) use the same bar without the right zone.
- Phone width: the centre group stays visible; the logo shrinks first, then the wordmark; search collapses to an icon; no sideways scroll.
- Until notifications are built (Sprint 3, C-11) the bell is shown without a count.

**Error pages** (`403.html`, `404.html`, both extend `base.html`): a short message and a "Back to your home" link to `/`, which sends signed-in users to their role home and everyone else to login.

| Sidebar | Links |
|---|---|
| Student | Home · New complaint · My complaints · Notifications · Profile |
| Dept Admin | Dashboard · Complaint queue · Students · Notifications · Profile |
| Super Admin | Dashboard · Complaint queue (all) · Students · Reports · Users · Notifications · Profile |

## Search (top bar, every signed-in page)

Search reuses the existing list pages with a `?q=` parameter instead of adding new screens. Matching is simple "contains" matching (Django `icontains`), case-insensitive.

| Role | What it searches | Matches on | Results shown in |
|---|---|---|---|
| Student | Own complaints and complaints they supported | Tracking ID, title, room | S-03 My complaints |
| Dept Admin | Complaints in own department; students who filed in it | Tracking ID, title, room, reporter name, student ID, email | A-02 queue (Complaints tab) and A-04 Students (Students tab) |
| Super Admin | All complaints and all users | Same as Dept Admin, plus admin accounts | A-02 (all departments) and SA-02 Users |

- **Exact tracking ID** (e.g. `UF-1042`) jumps straight to the complaint's detail page if the user is allowed to see it.
- **Students cannot search other students' complaints.** Finding existing issues is handled by the automatic duplicate check on S-02 (and optionally the campus issue board, OP-09).
- **Results respect permissions** (VR-14). Searches outside a user's scope return no results rather than an error.
- List pages combine search with their filters (status, category, priority, overdue).

## Public

### P-01 Login
`accounts:login` · `accounts/login.html`

- Shows: login type tabs (CR-10) **Student** (default) and **Staff**, submitted with the form as `login_type`; email and password fields.
  - Student tab: hint "Use your @northsouth.edu student email"; link "Create an account" (P-02).
  - Staff tab: hint "For department coordinators and administrators"; note "Staff accounts are created by the Super Admin." (no register link).
  - The tabs are radio buttons styled as tabs: Tab reaches the group, arrow keys switch tabs, and the active tab is clearly highlighted. No JavaScript.
- Buttons: **Log in** → redirects by role (student → S-01, admin → A-01).
- R: User. Checks, in order: email and password; suspended or deleted accounts see "Account inactive" (VR-11); a tab that does not match the role is refused with "This is a staff account. Please use the Staff tab." or "This is a student account. Please use the Student tab." (VR-15). The form keeps the chosen tab after an error.

### P-02 Register (students)
`accounts:register` · `accounts/register.html`

- Shows: full name, student ID, NSU email, phone, password, confirm password.
- Buttons: **Create account**.
- W: User (`role=student`). VR-13.

## Student

### S-01 Home
`student:home` · `student/home.html`

- Shows: greeting; cards (Open, Awaiting your confirmation, Closed, Issues you supported); "Needs your action" list (Resolved → Confirm/Reopen, Closed and unrated → Rate); recent complaints table (tracking ID, title, location, status badge, due date, updated); latest notifications.
- Buttons: **New complaint**; row → S-04.
- R: Complaint, Support, Notification, Rating.
- Built in stages: Sprint 2 shows the cards, recent complaints and the Confirm/Reopen items of "Needs your action" as links to S-04; latest notifications arrive in Sprint 3, and Rate items with ratings in Sprint 4.

### S-02 New complaint
`student:complaint_new` · `student/complaint_form.html`

Two steps on one URL, so files are uploaded only once (`03_workflow.md` §6). Steps 1 and 2 are plain GET pages that save nothing; only **Submit** posts.

- **Step 1** shows: category (active categories, grouped by department), building, room. Button: **Check for similar issues** (runs `find_duplicates()`).
  - If matches are found: "Similar open complaints" list (limited summaries, VR-01: title, category, location, date reported, status, due date, students affected). Each has **Me too** (posts to `student:complaint_action` with `support`, then opens S-04 in the limited view), except the student's own complaints ("You reported this") and ones they already support ("You support this"). Below the list: **Continue with a new complaint** (→ step 2).
  - If none: step 2 opens directly.
- **Step 2** shows: category, building and room read-only with a **Change** link (→ step 1, values kept); title, description, attachments (multiple files, accepted types and limits listed, VR-07; a list of chosen files with sizes and a **Clear files** link). Button: **Submit** (runs `Complaint.submit()`, then opens S-04).
  - The server re-checks the carried-over category and location on Submit; the duplicate check is not repeated.
- Side panel (both steps): "What happens next" (routing department and the steps that follow).
- R: Category, Complaint (open, same category and location), Support. W: Complaint, Attachment, ComplaintUpdate, Support, Notification.

### S-03 My complaints
`student:complaint_list` · `student/complaint_list.html`

- Shows: table of own complaints and supported complaints (tracking ID, title, location, status badge, due date, updated; supported rows labelled "Supported"); filter by status; search by tracking ID, title or room (`?q=`, reused by the top-bar search in C-18).
- Buttons: row → S-04.
- R: Complaint, Support.

### S-04 Complaint detail
`student:complaint_detail` · `student/complaint_detail.html`

- Shows: tracking ID, status badge, category, department, location, description, evidence, public timeline, proof-of-fix photo, students affected, due date (once verified).
- Timeline entries name the actor by role or department ("Reporter", "You", "Facilities Management", "A student supported this"), never by a person's name (VR-01).
- Evidence and proof files open through `student:attachment` (permission-checked, NFR-03); the file list is the include `student/attachment_list.html` (images as thumbnails, other files as links).
- For a supported (not reported) complaint: limited view only (VR-01), with no action buttons.
- A complaint the student may not see shows the 404 page.
- Buttons (by status): **Withdraw** (submitted) · **Confirm fix** and **Reopen** (resolved, within 7 days) · **Rate** (closed, not yet rated). Read-only in Sprint 2; Withdraw arrives in Sprint 3, the others in Sprint 4.
- R: Complaint, Attachment, ComplaintUpdate (public only), Support, Rating. W: via workflow actions.

### S-05 Notifications
`notifications:list` · `notifications/list.html` (shared by all roles)

- Shows: newest first; unread highlighted; each links to its complaint.
- Buttons: **Mark all as read** (`notifications:mark_all_read`).
- R/W: Notification.

### S-06 Profile
`accounts:profile` · `accounts/profile.html` (shared by all roles)

- Shows: name, email (read-only), student ID, phone; change password form.
- Buttons: **Save changes** · **Change password** (`accounts:password_change`).
- W: User.

## Department Admin

### A-01 Dashboard
`console:dashboard` · `console/dashboard.html`

- Dept Admin: own department. Super Admin: all departments (same page).

- Shows: cards (New, In progress, Overdue, Resolved this week, Average rating); Overdue table; Due in next 3 days; Most supported; charts (by status, by category, weekly trend).
- Buttons: card or row → A-02 filtered, or A-03.
- R: Complaint, Rating, Support.

### A-02 Complaint queue
`console:queue` · `console/queue.html`

- Shows: table (tracking ID, title, category, location, status, priority, due date, supporters, updated); overdue rows flagged.
- Filters: status, category, priority, overdue only; search; sort by due date or updated.
- Buttons: row → A-03.
- R: Complaint (own department; all for Super Admin).

### A-03 Complaint detail and actions
`console:complaint_detail` · `console/complaint_detail.html`

- Shows: everything in S-04 plus reporter card (links to A-05; complaints filed, complaints rejected), internal notes, full history with actor names (consecutive "Me too" entries grouped), and students affected.
- Action bar: **Start review · Verify · Reject · Start work · Mark resolved**. Only valid buttons are enabled; disabled ones show when they become available.
- Each button opens an inline form: Verify (priority, due date) · Reject (reason) · Mark resolved (note, optional photo) · Start work (optional note).
- **Add note** (public or internal). Super Admin also sees **Reassign** (department, reason).
- R: Complaint, Attachment, ComplaintUpdate, User. W: per `03_workflow.md` section 4.

### A-04 Students
`console:student_list` · `console/student_list.html`

- Shows: table (name, student ID, email, complaints count, open count, account state); search.
- Dept Admin sees students who filed complaints in their department, read-only. Super Admin sees all students.
- R: User, Complaint.

### A-05 Student detail
`console:student_detail` · `console/student_detail.html`

- Shows: profile fields, account state, joined date, complaint history table, ratings given.
- Buttons (Super Admin only): **Edit** (→ SA-03) · **Suspend / Reactivate** · **Delete**.
- R: User, Complaint, Rating.

### A-06 Notifications · A-07 Profile
Same as S-05 and S-06.

## Super Admin

### SA-01 Reports
`console:reports` · `console/reports.html`

- Shows: cards (Total open, Overdue, Average resolution time, Average rating, Active students); Department scorecard; Hotspot locations; Recently suspended users; charts (by department, monthly trend, resolution time per department).
- Filter: date range.
- R: Complaint, Rating, User, Department.

### SA-02 Users
`console:user_list` · `console/user_list.html`

- Shows: all accounts; filter by role, department, account state; search.
- Buttons: **Add admin** (`console:user_create`, opens SA-03 empty) · row → A-05 (students) or SA-03 (admins).
- R: User.

### SA-03 Add / edit user
`console:user_create`, `console:user_edit` · `console/user_form.html`

- Shows: name, email, phone, role, department (admins), account state.
- Buttons: **Save** · **Suspend / Reactivate** · **Delete** (soft; confirmation dialog).
- W: User. VR-12.
