# WORKSHEET 2 — Cost Anatomy Lab

**Nhóm:** 20 · **Lớp:** E403  
**Thời gian:** 09:35–10:15  
**Chủ đề:** Chatbot AI hỗ trợ đa vai trò Xanh SM

---

## Mục tiêu
Bóc tách toàn bộ cost của hệ thống AI — không chỉ nhìn vào token/API, mà nhìn vào toàn bộ chi phí thực tế khi vận hành production.

---

## Ước lượng traffic

> Lưu ý: Mỗi request thực ra gồm **3 LLM calls**: intent detector (gpt-4o-mini, ~50 tokens), query rewriter (gpt-4o-mini, ~200 tokens), main chat (gpt-4o, ~1.100 tokens). Ngoài ra, một số request gọi thêm `lookup_fare` tool (không tốn token riêng, chỉ là function call trong cùng turn GPT-4o).

| Chỉ số | Conservative | Realistic | Optimistic |
|--------|-------------|-----------|-----------|
| User/ngày | 500 | 3.000 | 10.000 |
| Request/ngày | 500 | 3.000 | 10.000 |
| Peak traffic | 50 req/giờ | 300 req/giờ | 1.000 req/giờ |
| Input tokens/request (avg) — gpt-4o main | ~1.500 tokens | ~1.500 tokens | ~1.500 tokens |
| Output tokens/request (avg) — gpt-4o main | ~300 tokens | ~300 tokens | ~300 tokens |
| Input tokens/request — gpt-4o-mini (2 calls) | ~250 tokens | ~250 tokens | ~250 tokens |
| Output tokens/request — gpt-4o-mini (2 calls) | ~50 tokens | ~50 tokens | ~50 tokens |

> **Lưu ý quan trọng:** System prompt của chatbot (~800 tokens) + RAG context (~600 tokens) + conversation history → input thực tế main chat có thể **1.500–2.000 tokens/request** — cao hơn ước tính ban đầu trong phase1-summary.

---

## Bóc tách các lớp cost — Mức Realistic (3.000 req/ngày)

### Pricing thực tế (từ `bot/middleware/cost_guard.py`):
- GPT-4o: $5.00 input / 1M tokens · $15.00 output / 1M tokens
- GPT-4o-mini: $0.15 input / 1M tokens · $0.60 output / 1M tokens

| Lớp cost | Thành phần | Tính toán | Ước tính/tháng | Ghi chú |
|----------|-----------|-----------|----------------|---------|
| **Token / LLM API** | GPT-4o main chat (input) | 3.000 × 1.500 × $0.000005 × 30 | ~$675 | System prompt + RAG context + history |
| | GPT-4o main chat (output) | 3.000 × 300 × $0.000015 × 30 | ~$405 | Streaming response |
| | GPT-4o-mini intent detector | 3.000 × 50 × $0.00000015 × 30 | ~$0.7 | ~50 tokens input + 5 output |
| | GPT-4o-mini query rewriter | 3.000 × 200 × $0.00000015 × 30 | ~$2.7 | ~200 tokens input + 30 output |
| **Subtotal Token** | | | **~$1.083/tháng** | GPT-4o là cost driver lớn nhất |
| **Compute** | VPS chạy Chainlit app | 1 instance 4 vCPU / 8GB RAM | ~$50–100 | Render/Railway Starter plan |
| | ChromaDB (local, same server) | Chạy cùng VPS | $0 thêm | Không cần instance riêng |
| | Redis (optional, rate limiting) | Redis Alpine | ~$10 | Nếu multi-instance |
| **Storage** | ChromaDB vector store | ~110 Q&A + Facebook posts (~5.3MB) | ~$5 | Persistent volume |
| | Feedback log (`data/feedback.jsonl`) | Tăng theo usage | ~$1 | JSONL file |
| | Driver applications JSON | Tăng theo form submissions | ~$1 | `Dataset/driver_applications.json` |
| **Embedding** | Vietnamese SBERT (local) | Self-hosted, CPU inference | $0 | `keepitreal/vietnamese-sbert` — no API cost |
| **Human review** | Content team review feedback.jsonl | 2h/tuần × 4 tuần × $25/h | ~$200 | Đọc và update KB từ dislike feedback |
| | FAQ update & re-ingest | 1h/tuần × 4 tuần × $25/h | ~$100 | Crawl + re-ingest ChromaDB |
| **Logging & monitoring** | Structured log aggregation | CloudWatch / Grafana Cloud free tier | ~$20 | JSON logs từ app.py |
| | `/metrics` endpoint monitoring | Self-hosted (có sẵn trong app) | $0 | `daily_cost_usd`, `total_requests` |
| **Maintenance** | `crawlFAQ.py` cron job | Chạy Selenium scraper hàng ngày | ~$10 | EC2 t3.micro hoặc GitHub Actions |
| | Dependency updates & DevOps | 2h/tháng | ~$50 | `requirements.txt` updates |

