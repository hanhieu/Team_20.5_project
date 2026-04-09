# Demo Script — 2 phút

**Nhóm:** 29
**Product:** Xanh SM AI Support Chatbot

---

## Structure (tổng 2 phút)

| Phần | Thời gian | Nội dung | Ai nói |
|------|-----------|----------|--------|
| **Problem** | 20 giây | Khách hàng Xanh SM (đặc biệt người mới, khách du lịch) mất 5-10 phút tìm thông tin giá cước, khu vực phục vụ qua nhiều kênh rời rạc (website, hotline, mạng xã hội). Hiện tại: phải gọi hotline 1900 2088 hoặc lục website — chậm và không tiện. | ___ |
| **Solution** | 20 giây | AI chatbot trả lời tức thì (<3s) dựa trên FAQ chính thức + phản hồi cộng đồng. Augmentation — AI gợi ý, user quyết định. Câu hỏi khẩn cấp (tai nạn, khiếu nại) tự động chuyển hotline. Chọn augmentation vì cost of reject = 0, và thông tin giá/chính sách sai có hậu quả trực tiếp. | ___ |
| **Live demo** | 60 giây | **Show 1 flow chính:** User mở chatbot → hỏi "Xanh SM Bike giá bao nhiêu?" → AI trả lời giá cước (mở cửa 10.000đ + 4.500đ/km) + hiển thị nút "Đặt Xanh SM Bike ngay". **Chỉ ra:** (1) AI trả lời từ FAQ chính thức, (2) có disclaimer "Giá có thể thay đổi", (3) nút "Báo sai" và "Gọi hotline" luôn hiển thị. | ___ |
| **Lessons** | 20 giây | Failure mode nguy hiểm nhất: giá thay đổi mà knowledge base chưa cập nhật — user KHÔNG BIẾT bị sai. Mitigation: timestamp + auto-disclaimer cho FAQ >7 ngày. Điều học được: precision > recall cho chatbot dịch vụ — thà escalate sang hotline còn hơn trả lời sai. | ___ |

---

## Checklist trước demo

- [x] Demo script viết sẵn, mỗi người biết phần mình
- [x] Dry run ít nhất 1 lần, bấm giờ (không quá 2 phút)
- [ ] Backup plan nếu demo crash (screenshot hoặc video)
- [x] Mỗi người trả lời được 3 câu hỏi:
  - "Auto hay augmentation? Tại sao?"
  - "Failure mode chính là gì?"
  - "Phần mình làm gì trong project?"
- [ ] Laptop mở sẵn demo, không để mất thời gian load

---

## Tips

- **Show, don't tell:** demo chạy thật, không chỉ nói miệng
- **Nói chậm:** 2 phút ngắn hơn bạn nghĩ
- **Mỗi người nói:** phân công rõ, không để 1 người nói hết
- **Đừng show code:** peer cần thấy product, không cần thấy code
- **Đừng giải thích API:** "dùng Gemini Flash" là đủ

---

*Demo Script — Nhóm 29 — Track XanhSM — Day 6 Hackathon*
