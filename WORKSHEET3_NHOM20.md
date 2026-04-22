# WORKSHEET 3 — Cost Optimization Debate

**Nhóm:** 20 · **Lớp:** E403  
**Thời gian:** 10:15–10:50  
**Chủ đề:** Chatbot AI hỗ trợ đa vai trò Xanh SM

---

## Mục tiêu
Chọn đúng chiến lược tối ưu phù hợp với hệ thống — không tối ưu theo phong trào mà dựa trên cost anatomy đã phân tích.

---

## Bối cảnh tối ưu

**Cost driver chính (từ Worksheet 2):**
- GPT-4o token: ~73% tổng cost ở mức Realistic
- Breakdown: input token (system prompt 800t + RAG context 600t + history 400t) >> output token
- Human review: ~20% — khó tự động hóa ngay

**Kết luận:** Ưu tiên tối ưu **input token** và **giảm số lần gọi GPT-4o** — đây là đòn bẩy lớn nhất.

---

## 3 Chiến lược được chọn

---

### Chiến lược 1: Prompt Compression

| | Chi tiết |
|---|---|
| **Tiết kiệm phần nào** | **Input token cost** — system prompt hiện tại ~800 tokens (đo được qua `/metrics` endpoint). Nén xuống ~400 tokens bằng cách loại bỏ ví dụ thừa, hợp nhất các rule tương tự, giữ nguyên instruction cốt lõi. |
| **Lợi ích** | Giảm ~25% input tokens mà không ảnh hưởng đáng kể đến chất lượng; không cần thay đổi infrastructure; effort thấp (1–2 ngày). |
| **Trade-off** | Cần test kỹ với bộ test cases hiện có (`test_cases.md`) để đảm bảo không mất instruction quan trọng (đặc biệt: feedback_policy, source labeling [Chính thức]/[Cộng đồng], tool calling rules). Một số edge case có thể bị model bỏ qua khi prompt ngắn hơn. |
| **Thời điểm áp dụng** | **Làm ngay** — low effort, high impact (~$270/tháng tiết kiệm ở mức Realistic), không cần thay đổi architecture. |

---

### Chiến lược 2: Semantic Caching

| | Chi tiết |
|---|---|
| **Tiết kiệm phần nào** | **GPT-4o LLM calls** — cache câu trả lời cho các câu hỏi tương tự về ngữ nghĩa (giá cước, FAQ phổ biến). Thay vì gọi GPT-4o mỗi request, check cache trước bằng cosine similarity với Vietnamese SBERT (đã có sẵn trong hệ thống). |
| **Lợi ích** | Giảm 30–50% LLM calls cho FAQ lặp lại (giá Hà Nội, khu vực phục vụ, cách đăng ký); latency gần 0 cho cached queries (<50ms thay vì 2–3s); đã có infrastructure SBERT cho similarity search. |
| **Trade-off** | Cache có thể stale nếu giá cước hoặc chính sách thay đổi — cần TTL hợp lý: 24h cho giá cước (`pricedata.json`), 7 ngày cho FAQ ổn định. Cần storage cho cache (Redis hoặc in-memory dict — đã có Redis trong `docker-compose.yml`). Câu hỏi cá nhân hóa (liên quan session) không nên cache. |
| **Thời điểm áp dụng** | **Làm ngay** — Redis đã có trong `docker-compose.yml`, Vietnamese SBERT đã chạy local. Ước tính 1 tuần implement. Tiết kiệm 30–50% LLM cost = ~$325–540/tháng ở mức Realistic. |

---

### Chiến lược 3: Model Routing (gpt-4o-mini cho câu hỏi đơn giản)

| | Chi tiết |
|---|---|
| **Tiết kiệm phần nào** | **80–90% cost cho câu hỏi FAQ đơn giản** — giá cước, giờ hoạt động, khu vực phục vụ, cách đặt xe. Các câu hỏi này có câu trả lời rõ ràng trong context RAG, không cần reasoning phức tạp của gpt-4o. |
| **Lợi ích** | gpt-4o-mini rẻ hơn **33x input** và **25x output** so với gpt-4o. Nếu 70% query là FAQ đơn giản, tiết kiệm ~50% tổng LLM cost. Đã có intent detector (gpt-4o-mini) — có thể mở rộng để phân loại complexity. |
| **Trade-off** | Cần complexity classifier để phân loại câu hỏi đơn giản vs phức tạp (khiếu nại, tai nạn, câu hỏi ambiguous về chính sách) — cần eval framework để đo accuracy của classifier. Câu hỏi phức tạp vẫn cần gpt-4o. Cần A/B test để validate quality không giảm. |
| **Thời điểm áp dụng** | **Phase 2** — cần build eval framework trước, thu thập enough data để train/validate classifier. Không nên rush vì quality regression khó detect mà không có eval. |

---

## Ưu tiên thực hiện

| Timeline | Chiến lược | Tiết kiệm ước tính | Effort |
|----------|-----------|-------------------|--------|
| **Làm ngay (Sprint 1)** | Prompt compression | ~$270/tháng (~25% input token) | 1–2 ngày |
| **Làm ngay (Sprint 2)** | Semantic caching với TTL | ~$325–540/tháng (~30–50% LLM calls) | 1 tuần |
| **Phase 2** | Model routing (gpt-4o-mini) | ~$500–800/tháng (~50% LLM cost) | 3–4 tuần |
| **Phase 2 (nếu volume đủ lớn)** | Self-hosted model (Mistral/Qwen) | ~$800+/tháng | 2–3 tháng + GPU infra |

---

## Chiến lược nào KHÔNG được áp dụng và lý do

| Chiến lược | Lý do không chọn ngay |
|-----------|----------------------|
| **Selective inference / batch processing** | Chatbot yêu cầu real-time (<3s) — batch processing không phù hợp cho conversational UI. Chỉ áp dụng được cho driver form submission (đã async). |
| **Giảm top_k RAG** | top_k=3 đã khá thấp; giảm thêm sẽ ảnh hưởng recall — chất lượng câu trả lời sẽ giảm. Cost savings không đáng kể so với rủi ro. |
| **Self-hosted LLM (ngay)** | Cần GPU infrastructure đắt tiền và team MLOps mà nhóm chưa có. Phù hợp khi volume >50.000 req/ngày và cần lock-in avoidance. |
