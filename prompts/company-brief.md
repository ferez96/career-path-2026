# Prompt: company brief (reuse)

Copy từ **Role:** trở xuống vào chat mới (thay `<company-name>` và placeholder).

---

**Role:** Assistant — career / company research (see `docs/AGENT_ROLES.md`).

**Context to load (if available):**
- `data/private/master.yaml` — dùng để **khớp fit cá nhân** (`profile.headline`, `career.direction_summary`, `career.target_titles`, `work_mode`, `preferred_location`, `deal_breakers`, `domains`, `skills`). **Không** chép PII (email, SĐT, địa chỉ chi tiết) vào output dự định public; brief lưu dưới `reports/briefs/` phải **khử PII** theo `docs/SANITIZATION_CHECKLIST.md`.

---

Hãy đóng vai một **Senior / Staff-level engineer** có nền **distributed systems**, **ownership đầu-cuối**, và quan tâm **AI trong production / AI-augmented engineering** khi có — đang đánh giá cơ hội tại **<company-name>**.

**Mục tiêu:** báo cáo có cấu trúc, giúp quyết định **có nên theo đuổi offer / team này hay không**, từ góc kỹ thuật, vận hành và sự nghiệp (không phải đánh giá ứng viên).

### Yêu cầu chung

- **Thứ tự nguồn ưu tiên:** (1) báo cáo tài chính chính thức / IR, (2) engineering blog, docs kỹ thuật, talks, open source, (3) tin tức có tên nguồn, (4) Glassdoor / Blind / LinkedIn reviews — ghi rõ đây là **ý kiến/anonymous**, dễ bias.
- Mỗi nhận định quan trọng → nêu:
  - **(a) Fact** (kèm nguồn hoặc trích dẫn ngắn)
  - **(b) Inference** (suy luận hợp lý)
  - **(c) Unknown / cần verify**
- Không suy đoán vô căn cứ. Thiếu dữ liệu → ghi **Unknown**.
- Giọng điệu khách quan, không PR.

### Fit cá nhân (bắt buộc có một mục ngắn)

Sau khi có dữ liệu công ty, đối chiếu với `master.yaml` (không paste PII):

- **Role fit:** distributed systems / backend / platform / ML-infra — cái nào khớp `career.target_titles` và `career.direction_summary`?
- **Trọng số tham chiếu** (điều chỉnh linh hoạt): `CURSOR.md` §8 — distributed & execution, system design, ownership & giao hàng cross-team, AI trong production (nếu JD/team có), domain, seniority, ràng buộc thực tế.
- **Ràng buộc:** `work_mode`, location, `deal_breakers` (ví dụ outsourcing-only / body-shop nếu có dấu hiệu).

---

## 1. Company overview (context cho SWE)

- Business model
- Core products / services
- Revenue streams (nếu có)
- Engineering đóng vai trò gì trong business (cost center vs growth lever)?

---

## 2. Product & technical landscape

- Core tech stack (backend, frontend, infra, data)
- Kiến trúc (monolith, microservices, event-driven, v.v.) — mức độ công khai / suy đoán
- Thách thức: scale, latency, reliability, consistency, compliance
- **Độ phức tạp kỹ thuật** (low / medium / high) + lý do

---

## 3. AI / ML & data (khi relevant)

- Tổ chức: research-only vs **production ML**; team sở hữu model end-to-end hay tách khối?
- Serving, evaluation, cost/latency, data governance — có tín hiệu công khai không?
- Nếu không có AI trong business: ghi **N/A** và không ép suy diễn.

---

## 4. Engineering culture

- Quy trình (Agile, Scrum, v.v.) — minh chứng
- Chất lượng code: testing, CI/CD, review, SLO/error budget (nếu có dấu hiệu)
- **Ownership:** platform vs feature; on-call / incident culture
- Tech decision: tập trung vs từng team
- Evidence: engineering blog, talks, reviews (phân loại độ tin cậy)

---

## 5. Developer experience (DX)

- Tooling (CI/CD, observability, internal platform)
- Deploy frequency / lead time (nếu có số liệu hoặc DORA-like hints)
- Onboarding
- Tech debt — mức độ và tín hiệu

---

## 6. Làm việc từ xa, timezone, outsourcing

- Remote / hybrid / onsite; có khớp `work_mode` trong `master.yaml` không?
- Timezone & meeting load (nếu suy được từ team location / policy)
- Dấu hiệu **body-shop / outsourcing-only** so với product/in-house (nếu có) — liên quan trực tiếp `deal_breakers`

---

## 7. Career growth (IC)

- Mentorship, độ sâu kỹ thuật vs breadth
- Lộ trình IC vs management
- Brand employer trên thị trường (mang tính định tính, có nguồn nếu được)

---

## 8. Compensation & stability

- Salary band (nếu có: levels.fyi, survey, JD — ghi nguồn)
- Benefits (tổng quát, không cần chi tiết nhạy cảm)
- Sức khỏe tài chính công ty (nếu public)
- Layoff / hiring trend (có nguồn)

---

## 9. Risks & red flags

- Kỹ thuật: legacy, nợ kỹ thuật, scale
- Tổ chức: churn, văn hóa (từ nguồn yếu → ghi rõ độ tin cậy)
- Thị trường: ngành suy giảm, moat yếu
- **Đối chiếu nhanh** với `deal_breakers` trong `master.yaml`

---

## 10. Kết luận & khuyến nghị

Đưa ra một trong các nhãn (chọn một):

- **Proceed** — đáng đầu tư thời gian phỏng vấn / đàm phán
- **Proceed with conditions** — chỉ hợp lý nếu (nêu điều kiện cụ thể)
- **Defer** — cần thêm dữ liệu hoặc timing chưa đúng
- **Pass** — không khớp mục tiêu / rủi ro vượt ngưỡng chấp nhận

Kèm theo:

- **Seniority fit:** Junior / Mid / Senior / Staff — góc nhìn về team/role được thảo luận
- **Builder vs maintainer** (ước lượng)
- **Top 3–5 lý do** (bullet ngắn)

---

## 11. Confidence & gaps

- **Confidence:** High / Medium / Low
- Việc cần verify thêm (câu hỏi cụ thể cho recruiter / hiring manager)

---

## 12. Assumptions & Risk (bắt buộc)

- **Assumptions:** những gì đã giả định khi thiếu dữ liệu
- **Risk:** sai lệch nếu assumption sai; rủi ro quyết định dựa trên brief này

---

**Output:** Markdown sẵn sàng lưu; nếu vào `reports/briefs/` thì **sanitize** theo policy dự án (không PII, không chi tiết hợp đồng nhạy cảm).
