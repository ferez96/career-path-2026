# JD Analysis — Company-Alias B (Senior Golang Developer — Backend, AWS, MySQL)

**Raw JD import key:** `alias-b`  
**Source:** Third-party recruitment posting (status Active; internal listing ref withheld).  
**Company brief (đã làm giàu từ `data/raw`):** [alias-b_company-brief.md](../briefs/alias-b_company-brief.md) — tổng hợp từ [data/raw/alias-b-brief-chatgpt.md](../../data/raw/alias-b-brief-chatgpt.md).

---

## Input

- **Raw JD content (chuẩn hóa):** **Senior Golang Developer** (Backend, AWS, MySQL). Làm theo squad; thiết kế/triển khai tính năng bằng **Go**; refactor hướng **microservices**; làm việc với PM/designer; kiến trúc, chọn middleware; đo lường và cải thiện chất lượng dịch vụ. Stack gợi ý: AWS/GCP, Aurora MySQL, Elasticsearch, DynamoDB, CI/CD (CircleCI, CodeBuild, CodePipeline, GitHub Actions), Terraform/Packer, Datadog, Docker, Jira/Slack, v.v. **Must-have:** Đồng cảm mission/giá trị công ty; **≥5 năm** Go + **AWS** + **gRPC** cho web services; **technical lead** full lifecycle; framework web; thiết kế schema RDB/KVS và query; bảo mật ứng dụng web; unit test; tiếng Anh tốt. **Nice-to-have:** Debug từ log; Docker/**Kubernetes**; thiết kế kiến trúc & middleware; OSS; technical writing/talks. **Location:** TP.HCM / Hà Nội; **hybrid**. Phúc lợi: lương cạnh tranh, review 2 lần/năm, tháng 13, 18 ngày nghỉ (12 AL + 6 Tết), bảo hiểm sức khỏe, MacBook/laptop.
- **Bối cảnh công ty (từ brief nội bộ, không-PII):** **ConTech** SaaS; công ty mẹ nước ngoài; sản phẩm đã **có thị phần/validation mạnh tại thị trường chính** (theo báo cáo gốc) — giảm một phần rủi ro “sản phẩm chưa chứng minh” so với startup mới. VN là development center + mở rộng ASEAN; stack Go/AWS/MySQL khớp JD; văn hóa lai Nhật–tech, hybrid, ít OT theo nhiều review (cần tự xác minh). Org VN còn tương đối trẻ → quy trình có thể chưa mature.
- **Role target:** Senior Backend / Golang + cloud (theo [CURSOR.md](../../CURSOR.md)).
- **Company tier (ước lượng):** **Solid mid-tier product** trong niche ConTech, có backing từ tập đoàn mẹ — không phải FAANG-scale nhưng product và stack “đủ thực chiến”.
- **Personal profile summary (không-PII, từ resume nội bộ):** Go **6+** năm; lead tách monolith/microservices; **gRPC**; Kubernetes, Docker, Terraform, CI/CD; datastore SQL/NoSQL, messaging; observability đầy đủ. Resume nhấn mạnh **Azure** stack (SQL, blob) hơn **AWS** — khoảng trống cần giải thích khi phỏng vấn.
- **Constraints:** Hybrid 2 thành phố; ứng viên base **HCMC**; mục tiêu remote-first — cần xác nhận ngày lên văn phòng.

---

## Output

### 1) Job Snapshot

- **Company:** Company-Alias B (SaaS ConTech; product; dev center VN).
- **Role:** Senior Golang Developer (Backend, AWS, MySQL).
- **Level:** Senior (5+ năm + technical lead).
- **Location / Work mode:** TP.HCM hoặc Hà Nội; hybrid.
- **Core domain:** Quản lý dự án/công trường/tài liệu xây dựng (cloud).

### 2) Skills Extraction

- **Must-have:** Go, AWS, gRPC, technical leadership full project lifecycle, web frameworks, RDB/KVS schema & query, web app security, unit tests, English.
- **Nice-to-have:** Log-driven debugging; Docker/K8s; architecture & middleware selection; OSS; public technical content.
- **Responsibilities:** Feature design/implementation (Go); microservices refactor; requirements with PM; architecture & middleware; quality measurement & service improvement.

### 3) Fit Scoring (Weighted) — theo [CURSOR.md](../../CURSOR.md) §8

| Tiêu chí | Trọng số | Điểm thành phần (0–100) | Nhận xét ngắn |
|----------|----------|-------------------------|----------------|
| Core Backend Skills | 40% | **78** | Go + gRPC + web services mạnh; **AWS** ít thể hiện trực tiếp trên CV (nhiều Azure/K8s). |
| System Design / Scalability | 25% | **92** | Lead tách monolith, microservices, CI/CD, observability — khớp refactor & vận hành trong JD và brief. |
| Domain & Product Fit | 15% | **59** | Domain xây dựng **mới** với ứng viên; brief củng cố **độ ổn định sản phẩm/công ty** (giảm rủi ro “startup greenfield”) — điểm domain vẫn trung bình vì **transferable domain knowledge** thấp. |
| Seniority Match | 10% | **90** | ≥5 năm và vai trò lead/design — phù hợp. |
| Practical Constraints | 10% | **85** | HCMC trong JD; hybrid vs mong muốn remote-first cần làm rõ. |

- Core Backend Skills (40%): 78  
- System Design / Scalability (25%): 92  
- Domain & Product Fit (15%): 59  
- Seniority Match (10%): 90  
- Practical Constraints (10%): 85  

**Final Fit Score (0–100):** **81**  
*(0,4×78 + 0,25×92 + 0,15×59 + 0,1×90 + 0,1×85 ≈ 80,55 → làm tròn **81**.)*

### 4) Decision Recommendation

- **Recommendation:** **Prepare First** (có thể **apply song song** nếu pipeline thời gian; ưu tiên lấp gap AWS + câu chuyện domain trong 24–48h).
- **Why:** Brief nội bộ xác nhận hướng **product + Go + AWS** và bối cảnh squad/microservices khớp kinh nghiệm lead; tuy nhiên JD vẫn **explicit** về **AWS** và **technical lead** end-to-end, trong khi CV nặng **Azure**; ConTech cần story học domain nhanh. Điểm tổng tăng nhẹ so với phân tích chỉ dựa JD vì **product đã validate** (giảm rủi ro fit “công ty/sản phẩm”).
- **Risks:** Phỏng vấn sâu dịch vụ AWS; kỳ vọng tương tác **team Nhật** (quy trình/ngôn ngữ); phỏng vấn có thể nặng lý thuyết (gợi ý từ review trong brief — không khẳng định).
- **Assumptions:** Tóm tắt từ [data/raw/alias-b-brief-chatgpt.md](../../data/raw/alias-b-brief-chatgpt.md) phản ánh đúng bối cảnh hiện tại; “technical lead” tương đương vai trò lead kỹ thuật đã có trên CV.

### 5) Action Plan (48h)

- [ ] Ôn nhanh **AWS** tương đương workload JD: ECS/EKS hoặc EC2, RDS/Aurora MySQL, DynamoDB, IAM, CloudWatch; map với kinh nghiệm Azure/K8s hiện có.
- [ ] Chuẩn bị pitch 3 phút: lead monolith→microservices + an toàn triển khai; thêm 1 đoạn **vì sao ConTech hấp dẫn** (ops thực địa, tài liệu, workflow) mà không bịa số liệu.
- [ ] Ghi câu hỏi: tỷ lệ hybrid; tương tác với team nước ngoài; roadmap microservices; kỳ vọng on-call.
