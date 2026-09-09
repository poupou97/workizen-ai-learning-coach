# Biên bản đính chính số đo — 2026-09-09

Founder: «Do not erase today's falsified measurements. Keep: reported value →
corrected value → root cause. The purpose is reproducibility, not blame.»

Trong một ngày có **năm** con số tôi báo sai rồi tự tìm ra. Cả năm đều bị bắt
bởi **một lượt chạy thật hoặc một phép đo đối chứng**, không cái nào bị test
bắt. Ghi lại để tái hiện được, và để bốn cái bẫy dưới đây có tên.

| # | đã báo | đúng | nguyên nhân gốc |
|---|---|---|---|
| 1 | `IDENTITY_LINKED` **49,1%** | **52,0%** | đếm theo LƯỢT XUẤT HIỆN (17.301) thay vì HÌNH DUY NHẤT (15.344) — attach làm một trang đi qua nhiều bài |
| 2 | `SUBFIGURE_NAME_CLASH` **450** | **0** | nhật ký ghi một dòng mỗi LƯỢT XỬ LÝ; trang 97 GDTC 6 đi qua 6 bài nên MỘT vùng hiện thành sáu dòng |
| 3 | `CONTAINS_OTHER_NAMED_VISUAL` **6** | **822** (lỗi mã, đã sửa còn 6) | chốt so khung với hình D của MỌI TRANG trong bài, mà hộp là toạ độ chuẩn hoá THEO TRANG |
| 4 | vùng `formula` **trung vị 29,9% trang** | **0,91%** | đọc GÓC `[x0,y0,x1,y1]` thành `[x,y,w,h]`; hai quy ước cùng tồn tại trong kho |
| 5 | tín hiệu STEM theo hình dạng ký tự | **bác bỏ toàn bộ** | nhóm đối chứng (môn khác 32,9%) CAO HƠN nhóm cần bắt (STEM 27,9%) |

## Bốn cái bẫy, đặt tên để nhận ra lần sau

1. **LƯỢT XỬ LÝ ≠ VẬT THỂ DUY NHẤT.** Nhật ký, `content`, vòng lặp theo bài —
   tất cả đếm theo lượt. Muốn đếm vật thể thì phải khử trùng lặp theo khoá
   nhận dạng trước. Dính hai lần trong một ngày (#1, #2).
2. **HỘP CHUẨN HOÁ ≠ HỘP TUYỆT ĐỐI, VÀ GÓC ≠ x,y,w,h.** Cùng một mảng bốn số
   mang hai nghĩa khác nhau ở hai tệp khác nhau. Cùng họ với bẫy `aspect()`
   (pixel vs chuẩn hoá) đã dính trước đây (#3, #4).
3. **CHỒNG HÌNH HỌC ≠ CÙNG MỘT VẬT.** Đã ghi thành luật trong bộ chọn hình.
4. **TÍN HIỆU THAY THẾ ≠ TÍNH ĐÚNG.** Hình dạng ký tự không đo được nghĩa (#5).

## Phép thử rẻ nhất, và nó đã hiệu quả

- **Chạy tín hiệu trên NHÓM ĐỐI CHỨNG.** «Môn khác cao hơn STEM» tự tố cáo
  ngay, trước khi tôi kịp tin vào nó.
- **Tỉ lệ vô lý là dữ liệu đang nói PHÉP ĐỌC của mình sai.** «69,5% hộp tràn
  ra ngoài trang» và «vùng công thức chiếm 30% trang» đều vô lý ngay từ đầu.
- **Đối chiếu đo-ngoài-luồng với LƯỢT DỰNG THẬT.** Chính chỗ lệch giữa hai
  đường đã lộ ra cả #2 lẫn #3.

## Bất biến kỹ thuật (Founder chốt, KHÔNG phải quy trình duyệt)

Trước khi báo bất kỳ số đo cấp Founder nào:

**A** nói rõ ĐƠN VỊ và MẪU SỐ · **B** tái dẫn lại từ bản ghi gốc nếu làm được ·
**C** soi một mẫu dương nhỏ · **D** soi một mẫu ĐỐI CHỨNG · **E** gặp tỉ lệ vô
lý thì điều tra, đừng mừng · **F** phân biệt SỐ LƯỢT với SỐ VẬT THỂ DUY NHẤT.

Đây là bất biến của phép đo, không phải giấy tờ. Không được dùng nó để chặn
việc phát triển thường ngày.
