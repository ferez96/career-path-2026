Hãy xử lý JD mới nhất trong thư mục raw-jd/ theo Workflow 1 trong CURSOR.md.
Yêu cầu:
0) **Đọc resume** ứng viên từ path trong `data/private/master.yaml` (`profile.resume`) và trích nội dung cần thiết **trước** khi chấm Fit Score / Apply–Prepare–Skip. Báo cáo public chỉ tóm tắt không-PII.
0.1) **Đọc báo cáo brief của công ty** liên quan tới JD (tìm trong thư mục data/* hoặc tương đương). Nếu không tìm thấy, hãy xuất bản báo cáo brief sử dụng template trong @promts/company-brief.md trước khi tiếp tục các bước phân tích JD.
1) Đọc JD raw và chuẩn hóa nội dung.
2) Phân tích theo đúng templates/jd_analysis_template.md.
3) Tính Fit Score theo trọng số trong CURSOR.md (lập luận dựa trên khớp JD ↔ resume).
4) Kết luận Apply Now / Prepare First / Skip + lý do.
5) Xuất kết quả markdown vào reports/jd-analysis/ (đặt tên sanitized: alias-{mã-ngắn}_{role-slug}_analysis.md, ví dụ alias-a_golang_analysis.md; trong file dùng Company-Alias A/B và Raw JD import key alias-a — không lặp tên thương hiệu trong tên file/tiêu đề nếu cần sanitize theo docs/SANITIZATION_CHECKLIST.md).
6) Nếu thiếu dữ liệu, ghi rõ Assumptions và Risks, không bịa thông tin.