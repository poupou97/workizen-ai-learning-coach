/// ⭐ Lệnh 53 §2 — chọn ảnh đại diện bài học: TẤT ĐỊNH, đo được, và không bao
/// giờ lấy ảnh của bài khác.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/features/mission/home_cards.dart';

import '../lesson_workspace/support.dart';

LessonDocument? _realB17() {
  final f = File(
    'assets/fixtures/real/lesson-06-sgk-khoa-hoc-tu-nhien-6-b17.json',
  );
  if (!f.existsSync()) return null;
  return LessonDocument.fromJson(
    (jsonDecode(f.readAsStringSync()) as Map).cast<String, Object?>(),
    assetBase: 'assets/fixtures/real/',
  );
}

void main() {
  group('luật chọn — trên BÀI THẬT (Bài 17)', () {
    test('⭐ chọn hình LỚN NHẤT trong khoảng tỉ lệ dùng được', () {
      final doc = _realB17();
      if (doc == null) return; // fixture ngoài git ⇒ bỏ qua (xem skip bên dưới)
      final hero = lessonHeroImage(doc);
      expect(hero, isNotNull);
      // p061-fig03: area .1461 — lớn nhất trong số hình có tỉ lệ hợp lệ.
      expect(hero!.asset, endsWith('p061-fig03.png'));
      expect(hero.aspect, closeTo(1.1824, 0.001));
    });

    test('⭐⭐ hình DẸT hơn ngưỡng bị loại DÙ diện tích lớn', () {
      final doc = _realB17();
      if (doc == null) return;
      // p064-fig02 có aspect 2.99 và area .1197 — lớn thứ nhì, nhưng dẹt quá:
      // làm hero thì cắt mất nội dung. Luật phải loại nó.
      expect(lessonHeroImage(doc)!.asset, isNot(contains('p064-fig02')));
    });

    test('gọi hai lần ⇒ CÙNG một ảnh (tất định)', () {
      final doc = _realB17();
      if (doc == null) return;
      expect(lessonHeroImage(doc)!.asset, lessonHeroImage(doc)!.asset);
    });

    test('ảnh mang assetBase của CHÍNH tài liệu', () {
      final doc = _realB17();
      if (doc == null) return;
      expect(lessonHeroImage(doc)!.asset, startsWith('assets/fixtures/real/'));
    });
  }, skip: _realB17() == null ? 'fixture thật nằm ngoài git' : null);

  group('biên', () {
    test('bài KHÔNG có hình nào ⇒ null, không bịa ảnh', () {
      final doc = loadSyntheticDoc();
      final imgs = doc.blocks.whereType<ImageBlock>();
      if (imgs.isEmpty) {
        expect(lessonHeroImage(doc), isNull);
      } else {
        // Bài mẫu CÓ hình ⇒ chỉ kiểm rằng ảnh trả về thuộc chính bài này.
        final hero = lessonHeroImage(doc);
        if (hero != null) {
          expect(
            imgs.map((b) => '${doc.assetBase}${b.crop}'),
            contains(hero.asset),
          );
        }
      }
    });

    test('ngưỡng là HẰNG đọc được, không phải số ma thuật rải rác', () {
      expect(kHeroMinAspect, lessThan(kHeroMaxAspect));
      expect(kHeroMinArea, greaterThan(0));
    });
  });
}
