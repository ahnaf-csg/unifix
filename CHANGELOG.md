# Changelog

Format: [Keep a Changelog](https://keepachangelog.com). Versions match Git tags. Reasons for changes are in `docs/08_iteration_log.md`.

## [Unreleased]
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
