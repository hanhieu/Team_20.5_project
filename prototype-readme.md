# Prototype — Xanh SM AI Support Chatbot

## Mô tả
Chatbot AI hỗ trợ khách hàng Xanh SM trả lời câu hỏi theo từng nhóm người dùng (Hành khách, Tài xế Taxi, Tài xế Bike, Nhà hàng đối tác). Hệ thống dùng RAG (Retrieval-Augmented Generation) để tìm kiếm câu trả lời từ knowledge base chính thức và dữ liệu cộng đồng Facebook, sau đó sinh câu trả lời bằng GPT-4o theo luồng streaming. Ngoài RAG, agent còn được trang bị **tool calling** để tra cứu giá cước thực tế theo thành phố (Xanh SM Car, Luxury, Premium, phụ phí).

## Level
- [ ] **Sketch** — Vẽ user journey trên giấy/slides, chưa build gì
- [ ] **Mock prototype** — UI build được (HTML/app) nhưng chưa gắn AI thật
- [x] **Working prototype** — Có AI chạy thật, input → AI xử lý → output

## Links
- Prototype: https://github.com/hanhieu/Team_29_project
- Prompt test log: _(nếu có — file ghi kết quả test prompt với các câu hỏi mẫu)_
- Video demo backup: _(nếu có — phòng internet chết khi demo)_

## Kiến trúc hệ thống

```
User chọn loại tài khoản (tùy chọn — 4 nút: Hành khách / Tài xế Taxi / Tài xế Bike / Nhà hàng)
    ↓
Session lưu user_type (hoặc None nếu bỏ qua)
    ↓
User nhập câu hỏi
    ↓
RAG Retriever:
  ├─ Search 1: WHERE user_type = <loại đã chọn>  → top 3 chunks  (bỏ qua nếu không chọn role)
  └─ Search 2: no filter (toàn bộ DB)            → top 3 chunks (có role) / top 6 chunks (không có role)
    ↓
Deduplicate & merge (tối đa ~6 unique chunks)
    ↓
GPT-4o (tool_choice=auto) — Lượt 1:
  ├─ Nếu model gọi tool lookup_fare(city, service_type):
  │     └─ Tra Dataset/pricedata.json → trả kết quả markdown
  │         ↓
  │     GPT-4o stream — Lượt 2 (có tool result)
  └─ Nếu không gọi tool:
        GPT-4o stream trực tiếp
          - [Chính thức]: ưu tiên trả lời
          - [Cộng đồng]: chỉ dùng làm ngữ cảnh
```

## Tools và API đã dùng

| Hạng mục | Chi tiết |
|---|---|
| **UI** | Chainlit (chat interface, action buttons, streaming) |
| **AI** | OpenAI GPT-4o (`gpt-4o`) |
| **Embedding** | `keepitreal/vietnamese-sbert` — SentenceTransformer cho tiếng Việt |
| **Vector DB** | ChromaDB (persistent, local) |
| **RAG** | Custom retriever: dual-search (user_type filter optional + no filter) + dedup, TOP_K=3 |
| **Tool calling** | OpenAI function calling — `lookup_fare(city, service_type)` tra giá cước thực tế |
| **Knowledge base** | FAQ chính thức (`data/qa.json`) + Facebook community posts (`Dataset/`) |
| **Price data** | `Dataset/pricedata.json` — giá cước 45 thành phố × 4 loại (taxi, luxury, premium, two_ways) |
| **Social crawler** | Apify Facebook Groups Scraper → `dataset_facebook-groups-scraper_*.json` |

## Cấu trúc project

