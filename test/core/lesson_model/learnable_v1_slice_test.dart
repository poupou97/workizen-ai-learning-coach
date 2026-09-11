/// LEARNABLE_V1 — lát cắt đầu tiên đi qua ĐÚNG ĐƯỜNG SẢN PHẨM.
///
/// Founder duyệt 2026-09-10: bốn cổng — `OPENABLE` · `READ_SAFE` ·
/// `VISUAL_GROUNDED` · `NEXT_ACTION_REAL`. Kịch bản SAM và chấm điểm KHÔNG
/// phải cổng.
///
/// Bộ này nghiệm thu hai cổng nằm ở phía client (③ và ④) trên chính
/// `WorkspaceCatalog` mà app dùng — không dựng tài liệu giả.
///
/// ⚠ CỔNG ③ ĐÒI **BƯỚC THẬT**, không chỉ đòi «có SemanticData». Đo được trên
/// 44 bài ứng viên: **7 bài (15,9%)** có process mà MỌI bước đều bị giữ lại —
/// với trẻ đó là một tab ✨ Trực quan rỗng có tiêu đề. KHTN 6 Bài 8 đúng là ca
/// ấy, nên nó KHÔNG được nối vào sản phẩm.
///
/// `assets/fixtures/real/` là gitignore ⇒ clone sạch thì skip, nói rõ lý do.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/tutor_script.dart';
import 'package:learning_coach/core/lesson_model/semantic_data.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';

/// Lát cắt Founder chốt — seed `20260910`, rút LẠI CẢ SÁU LỚP trên quần thể
/// đã sửa (37 bài). KHÔNG thay bằng ví dụ đẹp hơn.
const _slice = [
  ('04-sgk-khoa-hoc-4', 4),
  ('05-sgk-khoa-hoc-5', 4),
  ('06-sgk-khoa-hoc-tu-nhien-6', 9),
  ('07-sgk-khoa-hoc-tu-nhien-7', 4),
  ('08-sgk-khoa-hoc-tu-nhien-8', 19),
  ('09-sgk-khoa-hoc-tu-nhien-9', 14),
];

/// Bài lớp 6 rút được dưới cổng ③ CŨ, nhưng cổng ấy đã bị BÁC BỎ: `process`
/// duy nhất của nó có đúng một bước và bước ấy BỊ GIỮ LẠI. Giữ tên ở đây để
/// nếu có ai lặng lẽ nối nó vào thì test đỏ.
const _failed = ('06-sgk-khoa-hoc-tu-nhien-6', 8);

bool _hasRealStep(SemanticData s) => switch (s) {
      ProcessSemantic p => p.steps.any((x) => (x.text ?? '').trim().isNotEmpty),
      _ => true,
    };

