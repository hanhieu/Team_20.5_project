# Mini Project Proposal
## Xanh SM AI Support Chatbot — Production Deployment Plan

**Nhóm:** 29 · **Track:** XanhSM · VinUni A20 AI Thực Chiến
**Ngày:** 22/04/2026

---

## 1. Project Overview

### Tên sản phẩm
**Xanh SM AI Support Chatbot** — Trợ lý ảo hỗ trợ đa vai trò trong hệ sinh thái Xanh SM

### Bài toán
Người dùng Xanh SM — hành khách, tài xế, nhà hàng đối tác — mất 5–10 phút mỗi lần cần thông tin về giá cước, chính sách, khu vực phục vụ vì thông tin phân tán trên nhiều kênh (website, hotline 1900 2088, mạng xã hội) và không được phân loại theo vai trò. Hotline hiện nhận ~300+ cuộc gọi/ngày cho các câu hỏi lặp lại có thể tự động hóa.

Đặc biệt, **khách nước ngoài** — nhóm dùng mobility nhiều nhất (không có xe riêng, không quen đường) — bị underserved nhất vì hotline và website chủ yếu tiếng Việt.

### Giải pháp AI
Chatbot RAG (Retrieval-Augmented Generation) tích hợp trực tiếp vào app Xanh SM:
- Trả lời tức thì (<3s) bằng tiếng Việt **và** tiếng Anh (auto-detect ngôn ngữ)
- Phân loại theo 4 vai trò: 👤 Hành khách · 🚖 Tài xế Taxi · 🛵 Tài xế Bike · 🍜 Nhà hàng
- Tra cứu giá cước thực tế 50+ tỉnh thành qua function tool (không phụ thuộc semantic search)
- Guided form đăng ký tài xế 5 bước
- Hard-route câu hỏi khẩn cấp (tai nạn, khiếu nại) sang hotline ngay lập tức

### Kiến trúc kỹ thuật hiện tại (prototype)
```
User chọn vai trò (4 nút)
    ↓
Intent Detector (GPT-4o-mini) → driver_registration | general
    ↓ [general]
Query Rewriter (GPT-4o-mini) — giải quyết follow-up, đại từ, ngữ cảnh
    ↓
Dual-Search RAG (ChromaDB + Vietnamese SBERT)
  ├── Search 1: filter user_type → top 3 chunks [Chính thức]
  └── Search 2: no filter → top 3 chunks [Cộng đồng]
    ↓ deduplicate → max 6 chunks
GPT-4o streaming response
  └── nếu hỏi giá → gọi lookup_fare tool → bảng giá thực từ JSON
```

**Stack:** Python · Chainlit · OpenAI GPT-4o + GPT-4o-mini · ChromaDB · Vietnamese SBERT · Selenium crawler

**Knowledge base:**
- ~110 Q&A chính thức (crawl từ xanhsm.com/helps)
- Facebook community posts (Apify scraper)
- Bảng giá cước 50+ tỉnh (pricedata.json, price-bike.json)
- Thông tin dịch vụ đầy đủ (xanhsm_services.json, cities_type.json)

---

## 2. Enterprise Context

### Bối cảnh tổ chức
Xanh SM là thương hiệu của **GSM (Green and Smart Mobility)** — công ty con của Vingroup, tập đoàn lớn nhất Việt Nam. Điều này đặt ra các yêu cầu enterprise nghiêm ngặt mà prototype hiện tại chưa đáp ứng đủ.

### 3 ràng buộc enterprise lớn nhất

#### Ràng buộc 1: Data Residency & PII Compliance 🔴
**Vấn đề:** Thông tin đăng ký tài xế (họ tên, số điện thoại, số bằng lái) là **PII (Personally Identifiable Information)**. Theo Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân tại Việt Nam, dữ liệu này phải được lưu trữ trong hạ tầng Việt Nam.

**Hiện trạng:** Prototype đang gọi OpenAI API — mọi nội dung hội thoại (bao gồm thông tin tài xế nhập vào form) đi qua server tại Mỹ. Đây là vi phạm tiềm tàng.

