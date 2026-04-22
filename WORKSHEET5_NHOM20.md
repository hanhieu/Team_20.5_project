# WORKSHEET 5 — Skills Map & Track Direction

**Nhóm:** 20 · **Lớp:** E403  
**Thời gian:** 11:25–11:45  
**Chủ đề:** Chatbot AI hỗ trợ đa vai trò Xanh SM

---

## Mục tiêu
Kết nối dự án với năng lực hiện tại của từng thành viên — chọn Track Phase 2 phù hợp và xác định kỹ năng cần bù đắp.

---

## Self-assessment (thang điểm 1–5)

> **Chú thích thang điểm:**  
> 1 = Chưa biết · 2 = Nghe qua, chưa làm · 3 = Đã làm được, cần hỗ trợ · 4 = Tự làm được · 5 = Có thể hướng dẫn người khác

| Thành viên | Vai trò | Business / Product | Infra / Data / Ops | AI Engineering / Application |
|------------|---------|-------------------|-------------------|------------------------------|
| Nguyễn Bình Thành | Full-stack Developer | 5 | 4 | 5 |
| Hàn Quang Hiếu | Product & Data Engineer | 4 | 5 | 4 |
| Phan Anh Khôi | UX/UI & System Design | 5 | 4 | 3 |
| **Trung bình nhóm** | | **4.7** | **4.3** | **4.0** |

---

## Phân tích điểm mạnh của nhóm

### Điểm mạnh rõ ràng (dựa trên sản phẩm đã làm được)

**AI Engineering / Application (avg: 4.0) — điểm mạnh nhất:**
- RAG pipeline hoàn chỉnh: dual-search retriever, deduplication, source labeling ([Chính thức]/[Cộng đồng])
- Tool calling với GPT-4o: `lookup_fare` 45 tỉnh thành, 2-turn streaming strategy
- Intent classification 3-way routing: đã test và hoạt động ổn định
- Query rewriting: phát hiện follow-up, giải quyết đại từ với heuristics + LLM
- Streaming response với Chainlit, feedback injection, data layer custom

**Business / Product (avg: 4.0) — điểm mạnh nhất thứ hai:**
- AI Product Canvas hoàn chỉnh (`canvas-final.md`)
- Spec rõ ràng: 4 user stories, eval metrics có threshold (precision ≥90%, escalation ≤20%, thumbs-up ≥75%)
- Failure modes documented với trigger, impact, mitigation
- ROI analysis 3 kịch bản (conservative/realistic/optimistic)

**Infra / Data / Ops (avg: 3.0) — cần cải thiện:**
- Có: Dockerfile multi-stage, health check endpoints, structured JSON logging, Render + Railway deploy config
- Thiếu: Monitoring dashboard, CI/CD pipeline, full audit trail logging, automated testing, knowledge base crawl pipeline chạy production

---

## Điểm cần bù đắp nếu muốn tiếp tục dự án này

| # | Kỹ năng cần bù | Lý do | Cách học/thực hành |
|---|----------------|-------|-------------------|
| 1 | **Monitoring & observability** (Infra/Ops) | Chưa có dashboard theo dõi latency, cost, quality metrics theo thời gian thực. `/metrics` endpoint có nhưng không có visualization. Không biết hệ thống đang "khỏe" hay không trong production. | Dùng Grafana Cloud free tier + export metrics từ `/metrics`; hoặc Datadog free trial. |
| 2 | **Eval framework tự động** (AI Engineering) | Chưa có automated testing cho precision/recall. Test cases hiện tại (`test_cases.md`) chạy tay. Không biết thay đổi system prompt hoặc top_k có làm regression không. | Xây pytest-based eval: load `data/qa.json`, chạy bot, so sánh output với expected answer bằng cosine similarity hoặc LLM judge. |
| 3 | **Data pipeline tự động** (Infra/Data) | `crawlFAQ.py` chạy tay với Selenium — không scheduled, không tự động re-ingest ChromaDB. Nếu Xanh SM cập nhật chính sách mà không chạy crawl, knowledge base stale trong production. | GitHub Actions cron job (free): chạy crawl hàng ngày → diff với `data/qa.json` → auto re-ingest nếu có thay đổi → alert team. |

---

## Track Phase 2 đề xuất

**☑ AI Engineering / Application**

### Lý do chọn track này:

Nhóm đã có nền tảng kỹ thuật AI Engineering vững (RAG, tool calling, intent classification, streaming — tất cả đều đang chạy). Đây là lợi thế cạnh tranh rõ ràng. Phase 2 nên **đi sâu vào production hardening** thay vì mở rộng tính năng — vì hệ thống đã có đủ feature, thiếu khâu vận hành ổn định.

### Next steps Phase 2 (cụ thể, có thể thực hiện):

| # | Mục tiêu | Output | Thời gian |
|---|---------|--------|----------|
| 1 | **Implement semantic caching + prompt compression** | Giảm ~50% LLM cost; cache layer với Redis + TTL | 2 tuần |
| 2 | **Xây eval framework tự động** | pytest suite: chạy 110 Q&A test cases, báo cáo precision/recall/escalation rate | 1 tuần |
| 3 | **Crawl pipeline tự động cập nhật KB hàng ngày** | GitHub Actions cron: crawl → diff → re-ingest → alert | 1 tuần |
| 4 | **Monitoring dashboard** | Grafana/Datadog: latency p95, cost/ngày, thumbs-down rate, RAG hit rate | 1 tuần |
| 5 | **Full audit trail logging** | Log mọi interaction vào persistent store (PostgreSQL hoặc ClickHouse) để phục vụ compliance Vingroup | 2 tuần |

### Kill criteria (khi nào pivot sang track khác):

- Nếu eval framework cho thấy precision <70% mà không thể cải thiện bằng thêm data → cần xem xét model fine-tuning (AI Research track)
- Nếu Xanh SM yêu cầu tích hợp sâu hơn với hệ thống core (real-time pricing API, booking system) → cần Infra/Data/Ops support thêm

---

## Team Note Sheet (tổng kết)

| | |
|---|---|
| **Tên nhóm** | Nhóm 20 — E403 |
| **Chủ đề** | Xanh SM AI Support Chatbot |
| **3 ràng buộc enterprise lớn nhất** | 1. PII data residency — thông tin tài xế không được rời Việt Nam (Nghị định 13/2023) · 2. Audit trail đầy đủ mọi interaction · 3. Integration với hệ thống core Xanh SM (giá cước real-time, trạng thái tài xế) |
| **Cost driver lớn nhất** | GPT-4o input token cost — system prompt (~800t) + RAG context (~600t) + history (~400t) = ~1.800t/request, chiếm ~73% tổng cost |
| **3 chiến lược optimize** | 1. Prompt compression (làm ngay, ~25% input token saving) · 2. Semantic caching TTL 24h/7d (làm ngay, ~30–50% LLM call reduction) · 3. Model routing gpt-4o-mini cho FAQ đơn giản (Phase 2) |
| **Fallback / reliability plan** | GPT-4o (timeout 8s, retry 2) → rule-based FAQ top-10 → hotline 1900 2088; circuit breaker cho OpenAI; rate limiter 20 req/phút; cost guard $5/ngày |
| **Track Phase 2** | **AI Engineering / Application** — production hardening: semantic caching, eval framework tự động, crawl pipeline, monitoring dashboard, audit trail |
