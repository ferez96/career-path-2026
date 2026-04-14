# JobSeeker2026

Personal system for job search tracking, interview preparation, and weekly learning execution.

## Public Data Disclaimer

This public repository stores only sanitized and anonymized content.
Do not commit personal data, recruiter/interviewer contacts, or confidential hiring details.

## Repository layout

- `CURSOR.md`: project operating guide and decision framework.
- `data/job_pipeline_master.csv`: single source of truth for all job applications.
- `data/weekly/`: one data-driven weekly file per ISO week.
- `templates/`: reusable prompt and reporting templates.
- `reports/`: generated reports from weekly and JD analysis workflows.
- `docs/`: public safety policy and sanitization checklist.

## Git usage

Track source documents and planning data in Git while excluding generated artifacts and local secrets via `.gitignore`.

Suggested commit pattern:

- `docs: update weekly planning framework`
- `data: add week 2026-W16 tracking`
- `templates: refine JD analysis template`

## Public Safety Rules

- Follow `docs/PUBLIC_REPO_POLICY.md` before publishing.
- Run `docs/SANITIZATION_CHECKLIST.md` before each public commit.
- Keep raw JD files and private notes in ignored local directories only.

## License

This project is licensed under the MIT License. See `LICENSE`.

## Operating flow

1. Add or update jobs in `data/job_pipeline_master.csv`.
2. Create or update the week file in `data/weekly/`.
3. Run analysis/planning with templates in `templates/`.
4. Save outputs to `reports/`.
5. Commit meaningful changes.