**Yêu cầu production:**
- PII phải được redact/mask trước khi gửi ra API bên ngoài
- Hoặc dùng Azure OpenAI với data residency tại Southeast Asia
- Thông tin tài xế lưu trong database nội bộ (không phải file JSON)
- Cần ký DPA (Data Processing Agreement) với OpenAI/Microsoft

#### Ràng buộc 2: Audit Trail & Traceability 🟡
**Vấn đề:** Vingroup yêu cầu log đầy đủ mọi interaction để phục vụ compliance, điều tra sự cố, và cải thiện chất lượng.

**Hiện trạng:** Chỉ có `feedback.jsonl` cơ bản — không đủ cho enterprise audit.

**Yêu cầu production:**
- Log mỗi request: timestamp, user_type, session_id, query, rewritten_query, RAG chunks retrieved, response, latency, feedback
- Retention policy: tối thiểu 90 ngày
- Immutable audit log (không thể sửa/xóa)
- Dashboard cho content team theo dõi quality metrics

#### Ràng buộc 3: Integration với Hệ thống Core 🟡
**Vấn đề:** Giá cước, chính sách, trạng thái tài xế trong hệ thống core của Xanh SM thay đổi thường xuyên. Prototype dùng file JSON tĩnh → stale data là failure mode nguy hiểm nhất (user đặt xe với giá sai).

**Yêu cầu production:**
- API integration với hệ thống pricing của Xanh SM (real-time hoặc sync hàng giờ)
- Webhook để nhận thông báo khi chính sách thay đổi → trigger re-ingest KB
- Timestamp + auto-disclaimer cho mọi FAQ entry (đã implement một phần)

### Phân loại dữ liệu theo mức độ nhạy cảm

| Loại dữ liệu | Mức độ | Xử lý |
|---|---|---|
| Thông tin đăng ký tài xế (họ tên, SĐT, bằng lái) | 🔴 PII — Cao | Lưu on-prem, KHÔNG gửi ra API ngoài |
| Lịch sử hội thoại | 🟡 Trung bình | Session-based, log có retention policy |
| Feedback / correction log | 🟡 Trung bình | Cần audit trail, batch process |
| Giá cước, FAQ | 🟢 Thấp — Công khai | Có thể dùng cloud cache |
| Facebook community data | 🟡 Trung bình | Cần xem xét Meta ToS |

---

## 3. Deployment Choice

### Quyết định: Hybrid Architecture

**LLM Inference (Cloud) + Data & Vector DB (On-prem / Private Cloud VN)**

```
┌─────────────────────────────────────────────────────────┐
│                    USER (App Xanh SM)                    │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTPS
┌─────────────────────────▼───────────────────────────────┐
│              API Gateway + Rate Limiter                  │
│              (On-prem / Private Cloud VN)                │
└──────┬──────────────────┬──────────────────┬────────────┘
       │                  │                  │
┌──────▼──────┐  ┌────────▼────────┐  ┌─────▼──────────┐
│  Chainlit   │  │   ChromaDB      │  │  Audit Logger  │
│  App Server │  │   (Vector DB)   │  │  (PostgreSQL)  │
│  (On-prem)  │  │   (On-prem)     │  │  (On-prem)     │
└──────┬──────┘  └────────┬────────┘  └────────────────┘
       │                  │
       │ [Query only,      │ [Embeddings
       │  no PII]          │  local SBERT]
┌──────▼──────────────────┘
│  OpenAI API / Azure OpenAI
│  (Cloud — GPT-4o, GPT-4o-mini)
│  [Data residency: SE Asia nếu dùng Azure]
└─────────────────────────────────────────
```

### Lý do chọn Hybrid

| Thành phần | On-prem | Cloud | Lý do |
|---|---|---|---|
| LLM inference (GPT-4o) | | ✅ | Không có GPU on-prem đủ mạnh; OpenAI/Azure cung cấp SLA tốt |
| ChromaDB + SBERT embedding | ✅ | | Zero latency cho retrieval; không cần internet cho mỗi query |
| PII data (thông tin tài xế) | ✅ | | Compliance — không được rời hạ tầng VN |
| Audit log | ✅ | | Immutable, retention policy nội bộ |
| FAQ knowledge base | ✅ | | Giảm phụ thuộc internet; dễ update |
| Semantic cache | | ✅ | Redis Cloud hoặc on-prem Redis đều được |

