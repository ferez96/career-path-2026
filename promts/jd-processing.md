Hãy xử lý JD mới nhất trong thư mục raw-jd/ theo Workflow 1 trong CURSOR.md.
Yêu cầu:
1) Đọc JD raw và chuẩn hóa nội dung.
2) Phân tích theo đúng templates/jd_analysis_template.md.
3) Tính Fit Score theo trọng số trong CURSOR.md.
4) Kết luận Apply Now / Prepare First / Skip + lý do.
5) Xuất kết quả markdown vào reports/jd-analysis/ (đặt tên sanitized: alias-{mã-ngắn}_{role-slug}_analysis.md, ví dụ alias-a_golang_analysis.md; trong file dùng Company-Alias A/B và Raw JD import key alias-a — không lặp tên thương hiệu trong tên file/tiêu đề nếu cần sanitize theo docs/SANITIZATION_CHECKLIST.md).
6) Nếu thiếu dữ liệu, ghi rõ Assumptions và Risks, không bịa thông tin.