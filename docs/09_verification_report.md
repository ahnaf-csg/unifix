# 09. Verification Report

Purpose: confirm that requirements, workflow, screens, data dictionary, diagrams, mockups and logs agree with each other before building. Re-run before every build phase and after any change to `03` or `05`.

## 1. Method

| # | Check | How | Result |
|---|---|---|---|
| V-01 | Every referenced ID (C, OP, VR, NFR, UC, FB, CR, screen) is defined | Automated scan of all files | Pass (after fixes) |
| V-02 | Every URL name used in `04` exists in `05` | Automated | Pass |
| V-03 | Every status in `03` has a badge class in `05` | Automated | Pass |
| V-04 | Every `ComplaintUpdate` action used in `03` is a choice in `05` | Automated | Pass (after adding `support`) |
| V-05 | Every field set in `03` §4 exists in `05` | Automated | Pass |
| V-06 | Button → URL slug → method → history action → status agree | Manual, action mapping table in `05` | Pass (after renaming `mark_resolved` to `resolve`) |
| V-07 | Permissions matrix agrees with validation rules and screens | Manual | Pass (after fixing VR-01) |
| V-08 | Notification recipients agree between C-11 and `03` §4 | Manual | Pass (after rewording C-11) |
| V-09 | Dashboard contents in `02` match `04` and the mockups | Manual | Pass (after adding missing items) |
| V-10 | Mockups only show data and buttons allowed by the rules | Manual | Pass (after removing "View details" from S-02) |
| V-11 | Every core feature traces to screens, rules, use cases and model elements | Traceability matrix (§3) | Pass |
| V-12 | Workflow diagram, transitions table, state diagram and status list agree | Manual | Pass |
| V-13 | Plan sprints cover every core feature | Manual | Pass (after adding C-18 to Sprint 4, and C-15 to Sprint 1 and C-10 to Sprint 3 in CR-09) |

## 2. Issues Found and Fixed

