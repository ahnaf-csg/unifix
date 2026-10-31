# Update 1 Walkthrough (presentation branch)

Branch `update-1`, created from tag `v0.3-sprint2` on 2026-10-31 for the instructor's Update 1. It shows the Sprint 1–2 state plus one addition: a placeholder shell of A-01 Dashboard (C-14) so the admin layout can be seen. The branch is **never merged into `main`** and is not part of Sprint 2.

Nothing on the page is computed: every card, table and chart is a labelled placeholder. The only real data is the existing "Categories routed to…" table, read from `Department` and `Category`.

The charts are labelled "Arrives in Sprint 5" because the Sprint 4/5 split (charts, SA-01 reports and the top-bar search in Sprint 5) was decided in planning and is recorded in `docs/01_project_plan.md` on `main` with the Sprint 4 doc-first commit, not on this branch.

Screenshots with seed data: `docs/screenshots/admin/08` to `10` (index in its `README.md`).

---

## 1. `templates/console/dashboard.html`
A-01 as listed in `04_screens.md` and `02_requirements.md` §4, in the same order:
- **Page head:** title and subtitle ("All departments" for the Super Admin, the department name for a Dept Admin; "Layout preview. Figures arrive in Sprint 4; charts in Sprint 5."). The **Open complaint queue** button is a real `<button>` with `disabled` and `title="Arrives in Sprint 3"`, the same pattern as the Sprint 1 student home button.
- **Cards:** New, In progress, Overdue, Resolved this week, Average rating. Each shows "–" and the note "Arrives in Sprint 4". They reuse `row`, `card card-stat`, `stat-label`, `stat-value` and `stat-note`; the coloured top borders come from the existing `.row > .card-stat:nth-child(n)` rules.
- **Tables:** Overdue (by due date), Due in next 3 days, Most supported. Column names are taken from A-02 (Tracking ID, Title, Category, Priority, Due date; Most supported: Tracking ID, Title, Status, Supporters). Each has one row "Arrives in Sprint 4". They sit in `table-scroll`, so at phone width a wide table scrolls inside its card and never the page.
- **Charts:** By status, By category, Weekly trend: three cards with an empty `chart-placeholder` box, "Arrives in Sprint 5". No Chart.js.
- **Categories routed to…:** unchanged loop over `departments` (now also wrapped in `table-scroll`).

## 2. `console/views.py`
Docstring only. The view logic is unchanged: `@admin_required` refuses students (403); the Super Admin gets every department, a Dept Admin only their own (VR-02); `prefetch_related("categories")` loads the categories in one extra query.

## 3. `static/css/unifix.css`
One rule, `.chart-placeholder`: a fixed-height box with a dashed border and centred muted text. No new colours or tokens; everything else on the page uses existing classes.

## 4. `console/tests.py` (new)
Three tests, with no TC IDs (this branch has no test-plan entry):
- A Dept Admin sees the placeholder labels, the disabled queue button, and only their own department's categories.
- The Super Admin sees the same placeholders and every department's categories.
- A student gets 403.

Total: 64 tests (61 from v0.3 + 3).

## 5. Top-bar search
Unchanged from v0.3: shown but disabled, with the tooltip "Search arrives in Sprint 4" (`templates/partials/topbar.html`).

## Commands
```
git switch update-1
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
python manage.py test        # 64 tests
```
