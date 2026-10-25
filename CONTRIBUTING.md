# Contributing to UniFix

## Golden rules

1. **Names come from `docs/05_data_dictionary.md`.** Models, fields, choices, URL names, templates and CSS classes must match it exactly. To rename or add something, update 05 first, in the same pull request.
2. **Workflow changes start in `docs/03_workflow.md`.** Statuses and transitions are the foundation; flag any change to 03 or 05 with the `foundation` label.
3. **Every change is traceable.** Reference IDs (C-xx, VR-xx, S-xx, CR-xx) in branches, commits and pull requests.
4. **Log it.** What changed goes in `CHANGELOG.md`; why it changed (feedback FB-xx, change request CR-xx) goes in `docs/08_iteration_log.md`; decisions go in `docs/07_decision_log.md`.

## Branches and commits

- `main` always runs.
- Branch per feature: `feature/c05-admin-actions`, `fix/vr06-reopen-window`, `docs/cr09-search-extension`.
- Commit messages start with the ID: `C-05: add verify action and form`.
- Small commits, one logical change each.

## Database

- Every model change gets a new migration (`python manage.py makemigrations`).
- Never edit or delete a migration that has been applied or pushed.
- Never commit `db.sqlite3`, `media/` or `.env`; recreate data with `python manage.py seed_demo`.

## Before opening a pull request

- `python manage.py test` passes.
- `python docs/verify_docs.py` reports no issues.
- New pages checked in the browser with seed data.
- `CHANGELOG.md` updated under "Unreleased".
