# Sprint 3 Walkthrough

Sprint goal: **full complaint lifecycle up to Resolved, run from the admin console** (`01_project_plan.md`). Features: C-05 action buttons, C-06 verify with due date, C-07 resolve with proof, C-08 history and notes, C-10 withdraw, C-11 notifications, plus CR-13 (optional gender, avatars) and CR-14 (NSU Navy). Rules: VR-02, VR-03, VR-04 (reject, resolve), VR-05, VR-16, NFR-03. Screens: A-01 (placeholder), A-02, A-03, A-06, S-01, S-04, S-05, S-06, P-02.

Each section lists what a file does and the key lines both team members should be able to explain. Read the files in this order; later files build on earlier ones. Screenshots with seed data are in `docs/screenshots/` (index in its `README.md`).

---

## 1. Docs first

Before any code: `02` (VR-16, gender in C-01/C-15, withdraw in C-11, OP-11), `03` §2 (notes also on Resolved) and §4 (withdraw notifies the department; notification messages), `04` (navy layout, avatars, bell, A-02 filters, A-03 action bar and hints, S-04 Withdraw), `05` (names below, tokens, classes, `console:attachment`), `06` and the ER diagram (`gender`), `07` decisions, `08` FB-15 to FB-18 and CR-13/CR-14, `09` I-54 to I-64, `10` TC-62 to TC-82.

---

## 2. Gender and avatars (CR-13, VR-16)

### `accounts/models.py`
- `User.Gender` choices `male`, `female`, `other`, `prefer_not_to_say`; the field defaults to `prefer_not_to_say`. Migration `accounts/migrations/0002_user_gender.py` (generated).
- `avatar_kind` (property): `male`, `female` or `neutral`. **Templates use it only for the signed-in user's own avatar**; every other person is shown with `kind="neutral"`. That is the whole of VR-16.
- `can_act_on_complaint(complaint)`: Super Admin always; a Dept Admin only for their department. Every workflow method and `allowed_actions()` asks this one question (VR-02).

### `accounts/forms.py`
- `OptionalGenderMixin`: makes the field optional and turns an empty answer into `prefer_not_to_say` (`clean_gender`). Without it, a form posted without gender would fail, because the model field is not blank. Used by `RegisterForm` and `ProfileForm`.

### `accounts/admin.py`
`gender` is deliberately missing from `list_display`, `list_filter` and `fieldsets`, so the Django admin never shows it (TC-63).

### `static/img/avatars/*.svg`, `templates/partials/avatar.html`
Three hand-drawn 64×64 SVGs (circle background, head, shoulders; hair differs). The partial is one `<img>`: `{% static 'img/avatars/'|add:kind|add:'.svg' %}`. Included as `with kind=user.avatar_kind` (own top bar, own profile) or `with kind="neutral"` (A-03 reporter card).

---

## 3. NSU Navy (CR-14)

### `static/css/unifix.css`
- Tokens (`05` §6): `--navy: #002f6c`, `--navy-2`, `--on-navy`, `--on-navy-muted` (light blue-grey), `--gold: #fec937`.
- `.topbar` is now navy; `.topbar-logo` gets a white rounded tile (`padding: 4px; background: var(--on-navy); border-radius: 8px`) so the blue NSU logo stays readable.
- Gold is only an accent: `.tab:has(input:checked)` keeps its blue text and background and gets a gold underline; `.bell-dot` is gold on navy, next to the unread number, which is the real cue (I-64).
- New sections 11c (console) and 11d (notifications); see section 7.

---

## 4. Workflow methods (`complaints/models.py`)

The most important file this sprint. Read it together with `03` §2 and §4.

**Constants**
- `ALLOWED_FROM`: action slug → statuses it may start from. This dictionary *is* the transition table of `03` §2 (VR-03). `NOTE_STATUSES` = open statuses + `resolved`.
- `ADMIN_ACTIONS`: the five A-03 buttons in order. `STATUS_STEP`, `ACTION_STEP`, `PREVIOUS_ACTION`: positions along the main path, used only for the hints.
- `PROOF_FILE_TYPES` and `check_proof_file()`: images only, then the normal VR-07 check (`check_attachment_file`) for size and real content.

