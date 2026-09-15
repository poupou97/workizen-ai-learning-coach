# DI TRÚ MÁY — Mac → Windows

Ngày 2026-09-15.

## Vai trò hai máy

| | vai |
|---|---|
| **Windows** | **máy phát triển chính** — Flutter/client, test, build APK, device |
| **Mac** | **máy dựng kho canonical / OCR, TẠM THỜI** — chỉ còn dùng khi cần OCR sách mới |

| | nguồn chân lí của |
|---|---|
| **Git** | mã nguồn + artefact được theo dõi |
| **Kho nặng trên Mac** | **dữ liệu nặng canonical hiện tại** — 26,2 GB, **0 tệp trong Git** |

---

## ⛔ ĐỪNG BIẾN DI TRÚ MÁY THÀNH DI TRÚ OCR

Kho canonical dựng bằng **`docling-2.126 + ocrmac 1.0.1`**. `ocrmac` bọc
**Apple Vision — chỉ chạy trên macOS**.

Mọi con số của dự án đều hiệu chỉnh trên đầu ra ấy: `OPENABLE_RECORDS` 2.974 ·
danh tính hình 80,2% · 589 cặp SGK↔SGV CONFIDENT · 33 `SAM_READY` · 18
`RUNTIME_GUIDED_READY` · mọi mẫu đóng băng và mọi ngưỡng.

Chạy lại OCR bằng engine khác (RapidOCR / PaddleOCR — kho **có** adapter, nhưng
đó là ứng viên của vòng bakeoff TC-v1) cho ra **một kho khác**, không phải một
bản sao. Mọi phép đo phải nghiệm thu lại từ đầu.

**Không đổi engine. Chép kho, đừng dựng lại kho.**

---

## Phân loại từng phần

| phần | dung lượng | phân loại |
|---|---|---|
| `nguon-chi-thuc/` | 9,8 GB | **SOURCE_OF_TRUTH** — văn bản quy định + tài liệu gốc |
| `poc-out/pdf/` | 11 GB | **SOURCE_OF_TRUTH** — PDF 531 cuốn sách |
| `poc-out/graph/` | 735 MB | ⚠ **CANNOT_SAFELY_REGENERATE_ON_WINDOWS** — đầu ra OCR ocrmac |
| `poc-out/trusted-corpus/` | 315 MB | ⚠ **CANNOT_SAFELY_REGENERATE_ON_WINDOWS** — TSL + 238 tệp attach, dẫn xuất từ OCR |
| `poc-out/packs/` | 511 MB | **CAN_REGENERATE** — từ `graph` + pack builder, mọi hệ điều hành |
| `assets/pack/` | 83 MB | **CAN_REGENERATE** — `build_lesson_index` → `build_lesson_figures` |
| `assets/fixtures/real/` | 43 MB | **CAN_REGENERATE** — `build_sam_workspace.py` |
| sách MỚI thêm sau này | — | **CAN_REGENERATE_ONLY_ON_MAC** — cần OCR ocrmac |
| `build/` · `.dart_tool/` · `.venv-bakeoff/` | 5 GB | **CAN_REGENERATE** — **không chép** |

⚠ `poc-out/graph` và `poc-out/trusted-corpus` cộng lại chỉ **1,05 GB** nhưng là
phần **không thể tạo lại trên Windows**. Nếu phải cắt gọn bản sao lưu, đây là
hai thư mục cuối cùng được phép bỏ.

---

## Bản sao lưu đã tạo

```
~/Desktop/wal-migration-20260915/
  MIGRATION-MANIFEST.json     bản kê + dụng cụ verify
  repo-heavy/                 nguon-chi-thuc · poc-out · assets
  desktop-backup/             wal-pack-backup-20260911 (bản lùi pack)
```

**93.165 tệp · 26,2 GB.** Hai mức kiểm, vì băm từng byte 26 GB quá lâu để làm
thường xuyên:

- **FULL** — 76.831 tệp · 1,23 GB: **SHA-256 từng tệp**
  (`assets/pack`, `assets/fixtures`, `poc-out/trusted-corpus`, `poc-out/graph`,
  `poc-out/pedagogy`, `poc-out/units-k12`)
- **QUICK** — 16.334 tệp · 24,93 GB: kích thước + mtime, kèm **chữ ký bảng**
  `21ab810c59898db8…`. Bắt được thiếu tệp, lệch kích thước, cắt cụt; **không**
  bắt được hỏng bit trong tệp giữ nguyên kích thước.

Verify (chạy được trên cả macOS lẫn Windows, chỉ cần Python chuẩn):

```
python3 tool/ops/migration_manifest.py \
    --base <thư-mục-đã-khôi-phục> --verify MIGRATION-MANIFEST.json
# thêm --deep để băm cả nhóm QUICK (~25 GB, chậm)
```

