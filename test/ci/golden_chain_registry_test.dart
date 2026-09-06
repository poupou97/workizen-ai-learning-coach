/// ⭐⭐ WAL-218 — **CÁI CANH SỔ, ĐƯỢC CANH LẠI.**
///
/// `tool/ci/golden_chain_verdict.py` bắt được «một test biến mất» vì nghĩa vụ
/// ấy không để lại bản ghi. Nhưng nếu ai đó xoá LUÔN dòng nghĩa vụ, mẫu số tụt
/// xuống và `0/0` đọc như một PASS — đúng hình dạng cái cổng vòng 7 từng in
/// `0/0 present · PASS` vì thứ nó canh không có mặt.
///
/// Tệp này khoá ba chỗ lại với nhau:
///
/// 1. mỗi dòng nghĩa vụ phải có một test THẬT gọi đúng mã của nó (không có
///    nghĩa vụ nào chỉ tồn tại trên giấy);
/// 2. sàn `--min-obligations` trong `.github/workflows/ci.yml` không được tụt
///    xuống dưới CHÍN — con số ĐO ĐƯỢC ngày 2026-09-06: đúng chín test rơi
///    xuống «skipped» khi fixture Golden #1 vắng mặt (1108/33 → 1099/42);
/// 3. đường fixture trong bản đăng ký phải là đúng đường hai tệp test dùng.
///
/// Muốn bỏ một nghĩa vụ phải sửa ba tệp cùng lúc, và bản diff sẽ nói ra.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

import '../support/golden_chain_ledger.dart';

/// Số nghĩa vụ ĐO ĐƯỢC khi mở WAL-218. Đây là một PHÉP ĐO, không phải một
/// tuỳ chọn: chín test Golden chain im lặng bỏ qua trên CI trong khi suite in
/// «All tests passed!».
const measuredGoldenObligations = 9;

List<Map<String, Object?>> _rows(String key) => [
  for (final o in (goldenChainRegistry[key]! as List))
    (o as Map).cast<String, Object?>(),
];

void main() {
  final obligations = _rows('obligations');
  final mirrors = _rows('syntheticMirrors');

  test('bản đăng ký khai ĐỦ chín nghĩa vụ, id không trùng', () {
    expect(
      obligations.length,
      greaterThanOrEqualTo(measuredGoldenObligations),
      reason: 'mẫu số tụt xuống là cách một cổng in «0/0 · PASS»',
    );
    final ids = obligations.map((o) => o['id']).toList();
    expect(ids.toSet(), hasLength(ids.length));
    expect(goldenChainIds, hasLength(obligations.length));
  });

  test('⭐ mỗi nghĩa vụ có một TEST THẬT gọi đúng mã của nó', () {
    for (final o in obligations) {
      final id = o['id']! as String;
      final path = o['test']! as String;
      final f = File(path);
      expect(f.existsSync(), isTrue, reason: '$id khai $path — không có tệp ấy');
      final src = f.readAsStringSync();
      expect(
        src.contains("goldenChainGate('$id')"),
        isTrue,
        reason: '$id: không tệp test nào mở cổng cho nó ⇒ nghĩa vụ trên giấy',
      );
      expect(
        src.contains("recordGoldenChain('$id', exercised: true)"),
        isTrue,
        reason: '$id: không có chỗ nào ghi «đã kiểm» ⇒ verdict không bao giờ '
            'nói được VERIFIED, kể cả khi fixture có mặt',
      );
    }
  });

  test('mỗi bản MÔ PHỎNG cũng có một test thật — và nó không cần corpus', () {
    for (final m in mirrors) {
      final id = m['id']! as String;
      final src = File(m['test']! as String).readAsStringSync();
      expect(
        src.contains("recordGoldenChain('$id', exercised: true)"),
        isTrue,
        reason: id,
      );
      expect(
        src.contains("goldenChainGate('$id')"),
        isFalse,
        reason: '$id: bản mô phỏng KHÔNG được phụ thuộc fixture thật — nếu có '
            'thì nó đã không phải bản mô phỏng',
      );
    }
    expect(mirrors.length, greaterThanOrEqualTo(obligations.length));
  });

  test('⭐ CI đặt sàn --min-obligations, và sàn không tụt dưới phép đo', () {
    final ci = File('.github/workflows/ci.yml').readAsStringSync();
    expect(
      ci.contains('golden_chain_verdict.py'),
      isTrue,
      reason: 'không có bước verdict thì CI lại không tự nói được độ phủ',
    );
    final m = RegExp(r'--min-obligations\s+(\d+)').firstMatch(ci);
    expect(m, isNotNull, reason: 'bước verdict phải mang sàn mẫu số');
    final floor = int.parse(m!.group(1)!);
    expect(floor, greaterThanOrEqualTo(measuredGoldenObligations));
    expect(
      floor,
      lessThanOrEqualTo(obligations.length),
      reason: 'sàn cao hơn số nghĩa vụ khai ⇒ CI đỏ vĩnh viễn',
    );
  });

  test('đường fixture: bản đăng ký và hai tệp test nói CÙNG một tệp', () {
    expect(goldenChainFixturePath, contains('assets/fixtures/real/'));
    for (final path in {for (final o in obligations) o['test']! as String}) {
      final src = File(path).readAsStringSync();
      final namesIt =
          src.contains(goldenChainFixturePath) ||
          src.contains('goldenChainFixturePath');
      expect(namesIt, isTrue, reason: '$path không nói tới fixture ấy');
    }
  });

  test('bản đăng ký nói thẳng: fixture này KHÔNG BAO GIỜ vào git (D4)', () {
    expect(goldenChainRegistry['fixtureIsGitignored'], isTrue);
    final ignore = File('assets/fixtures/.gitignore').readAsStringSync();
    expect(ignore.contains('real/*'), isTrue);
    // Và nó thật sự không nằm trong cây git — kiểm bằng chính git, không bằng
    // niềm tin vào một dòng .gitignore.
    final tracked = Process.runSync('git', [
      'ls-files',
      '--',
      goldenChainFixturePath,
    ]);
    expect(
      (tracked.stdout as String).trim(),
      isEmpty,
      reason: '⭐ fixture Golden #1 ĐANG NẰM TRONG GIT. D4: chữ SGK nguyên văn '
          'và ảnh cắt trang là NỘI BỘ / NGHIÊN CỨU. Làm CI xanh bằng cách '
          'commit sách là không có phiên bản nào được phép.',
    );
  });

  test('sổ ghi nằm dưới thư mục build/ (không lọt vào git)', () {
    expect(goldenChainRegistry['ledgerDir'], startsWith('build/'));
    expect(File('.gitignore').readAsStringSync(), contains('build/'));
    expect(File(goldenChainRegistryPath).existsSync(), isTrue);
    expect(
      jsonDecode(File(goldenChainRegistryPath).readAsStringSync()),
      isA<Map<String, Object?>>(),
    );
  });
}