| # | Issue | Severity | Fix | Files |
|---|---|---|---|---|
| I-01 | Students could open supported complaints and duplicate matches, contradicting "students only see their own complaints" | High | VR-01 now defines a limited view for supported and duplicate complaints; "View details" removed from S-02 mockup | 02, 04, mockup S-02 |
| I-02 | Mockup history showed "Me too" entries, but supporting created no history record | Medium | Added `support` action; Me too writes a `ComplaintUpdate` | 03, 05, 06 |
| I-03 | Method `mark_resolved()` did not match URL slug `resolve` and history action `resolve` | Medium | Method renamed to `resolve()`; full action mapping table added | 05, 06 |
| I-04 | No model methods for Me too and Rate, though both are student actions | Medium | Added `support()` and `rate()`; added `find_duplicates()` | 05 |
| I-05 | Missing URLs: password change, mark all notifications read, create admin user | Medium | Added `accounts:password_change`, `notifications:mark_all_read`, `console:user_create` | 04, 05 |
| I-06 | Student-facing views had no home in the project structure | Medium | Placed in `complaints` app under the `student` namespace | 05 |
| I-07 | Custom user model did not say how email login works | Medium | `USERNAME_FIELD = "email"`; `full_name` replaces first/last name | 05 |
| I-08 | Duplicate rule was vague ("category and location") | Medium | Exact rule defined (category, building, normalized room, open status) | 03 |
| I-09 | C-11 notification recipients were narrower than `03` §4 | Low | C-11 reworded to match | 02 |
| I-10 | Dashboard spec missing items shown in mockups (supported card, notifications panel, reopened column, metric definitions) | Low | Spec updated; metrics defined | 02, 04 |
| I-11 | "Students affected" (mockups) vs "support count" (docs) | Low | Added `affected_count` = supporters + reporter | 02, 03, 05 |
| I-12 | Reopened complaints keep the old due date; behaviour was undocumented | Low | Documented in `03` §7; alternative added to keep-in-view | 03, 07 |
| I-13 | Search had no use case; Rating missing its User relationship in the ER diagram; Building enum missing | Low | UC-23 added; ER and class blueprint updated | 06 |
| I-14 | C-18 (search) not assigned to any sprint or person | Low | Added to Sprint 4 and the work split | 01 |
| I-15 | No seed data defined, though mockups and demo rely on it | Low | Seed departments, categories and demo accounts defined | 05 |
| I-16 | Example ID `CR-06` in the GitHub section clashed with real CR numbering | Low | Changed to `CR-xx` | 08 |
| I-17 | C-10 Withdraw and C-15 Profile had owners but no sprint; V-13 had been marked Pass | Medium | C-15 added to Sprint 1, C-10 to Sprint 3; V-13 note updated | 01, 09 |
| I-18 | `seed_demo` was described as seeding complaints, which do not exist until Sprint 2 | Low | Seed grows by sprint: Sprint 1 departments, categories, accounts | 05 |
| I-19 | Unclear whether inherited `username`, `first_name`, `last_name` are removed or left unused | Medium | Removed; custom `UserManager`; `REQUIRED_FIELDS = ["full_name"]` | 05 |
| I-20 | No names for the permission module, seed command or template partials | Medium | Added `accounts/permissions.py`, `seed_demo.py` path, `partials/topbar.html`, `sidebar.html`, `messages.html`, `status_badge.html` | 04, 05 |
| I-21 | Nobody was given access to the Django admin panel needed for C-16 | Medium | Super Admin accounts get `is_staff` and `is_superuser`; permissions matrix row added | 02, 05 |
| I-22 | `student_id` "unique when present" would clash on blank values for admins | Medium | Stored as NULL when empty (`null=True, blank=True, unique=True`), matching the ER diagram | 05 |
| I-23 | Mockup CSS is fixed-size (not responsive), lacks `badge-withdrawn`, repeats `:root`, and uses tokens and classes not in `05` | Medium | `05` §5–6 list all tokens, priority and component classes; `00` no longer says the mockup CSS is reused as-is | 00, 05 |
| I-24 | Super Admin could see all students on A-04 but had no sidebar link to it | Low | Students added to the Super Admin sidebar | 04 |
| I-25 | S-03 searched by title or tracking ID, but the Search table also matched room | Low | S-03 searches tracking ID, title or room | 04 |
| I-26 | `room` examples repeated the building ("NAC 512"), clashing with the separate `building` field and hotspot grouping | Low | `room` stores the label only (`512`, `L3`); pages show building + room; hotspots group by building + room; building labels defined | 05 |
| I-27 | ER diagram did not mention the undrawn `ComplaintUpdate.from_department` / `to_department` relationship | Low | Added to the figure footnote and the `06` caption | 06, diagrams |
| I-28 | VR-11 asks for an "Account inactive" message, but Django's default backend shows a generic login error | Low | `AllowAllUsersModelBackend` with the check in `confirm_login_allowed()` | 05 |
| I-29 | The notification bell's unread count depends on notifications, which are built in Sprint 3 | Low | Bell shown without a count until Sprint 3 | 04 |
| I-30 | Tag scheme in `08` (`v0.1-iter1`) differed from the real tag (`v0.1.3-planning`); tracking ID generation unspecified | Low | Tag scheme defined (planning `v0.1.x`, sprints `v0.2-sprint1` … , final `v1.0`); tracking ID = `UF-` + zero-padded pk | 05, 07, 08 |
| I-31 | After a failed profile save, the top bar showed the unsaved name | Low | Profile form edits a fresh copy of the user, not `request.user` | `accounts/views.py` |
| I-32 | `.claude/` (local tool config and worktrees) was not ignored by Git | Low | Added to `.gitignore` | `.gitignore` |
| I-33 | Test suite took about 50 s because of password hashing | Low | MD5 hasher when running tests only | `unifix/settings.py` |
| I-34 | 403 and 404 showed Django's plain pages with no way back | Low | `403.html` and `404.html` extend `base.html` with a link home | 04, 05, templates |
| I-35 | `/` routing by role was untested | Low | Verified correct (via the login page); test added | `accounts/tests.py` |
| I-36 | C-03 pointed to `03` §5 for the duplicate rule; the rule is in §6 | Low | Reference fixed | 02 |
| I-37 | VR-01's limited view omitted due date, students affected and date reported, which S-02 and its mockup show; the description was not mentioned | Medium | VR-01 lists the exact fields; no description | 02, 04 |
| I-38 | Submit had no model method, though `03` §4 and CLAUDE.md require one; the action mapping had no Submit row | Medium | `Complaint.submit()` added; Submit row in the action mapping | 05 |
| I-39 | S-02 writes a Notification, but notifications were planned for Sprint 3 | Medium | `Notification` model built in Sprint 2; list and bell stay in Sprint 3 | 07 |
| I-40 | S-01 read only Complaint and Rating, but shows supported complaints and notifications; Rate items need `Rating` (Sprint 4) | Low | Reads Support and Notification too; staged build noted | 04 |
| I-41 | The public timeline would name the reporter and other supporters, conflicting with VR-01 | Medium | Student pages name actors by role or department only | 02, 04 |
| I-42 | `support()` did not say whether closed complaints can be supported; own complaints among duplicate matches were not covered | Medium | Open statuses only (VR-09); own and supported matches labelled, without Me too | 02, 03, 04 |
| I-43 | `tracking_id` is unique and built from the primary key, which does not exist before the first insert | Low | Field is nullable; `save()` fills it right after the insert in the same transaction | 05 |
| I-44 | NFR-03 keeps attachments private, but nothing said how files are served; `05` §4 had no file URL | High | Files sent only by `student:attachment` after a permission check; random names on disk | 02, 05 |
| I-45 | VR-07 had no limit on the number of files | Low | At most 5 files per complaint | 02, 05 |
| I-46 | Badge classes use hyphens (`badge-under-review`) but status values use underscores; no name for the mapping | Low | `Complaint.status_badge_class` property | 05 |
| I-47 | "NAC 512" display had no property name; the S-02 mockup puts "SAC 304" in the Room box and labels the building "SAC – South Academic Building" | Low | `Complaint.location` property; mockup refresh noted in §4 | 05, 09 |
| I-48 | C-06 and `03` §5 defined overdue in different words | Low | C-06 refers to `03` §5 | 02 |
| I-49 | `08` Iteration 1 said 25 tests (35 after the review round); `v0.2-sprint1` still "planned"; README status said Sprint 1 | Low | Corrected | 08, README |
| I-50 | `01` §3 said retrospectives go in `07`; they are recorded in `08` iteration entries | Low | Corrected | 01 |
| I-51 | Nothing said whether inactive categories or departments can receive complaints | Low | S-02 lists active categories only; Submit re-checks | 03, 04 |
| I-52 | S-02 mockup shows a Remove link per file, which a plain file input cannot do | Low | One "Clear files" link | 04, 07 |
| I-53 | Opening a complaint in the Django admin crashed (`FieldError`): the read-only inlines listed auto-set fields such as `uploaded_at`. Found while taking screenshots | Medium | Inline fields are all read-only; TC-61 | `complaints/admin.py` |

