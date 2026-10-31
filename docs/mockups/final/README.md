# UniFix Screens: Screenshots and Final Mockups (CR-03, CR-15)

Every main page of the finished product, one table for the report. Built pages are **real** screenshots of `main` at `v0.4-sprint3` (`docs/screenshots/`, headless Chrome, 1366 px). Pages and states not built yet are **mockups**: the real page chrome (`base.html`, NSU Navy top bar and sidebar, CR-14) rendered from the app for the right role, with static content using the existing classes. They link the real `static/css/unifix.css`; the few new rules are in `mockup.css` here, for Sprints 4–5 to port. Mockup PNGs are 1440 px wide, full page; phone versions are 375 px at 2×.

**Caption rule:** every mockup is labelled "Mockup — built in Sprint 4/5" (the sprint that builds it), both in the report caption and on the page itself. The mockups are the spec Sprints 4 and 5 must match.

Data: the `seed_demo` data as of 31 Oct 2026 plus the Sprint 4 seed additions below. Every figure is counted from that data, and pages agree with each other (e.g. the A-01 Overdue card counts the rows of its Overdue table).

## Screens

| Screen | Title | Image | Source | Sprint | US | C |
|---|---|---|---|---|---|---|
| P-01 | Login (Student and Staff tabs) | `../../screenshots/public/01-login-student-tab.png`, `02-login-staff-tab.png`, `03-login-wrong-tab-refused.png` | Real | 1 | US-01 | C-01 |
| P-02 | Register | `../../screenshots/public/04-register.png` | Real | 1 (gender 3) | US-05 | C-01 |
| S-01 | Student home | `../../screenshots/student/01-home.png`, `12-phone-home.png` | Real | 2–3 | US-09, US-03 | C-14, C-11 |
| S-01 | Home with Needs your action: Confirm/Reopen and Rate | `10-s01-home-needs-action.png` | Mockup — built in Sprint 4 | 4 | US-11, US-12, US-13 | C-09, C-17 |
| S-02 | New complaint (steps, duplicate check, files) | `../../screenshots/student/04` to `08`, `13-phone-duplicate-match.png` | Real | 2 | US-06, US-07, US-08 | C-02, C-03, C-04 |
| S-03 | My complaints | `../../screenshots/student/02-my-complaints.png`, `03-my-complaints-filtered.png` | Real | 2 | US-09, US-04 | C-08, C-18 |
| S-04 | Complaint detail (reporter, supporter, Withdraw) | `../../screenshots/student/09`, `10`, `15`, `16-phone-detail-proof-of-fix.png` | Real | 2–3 | US-09, US-10 | C-08, C-10 |
| S-04 | Resolved: Confirm fix and Reopen (reason form open) | `11-s04-resolved-confirm-reopen.png`, `11-s04-resolved-confirm-reopen-phone.png` | Mockup — built in Sprint 4 | 4 | US-11, US-12 | C-09 |
| S-04 | Closed: Rate form | `12-s04-closed-rate.png` | Mockup — built in Sprint 4 | 4 | US-13 | C-17 |
| S-05 | Notifications | `../../screenshots/student/14-notifications.png`, `17-phone-notifications.png` | Real | 3 | US-03 | C-11 |
| S-06 | Profile | `../../screenshots/student/11-profile.png` | Real | 1 (gender 3) | US-02 | C-15 |
| A-01 | Dept Admin dashboard: cards, 3 tables, 3 charts | `01-a01-dept-admin-dashboard.png`, `01-a01-dept-admin-dashboard-phone.png` | Mockup — built in Sprint 4 (cards, tables) and Sprint 5 (charts) | 4–5 | US-22 | C-14 |
| A-01 | Super Admin dashboard (all departments) | `02-a01-super-admin-dashboard.png` | Mockup — built in Sprint 4 (cards, tables) and Sprint 5 (charts) | 4–5 | US-22 | C-14 |
| A-02 | Complaint queue | `../../screenshots/admin/08`, `09`, `10`, `19-phone-queue.png` | Real | 3 | US-14, US-24 | C-05, C-13 |
| A-02 / A-04 | Top-bar search results, Complaints tab (Dept Admin) | `13-search-complaints-tab.png` | Mockup — built in Sprint 5 | 5 | US-04 | C-18 |
| A-02 / A-04 | Top-bar search results, Students tab (Dept Admin) | `14-search-students-tab.png` | Mockup — built in Sprint 5 | 5 | US-04 | C-18 |
| A-03 | Complaint detail and actions | `../../screenshots/admin/11` to `17`, `20-phone-detail-actions.png` | Real | 3 | US-15 to US-21, US-24 | C-05 to C-08, C-13 |
| A-03 | Super Admin with Reassign open | `03-a03-super-admin-reassign.png` | Mockup — built in Sprint 4 | 4 | US-25 | C-13 |
| A-03 | Under review with the Reject reason list open (FB-17) | `04-a03-under-review-reject.png` | Mockup — built in Sprint 4 | 4 | US-17 | C-05 |
| A-04 | Students (Dept Admin) | `05-a04-students.png` | Mockup — built in Sprint 4 | 4 | US-23 | C-12 |
| A-05 | Student detail (Super Admin: Edit, Suspend, Delete) | `06-a05-student-detail.png` | Mockup — built in Sprint 4 | 4 | US-23, US-26 | C-12 |
| A-06 | Notifications (admin) | `../../screenshots/admin/18-notifications.png` | Real | 3 | US-03 | C-11 |
| A-07 | Profile (admin) | `../../screenshots/admin/21-profile.png` | Real | 1 (gender 3) | US-02 | C-15 |
| SA-01 | Reports: cards, scorecard, hotspots, suspended users, 3 charts, date filter | `07-sa01-reports.png`, `07-sa01-reports-phone.png` | Mockup — built in Sprint 5 | 5 | US-27 | C-14 |
| SA-02 | Users | `08-sa02-users.png` | Mockup — built in Sprint 4 | 4 | US-26 | C-12 |
| SA-03 | Add admin | `09-sa03-add-admin.png` | Mockup — built in Sprint 4 | 4 | US-26 | C-12 |
| – | Django admin: departments and categories | `../../screenshots/admin/04` to `07` | Real | 1–2 | US-28 | C-16 |

