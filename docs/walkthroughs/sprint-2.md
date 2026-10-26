# Sprint 2 Walkthrough

Sprint goal: **end-to-end student submission** (`01_project_plan.md`). Features: C-02 submission, C-03 duplicate check and "Me too", C-04 routing, plus the `Notification` model for C-11. Rules: VR-01, VR-07, VR-08, VR-09, NFR-03. Screens: S-01 to S-04. Planning changes: CR-12 (`09` I-36 to I-52).

Each section lists what a file does and the key lines both team members should be able to explain. Read the files in this order; later files build on earlier ones. Screenshots with seed data are in `sprint-2-screens/`.

---

## 1. Requirements

### `requirements.txt`
Adds `filetype==1.2.0`. It recognises a file by its first bytes (its "signature"): JPEG files start `FF D8 FF`, PNG files `89 50 4E 47`, PDFs `%PDF`, MP4/MOV files have an `ftyp` box. It is pure Python, so nothing extra is needed on Windows (unlike `python-magic`). VR-07 says the real type must match the extension; a PDF renamed to `photo.jpg` is refused.

---

## 2. Models and migrations

### `notifications/models.py`
- `Notification` with the six `Event` choices from `05` §3. Built now so `Complaint.submit()` can notify department admins; the list page and bell count come in Sprint 3.
- `complaint = models.ForeignKey("complaints.Complaint", ...)`: a **string** reference, because `complaints/models.py` imports this module. Two modules importing each other at the top would fail; a string is resolved later by Django.

### `complaints/models.py`
The most important file this sprint.

**File rules (VR-07)**
- `ALLOWED_FILE_TYPES`: extension → allowed detected types. `MAX_FILE_SIZE = 15 * 1024 * 1024`, `MAX_FILES = 5` (evidence at submission only; the proof-of-fix photo in Sprint 3 does not count).
- `check_attachment_file(uploaded_file)`: checks extension, then size, then content. It reads the first 8 KB, asks `filetype.guess()`, and **`seek(0)` afterwards**, so the stored file starts from the beginning (TC-47). Returns the detected type, which is stored as `mime_type`. The browser's claimed type is never trusted.
- `attachment_upload_to()`: stores files as `complaints/<tracking_id>/<random hex>.<ext>`. The student's own file name never reaches the disk (no odd characters, no guessing of other files' names); it is kept in `original_name` for display.
- `normalise_room()`: `"L 3"` and `"l3"` become `"l3"` (`03` §6).

**`Complaint`**
- `Status`, `Priority`, `Building` are `TextChoices` with the values from `05` §3. `OPEN_STATUSES` lists the five open statuses (`03` §1).
- `tracking_id` is `null=True`: the ID is built from the primary key, which only exists after the row is inserted. `save()` inserts, then sets `UF-{pk:04d}` and saves that one field, inside `transaction.atomic()`. NULLs never clash in a unique column, so two inserts at the same moment are safe.
- `on_delete=models.PROTECT` on users, category and department: nothing that has complaints can be deleted (users are soft-deleted, `07`). Attachments, history and supports use `CASCADE`: they belong to the complaint.
- Properties (`03` §5): `is_overdue` uses `timezone.localdate()` (Dhaka date, `TIME_ZONE = "Asia/Dhaka"`, `USE_TZ = True`); `can_reopen` compares the Dhaka date of `resolved_at` + 7 days. `location` gives "NAC 512"; `status_badge_class` turns `under_review` into `badge-under-review` for the badge partial; `is_open`.
- `find_duplicates()`: the database narrows to same category, building and an open status; Python then compares the normalised rooms (a database cannot easily ignore spaces). A blank room on either side matches on the building alone.
- `submit()` (class method, C-02, C-04):
  1. Checks the reporter is a student, the category and its department are active, VR-08 (a required file), the 5-file limit, and **every** file with `check_attachment_file()` before anything is written.
  2. `_create_submitted()` does the database work in one transaction: the complaint (department copied from the category), one `Attachment` per file, `ComplaintUpdate(action="submitted")`, and a `Notification` for each active admin of that department (`bulk_create`, one query).
  3. A database rollback does not delete files already written to disk, so `submit()` keeps a list of stored files and deletes them if anything fails, then re-raises the error (TC-48).
- `support()` (C-03, VR-09): refuses non-students, the reporter, complaints that are not open, and a second "Me too". It writes the `Support` row and `ComplaintUpdate(action="support")`, and saves only `updated_at`.
- Errors are `ValidationError`s with a message for the student; views show them.

**`Attachment`, `ComplaintUpdate`, `Support`**
- `Attachment.is_image`: images are shown as thumbnails on S-04, other files as links.
- `ComplaintUpdate.Action` has all 12 actions from `05`; labels are what the timeline shows ("Review started", "Me too").
- `Support.Meta.constraints = [UniqueConstraint(fields=["complaint", "student"], ...)]`: the database itself refuses a second "Me too", as a backstop for VR-09.

