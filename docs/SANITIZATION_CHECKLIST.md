# Sanitization Checklist

Use this checklist before committing data-oriented files.

## File-Level Checks

- [ ] File contains no real person names.
- [ ] File contains no email addresses.
- [ ] File contains no phone numbers.
- [ ] File contains no private scheduling links.
- [ ] File contains no confidential interview details.

## Job Data Checks

- [ ] Company names are aliases.
- [ ] Role titles are generic enough for public sharing.
- [ ] Compensation is not exact or uniquely identifying.
- [ ] Notes are generalized and non-identifiable.
- [ ] Links are scrubbed from tracking parameters.

## Final Commit Gate

- [ ] Ran a quick manual scan for terms like `@`, `http`, `salary`, `recruiter`.
- [ ] Verified `.gitignore` still protects local sensitive folders.
- [ ] Commit message clearly describes sanitized scope.
