# Project: Career Path 2026

## 1) Mục tiêu dự án

Career Path 2026 là hệ thống hỗ trợ cá nhân để:
- Thiết kế lộ trình nghề nghiệp dài hạn theo giai đoạn (6-12-24 tháng), **theo định hướng ưu tiên: giao hàng ở tầng hệ thống (systems-level ownership), kết hợp AI / ML trong production và AI-augmented tooling để tăng hiệu năng delivery** (chi tiết trong `data/private/master.yaml` → `career.direction_summary`, `profile.headline`).
- Theo dõi tiến độ năng lực và kết quả thực thi theo tuần/tháng.
- Lập kế hoạch và review theo tuần/ngày.
- Thu thập và chuẩn hóa benchmark từ role/JD làm dữ liệu tham chiếu (không bắt buộc apply ngay).
- Tạo báo cáo gap năng lực để ra quyết định học tập và phát triển.
- Kết hợp học tập nâng cao năng lực (DSA, System Design, Coding, Problem Solving) với kế hoạch sự nghiệp.

## 2) Ngôn ngữ

- Tiếng Việt
- Tiếng Anh

Quy tắc:
- Mặc định phản hồi bằng Tiếng Việt.
- Khi được yêu cầu, xuất song ngữ Việt-Anh hoặc 100% English.

## 3) Định dạng file hỗ trợ

Input:
- Markdown
- Plaintext
- PDF
- PNG (OCR nếu có text)

Output:
- Markdown (báo cáo, kế hoạch, review)
- Plaintext (ghi chú nhanh)
- CSV/Markdown table (tracking)
- PDF (tùy chọn, xuất bản cuối)

## 4) Target Metadata

```yaml
target_profile:
  primary_role: "Distributed Systems Engineer"
  fallback_role:
    allowed: true
    role: "Senior Software Engineer (Backend / Distributed Systems)"
    company_tier_condition: "FAANG+"
  preferred_company_tiers:
    - "Tier-1"
    - "FAANG+"
  editable_for_publish: true
```

## 5) Phạm vi chức năng chính

### A. Career Path Tracking
- Quản lý các mốc nghề nghiệp theo giai đoạn (Now / Next / Later).
- Theo dõi trạng thái milestone:
  - Planned
  - In Progress
  - Blocked
  - Validated
  - Archived
- Theo dõi deadline, bằng chứng hoàn thành, mức độ ưu tiên.

### B. Market Benchmark Intelligence
- Thu thập benchmark từ JD/role profile/job post.
- Chuẩn hóa format benchmark.
- Trích lọc:
  - Must-have skills
  - Nice-to-have
  - Seniority
  - Domain/Industry
  - Responsibilities
  - Compensation band (nếu có)
  - Location/Work mode
- Tạo điểm phù hợp (fit score) giữa hồ sơ cá nhân và benchmark.
- Xuất báo cáo gap năng lực để ưu tiên roadmap học tập.

### C. Learning & Skill Sharpening
- Theo dõi lộ trình học:
  - DSA
  - System Design (ưu tiên bài có trade-off sản phẩm, ownership, reliability)
  - Coding
  - Problem Solving
  - AI/ML trong production & AI-augmented engineering (theo nhu cầu JD / gap)
- Mapping kỹ năng còn thiếu theo role mục tiêu và `career.direction_summary` trong `master.yaml`.
- Đề xuất bài tập và kế hoạch cải thiện theo tuần/ngày.

### D. Planning & Review
- Lập Weekly Plan (mục tiêu + hành động + KPI).
- Sinh Daily Plan từ Weekly Plan.
- End-of-day review và End-of-week review.
- Điều chỉnh roadmap nghề nghiệp dựa trên kết quả thực tế.

## 6) Dữ liệu cốt lõi cần quản lý

### Career Milestone Record
- Milestone ID
- Target Role/Scope
- Time Horizon (Now/Next/Later)
- Success Criteria
- Baseline Level
- Target Level
- Evidence Link (sanitized)
- Priority (P0/P1/P2)
- Status
- Target Date
- Next Action
- Next Action Date
- Notes

### Market Benchmark Record
- Company Alias
- Role Title
- Source
- Benchmark Raw Input
- Benchmark Summary
- Required Skills
- Preferred Skills
- Gap Score (0-100)
- Priority (P0/P1/P2)
- Status (Reference/Active)
- Next Action
- Next Action Date
- Notes

### Personal Progress Record
- Tuần số / ngày
- Mục tiêu tuần/ngày
- Số milestone đang active
- Số milestone hoàn thành
- Bài học kỹ năng đã hoàn thành
- Tổng thời gian học (giờ)
- Blockers
- Lessons learned
- Plan update

