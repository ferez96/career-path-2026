# JD Analysis — Company-Alias A (Golang Software Engineer)

**Raw JD import key:** `alias-a`  
**Source:** Third-party recruitment posting (status Active; internal listing ref withheld).  
**Company brief (đã làm giàu từ `data/raw`):** [alias-a_company-brief.md](../briefs/alias-a_company-brief.md)

---

## Input

- **Raw JD content (chuẩn hóa):** Vị trí **Golang Software Engineer** tại product company (hub kỹ thuật cho POS/SaaS B2B). Trách nhiệm: đề xuất phương án kỹ thuật và kế hoạch chi tiết; hỗ trợ production; tìm công nghệ/công cụ mới; xây dựng và duy trì core; TDD và DDD; tích hợp API/tools bên thứ ba. **Must-have:** ≥4 năm Golang; học ngôn ngữ/framework mới; tiếng Anh trung cấp (nghe/nói); đam mê chất lượng code. **Nice-to-have:** Docker/deploy; GenAI; eCommerce/CMS/ERP; tích hợp thanh toán/giao hàng/kế toán; code review & Git; concurrency/analytics/ML. **Location:** TP.HCM. Phần “What’s on offer” mô tả bonus, review lương 2 lần/năm, bảo hiểm, 14 ngày phép + tăng theo thâm niên, laptop, Agile, team activities, cơ hội đi nước ngoài (theo policy).
- **Bối cảnh công ty (từ brief nội bộ, không-PII):** Hub engineering cho sản phẩm POS/SaaS B2B; có các **đợt rewrite/migration** (JS/Python → Go/C#/RoR…) và bài toán **tích hợp + hiệu năng** thực tế; quy mô SME product (không phải hyperscaler). WLB và môi trường tiếng Anh được nêu trong nguồn tổng hợp — cần tự xác minh khi phỏng vấn.
- **Role target:** Senior Backend / Golang (theo [CURSOR.md](../../CURSOR.md) — primary: Senior Backend Software Engineer).
- **Company tier (ước lượng):** Mid-tier **product** B2B SaaS, niche POS/regional — phù hợp mục tiêu “product thật + học refactor” hơn “brand FAANG”.
- **Personal profile summary (không-PII, từ resume nội bộ):** Kỹ sư backend **Go**, **6+** năm kinh nghiệm; microservices, Kubernetes, CI/CD, observability; từng dẫn thiết kế/tách monolith; gRPC, Kafka/AMQP; cloud & IaC (Terraform, ArgoCD). Mục tiêu: lương cạnh tranh, làm việc tại Việt Nam, tăng trưởng nghề nghiệp, remote-first.
- **Constraints:** JD onsite TP.HCM; ứng viên ưu tiên **HCMC** và **remote-first** — cần xác nhận chính sách làm việc từ xa so với yêu cầu onsite.

---

## Output

### 1) Job Snapshot

- **Company:** Company-Alias A (product; POS/SaaS B2B; hub VN).
- **Role:** Golang Software Engineer.
- **Level:** Mid–Senior (JD yêu cầu ≥4 năm Golang).
- **Location / Work mode:** TP.HCM (JD; chi tiết hybrid/remote không rõ).
- **Core domain:** POS / SaaS cho SME; tích hợp thanh toán & nền tảng liên quan.

### 2) Skills Extraction

- **Must-have:** Golang (4+ năm); tiếng Anh giao tiếp; chất lượng code; làm việc nhóm và hỗ trợ production.
- **Nice-to-have:** Docker/deploy; GenAI; nền tảng thương mại điện tử/ERP; tích hợp thanh toán/vận chuyển/kế toán; Git, code review; concurrency / analytics / ML.
- **Responsibilities:** Thiết kế kỹ thuật + kế hoạch; vận hành production; cải tiến sản phẩm; core platform; TDD/DDD; integration.

### 3) Fit Scoring (Weighted) — theo [CURSOR.md](../../CURSOR.md) §8

| Tiêu chí | Trọng số | Điểm thành phần (0–100) | Nhận xét ngắn |
|----------|----------|-------------------------|----------------|
| Core Backend Skills | 40% | **95** | Go 6+ năm, production microservices, ownership end-to-end. |
| System Design / Scalability | 25% | **90** | Tách monolith, domain consolidation, integration, gRPC — **khớp** bối cảnh rewrite/tích hợp trong brief. |
| Domain & Product Fit | 15% | **70** | Vertical POS/F&B khác domain evidence trước đây; brief nhấn **B2B SaaS + integration + scale thực tế** → gần hơn với kinh nghiệm tích hợp/API so với đánh giá thuần JD. |
| Seniority Match | 10% | **95** | Vượt ngưỡng 4 năm; phù hợp senior. |
| Practical Constraints | 10% | **88** | Địa điểm HCMC khớp; remote-first vs onsite cần hỏi HR. |

- Core Backend Skills (40%): 95  
- System Design / Scalability (25%): 90  
- Domain & Product Fit (15%): 70  
- Seniority Match (10%): 95  
- Practical Constraints (10%): 88  

**Final Fit Score (0–100):** **89**  
*(0,4×95 + 0,25×90 + 0,15×70 + 0,1×95 + 0,1×88 ≈ 89,3 → làm tròn 89.)*

### 4) Decision Recommendation

- **Recommendation:** **Apply Now**
- **Why:** Khớp mạnh Go + distributed/microservices + technical ownership; JD nhấn TDD/DDD và tích hợp — phù hợp kinh nghiệm tách monolith và hợp đồng API. Brief nội bộ củng cố giá trị học từ **refactor/rewrite thật** (đúng hướng senior muốn depth thực chiến).
- **Risks:** Scope rewrite có thể biến động (theo brief); team không lớn → mentorship có thể hạn chế; domain POS cần thời gian làm quen dù pattern B2B integration quen thuộc.
- **Assumptions:** Mapping từ [data/raw/alias-a-brief-chatgpt.md](../../data/raw/alias-a-brief-chatgpt.md) phản ánh đúng thực tế tại thời điểm apply; JD qua nhà tuyển dụng phản ánh yêu cầu khách hàng.

### 5) Action Plan (48h)

- [ ] Gửi hồ sơ (CV tiếng Anh) nhấn mạnh Go production, tích hợp, TDD/DDD nếu có.
- [ ] Chuẩn bị 2 ví dụ: tích hợp API bên thứ ba + cải thiện độ tin cậy/observability; thêm 1 ý về **trade-off khi rewrite** (nếu có kinh nghiệm liên quan).
- [ ] Ghi câu hỏi cho HR/hiring: onsite/hybrid; ownership hub VN vs HQ; roadmap kiến trúc sau migration.
