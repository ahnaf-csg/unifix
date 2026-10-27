# 02. Requirements

## 1. Actors

| Actor | Description | Role value |
|---|---|---|
| Student | Reports and tracks campus issues | `student` |
| Department Admin | Coordinates complaints for one department (e.g. Facilities, IT Services) | `dept_admin` |
| Super Admin | Oversees all departments and manages user records; a specialization of Admin | `super_admin` |

Departments and categories are configured through Django's built-in admin panel (setup task, not an actor).

## 2. Permissions Matrix

| Capability | Student | Dept Admin | Super Admin |
|---|---|---|---|
| Submit, support ("Me too"), track own complaints | ✓ | – | – |
| Confirm, reopen, rate, withdraw own complaints | ✓ | – | – |
| See complaints of own department | – | ✓ | ✓ (all) |
| Status action buttons | – | ✓ (own department) | ✓ (any) |
| Reassign complaint to another department | – | – | ✓ |
| View student records and complaint history | – | ✓ (view only) | ✓ |
| Edit, suspend, delete (soft) user accounts | – | – | ✓ |
| Reports dashboard (all departments) | – | – | ✓ |
| Django admin panel (departments, categories) | – | – | ✓ |
| Edit own profile, change password | ✓ | ✓ | ✓ |

## 3. Core Features

| ID | Feature | Description |
|---|---|---|
| C-01 | Accounts and roles | Register (students only, `@northsouth.edu` email), login, logout. Admin accounts are created by the Super Admin or in Django admin. |
| C-02 | Complaint submission | Title, category, building, room, description, attachments (photo, video, PDF). Server-side checks on required fields, file type and size. Categories marked `requires_attachment` need at least one file. A tracking ID (e.g. UF-1042) is issued. |
| C-03 | Duplicate check and "Me too" | Step 1 of the form (category and location) checks for open complaints matching the duplicate rule (`03_workflow.md` §6) before any details or files are entered; matches are shown as limited summaries. The student can support one instead of submitting. Students affected = supporters + reporter. |
| C-04 | Department routing | The complaint's department is copied from its category at submission and stored on the complaint. |
| C-05 | Status action buttons | One button per step on the admin complaint page: Start review, Verify, Reject, Start work, Mark resolved. Only the buttons valid for the current status are enabled. |
| C-06 | Verification with priority and due date | Verify requires a priority (Low, Medium, High) and a due date in the future. A complaint is overdue as defined in `03_workflow.md` §5 (`is_overdue`). |
| C-07 | Resolution with proof | Mark resolved requires a resolution note; a proof-of-fix photo is optional. |
| C-08 | Status history | Every action creates a history record (who, what, when, note). Notes can be public (visible to the student) or internal (admins only). |
| C-09 | Confirm or reopen | The student confirms the fix (Closed) or reopens within 7 days of resolution with a reason (Reopened). |
| C-10 | Withdraw | The student can withdraw a complaint while it is still Submitted. *(Keep in view)* |
| C-11 | In-app notifications | The reporter is notified on every status change, reassignment and public note; department admins are notified of new, reassigned-in, reopened, closed and rated complaints in their department (see `03_workflow.md` §4). |
| C-12 | User records | Super Admin: view, edit, suspend, delete (soft) any account. Dept Admin: view students and their complaint history (read-only). |
| C-13 | Super Admin complaint control | Acts on any complaint and reassigns complaints between departments with a reason. |
| C-14 | Dashboards and reports | Student home, Dept Admin dashboard and Super Admin reports (see section 4). |
| C-15 | Profile | Edit name and phone; change password. |
| C-16 | Setup | Departments and categories managed in the Django admin panel (Super Admin accounts have `is_staff` and `is_superuser`). |
| C-17 | Student rating | After closing, the student rates the resolution 1–5 stars with an optional comment, once per complaint. *(Keep in view)* |
| C-18 | Search | Role-scoped search bar in the top bar (see `04_screens.md` §Search). An exact tracking ID opens the complaint directly. |

## 4. Dashboard Contents

