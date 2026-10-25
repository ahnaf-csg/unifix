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
| v0.2-sprint1 | Sprint 1 | planned | Setup, accounts, roles, login/register, profile, Django admin, seed |
| v0.3-sprint2 | Sprint 2 | planned | Complaint submission and student pages |
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
Feedback received: FB-09 (pre-build review)
Change requests: CR-09 (accepted, done before coding)
Foundation touched (03/05)? yes, 05 in CR-09 → ER diagram footnote updated
Built / changed: project setup; `accounts.User`; `Department`, `Category`; login, logout, register; role redirect; profile and password change; base layout and stylesheet; `seed_demo`; 25 tests (`10_test_plan.md`)
Carried over to next iteration: `User.can_view_complaint()` (needs `Complaint`, Sprint 2); complaints in `seed_demo` (Sprints 2–3)
Retrospective: keep … / change … (to be filled in at the sprint review)

## 7. Suggested GitHub Practice

- One GitHub Issue per CR, titled `CR-xx: …`, labelled `feedback`, `foundation` (if 03/05 change) and the sprint.
- Pull requests reference the CR (`Closes #12, CR-06`).
- Tag each iteration (`git tag v0.2-sprint1`) so any earlier version can be shown or restored.