### `complaints/migrations/0002_...py`, `notifications/migrations/0001_initial.py`
Generated by `makemigrations`. The notifications migration depends on the complaints one because of the `complaint` foreign key.

---

## 3. Permissions

### `accounts/models.py`: `User.can_view_complaint(complaint)`
Super Admin: always. Dept Admin: only their department (VR-02). Student: the reporter or a supporter (VR-01). It answers "may this user open the complaint at all"; which view they get is decided next.

### `accounts/permissions.py`
- `get_complaint_for_user(user, tracking_id)`: loads the complaint and raises `Http404` if it does not exist **or** the user may not see it. 404 (not 403) means a page never confirms that someone else's tracking ID exists.
- `has_full_view(user, complaint)`: students get the full view only for their own complaints; supporters get the limited view (VR-01). Admins get the full view of what they can see.
- Both live here, next to the role decorators, so every permission check is in one file (CLAUDE.md).

---

## 4. Forms

### `complaints/forms.py`
- `MultipleFileInput` / `MultipleFileField`: Django's file field accepts one file; this is the pattern from the Django docs for several (`allow_multiple_selected = True`, and `clean()` returns a list).
- `LocationForm` (step 1): `category` is a `ChoiceField` whose choices are grouped by department name, which renders `<optgroup>`s. Only active categories of active departments are offered; `clean_category()` turns the chosen ID into the `Category`.
- `ComplaintForm(LocationForm)` (step 2): the same three fields (sent again as hidden inputs, so they are re-checked on Submit) plus title, description and attachments. `clean_attachments()` collects one error per bad file; `clean()` adds the VR-08 error to the attachments field.
- `submit()` checks VR-07 and VR-08 again: the form gives friendly messages, the model guarantees the rule whoever calls it (seed, tests, Sprint 3 code).

---

## 5. Views and URLs

### `complaints/urls.py`
Names and paths from `05` §4. `complaints/new/` is listed **before** `complaints/<str:tracking_id>/`, otherwise "new" would be read as a tracking ID.

### `complaints/views.py`
- `own_and_supported(user)`: `Q(reporter=user) | Q(pk__in=supported)` for S-01 and S-03.
- `home` (S-01): four counts, "Needs your action" (own resolved complaints, with the 7-day window), recent complaints. Confirm/Reopen/Rate buttons are Sprint 4; notifications Sprint 3.
- `complaint_new` (S-02), the two-step flow (`03` §6):
  - `GET` with no `step`: step 1. The "Change" link also lands here with the values filled in (`initial=request.GET.dict()`).
  - `GET ?step=check`: validates step 1, runs `find_duplicates()`. Matches are labelled `is_own` / `is_supported` for the template; no matches → step 2 directly.
  - `GET ?step=details`: step 2 (from "Continue with a new complaint").
  - `POST`: checks everything again, calls `Complaint.submit()`, then Post/Redirect/Get to S-04. If the carried-over location is no longer valid (e.g. a category was deactivated in between), the student is sent back to step 1 with a message.
  - Steps 1 and 2 are GET pages: nothing is saved until Submit, and files are uploaded once. After a failed Submit the text is kept, but browsers never refill a file input, so files must be chosen again.
