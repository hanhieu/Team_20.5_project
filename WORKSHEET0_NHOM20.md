# WORKSHEET 0 — Learning Timeline

**Nhóm:** 20 · **Lớp:** E403  
**Thời gian:** 08:15–08:40  
**Chủ đề xuyên suốt:** Trợ lý ảo AI Agent hỗ trợ đa vai trò trong hệ sinh thái Xanh SM

---

## Mục tiêu
Xác định nhóm đã build được gì trong 15 ngày và chốt chủ đề sẽ phân tích production.

---

## 3 Kỹ năng nhóm tự tin nhất

1. **Vibe-coding**

2. **Crawl data + tiền xử lí dữ liệu**

3. **Xây dựng luồng RAG end-to-end**

---

## Mô tả sản phẩm đã làm

**Tên sản phẩm:** Xanh SM AI Support Chatbot

Chatbot AI hỗ trợ khách hàng Xanh SM — nền tảng xe điện (taxi + bike) của VinFast. Chatbot phục vụ 4 nhóm user:

| Nhóm | Vai trò |
|------|---------|
| Hành khách (`nguoi_dung`) | Đặt xe, hỏi giá, hỏi khu vực phục vụ |
| Tài xế Taxi (`tai_xe_taxi`) | Chính sách, thu nhập, BHXH |
| Tài xế Bike (`tai_xe_bike`) | Đăng ký, quyền lợi, yêu cầu bằng lái |
| Nhà hàng đối tác (`nha_hang`) | Onboarding, hoa hồng, quy trình hợp tác |

**Stack kỹ thuật:**
- LLM: GPT-4o (chat chính) + GPT-4o-mini (intent detector, query rewriter)
- Vector DB: ChromaDB v0.5.0 — local persistent, collection `xanhsm_qa`
- Embedding: `keepitreal/vietnamese-sbert` — self-hosted, không tốn API cost
- UI: Chainlit v2.0.0+ — streaming, action buttons, native 👍/👎 feedback
- Data: `data/qa.json` (~110 Q&A chính thức) + Facebook community posts (5.3 MB)
- Tool: `lookup_fare` tra cứu giá cước 45 tỉnh thành từ `Dataset/pricedata.json`
- Middleware: Rate limiter (20 req/phút/user) + Cost guard ($5/ngày)

**Production features đã có:**
- Health check endpoints (`/health`, `/ready`, `/metrics`)
- Structured JSON logging
- Graceful shutdown (SIGTERM handler)
- Security headers (X-Content-Type-Options, X-Frame-Options, CORS)
- Dockerfile multi-stage, Render.com + Railway deployment configs
- Feedback data layer lưu `data/feedback.jsonl`, inject dislike signal vào LLM turn kế tiếp

---

## Câu hỏi bắt buộc

| Câu hỏi | Trả lời |
|---------|---------|
| **Sản phẩm giải quyết bài toán gì?** | Người dùng Xanh SM (hành khách, tài xế, đối tác) mất thời gian tìm thông tin qua nhiều kênh rời rạc — website, hotline 1900 2088, mạng xã hội — không phân loại theo vai trò. Chatbot trả lời tức thì (<3s), phân loại theo user role, lọc context đúng nhóm từ knowledge base, thay thế hotline cho 80% câu hỏi thông thường. |
| **Ai là người dùng chính?** | 4 nhóm: Hành khách (đặt xe, hỏi giá, hỏi khu vực), Tài xế Taxi (chính sách hoa hồng, BHXH, thu nhập), Tài xế Bike (đăng ký, yêu cầu bằng A1/A2, quyền lợi), Nhà hàng đối tác (onboarding, hoa hồng, quy trình ký kết). |
| **Vì sao phù hợp để phân tích deployment và cost?** | Hệ thống đã có mô tả người dùng và luồng sử dụng, kiến trúc rõ ràng (RAG + LLM + tool calling + middleware), data thực tế (110+ Q&A chính thức + Facebook community data 5.3 MB, 45 tỉnh giá cước), có cost guard và metrics endpoint. Đang chạy được — đủ để phân tích production-readiness một cách cụ thể, ước lượng được traffic, dữ liệu và cost. |

---

## Phân công thành viên

| Thành viên | Vai trò | Đóng góp chính |
|------------|---------|----------------|
| Nguyễn Bình Thành | Full-stack Developer | RAG pipeline, ChromaDB, Chainlit UI, dual-search retriever, Facebook data ingestion (`app.py`, `bot/`, `rag/`, `config.py`) |
| Hàn Quang Hiếu | Product & Data Engineer | Spec, AI Product Canvas, crawl FAQ chính thức (`crawlFAQ.py`), thu thập price data, Facebook data (`spec-final.md`, datasets) |
| Phan Anh Khôi | UX/UI & System Design | UI/UX, kiến trúc hệ thống, system prompt, test cases, query rewriter (`bot/handlers/`, `.chainlit/config.toml`) |
