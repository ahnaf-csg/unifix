# 05. Data Dictionary (Foundation)

Source of truth for names. Code, templates and diagrams must match exactly.

## 1. Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Django apps | lowercase plural noun | `complaints` |
| Models | singular PascalCase | `ComplaintUpdate` |
| Fields, functions, methods | snake_case | `resolved_at`, `mark_resolved()` |
| Choice values (stored) | lowercase snake_case | `under_review` |
| Choice labels (displayed) | Sentence case | Under review |
| URL names | `namespace:noun_verb` | `console:complaint_detail` |
| Templates | `app_or_area/noun_purpose.html` | `console/complaint_detail.html` |
| CSS classes | kebab-case, prefixed by component | `badge-under-review`, `btn-primary` |
| Branches / commits | feature ID first | `feature/c05-admin-actions`, `C-05: ...` |

## 2. Project Structure

```
unifix/                 Django project settings and root urls
accounts/               User model, login, register, profile, user records
accounts/permissions.py Role mixins and decorators, and complaint access helpers `get_complaint_for_user()`
                        and `has_full_view()` (the one place for permission checks)
complaints/             Models: Department, Category, Complaint, Attachment, ComplaintUpdate, Support, Rating;
                        student-facing views (URL namespace `student`)
complaints/management/commands/seed_demo.py
                        Demo data command (`python manage.py seed_demo`)
notifications/          Notification model and list view
console/                Admin-side views (dashboard, queue, actions, students, users, reports)
templates/              base.html, 403.html, 404.html, partials/, accounts/, student/, console/, notifications/
templates/partials/     topbar.html, sidebar.html, messages.html, status_badge.html
static/css/unifix.css   Single stylesheet (design tokens at the top)
static/js/unifix.js     Small helpers only (form toggles, file previews, charts)
static/img/nsu_logo.png NSU logo shown in the top bar
media/                  Uploaded files (not committed to Git)
docs/                   These documents
```

## 3. Models

### accounts.User (extends Django `AbstractUser`)

Login uses email: `USERNAME_FIELD = "email"`, `REQUIRED_FIELDS = ["full_name"]`. The inherited `username`, `first_name` and `last_name` are removed (set to `None` on the model; `full_name` replaces them), so a custom `UserManager` creates users by email.

Authentication uses Django's `AllowAllUsersModelBackend`; the login form's `confirm_login_allowed()` rejects suspended and deleted accounts with "Account inactive" (VR-11).

| Field | Type | Rules |
|---|---|---|
| `email` | EmailField | Unique; login identifier; students must use `@northsouth.edu` |
| `full_name` | CharField(120) | Required |
| `student_id` | CharField(20), null | Students only; unique when present; stored as NULL (not "") when empty (`null=True, blank=True, unique=True`) |
| `phone` | CharField(20) | Optional |
| `role` | CharField choices | `student`, `dept_admin`, `super_admin` |
| `department` | FK → Department, null | Required for `dept_admin`; empty otherwise |
| `account_state` | CharField choices | `active`, `suspended`, `deleted`; default `active` |
| `is_active` | Boolean (built-in) | `False` when `account_state` is not `active` |
| `is_staff`, `is_superuser` | Boolean (built-in) | `True` only for `super_admin` (Django admin access, C-16) |
| `date_joined` | DateTime (built-in) | Auto |

Methods: `is_student()`, `is_dept_admin()`, `is_super_admin()`, `can_view_complaint(complaint)`, `suspend()`, `reactivate()`, `soft_delete()`.
`can_view_complaint(complaint)` is `True` for the reporter, a supporter (limited view, VR-01), a Dept Admin of the complaint's department (VR-02) and the Super Admin; otherwise `False`. Which view a student gets (full or limited) is decided by whether they are the reporter.

**Login form field** (P-01, VR-15): `login_type`, choices `student` (Student, default) and `staff` (Staff). Not stored; checked against `role` at login (`student` → `student`; `staff` → `dept_admin` or `super_admin`).

### complaints.Department

| Field | Type | Rules |
|---|---|---|
| `name` | CharField(80) | Unique (e.g. Facilities Management) |
| `code` | CharField(10) | Unique (e.g. `FAC`, `IT`, `HK`, `SEC`) |
| `is_active` | Boolean | Default `True` |

### complaints.Category

| Field | Type | Rules |
|---|---|---|
| `name` | CharField(80) | e.g. Electrical, Projector & AV, Plumbing |
| `department` | FK → Department | Routing target |
| `requires_attachment` | Boolean | VR-08 |
| `is_active` | Boolean | Default `True` |

