# Branch Workflow

## Purpose

Define a strict two-branch operating model that prevents private data leakage to public history.

## Branches

- `public` (`master`): public-facing branch for reusable assets.
- `personal`: private operating branch for real execution data.

## One-Way Data Flow

Data must move in a single direction:

1. Work in `personal`.
2. Sanitize/redact outputs.
3. Publish only approved artifacts to `public` (`master`).

Never move raw/private data directly from `personal` to `public`.

```mermaid
flowchart LR
    A["Work in <br/>`personal`"] --> B["Sanitize/<br/>Redact Outputs"]
    B --> C["Publish Approved Artifacts<br/>to `public` (`master`)"]
    A -.->|Block| C
```

## Allowed Data by Branch

- `public` (`master`):
  - `public-reusable`
  - `derived-sanitized` (validated)
- `personal`:
  - `public-reusable`
  - `derived-sanitized`
  - `raw-ingest`
  - `private-sensitive`

If classification is unclear, mark as `NEEDS_REVIEW` and block public merge.

## Public Merge Gate

Before merging to `public` (`master`), all checks must pass:

- [ ] No `private-sensitive` files are staged.
- [ ] No `raw-ingest` files are staged.
- [ ] `derived-sanitized` files passed `docs/SANITIZATION_CHECKLIST.md`.
- [ ] Files follow `docs/DATA_CLASSIFICATION.md`.
- [ ] Decision mode result is documented:
  - `ALLOW_PUBLIC`
  - `REQUIRE_SANITIZATION`
  - `PRIVATE_ONLY`

Any failed check means no merge to `public`.

## Publishing `personal` to `master` (squash)

Use a **squash merge** when promoting work from `personal` to `master` so the public branch gets **one** combined commit instead of replaying every intermediate commit from `personal` (reduces accidental detail in public history).

**CLI (local):** `git checkout master` → `git merge --squash personal` → review staged diff → `git commit` with a single message. **GitHub:** open a PR and choose **Squash and merge**.

**`data/daily/` and `data/weekly/`:** These paths are **gitignored** and not tracked in the repo. Keep any planning files **only on your machine** for your `personal` workflow; they must not appear in the tree on `master`.

**After publishing:** On `personal`, run **`git merge master`** to bring the squashed commit into your branch and keep your working tree aligned with `master` for continued work.

## Recommended PR Flow

1. Prepare changes in `personal`.
2. Classify changed files using `docs/DATA_CLASSIFICATION.md`.
3. Sanitize and re-check content.
4. Open PR from a sanitized working branch to `public` (`master`).
5. Prefer **Squash and merge** (or local squash as in the section above).
6. Include validation notes and decision mode result in PR description.

## Release Flow

Releases are tagged on `master` after merging a final set of PR(s). **Semantic Versioning** applies loosely: **MAJOR** = breaking governance/layout changes; **MINOR** = new workflows, templates, or features; **PATCH** = fixes and small doc updates.

### Steps

1. **Prepare release branch** (optional, for staging final changes):
   - Create `release/vX.Y.Z` from `master`.
   - Or work directly on `master` if the final commit is ready.

2. **Update `CHANGELOG.md`:**
   - Move all items from `[Unreleased]` into a new `## [X.Y.Z] - YYYY-MM-DD` section (using today's date).
   - Keep `[Unreleased]` as an empty template for future entries.
   - Example:
     ```markdown
     ## [Unreleased]

     ### Added

     ### Changed

     ### Fixed

     ### Removed

     ---

     ## [X.Y.Z] — 2026-MM-DD

     ### Added
     - (items from [Unreleased])

     ### Changed
     - (items from [Unreleased])
     ...
     ```

3. **Commit CHANGELOG update to `master`:**
   ```bash
   git checkout master
   git add CHANGELOG.md
   git commit -m "chore: cut release vX.Y.Z"
   ```

4. **Tag the commit:**
   ```bash
   git tag -a vX.Y.Z -m "Release X.Y.Z"
   ```
   Or for lightweight tag:
   ```bash
   git tag vX.Y.Z
   ```

5. **Push to remote:**
   ```bash
   git push origin master
   git push origin vX.Y.Z
   ```

6. **GitHub Releases (optional):**
   - Go to **Releases** on GitHub.
   - Create a release from tag `vX.Y.Z`.
   - Use the `## [X.Y.Z]` section from `CHANGELOG.md` as the release notes.

### Notes

- All release tags are on `master`. Do not tag `personal`.
- Keep `[Unreleased]` in `CHANGELOG.md` for future work (do not delete).
- If a release is needed from a long-lived branch other than `master`, document the exception in the release notes.
- Version strings in code (if any) should match the tag (`vX.Y.Z`); update before tagging.
