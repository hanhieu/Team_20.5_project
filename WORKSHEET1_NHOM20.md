# WORKSHEET 1 — Enterprise Deployment Clinic

**Nhóm:** 20 · **Lớp:** E403  
**Thời gian:** 08:40–09:25  
**Chủ đề:** Chatbot AI hỗ trợ đa vai trò Xanh SM

---

## Mục tiêu
Hiểu sự khác biệt giữa deploy demo và deploy enterprise — xác định ràng buộc thực tế khi triển khai cho Vingroup/Xanh SM.

---

## Bối cảnh tổ chức

**Khách hàng/Tổ chức sử dụng:** Xanh SM — thương hiệu xe điện của VinFast/Vingroup

Xanh SM là thương hiệu xe điện của VinFast (thuộc Vingroup) — tập đoàn lớn nhất Việt Nam với yêu cầu compliance cao, hệ thống IT nội bộ phức tạp (ERP, CRM, booking platform), và dữ liệu khách hàng nhạy cảm (thông tin cá nhân tài xế, lịch sử chuyến đi, dữ liệu thanh toán). Chatbot sẽ là kênh hỗ trợ chính thức cho 4 nhóm user — tiếp xúc trực tiếp với khách hàng cuối.

---

## Dữ liệu mà hệ thống sẽ động đến

| Loại dữ liệu | Nguồn trong hệ thống | Mức độ nhạy cảm | Ghi chú |
|---|---|---|---|
| Thông tin đăng ký tài xế (họ tên, SĐT, bằng lái) | `Dataset/driver_applications.json` | 🔴 Cao — PII | Dữ liệu định danh cá nhân, bắt buộc lưu tại Việt Nam theo Nghị định 13/2023/NĐ-CP |
| Lịch sử hội thoại chatbot | `cl.user_session` (in-memory) | 🟡 Trung bình | Session-based, không persist lâu dài — nhưng có thể chứa thông tin nhạy cảm nếu user nhắc đến SĐT/địa chỉ |
| Feedback & correction log | `data/feedback.jsonl` | 🟡 Trung bình | Chứa nội dung câu hỏi user — cần audit trail, retention policy |
| Giá cước (`Dataset/pricedata.json`) | File JSON tĩnh — 45 tỉnh thành × 4 dịch vụ | 🟢 Thấp | Thông tin công khai, nhưng phải đồng bộ với hệ thống core để tránh thông tin lỗi thời |
| FAQ knowledge base (`data/qa.json`) | ~110 Q&A chính thức | 🟢 Thấp | Thông tin công khai, cần cập nhật định kỳ theo chính sách Xanh SM |
| Facebook community data | `Dataset/dataset_facebook-groups-scraper_*.json` (5.3 MB) | 🟡 Trung bình | Cần xem xét ToS của Meta; không được dùng làm nguồn trích dẫn chính thức |

---

## 3 Ràng buộc enterprise lớn nhất

### Ràng buộc 1: Data residency & PII compliance (Nghị định 13/2023)

Thông tin tài xế đăng ký (họ tên, SĐT, số bằng lái) là **Dữ liệu cá nhân nhạy cảm** theo Nghị định 13/2023/NĐ-CP về Bảo vệ dữ liệu cá nhân. Dữ liệu này **phải được lưu tại hạ tầng tại Việt Nam**, không được gửi ra nước ngoài mà không có Thỏa thuận Xử lý Dữ liệu (DPA). Hệ thống hiện tại gọi OpenAI API → câu hỏi của user (có thể chứa PII nếu user nhắc tên/SĐT) đi qua server tại Mỹ — vi phạm nếu triển khai production.

### Ràng buộc 2: Audit trail & traceability đầy đủ

Vingroup yêu cầu log đầy đủ mọi interaction (ai hỏi gì, bot trả lời gì, timestamp, user_type, kết quả tool calling, feedback) để phục vụ compliance nội bộ và điều tra sự cố. Hệ thống hiện tại chỉ có:
- `data/feedback.jsonl` (chỉ lưu khi user bấm 👍/👎)
- Structured JSON logging (console/CloudWatch)

Chưa có: full interaction log với message ID, session ID, latency, token count per request — **chưa đủ để audit**.

### Ràng buộc 3: Integration với hệ thống nội bộ Xanh SM

Giá cước thực tế, trạng thái tài xế, lịch sử chuyến đi, chính sách hoa hồng nằm trong hệ thống core của Xanh SM (không phải file JSON tĩnh). Chatbot đang dùng `Dataset/pricedata.json` cập nhật thủ công — **stale data risk**. Cần API integration hoặc data sync pipeline (event-driven hoặc scheduled) để chatbot luôn có thông tin cập nhật.

---

## Lựa chọn mô hình triển khai

**Lựa chọn:** ☑ **Hybrid — Cloud (LLM inference) + On-prem / Private Cloud VN (data & vector DB)**

### 2 Lý do lựa chọn Hybrid

**Lý do 1 — Không có GPU on-prem đủ mạnh để self-host LLM tương đương GPT-4o:**  
LLM inference (GPT-4o) đòi hỏi GPU cluster tốn kém — Xanh SM không có sẵn. Cloud inference là lựa chọn duy nhất thực tế ở giai đoạn đầu. Tuy nhiên, **PII data (thông tin tài xế, lịch sử chat có thể chứa thông tin cá nhân) phải ở on-prem hoặc private cloud Việt Nam** để đáp ứng yêu cầu data residency theo Nghị định 13/2023.

**Lý do 2 — ChromaDB và knowledge base cần on-prem để giảm latency và tăng independence:**  
ChromaDB với Vietnamese SBERT chạy on-prem cho latency retrieval <100ms, không phụ thuộc internet cho mỗi query. Chỉ gọi ra ngoài khi cần LLM inference. Nếu cloud LLM có sự cố (OpenAI outage), rule-based fallback vẫn chạy được từ on-prem — **tăng reliability**.

---

## Gợi ý thảo luận

| Câu hỏi | Trả lời |
|---------|---------|
| **Có cần audit trail không?** | Có — mọi interaction cần log đầy đủ: timestamp, user_type, session_id, query gốc, query sau rewrite, chunks retrieved, response, token count, cost ước tính, feedback. Hiện tại chưa có logging đầy đủ ở mức này. |
| **Dữ liệu có được rời khỏi tổ chức không?** | Câu hỏi thông thường (không chứa PII) có thể gửi OpenAI API để inference. Thông tin tài xế (họ tên, SĐT, bằng lái) và dữ liệu feedback **KHÔNG được gửi ra ngoài**. Cần sanitize input trước khi gọi LLM nếu có PII. |
| **Cần tích hợp hệ thống cũ không?** | Có — cần sync giá cước và chính sách từ hệ thống core Xanh SM (thay vì file JSON tĩnh). Cần webhook hoặc scheduled sync pipeline. Cần API integration để kiểm tra trạng thái tài xế, lịch sử chuyến đi theo yêu cầu. |
| **Nếu trả lời sai thì ai bị ảnh hưởng đầu tiên?** | Hành khách bị báo giá sai → thanh toán nhầm; Tài xế hiểu sai chính sách thu nhập/BHXH → vi phạm quy định → bị phạt/khóa tài khoản; Nhà hàng đối tác hiểu sai hoa hồng → tranh chấp hợp đồng. **Rủi ro pháp lý và uy tín cho Vingroup.** |