### complaints.Complaint

| Field | Type | Rules |
|---|---|---|
| `tracking_id` | CharField(12), null | Unique; `UF-` + primary key zero-padded to 4 digits (`UF-0001`). The primary key exists only after the first insert, so `save()` inserts with NULL and fills the ID straight after, inside the same transaction (NULLs never clash in a unique column) |
| `reporter` | FK → User | Student who submitted |
| `category` | FK → Category | |
| `department` | FK → Department | Copied from category; changed only by reassign |
| `title` | CharField(120) | Required |
| `description` | TextField | Required |
| `building` | CharField choices | `nac` (NAC), `sac` (SAC), `library` (Library), `admin_building` (Admin Building), `plaza` (Plaza), `other` (Other) |
| `room` | CharField(30) | Optional; room label only, without the building (e.g. `512`, `L3`). Pages show building label + room ("NAC 512"); reports group locations by building + room. |
| `status` | CharField choices | See `03_workflow.md` §1 |
| `priority` | CharField choices, null | `low`, `medium`, `high`; set on verify |
| `due_date` | DateField, null | Set on verify; must be after today |
| `is_anonymous` | Boolean | Default `False`; reserved for OP-01 |
| `reopen_count` | PositiveSmallInteger | Default 0 |
| `created_at`, `updated_at` | DateTime | Auto |
| `verified_at`, `resolved_at`, `closed_at` | DateTime, null | Set by actions |

Methods (each validates the transition, writes `ComplaintUpdate`, sends notifications):
`start_review(actor)`, `verify(actor, priority, due_date)`, `reject(actor, reason)`, `start_work(actor, note="")`, `resolve(actor, note, proof_file=None)`, `confirm(student)`, `reopen(student, reason)`, `withdraw(student)`, `reassign(actor, department, reason)`, `add_note(actor, note, is_internal)`, `support(student)`, `rate(student, stars, comment="")`.
Class methods: `submit(reporter, category, building, room, title, description, files)` creates the complaint, its `Attachment` rows, `ComplaintUpdate(action=submitted)` and the Dept Admin notifications in one transaction (C-02, C-04; checks VR-08); `find_duplicates(category, building, room)` returns open matches (`03` §6).
Properties: `is_overdue`, `can_reopen`, `support_count`, `affected_count`, `allowed_actions(user)`, `is_open` (status in the open list, `03` §1), `location` (building label + room, e.g. "NAC 512"), `status_badge_class` (e.g. `badge-under-review`, used by `partials/status_badge.html`).

**Action mapping** (one row per button; names must match across layers):

| Button | URL action slug | Model method | `ComplaintUpdate.action` | Resulting status |
|---|---|---|---|---|
| Submit | (form post to `student:complaint_new`) | `submit()` | `submitted` | `submitted` |
| Me too | `support` | `support()` | `support` | unchanged |
| Withdraw | `withdraw` | `withdraw()` | `withdraw` | `withdrawn` |
| Start review | `start_review` | `start_review()` | `start_review` | `under_review` |
| Verify | `verify` | `verify()` | `verify` | `verified` |
| Reject | `reject` | `reject()` | `reject` | `rejected` |
| Start work | `start_work` | `start_work()` | `start_work` | `in_progress` |
| Mark resolved | `resolve` | `resolve()` | `resolve` | `resolved` |
| Confirm fix | `confirm` | `confirm()` | `close` | `closed` |
| Reopen | `reopen` | `reopen()` | `reopen` | `reopened` |
| Reassign | `reassign` | `reassign()` | `reassign` | `submitted` |
| Add note | `note` | `add_note()` | `note` | unchanged |
| Rate | `rate` | `rate()` | (none; `Rating` row) | unchanged |

### complaints.Attachment

| Field | Type | Rules |
|---|---|---|
| `complaint` | FK → Complaint | |
| `file` | FileField | `media/complaints/<tracking_id>/<uuid>.<ext>`: a random name on disk; never served directly, only through `student:attachment` (NFR-03) |
| `kind` | CharField choices | `evidence`, `proof_of_fix` |
| `original_name` | CharField(255) | Name shown to users |
| `mime_type` | CharField(100) | Detected from the file's content with the `filetype` library and checked against the extension (VR-07) |
| `size_bytes` | PositiveInteger | ≤ 15 MB; at most 5 evidence files per complaint (VR-07) |
| `uploaded_by` | FK → User | |
| `uploaded_at` | DateTime | Auto |

