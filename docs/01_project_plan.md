# 01. Project Plan

## 1. Process Model: Hybrid (Waterfall planning + Agile build)

| Stage | Model | Why |
|---|---|---|
| Requirements and design | Waterfall-style | The course is assessed on complete documents (SRS, diagrams, mockups) before building, so these are finished and approved in sequence. |
| Implementation and testing | Agile (2-week sprints) | Features are built in small, demonstrable increments; instructor feedback can be absorbed between sprints without redesign. |

The foundation (workflow states and data dictionary) is fixed during the design stage, so later sprints can add or drop features without breaking it.

## 2. Phases and Milestones

| Phase | Work | Output |
|---|---|---|
| P0. Proposal | Topic, scope, initial UI concepts | Approved proposal (done) |
| P1. Requirements | Actors, features, rules, screen inventory | `02_requirements.md`, `04_screens.md`, SRS |
| P2. Design | Use case, class, ER, sequence, activity, state diagrams; mockups; data dictionary | `05`, `06`, diagram files, mockups |
| Sprint 1 | Project setup, custom User model, roles, login/register, profile and password change (C-15), departments and categories via Django admin, seed data (departments, categories, users) | Users can log in by role |
| Sprint 2 | Complaint submission with media, duplicate check and "Me too", routing, student pages (home, list, detail) | End-to-end student submission |
| Sprint 3 | Admin console: queue, complaint detail with 5 action buttons, verification with due date, resolve with proof photo, withdraw (C-10), history, notifications | Full complaint lifecycle |
| Sprint 4 | Confirm/reopen, rating, student records, Super Admin (users, reassign, reports), dashboards, search | All core features |
| P3. Testing and finalization | Test cases, bug fixes, demo script, final report, optional features if time allows | Final report and demo |

Sprint length and dates are set once the semester deadlines are confirmed.

## 3. Sprint Routine (lightweight Scrum for two people)

- **Sprint planning:** pick features (by C-xx ID) from the backlog in `02_requirements.md`.
- **Mid-sprint check-in:** a 15-minute sync on blockers.
- **Sprint review:** demo working pages to each other, and to the instructor when possible.
- **Retrospective:** one thing to keep, one thing to change, recorded in the sprint's iteration entry in `08_iteration_log.md` (§6).

## 4. Work Split (suggested, to be agreed)

Split by vertical slices rather than front end vs. back end, so both members understand the full stack:

| Slice | Owner |
|---|---|
| Accounts, roles, profiles, user records (C-01, C-12, C-15) | Member A |
| Complaint submission, duplicates, routing (C-02 to C-04) | Member B |
| Admin actions, workflow, notifications (C-05 to C-11) | Member A |
| Rating, Super Admin, reports, dashboards, search (C-13, C-14, C-17, C-18) | Member B |
| Testing and documentation | Both |

## 5. Git Workflow

- `main` always runs. Each feature gets a branch named `feature/c05-admin-actions` (feature ID + short name).
- Commit messages start with the ID: `C-05: add verify action and form`.
- If a change touches names, update `05_data_dictionary.md` in the same pull request.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Scope grows beyond two people | Core vs. optional split; keep-in-view items decided at sprint planning |
| Permission mistakes | Checks enforced in views, tested with VR test cases |
| Media uploads fail or are too large | Server-side type and size checks; small demo files |
| Super Admin adds too much work | Fallback: drop Super Admin, give Department Admins full control (see 07) |
