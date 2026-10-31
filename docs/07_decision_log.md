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
| Oct 2026 | Login page has Student and Staff tabs; a wrong tab is refused (VR-15) | Clearer login for each group; staff are told their accounts come from the Super Admin (CR-10) |
| Oct 2026 | Login tabs are radio buttons styled with CSS, no JavaScript | Keyboard-accessible by default; the chosen tab is submitted with the form |
| Oct 2026 | Top bar: NSU logo left, UniFix wordmark centre, tools right | University identity visible on every page (CR-11) |
| Oct 2026 | CR-11 amended: NSU logo centred beside the wordmark (clarified by team) | One centred identity unit; the left zone stays free for a future mobile menu button |
| Oct 2026 | Friendly 403 and 404 pages using `base.html` | Users always have a way back home (I-34) |
| Oct 2026 | Tests use the MD5 password hasher (tests only) | Faster test runs; real passwords still use Django's default hasher (I-33) |
| Oct 2026 | Sprint 2: `Notification` model built now; `submit()` writes rows for Dept Admins (list page and bell count in Sprint 3) | `submit()` is finished once; Sprint 3 starts with real data (CR-12) |
| Oct 2026 | Sprint 2 seed: complaints in every status with history, supporters, notifications and sample files, dated relative to today | Every badge, overdue and reopened case can be shown from Sprint 2 (CR-12) |
| Oct 2026 | S-03 status filter and `?q=` search built in Sprint 2 | Small GET form; the C-18 top-bar search reuses `?q=` in Sprint 4 (CR-12) |
| Oct 2026 | Real file type detected with the `filetype` library (pure Python); 15 MB checked per file in the form; at most 5 files per complaint | No system library needed on Windows; limits enforced on the server (VR-07, CR-12) |
| Oct 2026 | Uploads never served from `/media/`; files sent by a permission-checked view; random file names on disk | Attachments stay private, also in development (NFR-03, CR-12) |
| Oct 2026 | S-02 is a two-step form: category and location → duplicate check → details and files | Files are uploaded only once, and only when no duplicate was chosen (CR-12) |
| Oct 2026 | Complaints a user may not see return 404, not 403 | Does not reveal that a tracking ID exists; matches VR-14 (CR-12) |
| Oct 2026 | Student pages name timeline actors by role or department, never by person; admin pages show names | Reporter and staff privacy (VR-01, CR-12) |
| Oct 2026 | Own and already-supported complaints are shown among duplicate matches, labelled, without Me too | The student learns they already reported or support the issue (VR-09, CR-12) |
| Oct 2026 | Submission logic in `Complaint.submit()` | Same pattern as every other action: one model method, one transaction (CR-12) |
| Oct 2026 | One "Clear files" link instead of a Remove link per file | A file input cannot drop single files without extra JavaScript (CR-12) |
| Oct 2026 | Me too is allowed on any open complaint a student can reach by URL; only the limited view (VR-01) is shown | The limited view holds the same fields as a duplicate summary on S-02, so nothing private is exposed; restricting Me too to S-02 matches would add complexity for no privacy gain (CR-12) |
| Oct 2026 | Optional gender (`male`, `female`, `other`, `prefer_not_to_say` by default) at registration and on the profile; three generic SVG avatars | Friendlier pages without collecting anything required (CR-13, extends C-01 and C-15, not an OP item) |
| Oct 2026 | Gender-based avatars are shown only to the user themselves (own top bar and profile); every other page, including all admin pages and the A-03 reporter card, shows the neutral avatar; gender is never shown, filtered or reported | Gender stays private to its owner (VR-16, CR-13) |
| Oct 2026 | CR-14 replaces CR-11's white top bar: top bar and sidebar in NSU Navy `#002f6c` with white text; the NSU logo sits on a small white rounded tile; subtitle in light blue-grey | University colours on every page; the logo stays readable on navy (CR-14) |
| Oct 2026 | NSU Gold `#FEC937` is an accent only (active login tab underline, unread dot), used on navy or beside another state cue, never the only cue; IEEE blue not used; status badge colours unchanged | Gold has too little contrast on white to carry meaning alone; `--primary` already has better contrast than IEEE blue (CR-14) |
| Oct 2026 | A-01 dashboard content stays in Sprint 4; Sprint 3 leaves a placeholder with a link to the queue | Matches the plan; Sprint 3 focuses on the lifecycle |
| Oct 2026 | A-03 inline action forms are `<details>`/`<summary>` blocks; Start review posts directly | No JavaScript, keyboard-accessible; a failed submit reopens the same form with errors |
| Oct 2026 | Disabled action buttons show a visible hint ("Done", "Available after <step>", "Not available: complaint is <status>") | Tooltips do not work on phones; the instructor asked to see where each button is and what it does |
| Oct 2026 | Bell count from a context processor (`notifications.context_processors.unread_count`) | One small query per page, rendered on the server; no JavaScript |
| Oct 2026 | The Super Admin can use every action button on every department's complaint from Sprint 3; Reassign stays in Sprint 4 | Matches the permissions matrix (`02` §2); `can_act_on_complaint()` is the single check |
| Oct 2026 | Withdraw notifies the department's admins | A withdrawn complaint does not silently leave the queue (`03` §4) |
| Oct 2026 | Add note is allowed on open statuses and on Resolved, not on Closed, Rejected or Withdrawn | Admins can still explain something while the student decides whether to confirm (`03` §2) |
| Oct 2026 | Proof of fix is one image (JPG, PNG, WEBP; 15 MB; content checked) | C-07 asks for a photo; same file checks as VR-07 |
| Oct 2026 | A-02 shows open complaints by default, sorted by due date; search (`?q=`) built now, top-bar search stays disabled until C-18 | The queue is a work list; `?q=` is reused by C-18 in Sprint 4 |
| Oct 2026 | Sprint 3 seed uses the real action methods; confirm and reopen steps keep direct writes until Sprint 4 | Those methods are Sprint 4 work (C-09) |
| Oct 2026 | The seed runs each step with the clock set to that step's time (`clock_at()`) | The methods stamp times with `timezone.now()`; setting the clock keeps every time stamp, notification and "reopen by" date consistent without rewriting rows afterwards |
| Oct 2026 | Reject and Resolved notifications carry the reason and the reopen deadline; the reason is shortened with "…" to fit 255 characters | The student learns why, or until when they can reopen, without opening the complaint (`03` §4) |
| Oct 2026 | An action that is no longer possible when posted (e.g. another admin acted first) shows its error above the A-03 action bar; the methods lock the complaint row while checking the status | Its button is disabled by then, so the form is not shown; two admins cannot both act on an old status |