Property: `is_image` (shown as a thumbnail; other files as a link). The VR-07 check is the module function `check_attachment_file(file)` in `complaints/models.py`, used by the form and by `submit()`; limits `MAX_FILE_SIZE` (15 MB) and `MAX_FILES` (5). The 5-file limit counts evidence files at submission only; the proof-of-fix photo added by `resolve()` (Sprint 3) is separate and does not count. `submit()` checks every file before writing any, and deletes files already written if the transaction fails (a rollback does not remove files from disk).

### complaints.ComplaintUpdate (history)

| Field | Type | Rules |
|---|---|---|
| `complaint` | FK → Complaint | |
| `actor` | FK → User | |
| `action` | CharField choices | `submitted`, `support`, `start_review`, `verify`, `reject`, `start_work`, `resolve`, `close`, `reopen`, `withdraw`, `reassign`, `note` |
| `from_status`, `to_status` | CharField, blank | Status values |
| `from_department`, `to_department` | FK → Department, null | Reassign only |
| `note` | TextField, blank | Reason or note |
| `is_internal` | Boolean | Default `False`; hidden from students |
| `created_at` | DateTime | Auto |

### complaints.Support ("Me too")

| Field | Type | Rules |
|---|---|---|
| `complaint` | FK → Complaint | |
| `student` | FK → User | Not the reporter (VR-09) |
| `created_at` | DateTime | Unique together: (`complaint`, `student`) |

### complaints.Rating

| Field | Type | Rules |
|---|---|---|
| `complaint` | OneToOne → Complaint | Only when `closed` (VR-10) |
| `student` | FK → User | Must be the reporter |
| `stars` | PositiveSmallInteger | 1–5 |
| `comment` | TextField, blank | |
| `created_at` | DateTime | Auto |

### notifications.Notification

| Field | Type | Rules |
|---|---|---|
| `recipient` | FK → User | |
| `complaint` | FK → Complaint, null | |
| `event` | CharField choices | `new_complaint`, `status_changed`, `note_added`, `reopened`, `reassigned`, `rated` |
| `message` | CharField(255) | e.g. "UF-1042 was marked Resolved" |
| `is_read` | Boolean | Default `False` |
| `created_at` | DateTime | Auto |

## 4. URL Names

| Namespace | Name | Path | Screen |
|---|---|---|---|
| accounts | `login` | `/login/` | P-01 |
| accounts | `logout` | `/logout/` | – |
| accounts | `register` | `/register/` | P-02 |
| accounts | `profile` | `/profile/` | S-06, A-07 |
| accounts | `password_change` | `/profile/password/` | S-06, A-07 (form post) |
| student | `home` | `/student/` | S-01 |
| student | `complaint_new` | `/student/complaints/new/` | S-02 |
| student | `complaint_list` | `/student/complaints/` | S-03 |
| student | `complaint_detail` | `/student/complaints/<tracking_id>/` | S-04 |
| student | `complaint_action` | `/student/complaints/<tracking_id>/<action>/` | support, withdraw, confirm, reopen, rate |
| student | `attachment` | `/student/complaints/<tracking_id>/files/<id>/` | S-04 (sends an evidence or proof file after a permission check) |
| notifications | `list` | `/notifications/` | S-05, A-06 |
| notifications | `mark_all_read` | `/notifications/read-all/` | S-05, A-06 (form post) |
| console | `dashboard` | `/console/` | A-01 |
| console | `queue` | `/console/complaints/` | A-02 |
| console | `complaint_detail` | `/console/complaints/<tracking_id>/` | A-03 |
| console | `complaint_action` | `/console/complaints/<tracking_id>/<action>/` | start_review, verify, reject, start_work, resolve, note, reassign |
| console | `student_list` | `/console/students/` | A-04 |
| console | `student_detail` | `/console/students/<id>/` | A-05 |
| console | `reports` | `/console/reports/` | SA-01 |
| console | `user_list` | `/console/users/` | SA-02 |
| console | `user_create` | `/console/users/new/` | SA-03 |
| console | `user_edit` | `/console/users/<id>/edit/` | SA-03 |
| console | `user_state` | `/console/users/<id>/<state_action>/` | suspend, reactivate, delete |

The Django admin panel stays at `/django-admin/` to avoid confusion with the console.

## 5. Status Badge Colours (CSS)

