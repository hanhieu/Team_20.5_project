# WORKSHEET 4 — Scaling & Reliability Tabletop

**Nhóm:** 20 · **Lớp:** E403  
**Thời gian:** 10:50–11:25  
**Chủ đề:** Chatbot AI hỗ trợ đa vai trò Xanh SM

---

## Mục tiêu
Luyện phản ứng khi hệ thống gặp tải tăng hoặc provider lỗi — từ đó xây dựng fallback proposal có thể deploy thực tế.

---

## Tình huống 1: Traffic tăng đột biến
*Kịch bản: Xanh SM chạy campaign khuyến mãi lớn, nhiều user hỏi cùng lúc về giá ưu đãi*

| | Chi tiết |
|---|---|
| **Tác động tới user** | Response time tăng từ <3s lên 10–30s; một số request timeout (budget guard $5/ngày có thể kích hoạt sớm); user bỏ chatbot và gọi hotline thay — tạo tải gấp đôi cho cả hai kênh. Chainlit WebSocket connection pool bị saturate → connection refused với user mới. |
| **Phản ứng ngắn hạn** | Kích hoạt rate limiter ngặt hơn (đã có: 20 req/phút/user trong `bot/middleware/rate_limiter.py`); tăng tạm thời `DAILY_BUDGET_USD` trong `config.py` (có thể set qua env var); hiển thị "Hệ thống đang bận, vui lòng chờ ~X giây" thay vì spinner vô tận. |
| **Giải pháp dài hạn** | Horizontal scaling: multiple Chainlit instances + NGINX load balancer; Redis cho cross-instance rate limiting (đã có Redis trong `docker-compose.yml`); semantic cache (Worksheet 3) để giảm số LLM calls thực tế; async queue (Celery/Redis) cho non-urgent requests (driver form submission đã async). |
| **Metric cần monitor** | p95 latency (target: <5s), active WebSocket connections, request queue depth, OpenAI API rate limit hits, `daily_cost_usd` từ `/metrics` endpoint, error rate (5xx). |

---

## Tình huống 2: OpenAI API timeout / outage
*Kịch bản: OpenAI có sự cố toàn cầu (đã xảy ra nhiều lần trong lịch sử), chatbot không gọi được API*

| | Chi tiết |
|---|---|
| **Tác động tới user** | Intent detector (gpt-4o-mini) timeout → routing không xác định được intent → có thể loop hoặc fail. GPT-4o main chat timeout → user nhận error hoặc spinner vô tận. Ảnh hưởng 100% request vì cả 3 LLM calls đều phụ thuộc OpenAI. |
| **Phản ứng ngắn hạn** | Retry với exponential backoff (đã có implicit trong OpenAI SDK, cần config max_retries=2, timeout=8s); fallback intent → "general"; fallback RAG context → trả câu trả lời từ top-10 FAQ phổ biến (hard-coded hoặc từ ChromaDB không qua LLM); hiển thị "Hệ thống tạm thời gián đoạn. Hotline: 1900 2088". |
| **Giải pháp dài hạn** | Multi-provider fallback: OpenAI → Anthropic Claude (claude-haiku-4-5 cho đơn giản, claude-sonnet-4-6 cho phức tạp) → Azure OpenAI; circuit breaker pattern để không spam API khi đang lỗi (half-open state sau 30s); monitor OpenAI status page tự động và alert team. |
| **Metric cần monitor** | OpenAI API error rate (target: <1%), p99 timeout rate, fallback activation rate, MTTR (mean time to recovery), số lần circuit breaker mở trong ngày. |

---

## Tình huống 3: RAG retrieval chất lượng thấp — bot không tìm được context tốt
*Kịch bản: User hỏi về chính sách mới chưa có trong knowledge base, hoặc hỏi theo cách khác với Q&A hiện có*

