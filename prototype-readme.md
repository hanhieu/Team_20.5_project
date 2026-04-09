# Prototype — Xanh SM AI Support Chatbot

## Mô tả
Chatbot AI hỗ trợ khách hàng Xanh SM trả lời câu hỏi theo từng nhóm người dùng (Hành khách, Tài xế Taxi, Tài xế Bike, Nhà hàng đối tác). Hệ thống dùng RAG (Retrieval-Augmented Generation) để tìm kiếm câu trả lời từ knowledge base chính thức và dữ liệu cộng đồng Facebook, sau đó sinh câu trả lời bằng GPT-4o theo luồng streaming.

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
User chọn loại tài khoản (4 nút)
    ↓
Session lưu user_type
    ↓
User nhập câu hỏi
    ↓
RAG Retriever:
  ├─ Search 1: WHERE user_type = <loại đã chọn>  → top 2 chunks [Chính thức]
  └─ Search 2: no filter (toàn bộ DB)            → top 2 chunks [Cộng đồng + all]
    ↓
Deduplicate & merge (tối đa ~4 chunks)
    ↓
GPT-4o stream response (có ghi rõ nguồn [Chính thức] / [Cộng đồng])
```

## Tools và API đã dùng

| Hạng mục | Chi tiết |
|---|---|
| **UI** | Chainlit (chat interface, action buttons, streaming) |
| **AI** | OpenAI GPT-4o (`gpt-4o`) |
| **Embedding** | `keepitreal/vietnamese-sbert` — SentenceTransformer cho tiếng Việt |
| **Vector DB** | ChromaDB (persistent, local) |
| **RAG** | Custom retriever: dual-search (user_type filter + no filter) + dedup |
| **Knowledge base** | FAQ chính thức (`data/qa.json`) + Facebook community posts (`Dataset/`) |
| **Social crawler** | Apify Facebook Groups Scraper → `dataset_facebook-groups-scraper_*.json` |

## Cấu trúc project

```
Team_29_project/
├── app.py                    # Chainlit entry point
├── config.py                 # API keys, model, constants
├── bot/
│   ├── router.py             # Route theo session state
│   └── handlers/
│       ├── onboarding.py     # 4 nút chọn loại tài khoản
│       └── chat.py           # RAG + GPT-4o streaming
├── rag/
│   ├── vectorstore.py        # ChromaDB singleton client
│   ├── retriever.py          # Dual-search + dedup
│   ├── ingest.py             # Ingest qa.json → ChromaDB
│   └── ingest_facebook.py    # Ingest Facebook posts → ChromaDB
├── data/
│   └── qa.json               # FAQ chính thức (4 user_type)
└── Dataset/
    └── dataset_facebook-groups-scraper_*.json
```

## Dữ liệu

| Nguồn | user_type | Ghi chú |
|---|---|---|
| FAQ chính thức | `nguoi_dung`, `tai_xe_taxi`, `tai_xe_bike`, `nha_hang` | ~110 Q&A |
| Facebook community | `tai_xe_taxi`, `tai_xe_bike` | Posts có topComments |

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
| Phan Anh Khôi | Thiết kế architecture và UX, tìm nguồn data, viết prompt, làm prototype demo | `bot/handlers/`, `app.py` |
| ___ | User stories 4 paths + Prompt engineering | spec-final.md phần 2, prototype/prompt-tests.md |
| ___ | Eval metrics + ROI + Demo slides | spec-final.md phần 3, 5, demo-slides.pdf |

## Notes
- Nếu level = Mock: phải có ít nhất 1 prompt/AI call chạy thật kèm theo (chạy riêng, show bên cạnh)
- Nếu level = Working: mỗi người giải thích được phần mình làm trong code/prompt
- Mỗi thành viên phải có ít nhất 1 commit trên repo nhóm

---

*Prototype README — Nhóm 29 — Track XanhSM — Day 6 Hackathon*