```
Team_29_project/
├── app.py                    # Chainlit entry point
├── config.py                 # API keys, model, constants
├── bot/
│   ├── router.py             # Route theo session state
│   ├── handlers/
│   │   ├── onboarding.py     # 4 nút chọn loại tài khoản
│   │   └── chat.py           # RAG + GPT-4o streaming + tool calling
│   └── tools/
│       └── fare_data.py      # Tool lookup_fare: đọc pricedata.json, format markdown
├── rag/
│   ├── vectorstore.py        # ChromaDB singleton client
│   ├── retriever.py          # Dual-search + dedup
│   ├── ingest.py             # Ingest qa.json → ChromaDB
│   └── ingest_facebook.py    # Ingest Facebook posts → ChromaDB
├── data/
│   └── qa.json               # FAQ chính thức (4 user_type)
└── Dataset/
    ├── pricedata.json                            # Giá cước 45 thành phố × 4 loại dịch vụ
    ├── cities_type.json                          # Danh sách thành phố hỗ trợ theo loại xe
    └── dataset_facebook-groups-scraper_*.json
```

## Dữ liệu

| Nguồn | user_type | Ghi chú |
|---|---|---|
| FAQ chính thức | `nguoi_dung`, `tai_xe_taxi`, `tai_xe_bike`, `nha_hang` | ~110 Q&A |
| Facebook community | `tai_xe_taxi`, `tai_xe_bike` | Posts có topComments |
| Giá cước (`pricedata.json`) | tất cả | 45 thành phố × 4 loại: `taxi`, `luxury`, `premium`, `two_ways` |

## Setup

```bash
pip install -r requirements.txt
# Thêm OPENAI_API_KEY vào .env
python rag/ingest.py            # Ingest FAQ chính thức
python rag/ingest_facebook.py   # Ingest Facebook community data
chainlit run app.py -w
```

## Phân công

| Thành viên | Phần phụ trách | Output cụ thể |
|---|---|---|
| Nguyễn Bình Thành | Full-stack prototype: RAG pipeline, ChromaDB, Chainlit UI, dual-search retriever, Facebook data ingestion | `app.py`, `bot/`, `rag/`, `config.py` |
| Hàn Quang Hiếu | Lên ý tưởng và viết hoàn chỉnh các phần spec (AI Product Canvas, User Stories 4 paths, Eval metrics, Failure modes, ROI, Mini AI spec); đề xuất insight foreigners là nhóm user chính bị underserved; xây dựng tool crawl website FAQ chính thức Xanh SM; xây dựng tool thu thập dữ liệu từ Facebook Group để bổ sung câu hỏi thường gặp từ cộng đồng; xây dựng khung prototype | `spec-final.md` (toàn bộ phần 1–6); `crawlFAQ.py`; `xanhsm_faqs.json`; `prototype-readme.md` |
| Phan Anh Khôi | Làm UI, thiết kế architecture và UX, tìm nguồn data, viết system prompt, làm prototype demo; đề xuất bổ sung tool viết lại query dựa trên memory; quản lý UX và thiết kế test case cho sản phẩm | `bot/handlers/`, `app.py`, `.chainlit/config.toml`, `public/theme.json` |
|Bùi Đức Thắng | sửa lỗi và hoàn thiện canvas,hoàn chỉnh bản SPEC cho Xanh SM AI Support Chatbot, bao gồm đầy đủ các phần: AI Product Canvas, User Stories theo 4 paths (Happy / Low‑confidence / Failure / Correction), Eval metrics & threshold, Top failure modes, ROI 3 kịch bản, và Mini AI spec. Spec được thiết kế theo hướng precision‑first, tập trung vào việc thay thế hotline ở các câu hỏi thông thường nhưng vẫn đảm bảo khả năng escalate khi cần. | `spec-final.md` phần 2, `canvas-final.md` |


## Notes
- Nếu level = Mock: phải có ít nhất 1 prompt/AI call chạy thật kèm theo (chạy riêng, show bên cạnh)
- Nếu level = Working: mỗi người giải thích được phần mình làm trong code/prompt
- Mỗi thành viên phải có ít nhất 1 commit trên repo nhóm

---

*Prototype README — Nhóm 29 — Track XanhSM — Day 6 Hackathon*