| | Chi tiết |
|---|---|
| **Tác động tới user** | Bot trả lời chung chung hoặc hallucinate — không dùng được `lookup_fare` đúng lúc, hoặc trả lời theo community post không chính xác. User phải hỏi lại nhiều lần → frustration → escalation. Thumbs-down rate tăng → feedback.jsonl chứa nhiều correction. |
| **Phản ứng ngắn hạn** | Query rewriter đã có — đảm bảo luôn active. Tăng `top_k` từ 3 lên 5 để có nhiều context hơn (config trong `rag/retriever.py`). Thêm confidence threshold: nếu similarity score thấp (<0.5), bot tự nhận "Tôi không tìm thấy thông tin chính xác về vấn đề này. Vui lòng liên hệ hotline: 1900 2088" thay vì hallucinate. |
| **Giải pháp dài hạn** | Hybrid search: BM25 (keyword) + vector search → combine scores; re-ranking layer (cross-encoder) để chọn chunk tốt nhất; tự động crawl và ingest FAQ mới hàng ngày (`crawlFAQ.py` → scheduled cron); data flywheel từ feedback: dislike → review → update `data/qa.json` → re-ingest ChromaDB. |
| **Metric cần monitor** | RAG hit rate (% query có max chunk score >0.5), escalation rate (target: <20%), thumbs-down rate (target: <25%), số correction per ngày từ `feedback.jsonl`. |

---

## Fallback Proposal

```
Request đến
    ↓
[Middleware] Rate limiter (20 req/phút) — nếu vượt → "Vui lòng chờ"
    ↓
[Middleware] Cost guard ($5/ngày) — nếu vượt → "Hệ thống tạm thời giới hạn. Hotline: 1900 2088"
    ↓
Intent Detector (gpt-4o-mini, timeout 2s)
    ↓ timeout/error → fallback intent = "general"
    ↓
ChromaDB RAG Retrieval (Vietnamese SBERT local, timeout 1s)
    ↓ timeout/error → context = "(Không tìm thấy thông tin)"
    ↓ score < threshold → add disclaimer "Thông tin có thể chưa đầy đủ"
    ↓
Query Rewriter (gpt-4o-mini, timeout 2s)
    ↓ timeout/error → dùng query gốc không rewrite
    ↓
GPT-4o main chat (timeout 8s, max_retries=2)
    ↓ success → stream response về user
    ↓ timeout sau 2 retries → SWITCH TO FALLBACK PATH
        ↓
        Rule-based FAQ response (top 10 câu hỏi phổ biến hard-coded)
        ↓ không match → "Xin lỗi, hệ thống đang bận. Hotline: 1900 2088"

[Parallel track — luôn chạy]
    ↓
Log toàn bộ interaction (intent, context, query, response, latency, cost)
    ↓
Record cost → daily_cost accumulator (/metrics endpoint)
```

---

## Phân loại request: Real-time vs Async

| Loại request | Xử lý | Lý do |
|---|---|---|
| Hỏi giá cước (`lookup_fare`) | **Real-time** | User đang chuẩn bị đặt xe, cần quyết định ngay — không thể chờ |
| Hỏi FAQ thông thường (khu vực, giờ hoạt động) | **Real-time** | Kỳ vọng conversational response tức thì (<3s) |
| Đăng ký tài xế (5-step form submit) | **Async OK** | Lưu vào `Dataset/driver_applications.json`, xử lý sau — confirm qua SMS/email |
| Feedback log (feedback.jsonl) | **Async** | Không cần real-time, batch process hàng ngày bởi content team |
| Crawl FAQ từ xanhsm.com | **Async (scheduled)** | `crawlFAQ.py` chạy cron hàng ngày, không blocking |

---

## Các metric cần monitor tổng hợp

| Category | Metric | Target | Alert threshold |
|----------|--------|--------|----------------|
| Latency | p95 end-to-end | <5s | >10s trong 5 phút |
| Latency | p95 GPT-4o turn | <3s | >6s |
| Quality | Thumbs-down rate | <25% | >40% trong 1 ngày |
| Quality | Escalation rate | <20% | >40% |
| Quality | RAG hit rate | >70% | <50% |
| Cost | Daily LLM spend | <$5 | >$4 (warning trước khi block) |
| Reliability | OpenAI error rate | <1% | >5% |
| Reliability | Fallback activation rate | <5% | >15% |
| Capacity | Active WebSocket connections | Monitor | >80% của limit |
