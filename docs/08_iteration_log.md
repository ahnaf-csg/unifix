# 08. Iteration Log

Tracks feedback and the changes it causes, iteration by iteration, so each phase can be compared with the last and nothing is lost when the plan changes.

## 1. How It Works

1. **Every piece of feedback gets an ID** (`FB-xx`): from the instructor, a teammate, testing or a demo.
2. **Each accepted change becomes a change request** (`CR-xx`) linked to the feedback and to the IDs it affects (C-xx, VR-xx, S-xx, UC-xx, model or field names).
3. **Impact is checked before work starts.** If a CR touches a foundation file (03 or 05), it is flagged so the diagrams in 06 are updated too.
4. **Status flow for each CR:** Proposed → Accepted / Deferred / Rejected → Done.
5. **Each iteration ends with a version tag** in Git and a summary of what changed. Planning iterations: `v0.1.x` (e.g. `v0.1.3-planning`). Code sprints: `v0.2-sprint1`, `v0.3-sprint2`, `v0.4-sprint3`, `v0.5-sprint4`. Final release: `v1.0`.

## 2. Versions

| Version | Iteration | Date | Summary |
|---|---|---|---|
| v0.0 | Proposal | Oct 2026 | Approved topic and initial proposal |
| v0.1 | Planning v1 | Oct 2026 | Documentation set, screens, data dictionary, mockups |
| v0.1.1 | Planning v1.1 | Oct 2026 | Search scope, system workflow, palette, this log |
| v0.1.2 | Planning v1.2 | Oct 2026 | Header spacing; full consistency verification and fixes |
| v0.1.3 | Planning v1.3 | Oct 2026 | ER diagram drawn for database planning |
| v0.1.4 | Planning v1.4 | Oct 2026 | Sprint 1 pre-build doc fixes (CR-09) |
| v0.2-sprint1 | Sprint 1 | Oct 2026 | Setup, accounts, roles, login/register, profile, Django admin, seed |
| v0.3-sprint2 | Sprint 2 | Oct 2026 | Complaint submission and student pages |
| v0.4-sprint3 | Sprint 3 | planned | Admin console and full lifecycle |
| v0.5-sprint4 | Sprint 4 | planned | Remaining core features |
| v1.0 | Final release | planned | Tested, documented, demo-ready |

## 3. Feedback Register

| ID | Date | Source | Feedback | Linked CRs |
|---|---|---|---|---|
| FB-01 | Oct 2026 | Instructor | Admin should be able to check user records | CR-01 |
| FB-02 | Oct 2026 | Instructor | Admin side needs more work (e.g. a Resolved button) | CR-02 |
| FB-03 | Oct 2026 | Instructor | Show features through every page instead of a requirements table | CR-03 |
| FB-04 | Oct 2026 | Team | Define how search works for each role | CR-04 |
| FB-05 | Oct 2026 | Team | Colour scheme should go beyond white while staying simple | CR-05 |
| FB-06 | Oct 2026 | Team | Top area of screens feels cluttered | CR-06 |
| FB-07 | Oct 2026 | Team | Verify all documents are aligned before building | CR-07 |
| FB-08 | Oct 2026 | Team | Plan the database visually before creating demo data | CR-08 |
| FB-09 | Oct 2026 | Claude Code review | Pre-build review found gaps: sprint coverage, User model details, missing file names, CSS not reusable, sidebar, search fields, room format, ER footnote, tag scheme | CR-09 |
| FB-10 | Oct 2026 | Team (Sprint 1 review) | Students and staff should choose how they log in; staff should not see the register link | CR-10 |
| FB-11 | Oct 2026 | Team (Sprint 1 review) | Top bar should show the NSU logo, with the UniFix wordmark centred and tools on the right | CR-11 |
| FB-12 | Oct 2026 | Claude Code review + team (Sprint 2 planning) | Pre-build review found gaps for Sprint 2 (submit method, limited view, private files, file limits, notifications timing, timeline privacy); team chose a two-step S-02 so files upload once | CR-12 |
| FB-13 | Oct 2026 | Team (Sprint 2 review) | Pages with many buttons feel cluttered; logic gaps will surface in hands-on testing after the first full build | – (keep in view in `07`; polish iteration) |
| FB-14 | Oct 2026 | Team (Sprint 2 review) | Optional gender at registration (male, female, other, prefer not to say) with generic default avatars (neutral for other / prefer not to say) | CR-13 |
| FB-15 | Oct 2026 | Team (Sprint 3 planning) | Use NSU colours: top bar and sidebar in NSU Navy with white text; NSU Gold only as a small accent | CR-14 |
| FB-16 | Oct 2026 | Team (Sprint 3 planning) | Protect the login page against repeated guessing (reCAPTCHA checkbox first; fallback: lock login for a few minutes after 5 failed attempts) | – (keep in view in `07`; no code this sprint) |

