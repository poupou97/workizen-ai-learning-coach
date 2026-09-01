# Audit mascot — cú tím-vàng (baseline theo lệnh Founder §19)

**Ngày:** 2026-09-01 · **Nguồn:** xem trực quan `concept/mascote.png` + `mascote-transparent.png` + `logo.png`
**Kết luận trước:** mascot hiện tại **ĐỦ làm baseline** — không generate nhân vật mới. Thiếu 2 pose, tạo Jira item thay vì vẽ lại.

| Tiêu chí (Founder §8) | Đánh giá | Bằng chứng |
|---|---|---|
| Silhouette | 🟢 mạnh | Đầu tròn + 2 túm lông tai + mũ cử nhân vuông — nhận ra ở dạng 1 màu (logo.png có bản mono tím/đen/trắng đều đọc được) |
| Nhận diện ở size nhỏ | 🟢 có bằng chứng | Size ladder 128→16px in sẵn trong sheet; 32px còn rõ mặt+mũ; 16px còn nhận silhouette |
| Hợp lứa tuổi | 🟡 lệch tiểu học | Tỷ lệ chibi, má hồng — rất hợp lớp 1–7; học sinh THPT có thể thấy trẻ con. Giảm nhẹ bằng: dùng biểu cảm điềm tĩnh (tập trung/suy nghĩ), bớt sticker hồng, chế độ "gọn" chỉ hiện đầu. KHÔNG cần nhân vật mới cho MVP (trọng tâm tiểu học) |
| Dải biểu cảm | 🟢 rộng | 10 biểu cảm mặt + 6 sticker thoại + pose buồn/tự hào — đủ cho vòng cảm xúc học tập, kể cả thất bại nhẹ ("Không sao!", "Mình thử lại nhé!") |
| Hấp dẫn học sinh | 🟢 | Màu tươi, mắt to, props học tập; cần user-test thật để xác nhận (Jira) |
| Tin cậy với phụ huynh | 🟢 hiếm có | Sheet có sẵn **chế độ App Parent riêng** (cú đeo kính + tablet) — cùng nhân vật, ngôn ngữ hình chững chạc hơn |
| Nhất quán thị giác | 🟢 trong bộ cú / 🔴 toàn kho | Bộ cú tự nhất quán (palette, mũ, chữ W). Toàn kho asset có 3 định danh (xem CONCEPT-ASSET-INVENTORY) — phải chốt cú, drop robot trắng |
| Nền sáng/tối | 🟡 | Thân tím + viền trắng nổi trên nền tối về lý thuyết; bản "transparent" thật ra nền mờ — cần cắt alpha thật rồi kiểm trên nền 2D2D3A (Jira) |
| Icon | 🟢 | App icon có sẵn 3 biến thể trong logo.png |
| Tiềm năng animation | 🟢 | Cánh/mắt/mũ là 3 điểm khớp tự nhiên; sticker sẵn keyframe cảm xúc; cần bộ rig/motion (Jira) |
| Persona giọng nói | 🟢 hợp | Cú-giáo-viên: kiên nhẫn, tò mò, không phán xét. Khớp doctrine "nói thật về bằng chứng". Tên nhân vật: **Founder-only** (§20) |

## Rủi ro ghi nhận
1. **Nhại theo archetype cú-giáo-dục (Duolingo là cú xanh).** Khác biệt đủ: species giống, thi pháp khác (chibi tím-vàng + mũ cử nhân vs cú xanh flat). Không coi là chặn, nhưng khi làm brand thật nên đo khoảng cách thị giác. Founder quyết brand cuối.
2. Asset là ảnh AI-generated độ phân giải 1536×1024 — đủ cho concept, **chưa đủ cho production** (cần vector/redraw sạch từng sprite). Jira item.