**One method per button**, all the same shape:
```python
def start_review(self, actor):
    with transaction.atomic():
        self._check_action(actor, "start_review")   # VR-02, then VR-03
        self.status = self.Status.UNDER_REVIEW
        self.save(update_fields=["status", "updated_at"])
        self._record(actor, ComplaintUpdate.Action.START_REVIEW, self.Status.SUBMITTED)
```
- Input rules are checked **before** the transaction: `verify()` needs a priority from `Priority.values` and `due_date > timezone.localdate()` (VR-05); `reject()` a non-blank reason and `resolve()` a non-blank note (VR-04).
- `_check_action()` → `can_act_on_complaint()` → `_lock_and_check()` → `_lock_status()`. `_lock_status()` re-reads the status with `select_for_update()` inside the transaction: if two admins press buttons at the same moment, the second one sees the new status and is refused instead of acting on an old one.
- `withdraw(student)`: only the reporter, only while Submitted (C-10). `add_note()`: not a status change, so it checks `NOTE_STATUSES` itself.
- `resolve()` writes the proof photo as `Attachment(kind=proof_of_fix)`. Like `submit()`, it remembers the written file and deletes it if anything fails, because a rollback does not delete files (TC-70).

**`_record()`**: one history row (`from_status`, `to_status`, `note`, `is_internal`) and the notifications of `03` §4:
- Reporter: "UF-… is now <status>"; Reject: `fit_message("UF-… was rejected: ", reason)`, shortened with "…" to 255 characters; Resolve: "UF-… was resolved. Please confirm or reopen by <date>" (Dhaka date of `resolved_at` + 7 days, the same window as `can_reopen`).
- Withdraw: the department's active admins (`department_admins()`). Public note: the reporter. Internal note: nobody.
- The actor is never a recipient, because admins act and the reporter is a student.

**`allowed_actions(user)`** returns five dicts `{slug, label, enabled, hint}` (empty list if the user cannot act). `_disabled_hint()`: final status → "Not available: complaint is X"; a step still ahead → "Available after <previous button>"; a step passed → "Done"; Reject after Verify → "Not available" (it was not done, the complaint was verified instead).

`submit()` now uses `department_admins()` and `_notify()` too; its behaviour is unchanged (TC-37).

---

## 5. Notifications (`notifications/`)

- `context_processors.py` `unread_count`: added to `TEMPLATES` in `unifix/settings.py`, so every template has `unread_count` (one `COUNT` query per page). The top bar bell uses it.
- `views.py`: `notification_list` (own notifications only, newest first; opening the page reads nothing) and `mark_all_read` (`@require_POST`, updates only `request.user.notifications`). `complaint_link()` decides where a notification leads: S-04 for students, A-03 for admins. `with_links()` adds that link to each row and is reused by S-01.
- `urls.py`: `notifications:list`, `notifications:mark_all_read` (`05` §4), included at `/notifications/` in `unifix/urls.py`.
- `templates/notifications/list.html`: shared by S-05 and A-06; unread rows get `notification-unread` (blue background and a left border, plus the word "Unread").

---

## 6. Student pages (`complaints/views.py`, templates)

- `home`: `latest_notifications` (5 newest, with links).
- `complaint_action` sends `withdraw` to `withdraw()`, which loads the complaint with `get_complaint_for_user()` (404 for strangers) and calls `complaint.withdraw(request.user)`; a supporter is refused by the model with a message.
- `send_attachment(complaint, pk)`: the file-sending code from Sprint 2, moved into one function so `student:attachment` and `console:attachment` share it (`07` keep-in-view "Admin file access"). The callers check permissions first.
- `templates/student/complaint_detail.html`: Withdraw is a `<details class="action-form">` whose `<summary>` looks like a button; opening it shows the confirmation and the real POST button. No JavaScript.
- `templates/student/attachment_list.html`: `{% url url_name|default:'student:attachment' … %}`, so A-03 can include it with `url_name="console:attachment"`.

---

## 7. Admin console (`console/`)

### `console/forms.py`
`VerifyForm` (date input with `min` = tomorrow; `clean_due_date` checks again), `RejectForm`, `StartWorkForm`, `ResolveForm` (`accept` limited to the proof types), `NoteForm` (public/internal radios). `ACTION_FORMS` maps URL slugs to forms. The forms give friendly messages; the model methods are still the real check.