### Luồng xử lý PII-safe
```
User nhập thông tin tài xế (họ tên, SĐT, bằng lái)
    ↓
PII Interceptor (on-prem) — KHÔNG gửi ra OpenAI
    ↓
Lưu trực tiếp vào PostgreSQL (on-prem)
    ↓
Confirmation message được generate locally (template, không cần LLM)
```

---

## 4. Cost Analysis

### Giả định kỹ thuật
Mỗi request thực ra gồm **3 LLM calls**:
1. Intent detector: GPT-4o-mini, ~50 input + 5 output tokens
2. Query rewriter: GPT-4o-mini, ~300 input + 80 output tokens (chỉ khi cần)
3. Main chat: GPT-4o, ~1.500 input (system prompt 800 + RAG context 600 + history 100) + 350 output tokens

### Bảng giá tham chiếu (tháng 4/2026)
- GPT-4o: $2.50/1M input tokens · $10.00/1M output tokens
- GPT-4o-mini: $0.15/1M input tokens · $0.60/1M output tokens

### Cost breakdown theo kịch bản

| Thành phần | Conservative (500 req/ngày) | Realistic (3.000 req/ngày) | Optimistic (10.000 req/ngày) |
|---|---|---|---|
| GPT-4o main chat | ~$65/tháng | ~$390/tháng | ~$1.300/tháng |
| GPT-4o-mini (intent + rewrite) | ~$1/tháng | ~$6/tháng | ~$20/tháng |
| **Tổng LLM API** | **~$66/tháng** | **~$396/tháng** | **~$1.320/tháng** |
| Compute (App server 4vCPU/8GB) | $50/tháng | $100/tháng | $300/tháng |
| ChromaDB + SBERT (on-prem) | $0 thêm | $0 thêm | $20/tháng (scale) |
| Storage (logs, DB) | $5/tháng | $15/tháng | $40/tháng |
| Monitoring & logging | $10/tháng | $20/tháng | $50/tháng |
| **Tổng infra** | **~$65/tháng** | **~$135/tháng** | **~$410/tháng** |
| Human review (content team) | $100/tháng | $300/tháng | $500/tháng |
| Maintenance & DevOps | $50/tháng | $100/tháng | $200/tháng |
| **Tổng human cost** | **~$150/tháng** | **~$400/tháng** | **~$700/tháng** |
| **TỔNG** | **~$281/tháng** | **~$931/tháng** | **~$2.430/tháng** |

### Cost driver analysis
- **GPT-4o token cost = ~70% tổng cost** ở mọi kịch bản → đây là nơi cần optimize trước
- **Human review = ~15–30% tổng cost** — hidden cost dễ bị quên, không xuất hiện trong cloud bill
- **Infra = ~20–25%** — tương đối ổn định, không scale tuyến tính

### ROI
| Kịch bản | Cost/tháng | Hotline calls saved | Benefit/tháng | Net ROI |
|---|---|---|---|---|
| Conservative | ~$281 (~7M VND) | 300 calls/ngày | ~225M VND | **+218M VND/tháng** |
| Realistic | ~$931 (~23M VND) | 2.250 calls/ngày | ~1.35 tỷ VND | **+1.33 tỷ VND/tháng** |
| Optimistic | ~$2.430 (~60M VND) | 8.500 calls/ngày | ~5.1 tỷ VND | **+5.04 tỷ VND/tháng** |

*Giả định: 1 cuộc gọi hotline = 15 phút × 50.000 VND/phút agent*

---

## 5. Optimization Plan

### Nguyên tắc: Optimize đúng chỗ, đúng thời điểm

Cost driver lớn nhất là GPT-4o token → tập trung optimize ở đây trước.

### Chiến lược 1: Prompt Compression — Làm ngay (1–2 ngày)

**Vấn đề:** System prompt hiện tại ~800 tokens. Nhiều phần có thể viết ngắn hơn mà không mất instruction.

