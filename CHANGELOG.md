# Changelog

All notable changes to **Career Path 2026** are recorded here for releases and public merge notes.

**Format:** inspired by [Keep a Changelog](https://keepachangelog.com/). Versioning follows **Semantic Versioning** where it fits this repo (framework + content, not a runtime API): **MAJOR** = breaking governance/layout; **MINOR** = new workflows, templates, or prompts; **PATCH** = fixes and small doc clarifications.

When cutting a release: move items from `[Unreleased]` into a new `## [x.y.z] - YYYY-MM-DD` section, then tag `vx.y.z` on the merge commit to `public` / `master` as per `docs/BRANCH_WORKFLOW.md`.

---

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

---

## [0.0.2] — draft (chưa tag; cập nhật ngày khi release)

> Nội dung dưới đây tóm tắt thay đổi trên nhánh phát triển so với `v0.0.1`. Chỉnh lại trước khi tag.

### Added

- **Opportunity tracking:** schema [`templates/opportunities_tracker_template.yaml`](templates/opportunities_tracker_template.yaml) (bản thử nghiệm dùng `data/private/opportunities.yaml`); prompts `prompts/opportunity-*.md` (từ JD, cập nhật, ba loại báo cáo); templates báo cáo `templates/opportunity_report_*.md`; rule [`.cursor/rules/opportunity-tracking.mdc`](.cursor/rules/opportunity-tracking.mdc); mục Opportunity Tracking trong [`CURSOR.md`](CURSOR.md); mục trong [`config/context_manifest.yaml`](config/context_manifest.yaml).
- **Weekly planning:** [`prompts/weekly-planning.md`](prompts/weekly-planning.md) (reuse cho job search / execution).
- **Company brief:** [`prompts/company-brief.md`](prompts/company-brief.md) (mẫu prompt).
- **Fit / resume vs JD:** [`.cursor/rules/career-path-resume.mdc`](.cursor/rules/career-path-resume.mdc) (đối chiếu `data/private/master.yaml`).
- **Dữ liệu vận hành (tracked):** [`data/weekly/2026-W16.md`](data/weekly/2026-W16.md); daily reviews [`data/daily/2026-04-17-daily-review.md`](data/daily/2026-04-17-daily-review.md), [`data/daily/2026-04-18-daily-review.md`](data/daily/2026-04-18-daily-review.md) — *có thể gỡ khỏi changelog nếu release chỉ public framework, không kèm dữ liệu cá nhân.*

### Changed

- [`CURSOR.md`](CURSOR.md): metadata mục tiêu, workflow (benchmark, career decision, weekly, daily), mở rộng fit weights; thêm workflow Opportunity.
- [`templates/jd_analysis_template.md`](templates/jd_analysis_template.md): fit scoring (systems ownership + AI khi JD có).
- [`templates/weekly_plan_template.md`](templates/weekly_plan_template.md): chỉnh nhẹ.
- [`README.md`](README.md), [`docs/AGENT_ROLES.md`](docs/AGENT_ROLES.md), [`docs/DATA_CLASSIFICATION.md`](docs/DATA_CLASSIFICATION.md), [`docs/REPO_LAYOUT.md`](docs/REPO_LAYOUT.md), [`reports/README.md`](reports/README.md), [`config/README.md`](config/README.md): đồng bộ opportunity tracking và `reports/private/`.
- [`config/context_manifest.yaml`](config/context_manifest.yaml): thêm context (opportunity + các entry liên quan).
- [`.cursor/rules/careerpath-shared-context.mdc`](.cursor/rules/careerpath-shared-context.mdc), [`.cursor/rules/agent-assistant.mdc`](.cursor/rules/agent-assistant.mdc): cập nhật hướng dẫn agent.

### Fixed

- Theo commit history: chỉnh lệ thức sau khi đổi tên project (rename).

### Repo / governance

- [`LICENSE`](LICENSE): chỉnh nhẹ (metadata).

---

## [0.0.1] — 2026-04-16

Baseline đầu tiên có tag `v0.0.1`: khung repo career path, docs governance, templates/prompts cốt lõi, `data/` / `config/` mở đầu. *(Chi tiết từng file có thể bổ sung nếu cần archive đầy đủ.)*
