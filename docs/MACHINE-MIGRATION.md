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
| **0** | `WAL-ESSENTIALS.zip` | 0,08 GB | ⭐ **chặn đường lên máy thật** — chứa `KEYS.zip.gpg` (khoá SSH+Android, **đã mã hoá AES-256**), `T0-evidence.zip` (249 ảnh, không khoá), bản kê, và các khối lệnh. Nằm NGOÀI repo và ngoài `repo-heavy/` |
| **1** | `T1-critical.zip` | 0,48 GB | ⭐ **không tạo lại được trên Windows** — OCR · TSL+attach · assets · **38 tệp bộ nhớ Claude** (37 bài học + MEMORY.md) · manifest |
| 2 | `T3-derived.zip` | 1,88 GB | dựng lại được, nhưng mất nhiều giờ |
| 3 | `T3b-pack-backup.zip` | 0,50 GB | bản lùi pack 11-09 |
| 4 | `T2a-nguon-chi-thuc.zip` | 10,56 GB | văn bản quy định + tài liệu gốc |
| 5 | `T2b-poc-out-pdf.zip` | 11,93 GB | PDF 531 cuốn |

Chia tầng để nếu phải dừng giữa chừng thì phần **sống còn đã lên trước**. T2
tách đôi để mỗi tệp dưới 12 GB — tải hỏng chỉ phải làm lại một nửa.

⚠ **`claude-memory/` không thuộc repo.** Nó nằm ở
`~/.claude/projects/<slug>/memory/` — **38 tệp**: 37 bài học đã trả giá + MEMORY.md. Máy mới phải
khôi phục vào đúng thư mục memory của Claude, nếu không thì mọi cái bẫy đã trả
giá sẽ bị dẫm lại.

⚠ **`zip -x` không loại được thư mục** ở lần dựng đầu — tệp tạm phình tới
23 GB vì nuốt cả 11 GB PDF. Bản hiện tại dựng bằng **danh sách tệp tường minh**
(`zip -@`), có kiểm lại bằng tổng byte trước khi nén.

---

## Checklist bootstrap Windows

**Công cụ — dùng đúng các phiên bản này**

- [ ] Git
- [ ] **Flutter `3.48.0-0.3.pre` · kênh `main`** — KHÔNG phải stable, KHÔNG
      phải 3.48.0 chung chung. Đây là bản CI pin (`.github/workflows/ci.yml`
      `FLUTTER_VERSION`), và mốc test 1.495/11 đo trên bản này.
      `pubspec.yaml` ràng `sdk: ^3.13.0-201.0.dev` ⇒ stable mang Dart cũ hơn
      thì `flutter pub get` gãy. Cài bản khác ⇒ số test lệch vì TOOLCHAIN,
      không phải vì thiếu dữ liệu — và ta sẽ chẩn đoán sai.
      (Bản đầu tài liệu này chỉ ghi "3.48.0"; máy mới vì thế cài 3.47.0.)
- [ ] Android SDK + **platform-tools (adb 1.0.41+)**
- [ ] JDK cho build Android (Mac này không có Java riêng — Android Studio cấp)
- [ ] **Python 3.11.x** (Mac đang 3.11.12)
- [ ] gói Python: `pymupdf==1.28.2` · `pillow==12.3.0` · `numpy==2.4.6`
      — **KHÔNG cài `ocrmac`**, nó không chạy trên Windows và không cần cho
      đường dựng pack/fixture
- [ ] `docling==2.126.0` chỉ cần nếu chạy lại TSL — **mà việc đó thuộc máy Mac**

## ⛔ MẤT 2026-09-15 — đọc trước khi tin bất cứ đường dẫn nào ở đây

Cả thư mục `~/Desktop/wal-migration-20260915/` biến mất. Desktop đổi lúc
**15-09 16:22**; Thùng rác trống; không có ở iCloud; `find` khắp `~` không ra.

**Mất hẳn, không tái tạo được:**

| | |
|---|---|
| **RAW DEVICE EVIDENCE ARCHIVE** | 249 ảnh máy thật (`wal-evidence`). Chỉ OneDrive **cá nhân** đồng bộ trên Mac; tài khoản `galaxydigitalvn` thì không — nên **không chứng minh được đã upload** ⇒ fail-closed, ghi LOST. |
| **T3b-pack-backup** | nguồn `~/Desktop/wal-pack-backup-20260911`, cũng trên Desktop. Bản lùi pack trước vòng map-label. |

Không tái tạo screenshot rồi gọi là bằng chứng lịch sử. **Không rollback các
device gate đã đóng** chỉ vì mất kho ảnh thô — kết luận cũ giữ nguyên với
xuất xứ thật của chúng.

**Dựng lại được** (nguồn còn trong repo): T1 · T2a · T2b · T3.

### Bài học cấu trúc — công thức phải nằm trong git

Lần đầu tôi đóng gói **thủ công**, nên mất Desktop là mất luôn cách làm. Nay
công thức ở `tool/ops/build_migration_zips.py`:

    python3 tool/ops/build_migration_zips.py --repo . --out ~/wal-migration

Định nghĩa tầng là khai báo, dựng **danh sách tệp tường minh** rồi nạp qua
`zip -@` (không dùng `zip -x` — nó không loại được thư mục), cộng tổng byte
trước khi nén và chạy `unzip -t` sau.

