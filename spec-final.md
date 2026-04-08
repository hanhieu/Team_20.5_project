# SPEC — AI Product Hackathon

**Nhóm:** 20.5
**Track:** ☑ XanhSM
**Problem statement:** Khách hàng Xanh SM — đặc biệt khách nước ngoài tại Việt Nam, nhóm dùng dịch vụ di chuyển nhiều hơn người địa phương nhưng lại gặp rào cản ngôn ngữ và thiếu thông tin — mất thời gian tìm kiếm thông tin dịch vụ, giá cước, chính sách qua nhiều kênh rời rạc — AI chatbot đa ngôn ngữ tổng hợp FAQ chính thức + phản hồi cộng đồng để trả lời tức thì và gợi ý dịch vụ phù hợp ngay trong app.

---

## 1. AI Product Canvas

|   | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Câu hỏi** | User nào? Pain gì? AI giải gì? | Khi AI sai thì sao? User sửa bằng cách nào? | Cost/latency bao nhiêu? Risk chính? |
| **Trả lời** | Hành khách Xanh SM — đặc biệt khách nước ngoài tại Việt Nam (du lịch, expat, công tác) và người dùng mới — mất 5–10 phút tìm thông tin giá cước, khu vực phục vụ, chính sách hoàn tiền qua hotline hoặc website. Khách nước ngoài còn gặp thêm rào cản ngôn ngữ (website/hotline chủ yếu tiếng Việt) và không quen hệ thống đặt xe VN. AI trả lời tức thì (<3s) bằng tiếng Anh/tiếng Việt, gợi ý đúng dịch vụ (Car / Premium / Bike / Express) và cung cấp nút đặt xe ngay | AI trả lời sai giá hoặc khu vực phục vụ → user đặt xe nhầm dịch vụ, bị tính phí sai → user thấy disclaimer "Thông tin có thể thay đổi, xác nhận qua app khi đặt xe", có nút "Báo sai" 1 click, agent human escalation qua hotline 1900 2088 | ~$0.002–0.005/query (Gemini Flash), latency <3s, risk chính: thông tin giá/khu vực thay đổi thường xuyên mà knowledge base chưa cập nhật kịp |

**Automation hay augmentation?** ☑ Augmentation
Justify: AI trả lời câu hỏi + gợi ý dịch vụ, nhưng user tự quyết định có đặt xe không. Với câu hỏi phức tạp (khiếu nại, tai nạn), AI escalate sang agent người thật — không tự xử lý.

**Learning signal:**

1. User correction đi vào đâu? → Log "Báo sai" + nội dung câu hỏi/câu trả lời → team content review → cập nhật knowledge base hàng tuần → model fine-tune theo chu kỳ 2 tuần
2. Product thu signal gì? → Implicit: tỷ lệ user click nút dịch vụ sau chatbot (conversion rate). Explicit: thumbs up/down sau mỗi câu trả lời. Correction: user nhấn "Báo sai". Alert tự động khi acceptance rate giảm >10% trong 1 tuần hoặc escalation rate tăng >5% so với baseline.
3. Data thuộc loại nào? ☑ Domain-specific · ☑ Real-time (giá, khuyến mãi thay đổi) · ☑ Human-judgment (phân loại câu hỏi mạng xã hội)
   Có marginal value không? Có — FAQ Xanh SM + phản hồi cộng đồng về taxi điện VN là domain cực kỳ đặc thù (tiếng Việt, địa phương, dịch vụ mới), model chung không có. Không đối thủ nào thu được data này ngoài Xanh SM.

---

## 2. User Stories — 4 paths

### Feature 1: Trả lời câu hỏi FAQ về dịch vụ & giá cước

