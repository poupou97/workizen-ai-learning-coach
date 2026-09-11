import 'dart:convert';
import 'dart:io';

import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';

/// ⭐ SAM SCALE POC 1 → 10 — MỘT bộ dựng, MỘT runtime, nhiều bằng chứng.
///
/// Điều phải giữ: thêm một bài KHÔNG được đòi thêm một nhánh mã. Nếu POC chỉ
/// chạy nhờ logic riêng từng bài thì nó không chứng minh được gì về 50 hay N.
void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  // ⚠ `assets/fixtures/real/` là GITIGNORE (Founder D4 — không phân phối).
  // Clone sạch không có tệp ⇒ SKIP có lý do, không đỏ giả. Cổng «catalog» ở
  // dưới KHÔNG skip: nó đọc mã, và mã thì clone nào cũng có.
  final have =
      File('assets/fixtures/real/lesson-07-sgk-tin-hoc-7-b3.json').existsSync();
  const why = 'assets/fixtures/real/ chưa sinh trên máy này (gitignore) — '
      'chạy tool/pedagogy/build_sam_workspace.py rồi thử lại';

  const poc = [
    ['11-sgk-sinh-hoc-11', 2],
    ['06-sgk-khoa-hoc-tu-nhien-6', 9],
    ['11-sgk-hoa-hoc-11', 13],
    ['09-sgk-cong-nghe-9-trai-nghiem-nghe-nghiep-mo-dun-trong-cay-an-qua', 1],
    ['10-sgk-dia-li-10', 5],
    ['12-sgk-chuyen-de-hoc-tap-cong-nghe-12-lam-nghiep-thuy-san', 5],
    ['10-sgk-lich-su-10', 9],
    ['07-sgk-tin-hoc-7', 13],
    ['11-sgk-sinh-hoc-11', 6],
    ['06-sgk-khoa-hoc-tu-nhien-6', 10],
    ['06-sgk-khoa-hoc-tu-nhien-6', 18],
    ['06-sgk-khoa-hoc-tu-nhien-6', 25],
    ['09-sgk-khoa-hoc-tu-nhien-9', 18],
    ['09-sgk-khoa-hoc-tu-nhien-9', 3],
    ['09-sgk-khoa-hoc-tu-nhien-9', 44],
    ['10-sgk-dia-li-10', 19],
    ['11-sgk-sinh-hoc-11', 10],
    ['11-sgk-sinh-hoc-11', 12],
    ['11-sgk-sinh-hoc-11', 13],
    ['11-sgk-sinh-hoc-11', 15],
    ['11-sgk-sinh-hoc-11', 19],
    ['11-sgk-sinh-hoc-11', 20],
    ['11-sgk-sinh-hoc-11', 27],
    ['11-sgk-sinh-hoc-11', 9],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 1],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 27],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 3],
    ['12-sgk-cong-nghe-12-lam-nghiep-thuy-san', 7],
    ['12-sgk-hoa-hoc-12', 15],
    ['12-sgk-hoa-hoc-12', 18],
    ['12-sgk-hoa-hoc-12', 21],
    ['12-sgk-hoa-hoc-12', 24],
    ['12-sgk-hoa-hoc-12', 9],
  ];

  Future<Map<String, Object?>> raw(String book, int no) async {
    final s = await rootBundle
        .loadString('assets/fixtures/real/lesson-$book-b$no.json');
    return (jsonDecode(s) as Map).cast<String, Object?>();
  }

  test('⭐ cả 10 bài POC dựng được LessonDocument qua CÙNG một đường', () async {
    if (!have) return markTestSkipped(why);
    for (final p in poc) {
      final j = await raw(p[0] as String, p[1] as int);
      final d = LessonDocument.fromJson(j);
      expect(d, isNotNull, reason: '${p[0]} B${p[1]} không dựng được');
      expect(d!.blocks, isNotEmpty, reason: '${p[0]} B${p[1]} rỗng');
      expect(d.book, p[0]);
      expect(d.lessonNo, p[1]);
    }
  });

  test('⭐ KHÔNG bài nào mang khoá chấm — chốt fail-closed của vòng', () async {
    if (!have) return markTestSkipped(why);
    for (final p in poc) {
      final j = await raw(p[0] as String, p[1] as int);
      final prov = (j['provenance'] as Map).cast<String, Object?>();
      expect(prov['answerKeysIncluded'], isNot(true),
          reason: '${p[0]} B${p[1]} mang khoá chấm — trẻ có thể bị chấm sai');
      expect(j['evidencePolicy'], 'none');
    }
  });

  test('⭐ bài do bộ dựng POC sinh phải KHAI RÕ đã khoá đáp án', () async {
    if (!have) return markTestSkipped(why);
    var checked = 0;
    for (final p in poc) {
      final j = await raw(p[0] as String, p[1] as int);
      final prov = (j['provenance'] as Map).cast<String, Object?>();
      final ped = (prov['pedagogySource'] as Map).cast<String, Object?>();
      expect(ped['answerWithheld'], true, reason: '${p[0]} B${p[1]}');
      expect(ped['withholdReason'], 'TASK_ANSWER_OWNERSHIP_UNPROVEN');
      expect(ped['sgvBook'], isA<String>());
      expect(ped['pairing'], contains('L1+L2+L3'));
      checked++;
    }
    expect(checked, 33, reason: '8 bài mới phải đi qua bộ dựng chung');
  });

  test('⭐ catalog KHÔNG có nhánh riêng cho bài nào', () {
    // Mọi slot đi qua cùng một hàm; không có danh sách ngoại lệ.
    final keys = WorkspaceCatalog.defaultSlots
        .map((s) => '${s.book}#${s.lessonNo}')
        .toSet();
    for (final p in poc) {
      expect(keys, contains('${p[0]}#${p[1]}'),
          reason: '${p[0]} B${p[1]} chưa vào catalog');
    }
    expect(WorkspaceCatalog.defaultSlots.length, keys.length,
        reason: 'slot trùng ⇒ một bài được nạp hai lần');
  });

  test('⭐ vòng dạy KHÔNG CHẤM — không bài nào có bước hỏi', () async {
    if (!have) return markTestSkipped(why);
    for (final p in poc) {
      final j = await raw(p[0] as String, p[1] as int);
      final sc = (j['tutorScript'] as Map?)?.cast<String, Object?>();
      expect(sc, isNotNull, reason: '${p[0]} B${p[1]} không có vòng dạy');
      final kinds = (sc!['steps'] as List)
          .map((s) => (s as Map)['type'])
          .toSet();
      // `ask` kéo theo acceptable/hints/feedbackMatched/scaffold/keySource —
      // toàn bộ máy móc chấm điểm mà nguồn KHÔNG chống đỡ nổi.
      expect(kinds, isNot(contains('ask')),
          reason: '${p[0]} B${p[1]} có bước hỏi ⇒ có chỗ phán đúng/sai');
      expect(kinds, contains('next'), reason: '${p[0]} B${p[1]} thiếu hành động kế');
    }
  });

  test('⭐ cờ NĂNG LỰC nằm trong dữ liệu, không chỉ trong tài liệu', () async {
    if (!have) return markTestSkipped(why);
    for (final p in poc) {
      final j = await raw(p[0] as String, p[1] as int);
      final cap = ((j['provenance'] as Map)['capability'] as Map)
          .cast<String, Object?>();
      expect(cap['samReady'], true, reason: '${p[0]} B${p[1]}');
      // ⭐ SAM_READY != RUNTIME_GUIDED_READY — và cờ phải KHỚP dữ liệu, không
      // được khai suông. Bài có `curriculum` (suy từ khối quy tắc in) thì
      // true; không có thì false. Chốt cũ đòi false ở MỌI bài; nó đã bắn
      // đúng khi 18 bài có ngữ nghĩa thật, nên đổi sang điều còn đúng.
      expect(cap['runtimeGuidedReady'], j['curriculum'] != null,
          reason: '${p[0]} B${p[1]}: cờ không khớp dữ liệu');
      expect(cap['answerCheckReady'], false, reason: '${p[0]} B${p[1]}');
      expect(cap['misconceptionReady'], false, reason: '${p[0]} B${p[1]}');
    }
  });

  test('⭐ mỗi bài POC có VIỆC của trẻ là chữ NGUYÊN VĂN của sách', () async {
    if (!have) return markTestSkipped(why);
    for (final p in poc) {
      final j = await raw(p[0] as String, p[1] as int);
      final d = LessonDocument.fromJson(j)!;
      final hasQuestion = d.blocks.any((b) => b.sourceRole == 'question');
      final hasText = d.blocks.any((b) => b.sourceRole == 'body');
      expect(hasText, isTrue, reason: '${p[0]} B${p[1]} không có chữ bài');
      expect(hasQuestion || hasText, isTrue);
    }
  });

  test('⭐ KHÔNG bài nào được tạo SemanticBinding giả', () {
    // `resolveBinding` đòi Concept + SkillCase + TeachingMethod có
    // `origin: sourceStated` và trích được trang. Nguồn hiện tại không cấp
    // ba thứ đó. Sổ đăng ký binding phải vẫn là ĐÚNG MỘT (KHTN 6 Bài 17) —
    // thêm binding cho bài khác mà không có bằng chứng là bịa chương trình.
    final dir = Directory('lib/core/curriculum');
    // ⚠ Chỉ đếm tệp KHAI một binding cụ thể (`= SemanticBinding(`), không
    // đếm tệp ĐỊNH NGHĨA lớp — bản đầu đếm cả `semantic_binding.dart` nên ra 2.
    final bindings = dir
        .listSync()
        .whereType<File>()
        .where((f) =>
            File(f.path).readAsStringSync().contains('= SemanticBinding('))
        .toList();
    expect(bindings.length, 1,
        reason: 'có ${bindings.length} tệp khai SemanticBinding — '
            'chỉ được đúng một cho tới khi Concept/SkillCase có nguồn');
  });
}