## 4. Change Requests

| ID | From | Change | Affects | Status |
|---|---|---|---|---|
| CR-01 | FB-01 | User records with full Super Admin control, view-only for Dept Admins | C-12, VR-12, A-04, A-05, SA-02, SA-03, `User.account_state` | Done (planning) |
| CR-02 | FB-02 | One button per workflow step with inline forms | C-05, A-03, `03_workflow.md` §2, §4 | Done (planning) |
| CR-03 | FB-03 | Screen inventory and mockups for every page | `04_screens.md`, mockups | In progress (4 of 18 mocked) |
| CR-04 | FB-04 | Role-scoped search via list pages | C-18, VR-14, `04_screens.md` | Done (planning) |
| CR-05 | FB-05 | Navy chrome, tinted background, accented cards | `05` §6, `unifix.css` | Done (planning) |
| CR-06 | FB-06 | More spacing in top bar and page header | `unifix.css`, mockups | Done (keep in view) |
| CR-07 | FB-07 | Consistency fixes from the verification pass | 01–06, mockups; see `09_verification_report.md` | Done (planning) |
| CR-08 | FB-08 | ER diagram with keys and cardinalities, matching `05` §3 | `06` §3, `diagrams/er_diagram.*` | Done (planning) |
| CR-09 | FB-09 | Sprint 1 pre-build doc fixes (`09` I-17 to I-30) | C-10, C-15, C-16, C-18, VR-11, S-03, `User`, `Complaint.room`, `Complaint.tracking_id`, `05` §2, §5–7, `06` §3, `diagrams/er_diagram.*` | Done (planning) |
| CR-10 | FB-10 | Student/Staff tabs on P-01; wrong tab refused | P-01, VR-15, `login_type` (`05` §3), tab classes (`05` §5), TC-30 to TC-34 | Done (Sprint 1) |
| CR-11 | FB-11 | Three-zone top bar with NSU logo. *Amended (clarified by team):* NSU logo moves to the centre beside the wordmark, replacing the "U" square; left zone left empty | `04` Layout, `static/img/nsu_logo.png`, top bar classes (`05` §5) | Done (Sprint 1, amended) |
| CR-12 | FB-12 | Sprint 2 pre-build doc fixes (`09` I-36 to I-52) and decisions (`07`): two-step S-02, `submit()`, limited view fields and actor naming, 5-file limit, private files via `student:attachment`, `Notification` now, seed plan | C-02, C-03, C-06, VR-01, VR-07, VR-09, NFR-03, S-01 to S-04, `Complaint.submit()`, `tracking_id`, `location`, `status_badge_class`, `Attachment.file`, `03` §0, §4, §6, `05` §3, §4, §7, `06` §4 | Done (Sprint 2) |
| CR-13 | FB-14 | Optional gender at registration and on the profile: `User.gender` (`male`, `female`, `other`, `prefer_not_to_say` by default), `User.avatar_kind`, three SVG avatars (`static/img/avatars/`), `partials/avatar.html`. Gender-based avatars only for the user themselves; everyone else sees the neutral avatar (VR-16). Extends C-01 and C-15 | C-01, C-15, VR-16, P-02, S-06, A-03, top bar (`04` Layout), `User` (`05` §3), `06` §2–3, `diagrams/er_diagram.*` | Accepted (Sprint 3) |
| CR-14 | FB-15 | NSU Navy `#002f6c` top bar and sidebar with white text, logo on a white tile, light blue-grey subtitle; NSU Gold `#FEC937` as an accent only; IEEE blue not used; badge colours unchanged. Replaces CR-11's white top bar | `04` Layout, P-01, `05` §6 tokens, `unifix.css` | Accepted (Sprint 3) |

