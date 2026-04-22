# Prompt for AI Slide Creation Agent
## Xanh SM AI Support Chatbot — Mini Project Proposal Slides

Paste toàn bộ prompt này vào AI có khả năng tạo slides (Gamma, Beautiful.ai, Claude, GPT-4o với canvas, v.v.)

---

## MASTER PROMPT

```
Tạo cho tôi một bộ 7 slides chuyên nghiệp cho một mini project proposal về AI chatbot.
Đây là bài trình bày trong hackathon AI tại VinUni, Việt Nam.

=== THÔNG TIN CHUNG ===
Tên dự án: Xanh SM AI Support Chatbot
Nhóm: Nhóm 29 — Track XanhSM
Sự kiện: VinUni A20 AI Thực Chiến — Day 7 (Phase 1 Summary)
Ngôn ngữ: Tiếng Việt chính, có thể có subtitle tiếng Anh cho thuật ngữ kỹ thuật

=== DESIGN DIRECTION ===
- Màu chủ đạo: Xanh lá (#00A651 hoặc tương đương), trắng, xám đậm
- Font: Sans-serif hiện đại (Inter, Nunito, hoặc tương đương)
- Phong cách: Clean, professional, tech startup — không quá formal, không quá casual
- Mỗi slide: ít text, nhiều visual (diagram, icon, bảng, số liệu nổi bật)
- Icon style: Line icons hoặc filled icons — nhất quán xuyên suốt
- Tránh: bullet point dày đặc, wall of text, clipart lỗi thời

=== NỘI DUNG 7 SLIDES ===

---

SLIDE 1 — COVER
Layout: Full-bleed background + centered text
Background: Ảnh xe điện VinFast hoặc cityscape Hà Nội/HCM ban đêm, overlay gradient xanh lá semi-transparent
Nội dung:
- Headline lớn (font size 48–60pt): "Xanh SM AI Support Chatbot"
- Subtitle (font size 20pt): "Trợ lý ảo hỗ trợ đa vai trò — Trả lời tức thì, gợi ý đúng dịch vụ"
- English sub (font size 14pt, italic): "AI-powered customer support for Vietnam's first all-electric ride-hailing platform"
- Badge góc trên phải: "Working Prototype ✓" (màu xanh lá, border rounded)
- Footer: "Nhóm 29 · Track XanhSM · VinUni A20 AI Thực Chiến · 2026"
- 4 icon nhỏ hàng ngang ở giữa-dưới: 👤 Hành khách · 🚖 Tài xế Taxi · 🛵 Tài xế Bike · 🍜 Nhà hàng

---

SLIDE 2 — THE PROBLEM & SOLUTION
Layout: 2 cột (Problem | Solution) + 1 callout box ở dưới
Headline: "Bài toán & Giải pháp"

CỘT TRÁI — PROBLEM (background nhạt đỏ/cam):
Title: "❌ Hiện tại"
- Icon 🌍 + text: "Khách nước ngoài: hotline tiếng Việt, website tiếng Việt, không biết chọn dịch vụ nào"
- Icon 📱 + text: "Người dùng mới: 4 dịch vụ khác nhau, giá khác nhau theo tỉnh, thông tin phân tán"
- Icon ⏱️ + text: "5–10 phút/lần tìm thông tin"
- Icon 📞 + text: "~300 cuộc gọi hotline/ngày có thể tự động hóa"

CỘT PHẢI — SOLUTION (background nhạt xanh):
Title: "✅ AI Chatbot"
- Icon ⚡ + text: "Trả lời tức thì <3 giây"
- Icon 🌐 + text: "Tiếng Việt & tiếng Anh (auto-detect)"
- Icon 🎯 + text: "Phân loại theo 4 vai trò người dùng"
- Icon 💰 + text: "Tra cứu giá cước thực tế 50+ tỉnh thành"
- Icon 🔄 + text: "Augmentation — AI gợi ý, user quyết định"

CALLOUT BOX DƯỚI (màu xanh đậm, text trắng):
"Vietnam đón ~18M khách nước ngoài/năm — nhóm dùng mobility nhiều nhất nhưng được hỗ trợ kém nhất"

---

SLIDE 3 — ENTERPRISE CONTEXT & DEPLOYMENT
Layout: Top half = 3 constraint cards, Bottom half = architecture diagram
Headline: "Enterprise Context & Kiến trúc Hybrid"

TOP — 3 CONSTRAINT CARDS (3 cột, mỗi card có icon + title + 2 dòng mô tả):

Card 1 (icon 🔴🔒):
Title: "PII Compliance"
Text: "Thông tin tài xế (họ tên, SĐT, bằng lái) là PII — phải lưu trong hạ tầng Việt Nam. Không được gửi qua OpenAI API."

Card 2 (icon 🟡📋):
Title: "Audit Trail"
Text: "Vingroup yêu cầu log đầy đủ mọi interaction: timestamp, query, response, feedback. Retention ≥ 90 ngày."

Card 3 (icon 🟡🔗):
Title: "System Integration"
Text: "Giá cước thực tế nằm trong hệ thống core Xanh SM — cần API sync, không dùng file JSON tĩnh."

BOTTOM — ARCHITECTURE DIAGRAM (horizontal flow):
Vẽ diagram đơn giản với các box và mũi tên:

[User App] → [API Gateway + Rate Limiter] → [Chainlit App Server]
                                                      ↓
                                    [PII Interceptor] → [PostgreSQL (PII data)]
                                                      ↓
                                              [ChromaDB + SBERT]
                                              (on-prem, zero latency)
                                                      ↓
                                    [OpenAI GPT-4o] ← [Query only, no PII]
                                    (Cloud — SE Asia)

Label 2 zones rõ ràng:
- Zone xanh lá: "ON-PREM / PRIVATE CLOUD VN" (bao gồm: App Server, ChromaDB, PostgreSQL, PII data)
- Zone xanh dương: "CLOUD" (chỉ có: OpenAI API)

---

SLIDE 4 — COST ANALYSIS
Layout: Top = 3 scenario cards với số nổi bật, Bottom = cost breakdown bar chart hoặc pie chart
Headline: "Cost Analysis — 3 Kịch bản"

TOP — 3 SCENARIO CARDS (3 cột):

Card 1 — Conservative:
- Label: "Conservative"
- Sub: "500 req/ngày · 5 tỉnh"
- Số lớn nổi bật: "$281/tháng"
- (~7M VND)
- Breakdown nhỏ: LLM $66 · Infra $65 · Human $150
- ROI: "+218M VND/tháng net"

Card 2 — Realistic (highlighted, border đậm hơn):
- Label: "Realistic ⭐"
- Sub: "3.000 req/ngày · 20 tỉnh"
- Số lớn nổi bật: "$931/tháng"
- (~23M VND)
- Breakdown nhỏ: LLM $396 · Infra $135 · Human $400
- ROI: "+1.33 tỷ VND/tháng net"

Card 3 — Optimistic:
- Label: "Optimistic"
- Sub: "10.000 req/ngày · 60 tỉnh"
- Số lớn nổi bật: "$2.430/tháng"
- (~60M VND)
- Breakdown nhỏ: LLM $1.320 · Infra $410 · Human $700
- ROI: "+5.04 tỷ VND/tháng net"

BOTTOM — COST DRIVER PIE CHART (dùng cho kịch bản Realistic):
Pie chart 3 phần:
- 🔴 GPT-4o Token Cost: 43% ($396)
- 🟡 Human Review & Maintenance: 43% ($400)
- 🟢 Infra & Monitoring: 14% ($135)

Caption: "⚠️ Hidden cost: Human review (content team) chiếm ~43% — không xuất hiện trong cloud bill"

---

SLIDE 5 — COST OPTIMIZATION
Layout: 3 strategy cards (vertical timeline style) + summary box
Headline: "Optimization Plan — Giảm 50–60% Cost trong 1 Tháng"

TIMELINE (trái sang phải hoặc trên xuống dưới):

STRATEGY 1 — "Làm ngay · Tuần 1" (badge xanh lá):
Icon: ✂️
Title: "Prompt Compression"
Mô tả: "Rút ngắn system prompt từ 800 → 400 tokens"
Kết quả: "↓ 20% input token cost"
Effort: "1–2 ngày"
Risk: "Thấp — cần A/B test"

STRATEGY 2 — "Làm ngay · Tuần 2" (badge xanh lá):
Icon: 💾
Title: "Semantic Caching"
Mô tả: "Cache response theo embedding similarity (cosine > 0.92). TTL: giá cước 24h, FAQ 7 ngày"
Kết quả: "↓ 30–50% LLM calls"
Effort: "1 tuần"
Risk: "Trung bình — cần cache invalidation webhook"

STRATEGY 3 — "Phase 2 · Tháng 2" (badge xanh dương):
Icon: 🔀
Title: "Model Routing"
Mô tả: "Simple queries (giá cước, FAQ) → GPT-4o-mini (rẻ hơn 25x). Complex → GPT-4o"
Kết quả: "↓ 50–60% LLM cost tổng"
Effort: "2–4 tuần (cần eval framework trước)"
Risk: "Trung bình — cần classifier chính xác"

SUMMARY BOX (dưới cùng, màu xanh đậm):
"Sau 1 tháng optimize: $931/tháng → ~$450/tháng · Tiết kiệm ~$480/tháng (~12M VND)"

---

SLIDE 6 — RELIABILITY & SCALING
Layout: Top = fallback chain diagram, Bottom = 2 cột (failure scenarios + monitoring metrics)
Headline: "Reliability Plan — Luôn có Response trong 10 giây"

TOP — FALLBACK CHAIN DIAGRAM (horizontal flow với màu sắc):
[Request] → [Intent (2s timeout)] → [RAG (1s timeout)] → [GPT-4o (8s timeout)] → [Retry 1x] → [Rule-based FAQ] → [Hotline 1900 2088]

Mỗi bước có màu:
- Xanh lá: bước bình thường
- Vàng: timeout/error
- Đỏ: fallback cuối

BOTTOM LEFT — 3 FAILURE SCENARIOS (3 rows):
| Scenario | Trigger | Response |
|---|---|---|
| 🚀 Traffic spike | Campaign khuyến mãi | Rate limiting + async queue + horizontal scale |
| 💥 OpenAI outage | API down | Retry → Rule-based FAQ → Hotline redirect |
| 📅 Stale KB | Giá thay đổi | Auto-disclaimer + daily crawl + webhook invalidation |

BOTTOM RIGHT — KEY METRICS (2 cột icon + số):
- ⚡ p95 latency: < 3s (alert > 5s)
- ❌ Error rate: < 1% (alert > 5%)
- 📞 Escalation rate: ≤ 20% (alert > 40%)
- 👎 Thumbs-down: < 25% (alert > 40%)
- 🎯 RAG hit rate: > 80% (alert < 60%)
- 💰 Cost/ngày: < $15 (alert > $25)

---

SLIDE 7 — TRACK & NEXT STEPS
Layout: Top = track decision badge, Middle = 4 next steps timeline, Bottom = kill criteria
Headline: "Track Phase 2 & Roadmap"

TOP — TRACK DECISION (centered, large):
Big badge: "Track: AI Engineering / Application ✅"
Lý do (3 bullet ngắn):
- "Nền tảng kỹ thuật đã có (RAG + LLM + tool calling)"
- "Điểm yếu: production hardening, không phải AI capability"
- "Cần: monitoring, caching, eval framework, data flywheel"

MIDDLE — 4 NEXT STEPS (horizontal timeline, 4 boxes):

Box 1 — "Tuần 1–2" (màu xanh lá đậm):
Icon: 🔧
Title: "Production Hardening"
Items: Semantic caching · Prompt compression · Structured logging · PII interceptor

Box 2 — "Tuần 3–4" (màu xanh lá trung):
Icon: 🧪
Title: "Eval Framework"
Items: 200 test cases (50 câu × 4 roles) · CI/CD eval · Precision threshold 80%

Box 3 — "Tháng 2" (màu xanh lá nhạt):
Icon: 🔄
Title: "Data Flywheel"
Items: Daily crawl pipeline · Webhook giá cước · Correction → re-ingest KB

Box 4 — "Tháng 2–3" (màu xanh dương):
Icon: 🔀
Title: "Model Routing"
Items: Simple/complex classifier · GPT-4o-mini cho FAQ · -50% LLM cost

BOTTOM — KILL CRITERIA (red box, nhỏ):
"🛑 Dừng nếu: Precision < 80% sau 2 tuần · Escalation > 40% liên tục 1 tháng · Cost > Benefit 2 tháng"

=== YÊU CẦU KỸ THUẬT ===
- Format: 16:9 widescreen
- Mỗi slide có slide number ở góc dưới phải
- Footer nhỏ: "Nhóm 29 · Xanh SM AI Chatbot · VinUni A20 · 2026"
- Consistent color scheme xuyên suốt
- Diagram và chart phải rõ ràng, đọc được từ 2 mét
- Export: PDF + PPTX nếu có thể
```

---

## GHI CHÚ KHI DÙNG PROMPT

**Với Gamma (gamma.app):**
- Paste prompt vào "Generate with AI"
- Chọn theme "Professional" hoặc "Modern"
- Sau khi generate, chỉnh màu về xanh lá Xanh SM (#00A651)

**Với Beautiful.ai:**
- Dùng "Smart Slide" feature
- Paste từng slide một nếu cần

**Với Claude / GPT-4o (canvas mode):**
- Paste toàn bộ prompt
- Yêu cầu output dạng HTML slides hoặc Markdown với layout hints
- Sau đó copy vào Canva/Google Slides để polish

**Với Canva AI:**
- Dùng "Magic Design" với prompt ngắn hơn
- Paste từng slide description vào từng slide

**Số liệu quan trọng cần check lại trước khi present:**
- Giá GPT-4o: $2.50/1M input · $10/1M output (cập nhật tháng 4/2026)
- 18M khách nước ngoài/năm tại VN
- ~300 cuộc gọi hotline/ngày có thể tự động hóa
- ROI Conservative: +218M VND/tháng net

---

*Slide prompt — Nhóm 29 — Track XanhSM — VinUni A20 AI Thực Chiến*