| Status | Class | Colour |
|---|---|---|
| submitted | `badge-submitted` | Grey |
| under_review | `badge-under-review` | Purple |
| verified | `badge-verified` | Blue |
| in_progress | `badge-in-progress` | Amber |
| resolved | `badge-resolved` | Teal |
| closed | `badge-closed` | Green |
| reopened | `badge-reopened` | Orange |
| rejected | `badge-rejected` | Red |
| withdrawn | `badge-withdrawn` | Grey outline |
| overdue (flag) | `flag-overdue` | Red text |

Priority text: `pri-high` (red), `pri-medium` (amber), `pri-low` (muted grey).

**Component classes** (in `unifix.css`; mockup HTML uses shorter draft names):

| Component | Classes |
|---|---|
| Layout | `topbar`, `topbar-left`, `topbar-center`, `topbar-right`, `sidebar`, `sidebar-label`, `sidebar-link`, `sidebar-link-active`, `main`, `breadcrumb`, `page-title`, `page-sub`, `row` |
| Top bar | `brand` (centre group: NSU logo + UniFix wordmark), `topbar-logo` (NSU logo inside `brand`), `topbar-search`, `bell`, `bell-count`, `user-menu`, `avatar` |
| Cards | `card`, `card-stat`, `stat-label`, `stat-value`, `stat-note` |
| Buttons | `btn`, `btn-primary`, `btn-danger`, `btn-sm` (disabled buttons use the `disabled` attribute) |
| Forms | `form-field`, `form-help`, `form-error` |
| Tabs | `tab-list` (group), `tab` (one tab; the active tab is the checked radio button), `tab-panel` (content shown for a tab) |
| Messages | `alert-info`, `alert-success`, `alert-warning`, `alert-error` (Django message levels) |
| Text | `text-muted`, `text-mono` |
| Page structure (Sprint 2) | `page-head` (title + main button), `section` (top spacing), `card-wide`, `card-head`, `table-scroll` (tables scroll inside the card), `list-item` |
| Complaint pages (Sprint 2) | `steps` (S-02 progress), `match` (duplicate summary), `readonly-value`, `file-list` (chosen files), `next-steps`, `filters` (S-03), `details` (S-04 facts), `description`, `file-grid` (S-04 files), `timeline`, `timeline-note` |

## 6. Design Tokens (top of `unifix.css`)

| Token | Value | Use |
|---|---|---|
| `--navy` | `#14294a` | Sidebar, brand block, headings |
| `--navy-2` | `#1d3a66` | Active sidebar item |
| `--bg` | `#eef2f7` | Page background |
| `--surface` | `#ffffff` | Cards, tables, forms |
| `--border` | `#e1e4ea` | Card, table and input borders |
| `--text` | `#1c2433` | Body text |
| `--muted` | `#667085` | Secondary text, help text |
| `--primary` | `#1d5bbf` | Primary buttons, links |
| `--primary-soft` | `#e3ecfb` | Selected and info backgrounds |
| `--danger` | `#c0352b` | Reject, reopen, overdue |
| `--ok` | `#1a7f4b` | Success messages, closed |
| `--warn` | `#b26a00` | Warnings, medium priority |
| Card accents | blue `#1d5bbf`, teal `#0d8a7a`, amber `#b26a00`, purple `#6b4fd8`, green `#1a7f4b` | Top border of dashboard stat cards |

No animations, gradients or shadows beyond a 1 px card shadow.

## 7. Seed Data (demo and development)

| Department (`code`) | Categories (`requires_attachment`) |
|---|---|
| Facilities Management (`FAC`) | Air conditioning (yes), Electrical (yes), Furniture (yes), Plumbing (yes) |
| IT Services (`IT`) | Projector & AV (no), Network (no), Lab computers (no) |
| Housekeeping (`HK`) | Cleanliness (yes), Waste & bins (no) |
| Security (`SEC`) | Lost access card (no), Safety hazard (yes) |

Demo accounts: one Super Admin, one Dept Admin per department, about 10 students, and complaints in every status (including overdue and reopened examples).

`seed_demo` grows by sprint: Sprint 1 seeds departments, categories and accounts; Sprint 2 adds complaints in every status, with supporters, history rows, notifications and small generated sample files, all dated relative to the day the command runs (so overdue examples stay overdue). Until the Sprint 3 action methods exist, the seed writes these rows directly to match `03` §4; from Sprint 3 it calls the real methods. Running the command again adds nothing.