| Dashboard | Cards | Tables | Charts |
|---|---|---|---|
| Student home (S-01) | Open; Awaiting your confirmation; Closed; Issues you supported | Needs your action (confirm, reopen, rate); Recent complaints; Latest notifications | None |
| Dept Admin dashboard (A-01) | New; In progress; Overdue; Resolved this week; Average rating | Overdue (by due date); Due in next 3 days; Most supported | Complaints by status (bar); By category (bar); Weekly trend, last 8 weeks (line) |
| Super Admin reports (SA-01) | Total open; Overdue; Average resolution time (days); Average rating; Active students (and suspended count) | Department scorecard (open, overdue, avg days to resolve, avg rating, reopened); Hotspot locations (building + room, with top category); Recently suspended users | By department (bar); Monthly trend: submitted vs resolved (line); Average resolution time per department (bar) |

Charts are static (no animation): Chart.js with animation disabled, or plain CSS bars. The Super Admin's own dashboard is A-01 showing all departments.

**Metric definitions:** average resolution time = mean of (`resolved_at` − `created_at`) in days for complaints resolved in the selected period; average rating = mean `stars`; overdue as in `03_workflow.md` §5.

## 5. Optional Features

| ID | Feature |
|---|---|
| OP-01 | Anonymous complaints (identity hidden from department admins) |
| OP-02 | AI chatbot for preliminary self-help |
| OP-03 | AI category suggestion from the description |
| OP-04 | Room QR codes that pre-fill the location |
| OP-05 | Charts upgrade and CSV export of reports |
| OP-06 | Students edit a complaint while Submitted |
| OP-07 | Extra profile options (photo, preferences) |
| OP-08 | Quick-fix guides: admin-written self-help steps per category, shown before submitting |
| OP-09 | Campus issue board: public list of open issues by building |
| OP-10 | Auto-close Resolved complaints not confirmed within 7 days |

## 6. Validation Rules

| ID | Rule |
|---|---|
| VR-01 | Students see complaints they reported in full, and complaints they supported in a limited view: title, category, department, location, status, due date, students affected, date reported and the public timeline; no description, reporter identity or attachments. Duplicate matches on S-02 show the same limited summary (without the timeline). Every student-facing page names the actor of a timeline entry by role or department ("Reporter", "Facilities Management", "A student supported this"), never by a person's name. Complaints a student may not see return "not found". |
| VR-02 | Dept Admins can only see and act on complaints of their own department. |
| VR-03 | Only transitions listed in `03_workflow.md` are allowed; buttons for other transitions are disabled and rejected server-side. |
| VR-04 | Reject requires a reason; Mark resolved requires a note; Reopen requires a reason. |
| VR-05 | Verify requires a priority and a due date later than today. |
| VR-06 | Reopen is allowed only within 7 days of `resolved_at`. |
| VR-07 | Files: JPG, JPEG, PNG, WEBP, MP4, MOV, PDF only; maximum 15 MB each; at most 5 files per complaint; the file type detected from the file's content must match the extension. |
| VR-08 | Categories with `requires_attachment` need at least one evidence file. |
| VR-09 | A student cannot support their own complaint or support the same complaint twice; only complaints with an open status can be supported. |
| VR-10 | A complaint can be rated once, only by its reporter, and only when Closed. |
| VR-11 | Suspended and deleted accounts cannot log in. |
| VR-12 | Only the Super Admin can edit, suspend or delete users, and reassign complaints. |
| VR-13 | Registration requires an `@northsouth.edu` email address that is not already registered. |
| VR-14 | Search results only include records the user is allowed to see (VR-01, VR-02). |
| VR-15 | Login is refused when the chosen login type does not match the account role (Student tab: `student`; Staff tab: `dept_admin`, `super_admin`). Inactive accounts see "Account inactive" first (VR-11). |

## 7. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Usability | Every page uses the same layout, status badges and button styles; primary action is visually distinct. |
| NFR-02 | Security | Django password hashing; permission checks in every view; CSRF protection on all forms. |
| NFR-03 | Privacy | Attachments are only accessible to the reporter, the responsible department's admins and the Super Admin. Uploaded files are never served directly from `/media/`; they are sent by a view that checks permission first. |
| NFR-04 | Performance | Pages load in under 2 seconds with the demo dataset. |
| NFR-05 | Compatibility | Works on current Chrome, Firefox and Edge, on desktop and phone browsers (responsive layout). |
| NFR-06 | Maintainability | Names follow `05_data_dictionary.md`; workflow logic lives in model methods, not templates. |