**Trigger:** User mở chatbot trong app Xanh SM → gõ câu hỏi về dịch vụ (VD: "Xanh SM Bike giá bao nhiêu?", "Có phục vụ sân bay Nội Bài không?", "How do I book a ride to the airport?", "Is Xanh SM available in Da Nang?")

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? Flow kết thúc ra sao? | AI trả lời đúng giá cước Xanh SM Bike (mở cửa 10.000đ + 4.500đ/km) bằng ngôn ngữ user đang dùng (tiếng Anh nếu user hỏi tiếng Anh), kèm nút "Đặt Xanh SM Bike ngay" → user click đặt xe |
| Low-confidence — AI không chắc | System báo "không chắc" bằng cách nào? | AI hiển thị: "Tôi không chắc chắn về thông tin này. Bạn có thể xác nhận qua Hotline 1900 2088 hoặc kiểm tra trực tiếp khi đặt xe" + nút gọi hotline |
| Failure — AI sai | User biết AI sai bằng cách nào? Recover ra sao? | AI báo sai khu vực phục vụ → user đặt xe thất bại → user thấy nút "Báo thông tin sai" → ghi log → team review trong 24h |
| Correction — user sửa | User sửa bằng cách nào? Data đó đi vào đâu? | User nhấn "Báo sai" + nhập thông tin đúng (tùy chọn) → correction log → content team cập nhật FAQ → model được fine-tune theo chu kỳ |
| Mất tin — user không tin AI | Có exit không? Fallback ở đâu? Dễ tìm không? | User thấy nút "Gọi hotline 1900 2088" và "Chat với nhân viên" luôn hiển thị ở góc dưới chatbot — không bao giờ bị ẩn. User có thể thoát chatbot bất kỳ lúc nào, không bị lock-in. |

### Feature 2: Gợi ý dịch vụ phù hợp theo nhu cầu

**Trigger:** User mô tả nhu cầu di chuyển (VD: "Tôi cần đi sân bay lúc 5 giờ sáng với 2 vali lớn", "I just landed at Noi Bai, how do I get to Hoan Kiem?", "I want to explore Hoi An for a day, what service should I use?")

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? | AI gợi ý Xanh SM Car (đi sân bay sớm, hành lý nhiều) + giải thích lý do + nút "Đặt ngay" và "Xem giá chi tiết" |
| Low-confidence — AI không chắc | System báo thế nào? | AI hiển thị 2 lựa chọn (Car vs Premium) với mô tả ngắn từng loại + "Bạn muốn ưu tiên giá rẻ hay tiện nghi?" → user chọn |
| Failure — AI sai | Recover ra sao? | AI gợi ý Bike cho chuyến đi dài → user phản hồi "không phù hợp" → AI xin lỗi, hỏi lại thông tin (số người, hành lý, khoảng cách) → gợi ý lại |
| Correction — user sửa | Data đi vào đâu? | User chọn dịch vụ khác với gợi ý → implicit signal → cải thiện recommendation model |
| Mất tin — user không tin AI | Có exit không? Fallback ở đâu? | Nút "Xem tất cả dịch vụ" và "Gọi tư vấn" luôn hiển thị — user không bị ép theo gợi ý của AI |

### Feature 3: Tổng hợp câu hỏi từ mạng xã hội & so sánh với đối thủ

**Trigger:** User hỏi câu hỏi phổ biến từ cộng đồng (VD: "Xanh SM có tốt hơn Grab không?", "Tài xế Xanh SM có chuyên nghiệp không?", "Is Xanh SM safe for tourists?", "Do Xanh SM drivers speak English?")

| Path | Câu hỏi thiết kế | Mô tả |
|------|-------------------|-------|
| Happy — AI đúng, tự tin | User thấy gì? | AI tổng hợp điểm mạnh của Xanh SM (xe điện, không mùi xăng, tài xế được đào tạo 5 sao) dựa trên FAQ chính thức + phản hồi tích cực từ cộng đồng, không nói xấu đối thủ |
| Low-confidence — AI không chắc | System báo thế nào? | AI trả lời: "Đây là ý kiến cộng đồng, có thể không phản ánh đầy đủ. Bạn có thể thử dịch vụ và đánh giá trực tiếp" |
| Failure — AI sai | Recover ra sao? | AI trích dẫn thông tin lỗi thời từ social media → user báo sai → AI thêm disclaimer thời gian nguồn dữ liệu |
| Correction — user sửa | Data đi vào đâu? | User cung cấp trải nghiệm thực tế → ghi nhận làm dữ liệu training cho social crawling pipeline |
| Mất tin — user không tin AI | Có exit không? Fallback ở đâu? | Nút "Gọi hotline" và "Chat nhân viên" luôn hiển thị. AI không bao giờ so sánh trực tiếp với đối thủ để tránh mất tin tưởng. |

---

## 3. Eval metrics + threshold

**Optimize precision hay recall?** ☑ Precision
Tại sao? Chatbot hỗ trợ dịch vụ — trả lời sai thông tin giá/chính sách gây hại trực tiếp (user bị tính phí sai, mất tin tưởng). Thà không trả lời (escalate sang hotline) còn hơn trả lời sai.
Nếu sai ngược lại: Low precision → user nhận thông tin sai về giá, khu vực phục vụ → đặt xe nhầm → khiếu nại → tăng chi phí support