**Cách làm:**
- Loại bỏ ví dụ dư thừa trong prompt
- Dùng bullet points thay vì câu đầy đủ
- Merge các rule tương tự

**Kết quả kỳ vọng:** Giảm từ 800 → 400 tokens input/request → tiết kiệm ~20% input token cost

**Rủi ro:** Một số rule có thể bị model bỏ qua khi prompt ngắn hơn → cần A/B test trước khi deploy

### Chiến lược 2: Semantic Caching — Làm ngay (1 tuần)

**Vấn đề:** Nhiều user hỏi câu hỏi tương tự (giá cước Hà Nội, khu vực phục vụ, cách đăng ký tài xế). Mỗi câu hỏi đều gọi GPT-4o đầy đủ.

**Cách làm:**
- Cache response theo embedding similarity (cosine > 0.92 → cache hit)
- TTL theo loại nội dung:
  - Giá cước: TTL 24h (thay đổi thường xuyên)
  - FAQ chính sách: TTL 7 ngày
  - Thông tin dịch vụ: TTL 3 ngày
- Implementation: Redis + embedding lookup trước khi gọi LLM

**Kết quả kỳ vọng:** Giảm 30–50% LLM calls cho FAQ lặp lại; latency ~0ms cho cache hit

**Rủi ro:** Cache stale nếu giá/chính sách thay đổi → cần invalidation webhook từ hệ thống core Xanh SM

### Chiến lược 3: Model Routing — Phase 2 (2–4 tuần)

**Vấn đề:** GPT-4o đắt hơn GPT-4o-mini ~25x. Nhiều câu hỏi FAQ đơn giản không cần GPT-4o.

**Cách làm:**
- Classifier phân loại câu hỏi: simple (giá cước, giờ hoạt động, khu vực) vs complex (khiếu nại, tình huống đặc biệt, multi-turn)
- Simple → GPT-4o-mini (~$0.0002/request)
- Complex → GPT-4o (~$0.005/request)
- Ước tính 60–70% câu hỏi là simple

**Kết quả kỳ vọng:** Giảm 50–60% LLM cost tổng thể

**Rủi ro:** Cần eval framework để đảm bảo GPT-4o-mini đủ chất lượng cho simple queries trước khi deploy

### Timeline tối ưu

```
Tuần 1:  Prompt compression → -20% input tokens
Tuần 2:  Semantic caching (Redis) → -30% LLM calls
Tuần 3:  Eval framework cho model routing
Tuần 4+: Model routing deploy → -50% LLM cost tổng
```

**Kết quả kỳ vọng sau 1 tháng optimize:** Giảm từ ~$931/tháng xuống ~$400–500/tháng ở mức Realistic

---

## 6. Reliability Plan

### Fallback Chain

```
Request đến
    ↓
[1] Intent classifier (GPT-4o-mini, timeout 2s)
    ↓ timeout/error → fallback: intent = "general"
[2] RAG retrieval (ChromaDB local, timeout 1s)
    ↓ timeout/error → context = "(Không tìm thấy thông tin)"
[3] GPT-4o main chat (timeout 8s, streaming)
    ↓ timeout/error → retry 1 lần (exponential backoff 2s)
    ↓ vẫn lỗi → Rule-based FAQ (top 20 câu hỏi phổ biến, hardcoded)
    ↓ không match → "Xin lỗi, hệ thống đang bận. Vui lòng thử lại hoặc gọi hotline 1900 2088"
```

### 3 Failure Scenarios & Response

#### Scenario 1: Traffic spike (campaign khuyến mãi Xanh SM)
| | Chi tiết |
|---|---|
| Dấu hiệu | p95 latency > 5s; request queue depth > 100 |
| Tác động | Response chậm → user bỏ chatbot, gọi hotline → hotline quá tải |
| Ngắn hạn | Rate limiting: max 10 req/phút/session; queue với async processing; hiển thị "Đang xử lý..." |
| Dài hạn | Horizontal scaling (multiple instances + load balancer); semantic cache giảm LLM calls; async queue (Redis/Celery) cho non-urgent |

