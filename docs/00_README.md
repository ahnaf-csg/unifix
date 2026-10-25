# UniFix Documentation: Index

UniFix is a campus service request and complaint management system for North South University (CSE327, Software Engineering).
Team: Sami Mohammad Abdullah, Ahnaf Tazwar Unmesh.

## How these documents are organized

| File | Purpose | Changes how often |
|---|---|---|
| `01_project_plan.md` | Process model, phases, sprints, team workflow | Each sprint |
| `02_requirements.md` | Actors, core/optional features, rules, non-functional requirements | When scope changes |
| `03_workflow.md` | Complaint states, transitions, button → data effects | Rarely (foundation) |
| `04_screens.md` | Every page: purpose, data shown, buttons, reads/writes | When UI changes |
| `05_data_dictionary.md` | Fixed names: models, fields, choices, URLs, templates | Rarely (foundation) |
| `06_diagram_blueprint.md` | What each UML diagram must contain | When 02–05 change |
| `07_decision_log.md` | Decisions, keep-in-view items, change history | Every change |
| `08_iteration_log.md` | Feedback and change requests per iteration, with versions | Every feedback round |
| `09_verification_report.md` | Consistency checks, issues found and fixed, traceability matrix | Before each build phase |

## Rules for keeping the docs and code in sync

1. **The data dictionary (05) is the source of truth for names.** Code must use exactly these model, field, choice, URL and template names. To rename something, update 05 first, then the code, then log it in 07.
2. **Foundation vs. flexible.** Files 03 and 05 are the foundation and should change rarely. Files 02 and 04 may change freely, as long as they stay consistent with 03 and 05.
3. **Stable IDs.** Features (C-xx, OP-xx), rules (VR-xx), screens (S-xx, A-xx, SA-xx) and use cases (UC-xx) keep their IDs even if reordered. Removed items are marked *(removed)*, never reused.
4. **Every change gets a line in `07_decision_log.md`** with a date and a reason.
5. The submission PDF is generated from these Markdown files, so edit the Markdown, not the PDF.

## Diagrams

`diagrams/` holds the system workflow (PNG plus editable SVG). Course diagrams (use case, class, ER, sequence, activity) are added here as they are drawn.

## Mockups

`mockups/` contains the sample screens (PNG) and their HTML sources. `mockups/unifix.css` is the draft design system (colours, badges, buttons, cards, tables) and can be reused as `static/css/unifix.css` when building.

## Verification

Run `python verify_docs.py` inside `docs/` to re-check IDs, URL names, statuses, history actions and fields across files (see `09_verification_report.md`).

## Rebuilding the PDF

The submission PDF is compiled from these Markdown files plus the mockup images. After editing, regenerate it rather than editing the PDF by hand.