| Metric | Threshold | Red flag (dừng khi) |
|--------|-----------|---------------------|
| Precision câu trả lời đúng (so với FAQ chính thức) | ≥90% | <80% trong 3 ngày liên tiếp |
| Tỷ lệ user click dịch vụ sau chatbot (conversion) | ≥25% | <10% trong 1 tuần |
| Escalation rate (% câu hỏi chuyển hotline) | ≤20% | >40% (AI không đủ năng lực) |
| Thumbs up rate | ≥75% | <60% trong 1 tuần |

---

## 4. Top 3 failure modes

| # | Trigger | Hậu quả | Mitigation |
|---|---------|---------|------------|
| 1 | Giá cước / khuyến mãi thay đổi nhưng knowledge base chưa cập nhật (VD: Xanh SM tung chương trình giảm 30% nhưng chatbot vẫn báo giá cũ) | User đặt xe với kỳ vọng giá sai → thất vọng, khiếu nại, mất tin tưởng. **NGUY HIỂM NHẤT vì user KHÔNG BIẾT thông tin sai** — AI trả lời tự tin, user tin hoàn toàn, chỉ phát hiện khi thanh toán | Gắn timestamp cho mỗi FAQ entry. Nếu entry >7 ngày chưa verify → tự động thêm disclaimer "Giá có thể đã thay đổi, xác nhận khi đặt xe". Pipeline crawl website Xanh SM hàng ngày để detect thay đổi. Alert content team khi phát hiện mismatch giữa FAQ và website. |
| 2 | User hỏi câu hỏi về sự cố nghiêm trọng (tai nạn, mất đồ, tài xế có hành vi không phù hợp) nhưng AI cố gắng tự trả lời thay vì escalate | User nhận hướng dẫn không đầy đủ trong tình huống khẩn cấp → nguy hiểm tính mạng hoặc mất quyền lợi | Classifier phát hiện intent "khẩn cấp/khiếu nại nghiêm trọng" → hard-route sang hotline 1900 2088 ngay, không để AI tự xử lý |
| 3 | Social media crawling lấy phải thông tin sai lệch, review giả, hoặc thông tin về đối thủ bị nhầm sang Xanh SM | AI trả lời dựa trên thông tin sai từ mạng xã hội → ảnh hưởng uy tín, có thể vi phạm pháp lý nếu so sánh sai với đối thủ | Phân tầng nguồn dữ liệu: FAQ chính thức (tier 1, luôn ưu tiên) > social media đã verify (tier 2) > social media raw (tier 3, chỉ dùng để brainstorm, không trích dẫn trực tiếp). Không bao giờ so sánh trực tiếp với đối thủ |

---

## 5. ROI 3 kịch bản

|   | Conservative | Realistic | Optimistic |
|---|-------------|-----------|------------|
| **Assumption** | 500 query/ngày, 60% resolve không cần hotline, triển khai 5 tỉnh (chủ yếu HN, HCM) | 3.000 query/ngày, 75% resolve, triển khai 20 tỉnh — bao gồm các điểm du lịch lớn (Đà Nẵng, Hội An, Phú Quốc) nơi tỷ lệ khách nước ngoài cao | 10.000 query/ngày, 85% resolve, tích hợp toàn app 60 tỉnh + English-first UX thu hút khách quốc tế — VN đón ~18M khách nước ngoài/năm, Xanh SM có cơ hội trở thành default mobility app cho tourist |
| **Cost** | ~$5/ngày inference + $500/tháng maintenance | ~$25/ngày + $1.000/tháng | ~$80/ngày + $2.000/tháng |
| **Benefit** | Giảm 300 cuộc gọi hotline/ngày (~15 phút/cuộc × 50.000đ/phút agent) = ~225M VND/tháng tiết kiệm | Giảm 2.250 cuộc gọi/ngày = ~1,35 tỷ VND/tháng + tăng conversion đặt xe 5% | Giảm 8.500 cuộc gọi/ngày = ~5,1 tỷ VND/tháng + tăng retention 8% + data flywheel cho personalization |
| **Net** | ~225M VND/tháng benefit − ~4,5M VND/tháng cost ≈ **+220M VND/tháng** | ~1,35 tỷ/tháng − ~20M/tháng ≈ **+1,33 tỷ VND/tháng** | ~5,1 tỷ/tháng − ~60M/tháng ≈ **+5,04 tỷ VND/tháng + competitive moat** |