void main() {
  // ⚠ `testWidgets` chạy trong vùng ASYNC GIẢ — `rootBundle.loadString` là
  // I/O THẬT nên future không bao giờ hoàn tất ở đó (đã treo 10 phút). Dùng
  // `test` thường + binding: async thật, nạp asset thật.
  TestWidgetsFlutterBinding.ensureInitialized();
  final have = File('assets/fixtures/real/'
          'lesson-04-sgk-khoa-hoc-4-b4.json')
      .existsSync();
  const why = 'assets/fixtures/real/ chưa sinh trên máy này (gitignore) — '
      'chạy tool/fixtures/make_lesson_fixture.py rồi thử lại';

  test('lát cắt đúng SÁU chỗ Founder chốt, không thêm không bớt', () {
    final keys = WorkspaceCatalog.defaultSlots.map((s) => s.key).toSet();
    for (final (book, no) in _slice) {
      expect(keys, contains('$book#$no'), reason: 'thiếu $book bài $no');
    }
    expect(keys, isNot(contains('${_failed.$1}#${_failed.$2}')),
        reason: '⛔ KHTN 6 Bài 8 TRƯỢT cổng ③ (process toàn bước bị giữ lại) — '
            'không được nối vào sản phẩm');
  });

  test('③ VISUAL_GROUNDED — mỗi bài có SemanticData với BƯỚC THẬT', () async {
    if (!have) return markTestSkipped(why);
    final cat = WorkspaceCatalog();
    await cat.load();
    for (final (book, no) in _slice) {
      final d = cat.docFor(book, no);
      expect(d, isNotNull, reason: '$book bài $no chưa nạp được');
      expect(d!.semantic, isNotEmpty, reason: '$book bài $no không có semantic');
      expect(d.semantic.where(_hasRealStep), isNotEmpty,
          reason: '⛔ $book bài $no: MỌI bước đều bị giữ lại — '
              'Trực quan sẽ là tab rỗng');
    }
  });

  test('③b không có process TRÙNG LẶP — trẻ không thấy hai sơ đồ y nhau', () async {
    if (!have) return markTestSkipped(why);
    final cat = WorkspaceCatalog();
    await cat.load();
    for (final (book, no) in _slice) {
      final ps = cat.docFor(book, no)!.semantic.whereType<ProcessSemantic>();
      final sig = ps
          .map((p) => '${p.title}|${p.steps.map((s) => s.text ?? '~').join('¶')}')
          .toList();
      expect(sig.toSet().length, sig.length,
          reason: '⛔ $book bài $no có process trùng: $sig');
    }
  });

  test('④ NEXT_ACTION_REAL — bước tiếp theo trỏ vào thứ CÓ THẬT trong bài', () async {
    if (!have) return markTestSkipped(why);
    final cat = WorkspaceCatalog();
    await cat.load();
    for (final (book, no) in _slice) {
      final d = cat.docFor(book, no)!;
      final a = nextActionFor(doc: d, seen: const {});
      expect(a.view, isNotNull, reason: '$book bài $no: không có bước nào');
      expect(a.basis, isNotEmpty);
      // `basis` phải dẫn tới một thứ đọc được từ chính tài liệu, không phải
      // một chuỗi trang trí.
      if (a.basis.startsWith('semantic.process:')) {
        final id = a.basis.split(':').last;
        expect(d.semantic.whereType<ProcessSemantic>().map((p) => p.id),
            contains(id), reason: '$book bài $no: basis trỏ vào process không có');
      } else {
        expect(a.basis, matches(RegExp(r'^(blocks\.paragraph=\d+|tutorScript\.ask:.+)$')),
            reason: '$book bài $no: basis lạ «${a.basis}»');
      }
      expect(a.reason.trim(), isNotEmpty);
    }
  });

  /// ⭐ CHỐT NÀY ĐÃ BẮN ĐÚNG (2026-09-11). Bản trước đòi MỌI bài trong lát cắt
  /// có `tutorScript == null`, kèm lý do: «bỗng có kịch bản ⇒ con số
  /// SAM_READY=1 phải được đo lại». Vòng POC 1→10 thêm vòng dạy cho KHTN 6
  /// Bài 9, chốt đỏ, và **SAM_READY=1 đã được đo lại** — nay là 10.
  ///
  /// Chốt không bị gỡ, nó được ĐỔI SANG ĐIỀU CÒN ĐÚNG: `SAM_READY != LEARNABLE`
  /// (hai phép đo khác nhau), và kịch bản nào có mặt trong lát cắt phải là
  /// loại KHÔNG CHẤM — không bước hỏi, không khoá đáp án.
  test('SAM_READY != LEARNABLE; kịch bản trong lát cắt phải là loại KHÔNG CHẤM',
      () async {
    if (!have) return markTestSkipped(why);
    final cat = WorkspaceCatalog();
    await cat.load();
    for (final (book, no) in _slice) {
      final d = cat.docFor(book, no)!;
      final sc = d.tutorScript;
      if (sc == null) continue; // LEARNABLE không đòi có kịch bản
      expect(sc.steps.whereType<AskStep>(), isEmpty,
          reason: '$book bài $no có bước HỎI ⇒ có chỗ phán đúng/sai, '
              'mà nguồn chưa chứng minh được sở hữu đáp án');
      expect(d.provenance.answerKeysIncluded, isNot(true),
          reason: '$book bài $no mang khoá chấm');
    }
  });
}
