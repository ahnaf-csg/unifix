# UniFix

Campus service request and complaint management system for North South University (CSE327, Software Engineering).
Students report campus issues with photo, video or PDF evidence; complaints are checked for duplicates, routed to the responsible department, verified and resolved by department admins, and confirmed or reopened by the student.

**Team:** Sami Mohammad Abdullah, Ahnaf Tazwar Unmesh
**Stack:** Django, Django templates, vanilla CSS/JS, SQLite (development)
**Status:** Sprint 1 (accounts, roles, login/register, profile, setup) released as `v0.2-sprint1`; Sprint 2 (complaint submission and student pages) in progress on `feature/sprint-2`

## Documentation

All planning lives in [`docs/`](docs/00_README.md). Start with the index. The data dictionary (`docs/05_data_dictionary.md`) is the source of truth for every name used in the code.

## Running locally

Requires Python 3.13. Commands are for Windows PowerShell. In Git Bash use `source .venv/Scripts/activate` and `cp`; on macOS/Linux use `python3 -m venv .venv`, `source .venv/bin/activate` and `cp`.

```
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env            # then set SECRET_KEY (command in the file)
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://localhost:8000. The Django admin panel is at http://localhost:8000/django-admin/ (Super Admin only).

Checks before a pull request:

```
python manage.py test
python docs/verify_docs.py
```

### Demo accounts

Created by `python manage.py seed_demo` (local development only). All share the password `unifix-demo-2026`.

| Role | Email |
|---|---|
| Super Admin | `superadmin@northsouth.edu` |
| Dept Admin, Facilities Management | `fac.admin@northsouth.edu` |
| Dept Admin, IT Services | `it.admin@northsouth.edu` |
| Dept Admin, Housekeeping | `hk.admin@northsouth.edu` |
| Dept Admin, Security | `sec.admin@northsouth.edu` |
| Student (Rafiq Hasan) | `rafiq.hasan@northsouth.edu` |

Nine more students are listed in `complaints/management/commands/seed_demo.py`.