#### Scenario 2: OpenAI API outage
| | Chi tiết |
|---|---|
| Dấu hiệu | OpenAI error rate > 5% trong 1 phút |
| Tác động | Chatbot không trả lời được |
| Ngắn hạn | Retry với exponential backoff; fallback sang rule-based FAQ |
| Dài hạn | Multi-provider: OpenAI → Azure OpenAI → Anthropic Claude; circuit breaker pattern |

#### Scenario 3: Knowledge base stale (giá thay đổi)
| | Chi tiết |
|---|---|
| Dấu hiệu | Mismatch giữa giá chatbot trả lời và giá thực tế trên app |
| Tác động | User đặt xe với kỳ vọng giá sai → khiếu nại, mất tin tưởng |
| Ngắn hạn | Auto-disclaimer "Giá có thể đã thay đổi, xác nhận khi đặt xe" cho mọi câu trả lời về giá |
| Dài hạn | Webhook từ hệ thống core Xanh SM → trigger re-ingest KB; daily crawl pipeline |

### Monitoring Metrics

| Metric | Target | Alert khi |
|---|---|---|
| p95 response latency | < 3s | > 5s trong 5 phút |
| Error rate | < 1% | > 5% trong 1 phút |
| Escalation rate (% chuyển hotline) | ≤ 20% | > 40% liên tục 1 ngày |
| Thumbs-down rate | < 25% | > 40% trong 1 ngày |
| RAG hit rate (chunk score > threshold) | > 80% | < 60% trong 1 ngày |
| OpenAI API cost/ngày | < $15 (Realistic) | > $25 (anomaly detection) |
| Cache hit rate | > 30% | < 10% (cache không hiệu quả) |

### SLA Đề xuất
- **Availability:** 99.5% uptime (cho phép ~3.6h downtime/tháng)
- **Latency:** p95 < 3s, p99 < 8s
- **Fallback:** Luôn có response trong 10s (dù là rule-based hoặc hotline redirect)

---

## 7. Track Recommendation & Next Steps

### Track Phase 2: AI Engineering / Application ✅

**Lý do:**
- Nhóm đã có nền tảng kỹ thuật tốt (RAG + LLM + tool calling đã chạy được)
- Điểm yếu hiện tại là production hardening, không phải AI capability
- Cần đi sâu vào: monitoring, caching, eval framework, data flywheel

### 4 Next Steps cụ thể

**Step 1 — Production Hardening (Tuần 1–2)**
- Implement semantic caching (Redis, TTL theo loại nội dung)
- Prompt compression (giảm 20% input tokens)
- Structured logging (mọi request → PostgreSQL audit log)
- PII interceptor (mask thông tin tài xế trước khi gửi OpenAI)

**Step 2 — Eval Framework (Tuần 3–4)**
- Xây test suite tự động: 50 câu hỏi mẫu × 4 user types = 200 test cases
- Metrics: precision (câu trả lời đúng so với FAQ chính thức), latency, escalation rate
- CI/CD: chạy eval tự động trước mỗi deploy
- Threshold: precision < 80% → block deploy

**Step 3 — Data Flywheel (Tháng 2)**
- Crawl pipeline tự động (cron job hàng ngày) cập nhật FAQ từ xanhsm.com
- Webhook nhận thông báo thay đổi giá từ hệ thống core
- Correction log → content team review hàng tuần → re-ingest KB
- Dashboard theo dõi: stale entries, correction volume, acceptance rate

**Step 4 — Model Routing (Tháng 2–3)**
- Classifier phân loại simple vs complex queries
- Simple → GPT-4o-mini (tiết kiệm ~50% LLM cost)
- Eval framework đảm bảo chất lượng trước khi deploy routing

### Kill Criteria
Dừng và review lại nếu:
- Precision < 80% sau 2 tuần fine-tuning
- Escalation rate > 40% liên tục 1 tháng
- Cost > benefit trong 2 tháng liên tiếp
- Có vi phạm PII compliance được phát hiện

---

*Mini Project Proposal — Nhóm 29 — Track XanhSM — VinUni A20 AI Thực Chiến*
