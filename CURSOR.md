# Project: Job Seeker 2026

## 1) Mục tiêu dự án

Job Seeker 2026 là hệ thống hỗ trợ cá nhân để:
- Theo dõi toàn bộ hành trình tìm việc (pipeline ứng tuyển -> phỏng vấn -> kết quả).
- Lập kế hoạch và review theo tuần/ngày.
- Thu thập và chuẩn hóa JD từ nhiều nguồn (Text/Markdown/PDF).
- Trích lọc thông tin quan trọng từ JD và tạo báo cáo so sánh để ra quyết định nộp đơn.
- Kết hợp kế hoạch học tập nâng cao năng lực (DSA, System Design, Coding, Problem Solving) song song với tìm việc.

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
  primary_role: "Senior Backend Software Engineer"
  fallback_role:
    allowed: true
    role: "Mid-level Backend Software Engineer"
    company_tier_condition: "FAANG+"
  preferred_company_tiers:
    - "Tier-1"
    - "FAANG+"
  editable_for_publish: true
```

## 5) Phạm vi chức năng chính

### A. Job Tracking
- Quản lý danh sách công ty/vị trí/JD/link.
- Theo dõi trạng thái ứng tuyển:
  - Backlog
  - Shortlist
  - Applied
  - HR Screen
  - Technical Interview
  - Hiring Manager / Final
  - Offer
  - Rejected
  - Archived
- Theo dõi deadline, ngày follow-up, người liên hệ, mức độ ưu tiên.

### B. JD Intelligence
- Thu thập JD từ nhiều nguồn.
- Chuẩn hóa format JD.
- Trích lọc:
  - Must-have skills
  - Nice-to-have
  - Seniority
  - Domain/Industry
  - Responsibilities
  - Compensation (nếu có)
  - Location/Work mode
- Tạo điểm phù hợp (fit score) giữa hồ sơ cá nhân và JD.
- Xuất báo cáo so sánh nhiều job để chọn ứng tuyển.

### C. Learning & Skill Sharpening
- Theo dõi lộ trình học:
  - DSA
  - System Design
  - Coding
  - Problem Solving
- Mapping kỹ năng còn thiếu theo JD mục tiêu.
- Đề xuất bài tập và kế hoạch cải thiện theo tuần/ngày.

### D. Planning & Review
- Lập Weekly Plan (mục tiêu + hành động + KPI).
- Sinh Daily Plan từ Weekly Plan.
- End-of-day review và End-of-week review.
- Điều chỉnh kế hoạch tuần tiếp theo dựa trên kết quả thực tế.

## 6) Dữ liệu cốt lõi cần quản lý

### Candidate Job Record
- Company
- Role Title
- Source
- JD Raw Input
- JD Summary
- Required Skills
- Preferred Skills
- Fit Score (0-100)
- Priority (P0/P1/P2)
- Status
- Applied Date
- Next Action
- Next Action Date
- Notes
- Interview Feedback
- Final Outcome

### Personal Progress Record
- Tuần số / ngày
- Mục tiêu tuần/ngày
- Số job đã shortlist/applied
- Số interview rounds
- Bài học kỹ năng đã hoàn thành
- Tổng thời gian học (giờ)
- Blockers
- Lessons learned
- Plan update

## 7) Workflow vận hành chuẩn

### Workflow 1: JD Processing
1. Nhận JD (text/markdown/pdf/image OCR).
2. Chuẩn hóa nội dung.
3. Trích lọc thông tin chính.
4. Tạo JD summary ngắn + bảng kỹ năng.
5. Chấm fit score với profile cá nhân.
6. Gán priority + đề xuất hành động.
7. Ghi vào tracking report.

### Workflow 2: Application Decision
1. Tổng hợp danh sách job hiện có.
2. So sánh theo tiêu chí (fit, growth, location, compensation, interest).
3. Đề xuất:
   - Apply now
   - Need more prep
   - Skip
4. Sinh action list cho 24-72 giờ tới.

### Workflow 3: Weekly Planning
1. Thu thập kết quả tuần trước.
2. Đánh giá KPI đạt/chưa đạt.
3. Chọn 3-5 mục tiêu tuần mới.
4. Chia nhỏ thành daily tasks.
5. Xác định lịch phỏng vấn + lịch học.
6. Khóa kế hoạch và theo dõi thực thi.

### Workflow 4: Daily Review
1. Check kế hoạch ngày.
2. Đánh dấu done/pending.
3. Ghi feedback và blockers.
4. Cập nhật next action.
5. Chuẩn bị kế hoạch ngày tiếp theo.

## 8) Fit Score Weights (bản thử nghiệm)

- Core Backend Skills: 40%
- System Design / Scalability: 25%
- Domain & Product Fit: 15%
- Seniority Match: 10%
- Practical Constraints (location/timezone/work mode): 10%

## 9) KPI gợi ý

### Job Search KPI
- Số JD thu thập / tuần
- Số job shortlist / tuần
- Số đơn apply / tuần
- Tỉ lệ phản hồi HR
- Số vòng phỏng vấn / tuần
- Tỉ lệ chuyển vòng

### Learning KPI
- Số giờ học tập trung / tuần
- Số bài DSA hoàn thành
- Số mock interview
- Số chủ đề System Design hoàn thành
- Số lỗi lặp lại đã khắc phục

### Execution KPI
- % hoàn thành kế hoạch ngày
- % hoàn thành mục tiêu tuần
- Số blocker unresolved > 7 ngày

## 10) Prompting Rules (cho AI Assistant)

- Không bịa thông tin công ty/JD.
- Nếu thiếu dữ liệu, phải hỏi rõ trước khi kết luận.
- Ưu tiên output có cấu trúc bảng/checklist.
- Luôn đưa:
  - Insight chính
  - Recommended actions
  - Next-step trong 24h
- Mỗi báo cáo phải có mục "Assumptions" và "Risk".

## 11) Chu kỳ vận hành đề xuất

- Thứ 2: Weekly planning + shortlist jobs
- Thứ 3-5: Apply + interview prep + focused learning
- Thứ 6: Deep review + pipeline cleanup + plan adjustment
- Thứ 7: Mock interview + system design review
- Chủ nhật: Nhẹ, tổng kết tuần, chuẩn bị tuần mới
