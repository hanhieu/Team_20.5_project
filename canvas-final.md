# AI Product Canvas — Xanh SM AI Support Chatbot

**Nhóm:** 29 · **Track:** XanhSM

Điền Canvas cho product AI của nhóm. Mỗi ô có câu hỏi guide — trả lời trực tiếp, xóa phần in nghiêng khi điền.

---

## Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi guide** | User nào? Pain gì? AI giải quyết gì mà cách hiện tại không giải được? | Khi AI sai thì user bị ảnh hưởng thế nào? User biết AI sai bằng cách nào? User sửa bằng cách nào? | Cost bao nhiêu/request? Latency bao lâu? Risk chính là gì? |
| **Trả lời** | **User:** 4 nhóm khách hàng Xanh SM — Hành khách, Tài xế Taxi, Tài xế Bike, Nhà hàng đối tác. Mỗi nhóm có câu hỏi và nhu cầu hỗ trợ khác nhau. **Pain:** Mất thời gian tìm thông tin giá cước, khu vực phục vụ, chính sách qua nhiều kênh rời rạc (website, hotline 1900 2088, mạng xã hội) — thông tin không được phân loại theo từng nhóm user. **AI giải:** User có thể chọn loại tài khoản (4 nút tùy chọn: Hành khách / Tài xế Taxi / Tài xế Bike / Nhà hàng) để lọc kết quả chính xác hơn, hoặc hỏi thẳng không cần chọn — chatbot trả lời tức thì (<3s) kết hợp FAQ chính thức (ưu tiên) và kinh nghiệm cộng đồng (ngữ cảnh) — thay thế hoàn toàn việc gọi hotline cho câu hỏi thông thường. | **Khi AI sai:** AI báo sai giá hoặc khu vực phục vụ → user đặt xe nhầm dịch vụ, bị tính phí sai. **User biết sai:** Disclaimer *"Thông tin có thể thay đổi, xác nhận qua app khi đặt xe"* hiển thị mỗi câu trả lời. Nguồn được ghi rõ: [Chính thức] hoặc [Cộng đồng] — user tự đánh giá độ tin cậy. Nút **"Báo sai"** 1 click luôn hiển thị. **User sửa:** Nhấn "Báo sai" + nhập thông tin đúng (tùy chọn) → correction log → content team review → cập nhật knowledge base. Nút **"Gọi hotline 1900 2088"** và **"Chat với nhân viên"** luôn hiển thị ở góc dưới — user không bị lock-in. | **Cost:** ~$0.002–0.005/query (GPT-4o). **Latency:** <3s (streaming response via Chainlit). **Stack:** ChromaDB (vector DB local), `keepitreal/vietnamese-sbert` (embedding), RAG dual-search + dedup. **Risk chính:** Thông tin giá/khuyến mãi thay đổi thường xuyên mà knowledge base (~110 Q&A) chưa cập nhật kịp — user không biết bị sai vì AI trả lời tự tin. **Mitigation:** Timestamp mỗi FAQ entry, auto-disclaimer nếu entry >7 ngày chưa verify, pipeline crawl website Xanh SM hàng ngày. |

---

## Automation hay augmentation?

☐ Automation — AI làm thay, user không can thiệp
☑ Augmentation — AI gợi ý, user quyết định cuối cùng

**Justify:** AI trả lời câu hỏi + gợi ý dịch vụ, nhưng user tự quyết định có đặt xe không — cost of reject = 0. Thông tin giá/chính sách sai có hậu quả trực tiếp (user bị tính phí sai) nên không thể để AI tự động hóa hoàn toàn. Với câu hỏi phức tạp (khiếu nại, tai nạn), AI hard-route sang agent người thật — không tự xử lý.

---

## Learning signal

| # | Câu hỏi | Trả lời |
|---|---------|---------|
| 1 | User correction đi vào đâu? | Nút "Báo sai" + nội dung câu hỏi/câu trả lời → correction log → content team review hàng tuần → cập nhật `data/qa.json` → re-ingest ChromaDB → model fine-tune theo chu kỳ 2 tuần |
| 2 | Product thu signal gì để biết tốt lên hay tệ đi? | **Implicit:** tỷ lệ user click nút dịch vụ sau chatbot (conversion rate). **Explicit:** thumbs up/down sau mỗi câu trả lời. **Correction:** user nhấn "Báo sai". **Alert tự động** khi acceptance rate giảm >10% trong 1 tuần hoặc escalation rate tăng >5% so với baseline. |
| 3 | Data thuộc loại nào? ☐ User-specific · ☑ Domain-specific · ☑ Real-time · ☑ Human-judgment · ☐ Khác: ___ | FAQ Xanh SM + phản hồi cộng đồng Facebook (tài xế taxi, bike) là domain cực kỳ đặc thù — model chung không có. Giá/khuyến mãi thay đổi real-time. Phân loại chất lượng posts Facebook cần human judgment. |

**Có marginal value không?** Có — không đối thủ nào (Grab, Be, Gojek) thu được data này. FAQ Xanh SM + phản hồi cộng đồng về xe điện VN là competitive moat từ data, không phải từ model. Mỗi interaction thêm → data flywheel → model tốt hơn → escalation rate giảm → tiết kiệm chi phí hotline.