## Sprint 4 seed additions (required)

The mockups rely on these; `seed_demo` must create them in Sprint 4 (through the real workflow methods), so that the built pages match the mockups.

| # | Addition | Where it shows |
|---|---|---|
| 1 | **UF-0003** (Broken chair armrest, Facilities Management) is verified by Nusrat Karim: priority Medium, due **today + 2 days** (2 Nov in the mockups). It is the Facilities complaint due within the next 3 days | A-01 (Due in next 3 days), A-02 search, A-05, S-01 (Verified, latest notification "UF-0003 is now Verified", bell 1) |
| 2 | **UF-0013** (Power socket sparks, Facilities Management, Closed) is rated **4 stars** by its reporter Zubair Ahmed, comment "Fixed the same day. Thank you." | A-01 and SA-01 Average rating 4.0 (1 rating), SA-01 scorecard; Facilities admin bell 9 (8 seed + "UF-0013 was rated") |
| 3 | **Arif Mahmud** (student, no complaints) is **suspended** | SA-01 Recently suspended users and Active students 9 (1 suspended), SA-02 Users |
| 4 | **UF-0012** (Projector remote missing, IT Services) gets **Start review** by Farhan Kabir, so it is Under review | A-03 Reject mockup; A-01 Super Admin By status (Under review 1) |

Not shown anywhere: complaints and actions entered by hand in a local database (UF-0015, UF-0016 and the 31 Oct test actions on UF-0012 and UF-0014). UF-0014 is shown in its seed state (In progress, overdue since 30 Oct).

## Definitions used for the figures

As in `02` §4 (CR-15): New = `submitted`; In progress = `in_progress`; Overdue as in `03` §5; Resolved this week = `resolved_at` in the last 7 days; average resolution time = mean of (`resolved_at` − `created_at`) in days for complaints resolved in the period; average rating = mean `stars`. Most supported lists open complaints with at least one supporter, by students affected. The weekly trend counts new complaints per week (Monday start), last 8 weeks; the monthly trend counts submitted and resolved complaints per month in the SA-01 period (default: last 6 months). Hotspots: building + room, ordered by number of complaints, then most recent.

## Checked against `04_screens.md` and the rules (V-10)

| Mockup | Check |
|---|---|
| 01, 02 A-01 | Cards, 3 tables and 3 charts as in `02` §4; cards and rows link to A-02 filtered or A-03; Dept Admin sees own department only (VR-02); no gender (VR-16) |
| 03 A-03 Reassign | Super Admin only (VR-12), on a Submitted complaint; only Start review is enabled in the action bar; Add note allowed on Submitted (`03` §2) |
| 04 A-03 Reject | Under review: Start review "Done", Verify and Reject enabled, Start work and Mark resolved with hints (VR-03); reason list plus optional details (FB-17) |
| 05 A-04 | Dept Admin: students who filed in Facilities only, read-only, no edit buttons; counts in the viewer's scope (VR-02, VR-14) |
| 06 A-05 | Super Admin view with Edit, Suspend, Delete (VR-12); profile fields without gender (VR-16); no ratings given |
| 07 SA-01 | Cards, scorecard, hotspots, suspended users, 3 charts, date range as in `02` §4; no gender |
| 08, 09 SA-02, SA-03 | Super Admin only; Add admin sets name, email, phone, role, department, state; Suspend and Delete only when editing |
| 10 S-01 | Confirm fix and Reopen only on the Resolved complaint within 7 days (VR-03, VR-06); Rate only on the Closed, unrated one (VR-10) |
| 11 S-04 Resolved | Reporter's own complaint; Confirm fix and Reopen; Reopen needs a reason (VR-04) and shows the 7-day limit (VR-06); no Withdraw or Rate |
| 12 S-04 Closed | Rate once, 1–5 stars, optional comment (VR-10); no other buttons |
| 13, 14 Search | Dept Admin: own department's complaints and students only (VR-14); Complaints tab reuses A-02 filters |

## Files

- `NN-<screen>.html` and `.png`: the mockups; open the HTML from this folder in a browser (paths are relative to the repository).
- `mockup.css`: rules not yet in `unifix.css`: CSS bar and column charts, linked stat cards, page and item action rows, rating input, search tabs, the mockup label.
- `img/`: seed-generated sample images used by the S-04 mockups (the app serves them only through the permission-checked file view).
- Superseded drafts (CR-03 history): `../s01`, `../s02`, `../a03`, `../sa01` and `../unifix.css`.