## 5. Iteration Template

Copy this block for each new iteration.

```
### Iteration N (vX.Y): <dates>
Goal:
Feedback received: FB-..
Change requests: CR-.. (accepted), CR-.. (deferred)
Foundation touched (03/05)? yes/no → diagrams updated?
Built / changed:
Carried over to next iteration:
Retrospective: keep … / change …
```

## 6. Iterations

### Iteration 1 (v0.2-sprint1): Oct 2026
Goal: users can log in by role.
Feedback received: FB-09 (pre-build review), FB-10, FB-11 (Sprint 1 review)
Change requests: CR-09 (done before coding), CR-10, CR-11 (done in the review round)
Foundation touched (03/05)? yes, 05 in CR-09 → ER diagram footnote updated
Built / changed: project setup; `accounts.User`; `Department`, `Category`; login, logout, register; role redirect; profile and password change; base layout and stylesheet; `seed_demo`; 25 tests, 35 after the review round (`10_test_plan.md`)
Carried over to next iteration: `User.can_view_complaint()` (needs `Complaint`, Sprint 2); complaints in `seed_demo` (Sprints 2–3)
Retrospective: Keep: plan checkpoint before building. Change: confirm UI placement details with a sketch before implementing.

### Iteration 2 (v0.3-sprint2): Oct 2026
Goal: end-to-end student submission.
Feedback received: FB-12 (Sprint 2 pre-build review; team chose the two-step S-02 and asked for file-safety checks at the halfway checkpoint); FB-13, FB-14 (Sprint 2 review)
Change requests: CR-12 (doc fixes done before coding)
Foundation touched (03/05)? yes, 03 §0, §4, §6 and 05 §2–5, §7 → system workflow figure (two-step submission, login tabs) and ER diagram (`tracking_id` set after insert, `is_staff`/`is_superuser`, full footnote) updated
Built / changed: `Complaint`, `Attachment`, `ComplaintUpdate`, `Support`, `Notification`; `submit()` with routing, history, notifications and file clean-up; VR-07 content-based file checks; `find_duplicates()`, `support()`; `can_view_complaint()` and the access helpers; two-step S-02, S-01, S-03, S-04, private file view; read-only admin; seed complaints in every status; 26 tests (TC-36 to TC-61, 61 in total)
Carried over to next iteration: admin console and action methods (Sprint 3); `allowed_actions(user)`; console twin of `student:attachment`; notifications list and bell count; seed to call the real action methods; refresh the S-02 mockup; CR-13 (optional gender, default avatars) in the Sprint 3 doc-first commit
Retrospective: To be written after the first full draft.

### Iteration 3 (v0.4-sprint3): Oct 2026
Goal: full complaint lifecycle up to Resolved, run from the admin console.
Feedback received: FB-15 (NSU colours), FB-16 (login protection, kept in view)
Change requests: CR-13, CR-14 (doc-first commit before coding)
Foundation touched (03/05)? yes, 03 §2, §4 and 05 §1–7 → ER diagram (`User.gender`) and class blueprint enumerations updated
Built / changed: (in progress)
Carried over to next iteration: (in progress)
Retrospective: To be written after the first full draft.

## 7. Suggested GitHub Practice

- One GitHub Issue per CR, titled `CR-xx: …`, labelled `feedback`, `foundation` (if 03/05 change) and the sprint.
- Pull requests reference the CR (`Closes #12, CR-06`).
- Tag each iteration (`git tag v0.2-sprint1`) so any earlier version can be shown or restored.