### `console/views.py`
- `visible_complaints(user)`: own department or all (VR-02).
- `queue` (A-02): every filter is a GET parameter. `status` defaults to `open`; unknown values fall back to "all". The overdue filter is the `is_overdue` rule written as a database filter. `?q=` matches tracking ID, title, room and the reporter's name, student ID and email. `sort=due` uses `F("due_date").asc(nulls_last=True)`, so unverified complaints (no due date) come last. `annotate(supporters=Count("supports"))` avoids one count query per row; the template shows `supporters|add:1` (students affected).
- `history_entries()`: all history rows with real names (admin pages may show names, `07`); consecutive Me too rows are merged into one entry with several names.
- `render_detail()`: builds the page. Each button gets an empty form, or the bound form with errors if that action just failed (`open_action`). If the failed action's button is disabled by now (someone else acted first), its error goes to `bar_errors` above the action bar, because its form is no longer shown.
- `complaint_action`: `@require_POST`; unknown slugs (including `reassign` until Sprint 4) → 404; `get_complaint_for_user()` → 404 for another department. Invalid form or `ValidationError` → the page again with status 400 and that form open; success → message and redirect (Post/Redirect/Get).
- `attachment`: the console twin of `student:attachment` (NFR-03).

### Templates
- `console/queue.html`: the filter form (`filters`, `filter-check`), the table in `table-scroll`; overdue rows get `row-overdue`.
- `console/complaint_detail.html`: the action bar loops over `buttons`: disabled → `<button disabled>` plus `action-hint`; Start review → a plain POST form; others → `<details class="action-form">` with `{% include "console/action_fields.html" %}`. `.action:has(details[open]) { flex-basis: 100% }` gives an open form its own row. Reporter card: neutral avatar, counts, and a disabled A-05 link (`link-disabled`) until Sprint 4. Internal notes have `timeline-internal`.
- `console/dashboard.html`: placeholder with "Go to complaint queue".
- `partials/sidebar.html`: Complaint queue and Notifications are now links; the queue stays highlighted on A-03 and after a failed action.

---

## 8. Seed data (`complaints/management/commands/seed_demo.py`)

- Every step now runs through the real methods (`run_step()`), so the demo data is exactly what the app writes. Confirm and reopen are still written directly (`student_step()`) until Sprint 4.
- **`clock_at(when)`**: the methods stamp times with `timezone.now()`. `mock.patch("django.utils.timezone.now", return_value=when)` makes the code inside believe it is that moment, so `created_at`, `verified_at`, `resolved_at`, history and notification times and the "reopen by" date all agree. Without it, every step would happen "now" and the rows would have to be rewritten afterwards (the Sprint 2 approach).
- Due dates are counted from the real today (`today` is taken before the clock is set), so overdue examples stay overdue; at the time of each Verify they were still in the future, so VR-05 holds.
- UF-0001 (projector, NAC 512) is resolved with a proof photo for the demo.

---

## 9. Tests

`accounts/tests.py` TC-62, TC-63; `complaints/tests.py` TC-64 to TC-82 (see `10_test_plan.md`).
- `WorkflowFixtures.at_status()` puts a complaint straight into a status with `queryset.update()` (test set-up only), so every transition can be tried from every status (TC-65).
- TC-70 forces a failure with `mock.patch.object(Notification.objects, "bulk_create", side_effect=RuntimeError)` and compares the folder before and after (tests share one temporary `MEDIA_ROOT`, and tracking IDs repeat between tests).
- Page tests check status codes (403 wrong role, 404 other department, 405 GET on actions, 400 failed action) and that the right form is open.

---

## 10. Docs changed this sprint

- Doc-first commit (CR-13, CR-14): `01`, `02`, `03`, `04`, `05`, `06`, `07`, `08`, `09`, `10`, ER diagram.
- During the build: `03` §4 notification messages; `05` `ALLOWED_FROM`, `NOTE_STATUSES`, `department_admins()`, console templates and classes, seed `clock_at()`; `02` OP-11; `08` FB-17, FB-18, Iteration 3; `07` build decisions; `10` TC-62 to TC-82 and checklist items 15–24; screenshots; `CHANGELOG.md`; this walkthrough.
