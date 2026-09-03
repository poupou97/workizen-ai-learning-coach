# Dấu ấn hình ảnh theo môn (WAL-133)

Viết SAU khi cắt thật 3 môn, không viết trước. Mọi câu dưới đây đối chiếu được
với `poc-out/ui-assets/source-assets.json` và frame `~/Desktop/wal-evidence/`.

## Nguyên tắc gốc

Mỗi môn có **loại hình riêng vì sách vốn đã khác nhau**, không phải vì ta muốn
trang trí cho khác. Nếu sách của một môn không có hình dùng được, môn đó
**không có tile hình** — im lặng đúng hơn là lấp đầy.

## Ba loại tài sản (mô hình ở `lib/core/assets/learning_asset.dart`)

| Loại | Được nói gì | Nhãn bắt buộc |
|---|---|---|
| `SourceAsset` | ảnh chụp/cắt từ SGK, có nguồn + trang + khung cắt + phiên bản trích | không (dòng nguồn nói thay) |
| `SamGeneratedAsset` | hình SAM dựng | **«Minh hoạ của SAM»**, không tắt được |
| `UiDecorativeAsset` | trang trí, không mang tuyên bố nội dung | không — và **không được dùng để minh hoạ tri thức** |

## Đã cắt thật (3 môn, `source-crop-v1`)

| Môn | Loại | Nguồn | Caption sách | Lời SAM |
|---|---|---|---|---|
| LS&ĐL | `MAP` | LS&ĐL 5, tr. in 10 | «Hình 1. Bản đồ tự nhiên Việt Nam» | — |
| Toán | `FIGURE` | Toán 5 tập một, tr. in 22 | **KHÔNG có** | có, dán nhãn riêng |
| Khoa học | `EXPERIMENT` | Khoa học 5, tr. in 16 | «Hình 5» | — |

### Bài học rút ra từ chính việc cắt

**Không phải hình nào trong sách cũng có caption.** Hình phân số Toán 5 tr.22
không in caption nào. Mô hình bản đầu bắt buộc trường `caption`, nên muốn dùng
hình đó thì phải tự viết một câu rồi đặt vào ô «nguyên văn sách» — đúng kiểu
nói dối mà cả mô hình sinh ra để chặn. Đã sửa: `printedCaption` **nullable**,
và lời của SAM đi vào `samGloss` với nhãn «SAM NÓI THÊM» hiển thị riêng.

Đây là lý do slice 2 phải cắt ĐỦ 3 môn chứ không phải 1: lỗ hổng của mô hình
chỉ lộ ra khi gặp môn thứ hai.

## Hướng cho các môn còn lại (giả thuyết, CHƯA cắt)

Sử → chân dung / tư liệu / lược đồ · Địa → bản đồ / biểu đồ · Toán → hình học,
mô hình phân số, đồ thị · KHTN → sơ đồ thí nghiệm, vòng đời · TV/Văn → tranh
minh hoạ bài đọc, chân dung tác giả · Ngoại ngữ → tranh tình huống.

Ghi là **giả thuyết** vì chưa mở sách kiểm. Khi cắt tới đâu, sửa bảng tới đó.

## Quy trình cắt (người làm, máy đỡ)

```
python3 tool/ui/preview_page_grid.py <pdf> <trang> /tmp/xem.png   # lưới 0.1
# nhìn, chấm bbox, điền vào CURATED trong tool/ui/crop_source_assets.py
python3 tool/ui/crop_source_assets.py
python3 tool/ui/build_lesson_index.py 5
```

Máy **không** tự đoán đâu là «hình của bài» — đó là việc của mắt người. Công
cụ chỉ làm cho việc chấm chính xác và lặp lại được.

## Luật phân phối (WAL-43)

PNG cắt ra nằm trong `assets/pack/` — **gitignored, không commit, không phân
phối**. Ràng buộc này được assert ngay trong constructor `SourceAsset`, và có
test chạy `git ls-files assets/pack/` trong CI mỗi lần push. Phát hành ra ngoài
= Founder/Legal Gate.