## 3. Traceability Matrix

| Feature | Screens | Rules | Use cases | Model elements |
|---|---|---|---|---|
| C-01 Accounts and roles | P-01, P-02 | VR-11, VR-13, VR-15 | UC-01, UC-02 | `User.role`, `account_state`, `login_type` |
| C-02 Submission | S-02 | VR-07, VR-08 | UC-03 | `Complaint.submit()`, `Attachment` |
| C-03 Duplicates and Me too | S-02, S-03 | VR-01, VR-09 | UC-04, UC-05 | `find_duplicates()`, `support()`, `Support` |
| C-04 Routing | S-02, A-02 | VR-02 | UC-03 | `Complaint.department`, `Category.department` |
| C-05 Action buttons | A-03 | VR-02, VR-03 | UC-11 to UC-16 | Action mapping (`05`) |
| C-06 Verify, priority, due date | A-03, A-01, A-02 | VR-05 | UC-12 | `verify()`, `priority`, `due_date`, `is_overdue` |
| C-07 Resolve with proof | A-03, S-04 | VR-04 | UC-15 | `resolve()`, `Attachment.kind=proof_of_fix` |
| C-08 History | S-04, A-03 | VR-01 | UC-06, UC-16 | `ComplaintUpdate` |
| C-09 Confirm or reopen | S-01, S-04 | VR-04, VR-06 | UC-07, UC-08 | `confirm()`, `reopen()`, `can_reopen` |
| C-10 Withdraw | S-04 | VR-03 | UC-10 | `withdraw()` |
| C-11 Notifications | S-05, A-06 | VR-01, VR-02 | UC-21 | `Notification` |
| C-12 User records | A-04, A-05, SA-02, SA-03 | VR-11, VR-12 | UC-17, UC-18 | `User.suspend()`, `soft_delete()` |
| C-13 Super Admin control | A-03, A-02 | VR-12 | UC-19 | `reassign()` |
| C-14 Dashboards | S-01, A-01, SA-01 | VR-01, VR-02 | UC-20 | Aggregates over `Complaint`, `Rating` |
| C-15 Profile | S-06, A-07 | – | UC-22 | `User` |
| C-16 Setup | Django admin | – | – | `Department`, `Category` |
| C-17 Rating | S-01, S-04 | VR-10 | UC-09 | `rate()`, `Rating` |
| C-18 Search | Top bar → S-03, A-02, A-04, SA-02 | VR-14 | UC-23 | Query filters (`icontains`) |

## 4. Remaining Open Items (decided later, not inconsistencies)

- Keep-in-view items in `07_decision_log.md` (Super Admin fallback, soft delete, withdraw, rating, charts, search extension, header spacing, supporter notifications, due date after reopen).
- 14 of 18 screens still need mockups (CR-03). Existing mockups predate CR-09: the S-01/S-02 search placeholder omits room, the SA-01 sidebar has no Students link, and class names are draft names; they are refreshed when the remaining mockups are drawn.
- Sprint dates depend on semester deadlines.
- The submitted proposal (v2 PDF) predates these decisions and is superseded by this documentation set.
- Course diagrams (use case, class, ER, sequence, activity) still to be drawn from `06`.
- CR-12 follow-up for the next mockup update: the S-02 mockup shows one combined form, a Room value with the building, a long building label and per-file Remove links.

## 5. How to Re-run

1. Run the automated checks (V-01 to V-05) with the verification script kept alongside these docs.
2. Walk through the manual checks V-06 to V-13 for any section that changed.
3. Log new issues here as I-54, I-55, … and link fixes to a CR in `08_iteration_log.md`.