**Kill criteria:** Nếu precision <80% sau 2 tuần fine-tuning, HOẶC escalation rate >40% liên tục 1 tháng (AI không giải quyết được câu hỏi thực tế) → dừng, review lại knowledge base và pipeline crawling trước khi tiếp tục.

---

## 6. Mini AI spec

**Xanh SM AI Support Chatbot** giải quyết bài toán: hành khách — đặc biệt khách nước ngoài tại Việt Nam — mất thời gian tìm thông tin dịch vụ qua nhiều kênh rời rạc, gặp rào cản ngôn ngữ, và không biết bắt đầu từ đâu khi cần di chuyển tại một đất nước xa lạ. Khách nước ngoài là nhóm user có nhu cầu mobility cao hơn người địa phương (không có xe riêng, không quen đường, phụ thuộc hoàn toàn vào ride-hailing) nhưng lại được phục vụ kém nhất bởi hệ thống hỗ trợ hiện tại của Xanh SM (hotline tiếng Việt, website chủ yếu tiếng Việt).

**Cho ai:** Hai nhóm user chính:
- **Khách nước ngoài tại Việt Nam** (du lịch, expat, công tác) — nhóm dùng mobility service nhiều hơn người địa phương vì không có xe riêng, không quen đường, phụ thuộc hoàn toàn vào dịch vụ đặt xe. Rào cản lớn: website/hotline chủ yếu tiếng Việt, không biết phân biệt các gói dịch vụ, không biết khu vực nào được phục vụ.
- **Người dùng mới / người dùng không thường xuyên** — cần so sánh các gói (Car / Premium / Bike / Express), hỏi về chính sách, hoặc gặp vấn đề sau chuyến đi.

**AI làm gì (Augmentation):** Trả lời câu hỏi FAQ tức thì dựa trên knowledge base từ website chính thức Xanh SM + dữ liệu mạng xã hội đã được kiểm duyệt. Sau khi trả lời, AI gợi ý dịch vụ phù hợp với nhu cầu và cung cấp nút CTA (đặt xe, xem giá, gọi hotline). User luôn là người quyết định cuối cùng. Câu hỏi phức tạp/khẩn cấp được escalate sang agent người thật.

**Agency Progression (V1 → V2 → V3):** 
- V1 (MVP): Chatbot trả lời FAQ + gợi ý dịch vụ, escalate 30-40% câu hỏi sang hotline. Thu data correction + acceptance rate.
- V2 (6 tháng): Giảm escalation xuống 15-20%, thêm personalization dựa trên lịch sử đặt xe. Model học từ 100K+ interactions thực tế.
- V3 (12 tháng): Tự động xử lý 90% câu hỏi, proactive suggestions (gợi ý trước khi user hỏi dựa trên context: vị trí, thời gian, lịch sử). Chỉ escalate case phức tạp/khẩn cấp.

**Quality (Precision-first):** Ưu tiên precision ≥90% — thà không trả lời còn hơn trả lời sai thông tin giá/chính sách. Threshold escalation 20% là mức chấp nhận được cho V1.

**Risk chính:** Knowledge base stale (giá/khuyến mãi thay đổi nhanh) và social media noise. Mitigated bằng: timestamp + auto-disclaimer cho FAQ cũ, phân tầng nguồn dữ liệu (tier 1 FAQ chính thức luôn override), hard-route cho intent khẩn cấp.

**Data flywheel:** Mỗi lần user tương tác → thumbs up/down + correction log → cập nhật knowledge base hàng tuần → model tốt hơn → escalation rate giảm → tiết kiệm chi phí hotline → reinvest vào data quality. Dữ liệu domain-specific (FAQ taxi điện VN + phản hồi cộng đồng Xanh SM) có marginal value cao vì model chung không có. Không đối thủ nào (Grab, Be, Gojek) có data này — competitive moat từ data, không phải từ model.

**Stack đề xuất:** Gemini Flash (low latency <3s, cost-effective $0.002-0.005/query, hỗ trợ đa ngôn ngữ tốt) + RAG trên knowledge base FAQ (tiếng Việt + tiếng Anh) + social media crawler (Facebook, Google Reviews, TripAdvisor, Reddit r/VietnamTravel — nơi khách nước ngoài hay hỏi về mobility tại VN) với tier-based trust scoring + intent classifier để route câu hỏi khẩn cấp + auto language detection để trả lời đúng ngôn ngữ user + monitoring dashboard cho content team track stale entries.
