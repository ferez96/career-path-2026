Hãy xử lý benchmark nghề nghiệp mới nhất trong `data/raw/` (ingest thô, gitignored) theo Workflow 1 trong CURSOR.md.
Yêu cầu:
0) **Đọc resume** ứng viên từ path trong `data/private/master.yaml` (`profile.resume`) và trích nội dung cần thiết **trước** khi chấm Fit Score / Execute–Prepare–Defer. Báo cáo public chỉ tóm tắt không-PII.
0.1) **Đọc báo cáo brief của công ty** liên quan tới JD (tìm trong `reports/briefs/` hoặc `data/*`). Nếu không tìm thấy, hãy tạo brief (template `prompts/company-brief.md`) và lưu sanitized vào `reports/briefs/` trước khi tiếp tục phân tích.
1) Đọc benchmark raw và chuẩn hóa nội dung.
2) Phân tích theo đúng templates/jd_analysis_template.md.
3) Tính Fit Score theo trọng số trong CURSOR.md (lập luận dựa trên khớp benchmark ↔ resume).
4) Kết luận Execute Now / Prepare Foundation First / Defer + lý do.
5) Xuất kết quả markdown vào `reports/benchmarks/` (đặt tên sanitized: alias-{mã-ngắn}_{role-slug}_analysis.md, ví dụ alias-a_golang_analysis.md; trong file dùng Company-Alias A/B và Raw JD import key alias-a — không lặp tên thương hiệu trong tên file/tiêu đề nếu cần sanitize theo docs/SANITIZATION_CHECKLIST.md).
6) Bắt buộc có phần "Gap Summary" và đề xuất hành động 48h để tiến milestone nghề nghiệp.
7) Nếu thiếu dữ liệu, ghi rõ Assumptions và Risks, không bịa thông tin.