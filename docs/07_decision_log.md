# 07. Decision Log

## Decisions

| Date | Decision | Reason |
|---|---|---|
| Oct 2026 | Topic: UniFix complaint management (instructor's pick) | Clear workflow, suitable size for two |
| Oct 2026 | Responsive web app (Django templates + vanilla CSS/JS), not native mobile | One codebase; phone browsers still capture photos and video |
| Oct 2026 | Database: SQLite in development, MySQL if required | Minimal setup; Django ORM makes switching easy |
| Oct 2026 | Hybrid process: Waterfall for requirements/design, Agile sprints for build | Course grades documents first; sprints absorb feedback |
| Oct 2026 | Roles: Student, Dept Admin, Super Admin (single `role` field) | Instructor feedback asked for richer admin side and user records |
| Oct 2026 | One button per workflow step | Instructor asked to see where buttons are and what each does |
| Oct 2026 | Admin picks due date on Verify; overdue computed | Simple and visible on dashboards |
| Oct 2026 | Resolve needs note; proof photo optional | Accountability without forcing uploads |
| Oct 2026 | Notifications and rating promoted to core | Make admin actions visible to students; feed department scorecards |
| Oct 2026 | Soft delete via `account_state` + `is_active` | Keeps complaint history intact |
| Oct 2026 | Departments and categories managed in Django admin | Less to build |
| Oct 2026 | Complaint stores its own `department` | Allows Super Admin reassignment |
| Oct 2026 | Supported complaints shown in a limited view (VR-01) | Privacy of the reporter; confirmed by team |
| Oct 2026 | Reopened complaints keep the original due date | Simple; overdue stays visible; confirmed by team |
| Oct 2026 | Super Admin accounts get Django admin access (`is_staff`, `is_superuser`) | One place to manage departments and categories (C-16) |
| Oct 2026 | `room` stores the room label only; building comes from `building` | Avoids repeating the building; clean hotspot grouping |
| Oct 2026 | Version tags: planning `v0.1.x`, sprints `v0.2-sprint1` … `v0.5-sprint4`, final `v1.0` | Tags line up with sprints |

## Keep in View

| Item | Current plan | Alternative |
|---|---|---|
| Super Admin | Keep (users, reassign, reports) | Drop it; Dept Admins get full user control and a "Forward to department" action |
| User deletion | Soft delete | Hard delete if soft delete causes issues |
| Withdraw | Allowed while Submitted (`withdrawn` status) | Complaints final once submitted |
| Student rating | Core | Move to optional if time is short |
| Charts | Static charts | Counts and tables only |
| Search scope | Role-scoped "contains" search on list pages | Extend: campus-wide issue search for students, filters by date, smarter matching |
| Header and top-area spacing | Calmer spacing (v1.2 mockups) | Revisit after usability testing |
| Supporter notifications | Only the reporter is notified | Also notify students who pressed "Me too" |
| Due date after reopen | Original due date kept (may show overdue) | Admin sets a new due date on Start work |

Instructor feedback and iteration changes are tracked in `08_iteration_log.md`.

## Change History

| Date | Change | Files |
|---|---|---|
| Oct 2026 | Documentation set created (v1) | All |
| Oct 2026 | v1.1: search scope (C-18, VR-14), system workflow diagram, colour palette, iteration log | 02, 03, 04, 05, 08 |
| Oct 2026 | v1.2: header spacing; verification fixes (see `09_verification_report.md`) | 01–08 |
| Oct 2026 | v1.3: ER diagram; supported-complaint limited view and reopen due-date behaviour confirmed by team | 06, 07 |
| Oct 2026 | v1.4 (CR-09): Sprint 1 pre-build fixes from the Claude Code review (I-17 to I-30): sprint coverage, User model details, file and partial names, CSS tokens and classes, Super Admin sidebar, search fields, room format, ER footnote, version tags | 00, 01, 02, 04, 05, 06, 07, 08, 09, `diagrams/er_diagram.*` |
