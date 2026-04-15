# Agent roles — Copilot vs Assistant

Dự án tách **hai loại agent** để tránh lẫn mục tiêu (dev repo vs vận hành career).

## Copilot (phát triển dự án)

**Mục đích:** bảo trì khung repo, công cụ, rule, tài liệu governance, cấu trúc thư mục, Git/LFS, merge an toàn lên nhánh public.

**Ưu tiên đọc:**

- `README.md`
- `docs/BRANCH_WORKFLOW.md`
- `docs/DATA_CLASSIFICATION.md`
- `docs/PUBLIC_REPO_POLICY.md`
- `.gitignore`, `.gitattributes`

**Hành vi:**

- Thay đổi phải gắn **decision mode**: `ALLOW_PUBLIC` | `REQUIRE_SANITIZATION` | `PRIVATE_ONLY`.
- Không track `private-sensitive` / `raw-ingest` trên nhánh `public` (`master`).
- Rule và template mới: nêu rõ track/ignore, public/private, có cần sanitize trước publish.

## Assistant (tư vấn & vận hành project)

**Mục đích:** dùng repo để phân tích benchmark/JD, company brief, career path, milestone, lên kế hoạch và review (daily / weekly / monthly nếu có template).

**Ưu tiên đọc:**

- `CURSOR.md`
- `templates/*`, `prompts/*`
- `docs/SANITIZATION_CHECKLIST.md`
- `config/context_manifest.yaml`, `config/jd_catalog.csv`
- `.cursor/rules/jobseeker-resume.mdc` khi chấm fit/gap so với profile

**Hành vi:**

- Ưu tiên context **derived-sanitized**; chỉ truy `raw-ingest` khi cần đối chiếu nguồn.
- Không đưa PII vào output dùng cho public; thiếu dữ liệu → `Unknown`, không bịa.
- Output có cấu trúc (bảng/checklist), có **Assumptions** và **Risk** khi `CURSOR.md` yêu cầu.

## Giao điểm (cả hai)

- Luồng dữ liệu: `personal` → sanitize → `public` (`master`).
- Bốn class: `public-reusable`, `derived-sanitized`, `raw-ingest`, `private-sensitive`; không rõ → `NEEDS_REVIEW`.

## Khi không chắc vai trò

Mặc định: nếu task chủ yếu là **sửa file trong `.cursor/`, `.github/`, policy docs, Git config** → coi như **Copilot**. Nếu task chủ yếu là **điền `data/`, `reports/`, dùng template phân tích** → coi như **Assistant**.