- `complaint_list` (S-03): `?status=` (only known values are applied) and `?q=` matching tracking ID, title or room (`icontains`). C-18 will reuse `?q=` in Sprint 4.
- `public_actor()`: how a student sees who acted (VR-01): "You", "A student" (Me too), "Reporter", the department name for a Dept Admin, otherwise the role ("Super admin"). Never a person's name; admin pages (Sprint 3) will show names.
- `complaint_detail` (S-04): loads through `get_complaint_for_user()`; internal notes are filtered out (`is_internal=False`); files are only put in the context for the full view.
- `complaint_action`: `@require_POST` (a link can't press Me too by accident). Only `support` exists this sprint; other slugs give 404 until Sprints 3–4. After Me too the student lands on the limited view.
- `attachment`: the only way to download a file (NFR-03). Same permission check, plus `has_full_view()` (supporters see no files), then `FileResponse` with the stored type and original name, `Cache-Control: private`.

### `complaints/admin.py`, `notifications/admin.py`
Complaints and notifications are visible in `/django-admin/` for checking data, but read-only (`has_add_permission`/`has_change_permission` return `False`): workflow changes must go through the model methods. The attachment inline shows names and types, not file links, because files have no public URL. `ReadOnlyInline.get_readonly_fields()` returns every listed field: auto-set fields such as `uploaded_at` cannot be part of an inline form, and listing them without this crashed the page (I-53, TC-61).

---

## 6. Templates and static files

### `templates/partials/status_badge.html`
`<span class="{{ complaint.status_badge_class }}">{{ complaint.get_status_display }}</span>` plus the `flag-overdue` flag. Used on every page that shows a status: `{% include "partials/status_badge.html" with complaint=c %}`.

### `templates/partials/sidebar.html`
New complaint and My complaints are now links; My complaints stays highlighted on S-04.

### `templates/student/home.html` (S-01), `complaint_list.html` (S-03)
Cards use `card-stat`; tables sit in `table-scroll`, so on a phone the table scrolls inside its card and the page never scrolls sideways. Supported rows say "Supported".

### `templates/student/complaint_form.html` (S-02)
One template, three states: `step == 1` (a `method="get"` form with a hidden `step=check`), `"matches"` (summaries with the limited fields only, Me too as a small POST form with `{% csrf_token %}`), and `step == 2` (`enctype="multipart/form-data"`, required for file uploads; the location fields as `{{ form.category.as_hidden }}` etc.). The side panel names the routing department.

### `templates/student/complaint_detail.html` (S-04), `attachment_list.html`
`{% if full_view %}` decides between the full and the limited view. `attachment_list.html` links every file to `student:attachment`, never to `/media/`.

### `static/css/unifix.css`
Section 11b adds the classes recorded in `05` §5 (page structure and complaint pages): steps, match cards, file list, filters, the details grid, file grid and timeline. `.table-scroll td:first-child, .text-mono { white-space: nowrap; }` keeps "UF-0001" on one line.

### `static/js/unifix.js`
Two small helpers; every page works without them.
- After choosing files: lists names and sizes, warns about files over 15 MB or more than 5 files (hints only; the server decides), and shows **Clear files** (`input.value = ""`), because a file input cannot drop a single file.
- Step 1: when the category changes, "What happens next" shows its department (the `<optgroup>` label).

### `unifix/settings.py`
- Comment: `MEDIA_ROOT` is where files are stored, but there is deliberately no `/media/` route (TC-58).
- `DATA_UPLOAD_MAX_NUMBER_FILES = 10`: Django refuses a request with more files (HTTP 400). It is set above 5 so that 6–10 files get the form's friendly message.

---

## 7. Seed data and tests

### `complaints/management/commands/seed_demo.py`
- `COMPLAINTS`: 14 complaints covering all 9 statuses, an overdue in-progress and an overdue reopened complaint, supporters, a public and an internal note, a Super Admin note, and duplicate matches for the demo (Projector & AV in NAC 512, Air conditioning in SAC 304).
- Each complaint is created with the real `Complaint.submit()` (so files, history and notifications are real), then moved back in time with `queryset.update(created_at=...)`: `update()` skips `auto_now_add`, which `save()` would not.
- `add_step()` writes the later steps as `03` §4 describes them (status, `verified_at`, `resolved_at`, `closed_at`, `reopen_count`, history, notifications), because the action methods arrive in Sprint 3. From Sprint 3 the seed calls the real methods instead.
- Due dates are `timezone.localdate() + timedelta(days=...)`, so overdue examples stay overdue whenever the command runs.
- `sample_png()` / `sample_pdf()` build tiny real files by hand (a one-colour PNG with `zlib`, a one-page PDF), so the seed needs no image library and the files pass VR-07.
- Re-running skips complaints that already exist (same reporter and title): no duplicates (TC-49).

### `complaints/tests.py`
26 new tests, TC-36 to TC-61 (see `10_test_plan.md`).
- `TempMediaMixin` points `MEDIA_ROOT` at a temporary folder for the test class and deletes it afterwards, so tests never write into `media/`.
- `FILE_BYTES` and `upload()` make fake uploads whose first bytes are a real signature; `upload("photo.jpg", kind="pdf")` is a PDF pretending to be a JPEG.
- `mock.patch.object(Notification.objects, "bulk_create", side_effect=RuntimeError)` forces a failure after the files are written, to prove they are cleaned up (TC-48).
- `b"".join(response.streaming_content)`: a `FileResponse` streams, so its body is read this way (TC-58).

---

## 8. Docs changed this sprint

- CR-12 before coding: `01` §3; `02` C-03, C-06, VR-01, VR-07, VR-09, NFR-03; `03` §0, §4, §6; `04` S-01 to S-04; `05` §2–4, §7; `06` §4; `07` decisions; `08` FB-12, CR-12; `09` I-36 to I-52.
- During the sprint: `05` records `is_open`, `Attachment.is_image`, `check_attachment_file()` and the limits, the access helpers, the evidence-only 5-file rule and the file clean-up, and the Sprint 2 CSS classes; `04` S-04 names `student/attachment_list.html`; `10` TC-36 to TC-61, the coverage table and the manual checklist; `08` Iteration 2; `CHANGELOG.md`; this walkthrough.
