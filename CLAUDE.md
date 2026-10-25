# CLAUDE.md: UniFix (CSE327)

Campus complaint management system for North South University. Django + templates + vanilla CSS/JS, SQLite in development. Team of two students who must be able to explain every file.

## Source of truth
- `docs/05_data_dictionary.md`: exact names for apps, models, fields, choices, URL names, templates, CSS classes, and the action mapping table (button → URL slug → model method → history action → status). Never invent or rename names; propose a doc change first.
- `docs/03_workflow.md`: statuses, allowed transitions, button → data effects, duplicate rule.
- `docs/04_screens.md`: what each page shows, its buttons, and the data it reads/writes.
- `docs/02_requirements.md`: features (C-xx), rules (VR-xx), permissions matrix.
- Refer to items by ID in code comments, tests and commits.

## Architecture rules
- Workflow logic lives in `Complaint` model methods (`start_review`, `verify`, `reject`, `start_work`, `resolve`, `confirm`, `reopen`, `withdraw`, `reassign`, `add_note`, `support`, `rate`). Each validates the transition, writes `ComplaintUpdate`, sends notifications, inside one transaction. Views only call these methods.
- Permission checks live in one place (role mixins/decorators) and are enforced server-side, never only hidden in templates.
- One stylesheet `static/css/unifix.css` (design tokens at top). Small helper JS only; no frameworks, no animations.
- Media files stored on disk; database keeps metadata only.

## Commands
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo          # demo departments, categories, users, complaints
python manage.py runserver
python manage.py test               # one or more tests per VR rule
python docs/verify_docs.py          # doc cross-reference check
```

## Change workflow
1. If names or the schema change: update `docs/05` (and `03` if workflow changes) first.
2. Make the code change in small commits: `C-05: add verify action`.
3. New migration for every model change; never edit an applied migration.
4. Run tests and `verify_docs.py`.
5. Log it: `CHANGELOG.md` (what changed) and `docs/08_iteration_log.md` (FB/CR, why).

## Do not
- Commit `db.sqlite3`, `media/`, `.env` or `.venv/`.
- Add features outside the current sprint or the core list without asking; optional items are OP-xx.
- Use JavaScript frameworks, CSS frameworks or heavy AI features unless an OP item is approved.

## Handover after each sprint
Working code, passing tests, screenshots of new pages with seed data, a CHANGELOG entry, and a short walkthrough of each new or changed file.