---

## Tổng ước tính chi phí

| Kịch bản | req/ngày | Token cost/tháng | Infra + Human | **Tổng/tháng** |
|----------|----------|-----------------|---------------|----------------|
| Conservative | 500 | ~$180 | ~$400 | **~$580** |
| Realistic | 3.000 | ~$1.083 | ~$400 | **~$1.483** |
| Optimistic | 10.000 | ~$3.610 | ~$600 | **~$4.210** |

> **Lưu ý:** Token cost ở mức Realistic cao hơn đáng kể so với ước tính ban đầu trong phase1-summary ($600–700) do tính lại chính xác input token với system prompt + RAG context thực tế.

---

## Câu hỏi bắt buộc

| Câu hỏi | Trả lời |
|---------|---------|
| **Cost driver lớn nhất?** | **GPT-4o token cost** — chiếm ~73% tổng cost ở mức Realistic (~$1.083/$1.483). Trong đó input token (system prompt 800 tokens + RAG context 600 tokens + history) là phần lớn nhất, không phải output. |
| **Hidden cost dễ bị quên nhất?** | **Human review của content team** (~$300/tháng): đọc `feedback.jsonl` để phát hiện câu trả lời sai, update `data/qa.json`, re-ingest ChromaDB. Cost này không xuất hiện trong cloud bill nhưng là thực tế. Ngoài ra: **model warm-up time** khi container khởi động — load Vietnamese SBERT (~400 MB) mất 30–60s, cần cân nhắc warm instance. |
| **Đang ước lượng quá lạc quan ở đâu?** | **Input token count:** System prompt thực tế ~800 tokens, RAG context ~600 tokens, conversation history 2–3 turns ~400 tokens → input/request có thể 1.800–2.000 tokens, **gấp 2x ước tính ban đầu (800 tokens)**. Cần benchmark thực tế bằng OpenAI usage dashboard. |

---

## Phân tích scale 5x–10x

| Thành phần | Tăng tuyến tính? | Ghi chú |
|------------|-----------------|---------|
| LLM API cost (GPT-4o) | ✅ Tuyến tính | Tăng đúng 5x–10x — không có economy of scale |
| Compute (VPS Chainlit) | ⚠️ Bậc thang | Cần scale out khi >1.000 req/giờ concurrent — add load balancer + multiple instances |
| ChromaDB | ✅ Gần tuyến tính | Query time tăng khi collection >10k chunks, cần evaluate indexing strategy |
| Vietnamese SBERT embedding | ✅ Tuyến tính (CPU-bound) | Mỗi query cần 1 embedding inference — cần thêm instance khi tải cao |
| Human review | ⚠️ Không tuyến tính | Correction volume tăng theo usage, nhưng content team không tăng tương ứng → bottleneck |
| Rate limiting | ✅ Không đổi | Đã implement 20 req/phút/user và $5/ngày budget guard trong code |
| Storage (ChromaDB + feedback) | ✅ Tuyến tính | Tăng nhỏ, không đáng kể |