Bằng chứng tái dựng trung thực: **T3-derived ra đúng 1.879.335.349 byte,
trùng từng byte bản gốc**; T2b nguồn 11.925.516.511 byte, khớp bản gốc.

### Nơi để gói

`~/wal-migration/` — **không** Desktop, **không** scratchpad. Và không bao
giờ để bản đó là bản duy nhất: phải có bản thứ hai ngoài máy, đã xác nhận tới
nơi. «Đã upload» mà không có bằng chứng thì bằng chưa upload.

---

**Gộp thì được, nhưng gói ngoài phải có băm của chính nó**

Gói nhỏ (~85 MB) gộp thành MỘT tệp `WAL-ESSENTIALS.zip` được — vì nó mang
`SHA256SUMS-BEN-TRONG.txt` cho từng tệp bên trong, VÀ băm của chính nó được
công bố khi tạo. Đó đúng là thứ lần trước thiếu: OneDrive tự bọc 5 tệp thành
một `zips.zip` **không ai lập băm**, nên cụt 85% mà không tín hiệu nào.

Bốn gói nặng (25 GB) **vẫn tải riêng từng tệp** — gộp lại là lặp đúng lỗi ấy
ở quy mô mà tải lại tốn cả ngày.

Khoá riêng đi trong `KEYS.zip.gpg` (AES-256, mật khẩu đưa qua kênh khác).
`T0-evidence.zip` cố ý **không chứa khoá nào**.

**Thứ nằm ngoài cả repo lẫn `repo-heavy/`** ⚠ bổ sung 15-09

Quét một lượt thay vì phát hiện lẻ tẻ. Cần chép sang (gói `T0-local-config.zip`):

- `~/.android/debug.keystore` → `%USERPROFILE%\.android\` — đi trong
  `KEYS.zip.gpg` **đã mã hoá**, không bao giờ để trần trên đám mây. **Khoá duy nhất**:
  `android/app/build.gradle.kts` dùng `signingConfigs.getByName("debug")` cho
  cả bản release. Ký khoá khác ⇒ cài đè trượt
  `INSTALL_FAILED_UPDATE_INCOMPATIBLE` ⇒ phải gỡ app ⇒ **mất hồ sơ con của
  Founder**, đúng thứ device-protocol cấm. SHA-256 `2da490dd…18bb`, 2.618 byte.
- `~/Desktop/wal-evidence/` — 249 ảnh máy thật, không tái tạo được.

KHÔNG chép, có chủ ý: `.claude/` (14 GB lịch sử phiên) · `research/oss`
(1,1 GB, clone lại được) · `android/local.properties` (đường dẫn riêng máy) ·
`~/.android/adbkey` (máy mới đã tự uỷ quyền).

Không có khoá phát hành nào trong dự án — đã kiểm, không `key.properties`,
không `.jks`.

**Ba repo, không phải một** ⚠ THIẾU trong bản đầu, bổ sung 15-09

`CLAUDE.md` gốc workspace và Canonical Knowledge **không nằm trong gói zip
nào** — `repo-heavy/` chỉ gói `nguon-chi-thuc` · `poc-out` · `assets`. Chúng
sống ở hai repo khác, đều có remote GitHub nên clone là đủ:

- [ ] `git clone https://github.com/poupou97/workforceos-project.git` → đặt
      làm thư mục CHA chứa các repo; `CLAUDE.md` gốc workspace nằm ở đây
- [ ] `git clone https://github.com/poupou97/workizen-knowledge-base.git` →
      `canonical/` là boot context bắt buộc theo CLAUDE.md gốc
- [ ] `git clone https://github.com/poupou97/workizen-ai-learning-coach.git`

Bỏ hai repo đầu thì Claude máy mới thiếu chính lớp doctrine mà `CLAUDE.md`
gốc bắt đọc trước mọi việc lớn.

**Tải zip: từng tệp một, KHÔNG tải cả thư mục** ⚠ bài học 15-09

Tải cả thư mục `zips/` từ OneDrive thì nó bọc 5 tệp thành **một** tệp
`zips.zip` — và bộ băm `SHA256SUMS.txt` lập cho 5 tệp bên trong trở nên vô
dụng, vì tệp bọc ngoài không có băm để đối chiếu. Lần đầu đã dính: nhận
3,96/25,35 GB, **cụt 85%**, không một tín hiệu nào cho tới khi mở ra xem.
Tải riêng từng tệp thì đứt tệp nào chỉ mất tệp đó, và băm bắt được ngay.

**Lệnh mở đầu cho Claude máy mới**

- [ ] Dán nguyên khối trong `docs/FIRST-PROMPT-WINDOWS.md` làm tin nhắn đầu
      tiên — nó chốt thứ tự đọc, cổng verify, và những việc **cấm** làm

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
- [ ] `flutter test` — **1.495 đạt + 11 bỏ qua** (bỏ qua = fixture gitignore)
- [ ] `cd tool && python -m unittest discover -s tests` — **1.516 test, 23 bỏ qua**
      (tài liệu trước ghi 1.505 — SAI, ghi mà không đo lại; đã sửa 15-09)
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
