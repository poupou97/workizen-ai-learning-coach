#!/bin/bash
# Tạo MỘT gói nhỏ để mang sang máy Windows: WAL-ESSENTIALS.zip
# FOUNDER TỰ CHẠY — script không chứa khoá, không chứa mật khẩu.
#   bash ~/wal-migration/dong-goi-khoa.sh
set -euo pipefail

OUT=~/wal-migration
REPO=~/projects/workizen-ai-learning-coach
S="$OUT/keys-stage"; B="$OUT/bundle-stage"
PLAIN="$OUT/KEYS.zip"; ENC="$OUT/KEYS.zip.gpg"; FINAL="$OUT/WAL-ESSENTIALS.zip"

command -v gpg >/dev/null || { echo "⛔ chưa có gpg: brew install gnupg"; exit 1; }
[ -f "$REPO/MIGRATION-MANIFEST.json" ] || { echo "⛔ thiếu MIGRATION-MANIFEST.json"; exit 1; }
rm -f "$ENC" "$PLAIN" "$FINAL"

rm -rf "$S"; mkdir -p "$S/ssh" "$S/android"
rsync -a --exclude 'agent/' --exclude 'known_hosts.old' ~/.ssh/ "$S/ssh/"
cp ~/.android/debug.keystore ~/.android/adbkey ~/.android/adbkey.pub "$S/android/"

cat > "$S/DAT-VAO-DAU.txt" <<'TXT'
ĐẶT VÀO ĐÂU TRÊN MÁY WINDOWS
  ssh\*      ->  %USERPROFILE%\.ssh\
  android\*  ->  %USERPROFILE%\.android\

BẮT BUỘC SIẾT QUYỀN, nếu không OpenSSH từ chối khoá
("UNPROTECTED PRIVATE KEY FILE"). PowerShell:

    cd $env:USERPROFILE\.ssh
    Get-ChildItem -File | Where-Object { $_.Name -notlike '*.pub' } | ForEach-Object {
        icacls $_.FullName /inheritance:r /grant:r "$($env:USERNAME):(R,W)" | Out-Null
    }

KHOÁ NÀO LÀM GÌ
  android\debug.keystore  Khoá DUY NHẤT của app — build.gradle.kts dùng
                          signingConfig debug cho CẢ bản release. Ký khoá khác
                          ⇒ cài đè lên S24 trượt INSTALL_FAILED_UPDATE_INCOMPATIBLE
                          ⇒ gỡ app để cài là MẤT HỒ SƠ CON của Founder.
                          SHA-256 phải là:
                          2da490ddd8bedba7bfd95bbc266129c5e247ab1ada0c0a26ad6f8da7b09118bb
  android\adbkey(.pub)    Uỷ quyền adb.
  ssh\*                   Toàn bộ khoá SSH + known_hosts, chép nguyên cụm.
                          Chọn lọc là rủi ro: sót một khoá là mất đường vào máy.

XONG: xoá KEYS.zip chưa mã hoá, và xoá WAL-ESSENTIALS.zip khỏi OneDrive.
TXT

(cd "$S" && zip -rq "$PLAIN" .)
echo; echo "════ Mật khẩu cho gói KHOÁ. Gõ hai lần. Đưa qua kênh KHÁC. ════"
gpg --symmetric --cipher-algo AES256 --output "$ENC" "$PLAIN"
rm -f "$PLAIN"; rm -rf "$S"

rm -rf "$B"; mkdir -p "$B/tai-lieu"
cp "$ENC" "$B/"
cp "$REPO/MIGRATION-MANIFEST.json" "$B/"
[ -f "$OUT/SHA256SUMS.txt" ] && cp "$OUT/SHA256SUMS.txt" "$B/"
for f in FIRST-PROMPT-WINDOWS.md CROSS-CHECK-WINDOWS.md MACHINE-MIGRATION.md \
         HANDOFF-TO-NEXT-CLAUDE.md MASTER-TODO.md; do
  [ -f "$REPO/docs/$f" ] && cp "$REPO/docs/$f" "$B/tai-lieu/"
done
(cd "$B" && shasum -a 256 KEYS.zip.gpg MIGRATION-MANIFEST.json > SHA256SUMS-BEN-TRONG.txt)

cat > "$B/DOC-TOI-TRUOC.txt" <<'TXT'
WAL-ESSENTIALS.zip — mọi thứ NHỎ mà máy Windows cần.

  KEYS.zip.gpg              khoá SSH + Android, AES-256.
                            gpg --output KEYS.zip --decrypt KEYS.zip.gpg
  MIGRATION-MANIFEST.json   -> đặt ở GỐC REPO, cổng verify cần nó
  SHA256SUMS.txt            băm 4 gói dữ liệu nặng (tải RIÊNG từng tệp)
  SHA256SUMS-BEN-TRONG.txt  băm của chính các tệp trong gói này
  tai-lieu/                 khối lệnh + tài liệu bàn giao

⚠ BỐN GÓI NẶNG TẢI RIÊNG TỪNG TỆP: T1 · T3 · T2a · T2b (~25 GB).
Tải cả thư mục thì OneDrive bọc thành một zip KHÔNG có băm ⇒ lần trước nhận
3,96/25,35 GB, cụt 85%, im lặng tới khi mở.

⚠ KHÔNG CÒN T0-evidence / T3b — 249 ảnh máy thật và bản lùi pack 11-09 đã MẤT
cùng thư mục Desktop ngày 15-09. Không tái tạo. Không rollback kết luận cũ.
TXT

(cd "$B" && zip -rq "$FINAL" .)
rm -rf "$B"; rm -f "$ENC"

unzip -tq "$FINAL" && echo "✓ $FINAL toàn vẹn"
echo "byte: $(wc -c < "$FINAL" | tr -d ' ')"
echo "SHA-256 CỦA CHÍNH GÓI NÀY — ghi lại:"
shasum -a 256 "$FINAL"