## 7) Workflow vận hành chuẩn

### Workflow 1: Benchmark Processing
1. Nhận benchmark (JD/role profile/text/markdown/pdf/image OCR).
2. Chuẩn hóa nội dung.
3. Trích lọc thông tin chính.
4. Tạo benchmark summary ngắn + bảng kỹ năng.
5. **Đọc hồ sơ ứng viên:** nguồn chuẩn là `data/private/master.yaml` (headline, `career.direction_summary`, kinh nghiệm, kỹ năng, mục tiêu). Nếu có thêm CV/PDF riêng, người dùng chỉ định path; không bắt buộc trường `profile.resume`. Chỉ trích xuất nội dung cần để đối chiếu JD; báo cáo public chỉ tóm tắt không-PII, không copy email/SĐT/địa chỉ vào `reports/`.
6. Chấm gap/fit score với profile cá nhân (dựa trên resume + metadata mục tiêu trong file này).
7. Gán priority + đề xuất hành động học tập.
8. Ghi vào tracking report.

### Workflow 2: Career Decision
1. Tổng hợp milestone và benchmark hiện có (khi cần điểm fit/gap, đọc resume theo `data/private/master.yaml` như Workflow 1).
2. So sánh theo tiêu chí (impact, growth, feasibility, interest, time horizon).
3. Đề xuất:
   - Execute now
   - Prepare foundation first
   - Defer
4. Sinh action list cho 24-72 giờ tới.

### Workflow 3: Weekly Planning
1. Thu thập kết quả tuần trước.
2. Đánh giá KPI đạt/chưa đạt.
3. Chọn 3-5 mục tiêu tuần mới.
4. Chia nhỏ thành daily tasks.
5. Xác định lịch học + lịch thực hành + lịch review.
6. Khóa kế hoạch và theo dõi thực thi.

### Workflow 4: Daily Review
1. Check kế hoạch ngày.
2. Đánh dấu done/pending.
3. Ghi feedback và blockers.
4. Cập nhật next action.
5. Chuẩn bị kế hoạch ngày tiếp theo.

## 8) Fit Score Weights (bản thử nghiệm)

Định hướng **systems ownership + AI trong delivery**; khi JD không đụng AI/ML, phân bổ phần trăm AI vào *Distributed systems* và *System design*.

- Distributed systems & backend execution: 32%
- System design & scalability / reliability: 22%
- Systems-level product ownership & cross-functional delivery: 18%
- AI/ML in production hoặc AI-augmented engineering (khi JD có yếu tố này): 5% — nếu không: cộng dồn vào hai mục đầu
- Domain & industry fit: 5%
- Seniority match: 8%
- Practical constraints (location/timezone/work mode): 10%

## 9) KPI gợi ý

### Career Path KPI
- Số benchmark thu thập / tuần
- Số milestone active / tuần
- Số milestone validated / tháng
- Tỉ lệ hoàn thành milestone đúng hạn
- Số bằng chứng năng lực được cập nhật

### Learning KPI
- Số giờ học tập trung / tuần
- Số bài DSA hoàn thành
- Số mock interview
- Số chủ đề System Design hoàn thành (ưu tiên case có **product trade-offs**, multi-team ownership, SLO/incident story)
- Thời gian hoặc bài tập liên quan **AI/ML trong production** (serving, evaluation, cost/latency, data pipelines) — khi roadmap tuần có mục này
- Thử nghiệm **AI-augmented workflow** (review, codegen, test) có bằng chứng (note ngắn, không cần PII)
- Số lỗi lặp lại đã khắc phục

### Execution KPI
- % hoàn thành kế hoạch ngày
- % hoàn thành mục tiêu tuần
- Số blocker unresolved > 7 ngày

## 10) Prompting Rules (cho AI Assistant)

- Tuân thủ docs/SANITIZATION_CHECKLIST.md
- Không bịa thông tin công ty/JD.
- Nếu thiếu dữ liệu, phải hỏi rõ trước khi kết luận.
- Ưu tiên output có cấu trúc bảng/checklist.
- Luôn đưa:
  - Insight chính
  - Recommended actions
  - Next-step trong 24h
- Mỗi báo cáo phải có mục "Assumptions" và "Risk".

## 11) Chu kỳ vận hành đề xuất

- Thứ 2: Weekly planning + milestone prioritization
- Thứ 3-5: Focused learning + hands-on practice
- Thứ 6: Deep review + progress tracking + plan adjustment
- Thứ 7: Mock interview / portfolio hardening / system design review
- Chủ nhật: Nhẹ, tổng kết tuần, chuẩn bị tuần mới
