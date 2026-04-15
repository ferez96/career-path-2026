# CareerPath2026

Personal system for career path design, skill progression, and weekly execution tracking.

## Public Data Disclaimer

This public repository stores only sanitized and anonymized content.
Do not commit personal data, mentor/manager contacts, or confidential company details.

## Repository layout

- `CURSOR.md`: project operating guide and career decision framework.
- `data/career_path_master.csv`: single source of truth for career milestones and progress.
- `data/weekly/`: one data-driven weekly file per ISO week.
- `templates/`: reusable prompt and reporting templates.
- `reports/`: generated reports from weekly and career analysis workflows.
- `docs/`: public safety policy and sanitization checklist.

## Two-Branch Architecture

- `public` (`master`) is the public branch.
- `personal` is the private operating branch.
- Data flow is one-way: `personal` -> sanitize -> `public`.
- Never merge `private-sensitive` or `raw-ingest` into `public`.

Branch and merge rules:

- `docs/BRANCH_WORKFLOW.md`
- `docs/DATA_CLASSIFICATION.md`

## Agent roles (Copilot vs Assistant)

This repo distinguishes **Copilot** (developing the framework: rules, Git, docs) from **Assistant** (using the system for career analysis, planning, and reviews). See `docs/AGENT_ROLES.md`.

## Git usage

Track source documents and planning data in Git while excluding generated artifacts and local secrets via `.gitignore`.

Suggested commit pattern:

- `docs: update career growth framework`
- `data: add week 2026-W16 progress tracking`
- `templates: refine capability analysis template`

## Public Safety Rules

- Follow `docs/PUBLIC_REPO_POLICY.md` before publishing.
- Run `docs/SANITIZATION_CHECKLIST.md` before each public commit.
- Keep raw personal notes and private files in ignored local directories only.
- Public merge gate accepts only `public-reusable` and validated `derived-sanitized`.

## License

This project is licensed under the MIT License. See `LICENSE`.

## Operating flow

1. Define or update career milestones in `data/career_path_master.csv`.
2. Create or update the week file in `data/weekly/`.
3. Run capability analysis and planning with templates in `templates/`.
4. Save outputs to `reports/`.
5. Commit meaningful changes.
