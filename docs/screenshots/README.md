# UniFix Screenshots (Sprint 3)

Evidence of the current interface, taken from the local development server with fresh `seed_demo` data (headless Chrome, 1366 px wide; phone shots at 375 px, 2x). Branch `feature/sprint-3`, October 2026. Since Sprint 3 every page has the NSU Navy top bar and sidebar (CR-14), so the Sprint 2 shots were retaken; only the Django admin shots (`admin/04` to `admin/07`) are from Sprint 2, because the Django admin is unchanged.

Demo accounts: see the README ("Demo accounts").

## Public (P-01, P-02)

| File | Shows |
|---|---|
| `public/01-login-student-tab.png` | P-01 Login, Student tab (default) with the register link; gold underline accent on the active tab (CR-14) |
| `public/02-login-staff-tab.png` | P-01 Login, Staff tab: "Staff accounts are created by the Super Admin" |
| `public/03-login-wrong-tab-refused.png` | A student account on the Staff tab is refused (VR-15) |
| `public/04-register.png` | P-02 Student registration with the optional gender field (CR-13) |

## Student (S-01 to S-06), as Rafiq Hasan

| File | Shows |
|---|---|
| `student/01-home.png` | S-01 Home: cards, recent complaints, needs your action, latest notifications (Sprint 3) |
| `student/02-my-complaints.png` | S-03 My complaints: own and supported, status badges, overdue flags |
| `student/03-my-complaints-filtered.png` | S-03 filtered by status (In progress) |
| `student/04-new-complaint-step1.png` | S-02 step 1: category (grouped by department), building, room |
| `student/05-new-complaint-duplicate-match.png` | S-02 duplicate check: another student's open complaint with Me too (C-03) |
| `student/06-new-complaint-own-match.png` | S-02 duplicate check: own complaint labelled "You reported this" (VR-09) |
| `student/07-new-complaint-step2.png` | S-02 step 2: location read-only with Change; title, description, files |
| `student/08-new-complaint-file-refused.png` | A PDF renamed `.jpg` is refused; the text is kept (VR-07) |
| `student/09-detail-reporter-full-view.png` | S-04 full view for the reporter: evidence, proof of fix (C-07), timeline by department |
| `student/10-detail-supporter-limited-view.png` | S-04 limited view for a supporter: no description, files or names (VR-01) |
| `student/11-profile.png` | S-06 Profile with own avatar and the optional gender field (CR-13, VR-16) |
| `student/12-phone-home.png` | S-01 at phone width (NFR-05) |
| `student/13-phone-duplicate-match.png` | S-02 duplicate check at phone width |
| `student/14-notifications.png` | S-05 Notifications: unread highlighted, Mark all as read, bell count (C-11) |
| `student/15-detail-withdraw-confirm.png` | S-04 Withdraw confirmation on a Submitted complaint (C-10) |
| `student/16-phone-detail-proof-of-fix.png` | S-04 with proof of fix at phone width |
| `student/17-phone-notifications.png` | S-05 at phone width |

## Admin (A-01 to A-03, A-06, Django admin)

| File | Shows |
|---|---|
| `admin/01-dept-admin-dashboard.png` | A-01 Dept Admin (IT Services) placeholder with "Go to complaint queue" (content in Sprint 4) |
| `admin/02-dept-admin-student-page-403.png` | A Dept Admin opening a student page gets the friendly 403 |
| `admin/03-super-admin-dashboard.png` | A-01 Super Admin placeholder (all departments) |
| `admin/04-django-admin-home.png` | `/django-admin/` home (C-16) *(Sprint 2)* |
| `admin/05-django-admin-complaints.png` | Seeded complaints, read-only list *(Sprint 2)* |
| `admin/06-django-admin-complaint-readonly.png` | One complaint with its files, history and supporters, view only *(Sprint 2)* |
| `admin/07-django-admin-categories.png` | Categories and their routing departments *(Sprint 2)* |
| `admin/08-queue-dept-admin.png` | A-02 queue (IT Services): open complaints, soonest due first, filters |
| `admin/09-queue-overdue-filter.png` | A-02 "Overdue only" (Facilities Management): overdue rows flagged |
| `admin/10-queue-super-admin-all.png` | A-02 for the Super Admin: all departments and statuses, department filter |
| `admin/11-detail-submitted-action-bar.png` | A-03 on a Submitted complaint: Start review enabled, other buttons with "Available after …" hints; reporter card with the neutral avatar (VR-16) |
| `admin/12-detail-verify-form-open.png` | A-03 Verify inline form (priority, due date) opened without JavaScript |
| `admin/13-detail-verify-error.png` | Verify with today's date refused; the form stays open with the error (VR-05) |
| `admin/14-detail-resolve-form-open.png` | A-03 Mark resolved form (note, optional proof photo) on an overdue complaint; grouped Me too history |
| `admin/15-detail-resolved-proof-history.png` | A-03 after Resolve: proof of fix through `console:attachment`, history with names |
| `admin/16-detail-internal-note-add-note.png` | A-03 with an internal note (marked "Internal") and the Add note form (public or internal) |
| `admin/17-detail-super-admin-other-department.png` | The Super Admin on a Security complaint: full action bar (C-13), own note in the history |
| `admin/18-notifications.png` | A-06 Notifications for the Facilities admin |
| `admin/19-phone-queue.png` | A-02 at phone width: the table scrolls inside its card |
| `admin/20-phone-detail-actions.png` | A-03 at phone width with the Mark resolved form open |
