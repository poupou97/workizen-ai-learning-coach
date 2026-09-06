/// ⭐⭐ WAL-218 — **CI GREEN ≠ GOLDEN CHAIN VERIFIED.**
///
/// Golden #1 (LS&ĐL 5 Bài 8) là chỗ duy nhất chuỗi giao hàng được ghim TRỌN
/// VẸN: nguồn → SDM → sổ sửa → `ValidatedRepair` → TSL đã chiếu →
/// `LessonDocument` → `assets/fixtures/real/` → `WorkspaceCatalog` → ba
/// Learning View. Fixture chở nó nằm trong `.gitignore` (Founder D4: chữ SGK
/// nguyên văn và ảnh cắt trang là NỘI BỘ / NGHIÊN CỨU), nên **CI không bao giờ
/// có nó** và chín khẳng định ấy biến thành `markTestSkipped` trên runner.
///
/// Đo được ngày 2026-09-06 trên `main` (6fd728d):
///
/// | cấu hình | passed | skipped |
/// |---|---|---|
/// | fixture CÓ | 1108 | 33 |
/// | fixture KHÔNG (đúng trạng thái CI) | 1099 | 42 |
///
/// Chín test rơi xuống, và `flutter test` vẫn in **«All tests passed!»**.
///
/// ⭐ **VẮNG MẶT KHÔNG THỂ THOẢ MÃN MỘT NGHĨA VỤ KHẲNG ĐỊNH.** Đây là luật của
/// tệp này, và nó cùng một hình dạng với cái cổng của vòng 7 từng in
/// `0/0 present · PASS` vì thứ nó canh không có mặt. Một lần chạy KHÔNG có
/// fixture phải để lại chín dòng `UNVERIFIED` đọc được bằng máy, và không cách
/// nào biến chín dòng ấy thành một PASS.
///
/// Sổ ghi: `build/golden-chain/<id>.json`, mỗi nghĩa vụ một tệp (các suite chạy
/// song song, mỗi tiến trình chỉ ghi tệp của mình nên không tranh nhau).
/// `tool/ci/golden_chain_verdict.py` đọc lại, đối chiếu với
/// `tool/ci/golden-chain-obligations.json`, và **thiếu một bản ghi là ĐỎ** —
/// xoá một test không làm coverage đẹp lên, nó làm CI hỏng.
///
/// Chạy một phần suite ⇒ sổ thiếu ⇒ verdict ĐỎ. Đúng như vậy: một lần chạy một
/// phần không được phép nói gì về độ phủ của cả chuỗi.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// Bản đăng ký nghĩa vụ — nguồn sự thật DUY NHẤT, dùng chung với tầng Python.
const goldenChainRegistryPath = 'tool/ci/golden-chain-obligations.json';

Map<String, Object?> _registry() =>
    (jsonDecode(File(goldenChainRegistryPath).readAsStringSync()) as Map)
        .cast<String, Object?>();

final Map<String, Object?> goldenChainRegistry = _registry();

/// Đường tới fixture THẬT của Golden #1 — do bản đăng ký nói, không hard-code
/// lần hai (hai chỗ ghi cùng một đường là hai chỗ để lệch nhau).
final String goldenChainFixturePath =
    goldenChainRegistry['fixture']! as String;

final String _ledgerDir = goldenChainRegistry['ledgerDir']! as String;

Set<String> _ids(String key) => {
  for (final o in (goldenChainRegistry[key]! as List))
    (o as Map)['id']! as String,
};

/// Chín nghĩa vụ trên fixture THẬT.
final Set<String> goldenChainIds = _ids('obligations');

/// Chín bản MÔ PHỎNG không cần corpus. `SYNTHETIC PASS ≠ GOLDEN VERIFIED` —
/// chúng chứng minh ĐƯỜNG MÃ, không chứng minh chuỗi Golden.
final Set<String> syntheticMirrorIds = _ids('syntheticMirrors');

/// Fixture thật có trên máy này không. Một lời gọi, một sự thật.
bool get goldenFixtureExists => File(goldenChainFixturePath).existsSync();

/// Ghi một dòng vào sổ. `exercised: false` ⇒ nghĩa vụ KHÔNG được kiểm ở lần
/// chạy này, và verdict sẽ nói UNVERIFIED chứ không nói PASS.
void recordGoldenChain(
  String id, {
  required bool exercised,
  String? reason,
}) {
  final known = goldenChainIds.contains(id) || syntheticMirrorIds.contains(id);
  if (!known) {
    throw StateError(
      'nghĩa vụ «$id» không có trong $goldenChainRegistryPath — '
      'thêm một khẳng định Golden chain nghĩa là thêm một dòng ở đó',
    );
  }
  final synthetic = syntheticMirrorIds.contains(id);
  final dir = Directory(_ledgerDir)..createSync(recursive: true);
  File('${dir.path}/$id.json').writeAsStringSync(
    const JsonEncoder.withIndent('  ').convert({
      'id': id,
      'kind': synthetic ? 'syntheticMirror' : 'goldenChain',
      'exercised': exercised,
      'reason': reason,
      // Chỉ nghĩa vụ THẬT mới nói về fixture; bản mô phỏng không cần corpus.
      'fixture': synthetic ? null : goldenChainFixturePath,
      'fixturePresent': synthetic ? null : goldenFixtureExists,
      'recordedAt': DateTime.now().toUtc().toIso8601String(),
    }),
  );
}

/// Cổng vào của mọi test Golden chain.
///
/// Trả `true` khi fixture có mặt (test chạy tiếp; nhớ gọi
/// [recordGoldenChain] với `exercised: true` ở CUỐI thân test — ghi ở cuối để
/// một thân test ném giữa chừng KHÔNG để lại bản ghi, và verdict đỏ).
/// Trả `false` khi vắng: đã ghi `UNVERIFIED` và đã `markTestSkipped`.
bool goldenChainGate(String id) {
  if (goldenFixtureExists) return true;
  recordGoldenChain(
    id,
    exercised: false,
    reason:
        'fixture thật chưa sinh trên máy này (poc-out) — D4: không commit, '
        'nên CI không bao giờ có. UNVERIFIED, không phải PASS.',
  );
  markTestSkipped(
    '[$id] UNVERIFIED — Golden #1 chưa sinh trên máy này (poc-out). '
    'Chạy tool/evidence/golden_delivery.py. Đây KHÔNG phải một test đạt.',
  );
  return false;
}
