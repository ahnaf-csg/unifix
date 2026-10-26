# UniFix Screenshots (Sprint 2)

Evidence of the current interface, taken from the local development server with `seed_demo` data (Chrome, 1366 px wide; phone shots at 375 px). Branch `feature/sprint-2`, October 2026.

Demo accounts: see the README ("Demo accounts").

## Public (P-01, P-02)

| File | Shows |
|---|---|
| `public/01-login-student-tab.png` | P-01 Login, Student tab (default) with the register link |
| `public/02-login-staff-tab.png` | P-01 Login, Staff tab: "Staff accounts are created by the Super Admin" |
| `public/03-login-wrong-tab-refused.png` | A student account on the Staff tab is refused (VR-15) |
| `public/04-register.png` | P-02 Student registration |

## Student (S-01 to S-04, S-06), as Rafiq Hasan

| File | Shows |
|---|---|
| `student/01-home.png` | S-01 Home: cards, recent complaints, needs your action |
| `student/02-my-complaints.png` | S-03 My complaints: own and supported, status badges, overdue flags |
| `student/03-my-complaints-filtered.png` | S-03 filtered by status (In progress) |
| `student/04-new-complaint-step1.png` | S-02 step 1: category (grouped by department), building, room |
| `student/05-new-complaint-duplicate-match.png` | S-02 duplicate check: another student's open complaint with Me too (C-03) |
| `student/06-new-complaint-own-match.png` | S-02 duplicate check: own complaint labelled "You reported this" (VR-09) |
| `student/07-new-complaint-step2.png` | S-02 step 2: location read-only with Change; title, description, files |
| `student/08-new-complaint-file-refused.png` | A PDF renamed `.jpg` is refused; the text is kept (VR-07) |
| `student/09-detail-reporter-full-view.png` | S-04 full view for the reporter: description, evidence, timeline by department |
| `student/10-detail-supporter-limited-view.png` | S-04 limited view for a supporter: no description, files or names (VR-01) |
| `student/11-profile.png` | S-06 Profile and password change |
| `student/12-phone-home.png` | S-01 at phone width (NFR-05) |
| `student/13-phone-duplicate-match.png` | S-02 duplicate check at phone width |

## Admin (A-01 placeholder, Django admin)

The admin console (queue, actions) arrives in Sprint 3; these show what exists now.

| File | Shows |
|---|---|
| `admin/01-dept-admin-dashboard.png` | A-01 Dept Admin (IT Services) placeholder dashboard |
| `admin/02-dept-admin-student-page-403.png` | A Dept Admin opening a student page gets the friendly 403 |
| `admin/03-super-admin-dashboard.png` | A-01 Super Admin placeholder dashboard (all departments) |
| `admin/04-django-admin-home.png` | `/django-admin/` home (C-16) |
| `admin/05-django-admin-complaints.png` | Seeded complaints, read-only list |
| `admin/06-django-admin-complaint-readonly.png` | One complaint with its files, history and supporters, view only |
| `admin/07-django-admin-categories.png` | Categories and their routing departments |
