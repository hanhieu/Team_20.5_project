# SPEC — AI Product Hackathon

**Nhóm:** 29  
**Track:** ☑ XanhSM  
**Problem statement (1 câu):**  
*Người dùng trong hệ sinh thái Xanh SM (Hành khách, Tài xế Taxi, Tài xế Bike, Nhà hàng đối tác) mất nhiều thời gian tìm thông tin giá cước, khu vực phục vụ và chính sách qua website, hotline và mạng xã hội rời rạc; AI chatbot phân loại theo từng nhóm user để trả lời FAQ tức thì và thay thế hotline cho các câu hỏi thông thường.*

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | **User:** 4 nhóm trong hệ sinh thái Xanh SM — Hành khách, Tài xế Taxi, Tài xế Bike, Nhà hàng đối tác. **Pain:** Mất thời gian tìm thông tin giá cước, khu vực hoạt động, chính sách vận hành qua nhiều kênh không phân loại theo vai trò (website, hotline 1900 2088, mạng xã hội). **AI giải:** User chọn loại tài khoản (4 nút) hoặc hỏi trực tiếp — chatbot trả lời tức thì (&lt;3s) dựa trên FAQ chính thức (ưu tiên) kết hợp kinh nghiệm cộng đồng (bổ trợ), thay thế việc gọi hotline cho câu hỏi thông thường. | **Khi AI sai:** AI báo sai giá, khu vực hoặc chính sách → user đặt xe/hoạt động sai → bị tính phí sai hoặc vi phạm chính sách. **User biết sai:** Disclaimer *“Thông tin có thể thay đổi, xác nhận trong app”* hiển thị mỗi câu trả lời; nguồn được gắn nhãn [Chính thức] / [Cộng đồng]. **User sửa:** Nút **“Báo sai”** 1 click → correction log → content team review → cập nhật knowledge base. Nút **“Gọi hotline 1900 2088”** và **“Chat nhân viên”** luôn hiển thị — user không bị lock‑in. | **Cost:** ~$0.002–0.005/query (GPT‑4o). **Latency:** &lt;3s (streaming). **Stack:** ChromaDB (local), `keepitreal/vietnamese-sbert`, RAG dual-search + dedup. **Risk chính:** Thông tin giá/khuyến mãi và chính sách thay đổi nhanh làm knowledge base bị stale trong khi AI trả lời tự tin. **Mitigation:** Timestamp mỗi FAQ, auto‑disclaimer nếu &gt;7 ngày chưa verify, pipeline crawl website Xanh SM hằng ngày. |

**Automation hay augmentation?** ☐ Automation · ☑ Augmentation  
Justify: *AI gợi ý và trả lời, user quyết định cuối cùng. Với câu hỏi phức tạp (khiếu nại nghiêm trọng, tai nạn), AI hard‑route sang agent người thật — không tự xử lý.*

**Learning signal:**

1. **User correction đi vào đâu?** Nút “Báo sai” → correction log → content team review hàng tuần → cập nhật `data/qa.json` → re‑ingest ChromaDB → fine‑tune định kỳ 2 tuần  
2. **Product thu signal gì?** Implicit: conversion sau chatbot. Explicit: thumbs up/down. Correction: “Báo sai”. Alert khi acceptance rate giảm &gt;10%/tuần hoặc escalation rate tăng &gt;5%.  
3. **Data thuộc loại nào?** ☐ User‑specific · ☑ Domain‑specific · ☑ Real‑time · ☑ Human‑judgment · ☐ Khác  
   **Có marginal value không?** Có — FAQ + phản hồi cộng đồng tài xế/đối tác Xanh SM là data đặc thù, tạo competitive moat từ data.

---

## 2. User Stories — 4 paths

### Feature: Trả lời FAQ theo từng nhóm user

**Trigger:** User mở chatbot → chọn loại tài khoản (hoặc hỏi trực tiếp)

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | AI trả lời đúng theo vai trò (VD: tài xế hỏi chính sách thưởng) → user áp dụng ngay |
| Low-confidence — AI không chắc | System báo thế nào? User quyết thế nào? | AI hiển thị mức độ không chắc + gợi ý xác nhận qua app hoặc hotline |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | User phát hiện sai khi thao tác → nhấn “Báo sai” |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | “Báo sai” → correction log → content team update KB |

---

### Feature: Gợi ý hành động phù hợp (đặt xe / kiểm tra chính sách)

**Trigger:** User mô tả nhu cầu (VD: hành khách cần đi sân bay, tài xế hỏi chính sách peak hour)

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? | AI gợi ý đúng hành động + CTA |
| Low-confidence — AI không chắc | System báo thế nào? | AI đưa 2 lựa chọn + hỏi user xác nhận |
| Failure — AI sai | Recover ra sao? | User phản hồi → AI hỏi lại thông tin |
| Correction — user sửa | Data đi vào đâu? | Implicit signal → cải thiện recommendation |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision · ☐ Recall  
**Tại sao?** Trả lời sai giá/chính sách gây hại trực tiếp về tiền và vận hành.  
**Nếu ưu tiên recall:** AI escalate nhiều hơn nhưng không gây thiệt hại.

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Precision theo FAQ chính thức | ≥90% | &lt;80% trong 3 ngày |
| Escalation rate | ≤20% | &gt;40% liên tục |
| Thumbs up rate | ≥75% | &lt;60% trong 1 tuần |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | FAQ giá/chính sách stale | User tin AI và làm sai | Timestamp + auto‑disclaimer + crawl |
| 2 | Nhận nhầm intent khẩn cấp | User không được hỗ trợ kịp thời | Intent classifier → hard‑route hotline |
| 3 | Data cộng đồng nhiễu | AI trả lời lệch | Ưu tiên nguồn chính thức |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 500 query/ngày | 3.000 query/ngày | 10.000 query/ngày |
| **Cost** | ~$5/ngày | ~$25/ngày | ~$80/ngày |
| **Benefit** | Giảm hàng trăm cuộc hotline/tháng | Giảm hàng nghìn cuộc | Thay thế phần lớn hotline |
| **Net** | + | ++ | +++ |

**Kill criteria:** Precision &lt;80% sau 2 tuần **hoặc** escalation rate &gt;40% trong 1 tháng → dừng để audit lại KB.

---

## 6. Mini AI spec (1 trang)

Xanh SM AI Support Chatbot là chatbot hỗ trợ đa vai trò trong hệ sinh thái Xanh SM, phục vụ đồng thời hành khách, tài xế taxi, tài xế bike và nhà hàng đối tác. Sản phẩm tập trung giải quyết bài toán thông tin rời rạc và không phân loại theo user role — nguyên nhân chính khiến hotline quá tải.

AI hoạt động theo hướng augmentation: trả lời FAQ và gợi ý hành động, user quyết định cuối cùng. Chất lượng tối ưu theo hướng precision‑first, chấp nhận escalate thay vì trả lời sai. Data flywheel đến từ correction, feedback và hành vi click giúp model cải thiện dần, tạo moat từ data đặc thù Xanh SM.
``