## Keep in View

| Item | Current plan | Alternative |
|---|---|---|
| Super Admin | Keep (users, reassign, reports) | Drop it; Dept Admins get full user control and a "Forward to department" action |
| User deletion | Soft delete | Hard delete if soft delete causes issues |
| Withdraw | Allowed while Submitted (`withdrawn` status) | Complaints final once submitted |
| Student rating | Core | Move to optional if time is short |
| Charts | Static charts | Counts and tables only |
| Search scope | Role-scoped "contains" search on list pages | Extend: campus-wide issue search for students, filters by date, smarter matching |
| Header, top-area spacing and layout density | Calmer header spacing (v1.2 mockups). Team note (FB-13): pages with many buttons feel cluttered; padding and spacing are reviewed after the first full build | Revisit after usability testing; adjust padding, spacing and button grouping in the polish iteration |
| Logic gaps from hands-on testing | Team note (FB-13): gaps found in hands-on testing after the first full build are logged as FB/CR items and fixed in a polish iteration | Fix within the sprint that built the feature, if small |
| Supporter notifications | Only the reporter is notified | Also notify students who pressed "Me too" |
| Due date after reopen | Original due date kept (may show overdue) | Admin sets a new due date on Start work |
| Admin file access | Console twin `console:attachment` sharing the helper `send_attachment()` (Sprint 3) | One shared file URL for all roles |
| Super Admin acting on another department | No extra notification to that department's admins | Notify the department's admins when the Super Admin acts on their complaint |
| Login protection (FB-16) | No protection beyond Django's password checks; no code this sprint | First choice: a reCAPTCHA checkbox on the login page. Fallback: lock login for a few minutes after 5 failed attempts |

Instructor feedback and iteration changes are tracked in `08_iteration_log.md`.

## Change History

| Date | Change | Files |
|---|---|---|
| Oct 2026 | Documentation set created (v1) | All |
| Oct 2026 | v1.1: search scope (C-18, VR-14), system workflow diagram, colour palette, iteration log | 02, 03, 04, 05, 08 |
| Oct 2026 | v1.2: header spacing; verification fixes (see `09_verification_report.md`) | 01–08 |
| Oct 2026 | v1.3: ER diagram; supported-complaint limited view and reopen due-date behaviour confirmed by team | 06, 07 |
| Oct 2026 | v1.4 (CR-09): Sprint 1 pre-build fixes from the Claude Code review (I-17 to I-30): sprint coverage, User model details, file and partial names, CSS tokens and classes, Super Admin sidebar, search fields, room format, ER footnote, version tags | 00, 01, 02, 04, 05, 06, 07, 08, 09, `diagrams/er_diagram.*` |
| Oct 2026 | Sprint 1 review: login type tabs and VR-15 (CR-10), three-zone top bar (CR-11), review fixes I-31 to I-35 (error pages, fast test hasher) | 02, 04, 05, 07, 08, 09, 10 |
| Oct 2026 | Sprint 2 pre-build doc fixes (CR-12, I-36 to I-52): two-step S-02, limited view fields, 5-file limit, private files, `submit()`, new properties and URL, seed plan | 01, 02, 03, 04, 05, 06, 07, 08, 09, 10 |
| Oct 2026 | Sprint 2 review notes: layout density and logic-gap keep-in-view rows (FB-13); optional gender and default avatars planned for Sprint 3 (FB-14, CR-13); screenshots folder | 00, 05, 07, 08 |
| Oct 2026 | Sprint 3 build: notification messages for Reject and Resolved (`03` §4); OP-11 email copies (FB-18); FB-17 Reject reason dropdown as a Sprint 4 idea; `ALLOWED_FROM`, `NOTE_STATUSES`, `department_admins()`, console templates and Sprint 3 classes in `05`; TC-62 to TC-82 and the Sprint 3 manual checklist in `10`; Iteration 3 in `08`; screenshots retaken | 02, 03, 04, 05, 07, 08, 10, screenshots |
| Oct 2026 | Sprint 3 doc-first changes: optional gender and avatars, VR-16 (CR-13); NSU Navy chrome and tokens (CR-14); login protection kept in view (FB-16); Sprint 3 decisions; fixes I-54 to I-64 | 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, `diagrams/er_diagram.*` |