⚠ **Tên tệp tiếng Việt.** macOS lưu NFD, Windows dùng NFC — cùng tên, khác
byte. Bản kê ghi tên đã chuẩn hoá **NFC** và giữ tên thô ở `rawName`; bộ verify
so hai phía ở NFC nên không báo động giả.

### Gói tải lên cloud (2026-09-15)

`~/Desktop/wal-migration-20260915/zips/` — **25,35 GB**, cả 5 đã kiểm
`unzip -t` toàn vẹn, có `SHA256SUMS.txt` và `README-UPLOAD.txt`.

| thứ tự tải | tệp | | |
|---|---|---|---|
| **1** | `T1-critical.zip` | 0,48 GB | ⭐ **không tạo lại được trên Windows** — OCR · TSL+attach · assets · **38 bài học bộ nhớ của Claude** · manifest |
| 2 | `T3-derived.zip` | 1,88 GB | dựng lại được, nhưng mất nhiều giờ |
| 3 | `T3b-pack-backup.zip` | 0,50 GB | bản lùi pack 11-09 |
| 4 | `T2a-nguon-chi-thuc.zip` | 10,56 GB | văn bản quy định + tài liệu gốc |
| 5 | `T2b-poc-out-pdf.zip` | 11,93 GB | PDF 531 cuốn |

Chia tầng để nếu phải dừng giữa chừng thì phần **sống còn đã lên trước**. T2
tách đôi để mỗi tệp dưới 12 GB — tải hỏng chỉ phải làm lại một nửa.

⚠ **`claude-memory/` không thuộc repo.** Nó nằm ở
`~/.claude/projects/<slug>/memory/` — 38 bài học đã trả giá. Máy mới phải
khôi phục vào đúng thư mục memory của Claude, nếu không thì mọi cái bẫy đã trả
giá sẽ bị dẫm lại.

⚠ **`zip -x` không loại được thư mục** ở lần dựng đầu — tệp tạm phình tới
23 GB vì nuốt cả 11 GB PDF. Bản hiện tại dựng bằng **danh sách tệp tường minh**
(`zip -@`), có kiểm lại bằng tổng byte trước khi nén.

---

## Checklist bootstrap Windows

**Công cụ — dùng đúng các phiên bản này**

- [ ] Git
- [ ] **Flutter 3.48.0** · **Dart 3.13.0** (`pubspec.yaml` ràng `sdk: ^3.13.0-201.0.dev`)
- [ ] Android SDK + **platform-tools (adb 1.0.41+)**
- [ ] JDK cho build Android (Mac này không có Java riêng — Android Studio cấp)
- [ ] **Python 3.11.x** (Mac đang 3.11.12)
- [ ] gói Python: `pymupdf==1.28.2` · `pillow==12.3.0` · `numpy==2.4.6`
      — **KHÔNG cài `ocrmac`**, nó không chạy trên Windows và không cần cho
      đường dựng pack/fixture
- [ ] `docling==2.126.0` chỉ cần nếu chạy lại TSL — **mà việc đó thuộc máy Mac**

**Hệ điều hành**

- [ ] Bật **long paths** (`HKLM\SYSTEM\CurrentControlSet\Control\FileSystem
      \LongPathsEnabled = 1`) — đường dài nhất hiện **169 ký tự**, cộng thư mục
      gốc là sát mốc 260
- [ ] Bật **Developer Mode** nếu cần symlink
- [ ] Chọn **PowerShell hay WSL**. Lưu ý nếu chọn WSL: Linux **phân biệt hoa
      thường**, macOS thì không — lệch hoa thường trong `import` sẽ vỡ ở WSL mà
      không vỡ ở đây

**Khôi phục**

- [ ] `git clone` repo
- [ ] Khôi phục `repo-heavy/` vào gốc repo (`nguon-chi-thuc`, `poc-out`, `assets`)
- [ ] **Verify bằng manifest** — chưa ĐẠT thì chưa được coi là khôi phục xong
- [ ] `flutter pub get`

**Nghiệm thu**

- [ ] `flutter analyze` — sạch
- [ ] `flutter test` — 1.495 test
- [ ] `cd tool && python3 -m unittest discover -s tests` — 1.505 test
- [ ] `flutter build apk --profile`
- [ ] `adb devices` → cài → **kéo APK từ máy về kiểm** (install Success không
      phải bằng chứng)
- [ ] Mở một bài trong 18 bài `RUNTIME_GUIDED_READY` — màn «Học với SAM» **không
      còn** dòng «Máy chưa ràng buộc được bài này với sách»

---

## Sau khi Windows chạy được

Máy Mac vẫn giữ vai **máy OCR** cho tới khi có quyết định khác. Thêm sách mới =
chạy OCR trên Mac → chép `poc-out/graph` phần mới sang Windows. Đừng OCR trên
Windows: kho hai engine là kho trôi phép đo.
