# Changelog

Format: [Keep a Changelog](https://keepachangelog.com). Versions match Git tags. Reasons for changes are in `docs/08_iteration_log.md`.

## [Unreleased]
### Added
- Sprint 3: optional gender at registration and on the profile with three SVG avatars; gender is only ever seen by its owner, everyone else sees the neutral avatar (CR-13, VR-16; migration `accounts/0002`).
- Workflow methods on `Complaint`: `start_review`, `verify` (priority, future due date), `reject` (reason), `start_work`, `resolve` (note, optional proof photo, file removed if it fails), `withdraw`, `add_note` (public or internal; also on Resolved). Each checks who acts (VR-02) and the transition (VR-03), and writes history and notifications in one transaction. `allowed_actions(user)` with disabled-button hints, `can_add_note()`, `User.can_act_on_complaint()`.
- Admin console: A-02 queue (own department, all for the Super Admin) with status, category, priority, overdue and department filters, search and sort; A-03 detail with the five action buttons, inline `<details>` forms, Add note, reporter card and full history; `console:attachment`.
- Notifications: S-05/A-06 list with Mark all as read, bell with unread count on every page, latest notifications on S-01 (C-11). Reject and Resolved messages carry the reason and the "reopen by" date.
- S-04 Withdraw with a confirmation (C-10).
- 21 tests (TC-62 to TC-82); 82 in total. Screenshots retaken; `docs/walkthroughs/sprint-3.md`.

### Changed
- NSU Navy top bar and sidebar with white text, logo on a white tile, gold as a small accent (CR-14).
- `seed_demo` runs every step through the real methods with the clock set to the step's time; the resolved projector complaint has a proof photo. Confirm and reopen remain direct writes until Sprint 4.
- Complaint files are sent by one shared helper, `send_attachment()`, for both `student:attachment` and `console:attachment`.
- Docs, Sprint 3 build: notification messages in `03` §4; OP-11 (email copies, FB-18); FB-17 (Reject reason dropdown) as a Sprint 4 idea; manual checklist items 15–24.
- Docs, Sprint 3 doc-first (CR-13, CR-14, FB-15, FB-16): optional gender and avatars with VR-16; NSU Navy chrome and new design tokens; Sprint 3 decisions in `07`; withdraw notifies department admins; notes allowed on Resolved; `console:attachment`; `allowed_actions(user)` as a method; login protection kept in view; fixes I-54 to I-64; ER diagram shows `gender`.

## [0.3-sprint2] - 2026-10
### Added
- Sprint 2: `Complaint`, `Attachment`, `ComplaintUpdate`, `Support` (migration `complaints/0002`) and `notifications.Notification` (`notifications/0001`).
- Complaint submission with up to 5 evidence files (C-02): `Complaint.submit()` routes to the category's department (C-04), writes history and notifies that department's admins, checks every file before writing any, and removes written files if it fails. Tracking IDs `UF-0001`.
- File checks (VR-07): type detected from the file's content with `filetype`, matched to the extension; 15 MB per file; 5 files. Categories that require a file (VR-08).
- Two-step New complaint page (S-02): category and location → duplicate check (`find_duplicates()`) → details and files; "Me too" (`support()`, VR-09); own and supported matches labelled.
- Student pages S-01 Home (cards, needs your action, recent complaints), S-03 My complaints (status filter and search), S-04 Complaint detail (full view for the reporter, limited view for supporters, public timeline naming roles and departments, VR-01); `partials/status_badge.html`.
- `User.can_view_complaint()`, `get_complaint_for_user()` (404 for complaints a user may not see) and `has_full_view()`.
- Private files (NFR-03): served only by `student:attachment` after a permission check; no `/media/` route; random file names on disk.
- Read-only complaints and notifications in the Django admin.
- `seed_demo`: 14 complaints in every status with history, supporters, notes, notifications and generated sample files, dated relative to today.
- 26 tests (TC-36 to TC-61); 61 in total. `docs/walkthroughs/sprint-2.md` and screenshots.

### Changed
- Docs (CR-12): Sprint 2 pre-build fixes I-36 to I-52. S-02 becomes a two-step form (category and location → duplicate check → details and files); VR-01 lists the limited-view fields and student pages name actors by role or department; VR-07 allows at most 5 files; VR-09 allows supporting open complaints only; files are served only through `student:attachment` (NFR-03); `Complaint.submit()`, `location` and `status_badge_class` added to `05`; Sprint 2 seed plan; decisions in `07`.
- Docs: retrospectives are recorded in `08` iteration entries; `08` Iteration 1 test count and `v0.2-sprint1` date corrected; README status.

### Fixed
- Opening a complaint in the Django admin no longer crashes: all inline fields are read-only, and complaints cannot be deleted there (I-53, TC-61).

## [0.2-sprint1] - 2026-10
### Added
- Sprint 1: Django 5.2 project with apps `accounts`, `complaints`, `notifications`, `console`; settings from `.env`; pinned `requirements.txt`.
- Custom `accounts.User` with email login, roles, department and account state (C-01); `Department` and `Category` in the Django admin at `/django-admin/` (C-16).
- Login, logout and student registration with role-based redirect; suspended and deleted accounts blocked with "Account inactive" (VR-11); `@northsouth.edu` emails only (VR-13).
- Profile with password change (C-15).
- `base.html` with top bar and role sidebars, responsive `static/css/unifix.css`, placeholder S-01 and A-01 pages.
- `seed_demo` command: departments, categories and demo accounts.
- 25 automated tests (TC-01 to TC-25), `docs/10_test_plan.md`, `docs/walkthroughs/sprint-1.md`.

- Sprint 1 review (FB-10, FB-11): Student and Staff login tabs, and a login on the wrong tab is refused (CR-10, VR-15); three-zone top bar with the NSU logo, centred UniFix wordmark and tools on the right (CR-11).
- Friendly `403.html` and `404.html` pages with a link home (I-34).
- 10 more tests (TC-26 to TC-35); 35 in total.

### Changed
- `docs/verify_docs.py` also checks `10_test_plan.md`.
- Tests use a fast password hasher; the suite runs in under a second instead of about 50 s (I-33).
- `.claude/` is ignored by Git (I-32).
- CR-11 amended: the NSU logo sits beside the UniFix wordmark in the centre (replacing the "U" square); the left zone is empty.
- The login email field renders as `type="email"`.

### Fixed
- After a failed profile save, the top bar no longer shows the unsaved name (I-31).
- Docs v0.1.4 (CR-09): Sprint 1 pre-build fixes from a documentation review: C-15 moved to Sprint 1 and C-10 to Sprint 3; User model details (email-only login, `student_id` NULL when empty, Django admin access for Super Admin, "Account inactive" message); names for the permission module, seed command and template partials; full CSS token and class list; Students link for Super Admin; room-only `room` field; ER diagram footnote; version tag scheme.

## [0.1.3-planning] - 2026-10
### Added
- Planning documentation set: plan, requirements, workflow, screens, data dictionary, diagram blueprint, decision log, iteration log, verification report.
- System workflow diagram, ER diagram, four sample screen mockups and draft stylesheet.
- `CLAUDE.md`, `CONTRIBUTING.md`, pull request template.
