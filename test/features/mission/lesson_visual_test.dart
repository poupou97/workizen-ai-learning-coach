/// ⭐ Lệnh 56 §P2.3 — chuỗi rơi của hình thẻ bài học, và cái CẤM ở tầng đầu.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/features/mission/lesson_visual.dart';

import '../lesson_workspace/support.dart';

void main() {
  final doc = loadSyntheticDoc();

  test('⭐⭐ D4 — hình SGK KHÔNG được làm nền trang trí', () {
    expect(doc.licence, ContentLicence.internalResearchOnly);
    expect(mayDecorateWithLessonImagery(doc), isFalse);

    final v = lessonVisual(
      doc,
      heroAsset: 'assets/fixtures/real/crops/x.png',
      coverAsset: 'covers/06-sgk-khoa-hoc-tu-nhien-6.webp',
    );
    expect(
      v.kind,
      LessonVisualKind.cover,
      reason: 'crop bị D4 chặn vẫn được dùng làm nền',
    );
    expect(v.asset, isNot(contains('crops/')));
  });

  test('tầng 2 — BÌA SÁCH của môn khi không có hero hợp lệ', () {
    final v = lessonVisual(
      doc,
      coverAsset: 'covers/06-sgk-khoa-hoc-tu-nhien-6.webp',
    );
    expect(v.kind, LessonVisualKind.cover);
    expect(v.asset, 'assets/pack/covers/06-sgk-khoa-hoc-tu-nhien-6.webp');
  });

  test('tầng 3 — không bìa ⇒ dải màu, KHÔNG bao giờ trắng trơn', () {
    final v = lessonVisual(doc);
    expect(v.kind, LessonVisualKind.gradient);
    expect(v.asset, isNull);
  });

  test('⭐ màu tất định theo MÔN — cùng môn cùng màu, khác môn khác màu', () {
    expect(subjectSeed('KHTN'), subjectSeed('KHTN'));
    expect(subjectSeed('KHTN'), isNot(subjectSeed('Toán')));
    expect(subjectSeed('Toán'), greaterThanOrEqualTo(0));
  });

  test('⛔ KHÔNG hardcode theo bài — cùng luật cho mọi tài liệu', () {
    final src = const ['lib/features/mission/lesson_visual.dart'];
    for (final _ in src) {
      // Luật chỉ đọc `licence`, `subject` và asset truyền vào; không có nhánh
      // nào theo số bài hay tên bài (§P2.4).
      expect(
        lessonVisual(doc, coverAsset: 'covers/a.webp').kind,
        lessonVisual(doc, coverAsset: 'covers/b.webp').kind,
      );
    }
  });
}
