/// WAL-133 slice 2 — «Hình trong sách»: lời SÁCH và lời SAM không đứng chung.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/source_gallery_screen.dart';

import '../../support/pack_bundle.dart';

const _withCaption = IndexedSourceAsset(
  subject: 'Khoa học',
  assetType: 'EXPERIMENT',
  asset: 'khoa-5-p017-tach-muoi-hinh5.png',
  sourceDocumentId: '05-sgk-khoa-hoc-5',
  pagePdf: 17,
  pagePrinted: 16,
  bboxFrac: [0.14, 0.409, 0.93, 0.618],
  extractionVersion: 'source-crop-v1',
  printedCaption: 'Hình 5',
);

const _noCaptionButGloss = IndexedSourceAsset(
  subject: 'Toán',
  assetType: 'FIGURE',
  asset: 'toan-5-p023-chia-banh-phan-so.png',
  sourceDocumentId: '05-sgk-toan-5-tap-mot',
  pagePdf: 23,
  pagePrinted: 22,
  bboxFrac: [0.185, 0.388, 0.8, 0.556],
  extractionVersion: 'source-crop-v1',
  samGloss: 'Hai cách chia 5 chiếc bánh cho 6 người — phần của mỗi người tô đỏ.',
);

void main() {
  testWidgets('caption IN trong sách ⇒ hiện; dòng nguồn có trang in',
      (t) async {
    await t.pumpWidget(packHost(
        const SourceGalleryScreen(subject: 'Khoa học', assets: [_withCaption])));
    await t.pump();
    expect(find.text('Hình 5'), findsOneWidget);
    expect(find.textContaining('05-sgk-khoa-hoc-5 · trang 16'), findsOneWidget);
    expect(find.text('SAM NÓI THÊM'), findsNothing,
        reason: 'không có gloss thì không dựng khối gloss rỗng');
  });

  testWidgets('⭐ sách KHÔNG in caption ⇒ KHÔNG bịa; lời SAM PHẢI có nhãn',
      (t) async {
    await t.pumpWidget(packHost(const SourceGalleryScreen(
        subject: 'Toán', assets: [_noCaptionButGloss])));
    await t.pump();
    // ⭐ Lời SAM chỉ được xuất hiện KÈM nhãn — không bao giờ đứng trần như
    // thể sách nói.
    expect(find.text('SAM NÓI THÊM'), findsOneWidget,
        reason: '⭐ đột biến bỏ nhãn ⇒ lời SAM đội lốt lời sách');
    expect(find.textContaining('chia 5 chiếc bánh'), findsOneWidget);
    // Không có caption sách ⇒ KHÔNG có ô chữ nào thêm vào đóng vai caption.
    // Đếm chính xác: tiêu đề + câu dẫn + nhãn SAM + lời SAM + dòng nguồn = 5.
    // Bịa thêm một caption là thành 6 ⇒ test đỏ.
    final texts = t
        .widgetList<Text>(find.byType(Text))
        .map((w) => w.data)
        .whereType<String>()
        .toList();
    expect(texts, hasLength(5), reason: 'thừa chữ ⇒ có chỗ đang bịa: $texts');
    expect(texts.any((x) => RegExp(r'^Hình\s*\d').hasMatch(x)), isFalse,
        reason: '⭐ không được dựng caption kiểu «Hình N» khi sách không in');
  });

  testWidgets('⭐ màn nói rõ đây là hình CHỤP TỪ SÁCH, không phải SAM vẽ',
      (t) async {
    await t.pumpWidget(packHost(const SourceGalleryScreen(
        subject: 'Toán', assets: [_noCaptionButGloss])));
    await t.pump();
    expect(find.textContaining('không phải hình SAM vẽ'), findsOneWidget);
  });

  test('⭐ parse: thiếu MẢNH provenance nào cũng bị loại (fail closed)', () {
    String j(String extra) => '''
{"grade":5,"subjects":{},"toanExercises":{},
 "sourceAssets":[{"asset":"a.png","subject":"Toán","sourceDocumentId":"b",
 "pagePdf":3,"bboxFrac":[0,0,1,1],"extractionVersion":"v1"$extra}]}''';
    expect(LessonIndex.fromJsonString(j(''))!.sourceAssets, hasLength(1));
    for (final broken in [
      '{"grade":5,"subjects":{},"toanExercises":{},"sourceAssets":[{"asset":"a.png","subject":"Toán","sourceDocumentId":"b","bboxFrac":[0,0,1,1],"extractionVersion":"v1"}]}',
      '{"grade":5,"subjects":{},"toanExercises":{},"sourceAssets":[{"asset":"a.png","subject":"Toán","sourceDocumentId":"b","pagePdf":3,"bboxFrac":[0,0,1],"extractionVersion":"v1"}]}',
      '{"grade":5,"subjects":{},"toanExercises":{},"sourceAssets":[{"asset":"a.png","subject":"Toán","sourceDocumentId":"b","pagePdf":3,"bboxFrac":[0,0,1,1]}]}',
    ]) {
      expect(LessonIndex.fromJsonString(broken)!.sourceAssets, isEmpty,
          reason: '⭐ asset không chứng minh được crop mà vẫn vào index ⇒ đỏ');
    }
  });

  test('FILE THẬT: index có asset của ≥3 môn, mỗi asset dựng được SourceAsset',
      () {
    final idx = LessonIndex.fromJsonString(
        _realIndex ?? '{"grade":5,"subjects":{},"toanExercises":{}}');
    if (_realIndex == null) {
      markTestSkipped('asset chưa build trên máy này');
      return;
    }
    final subjects = {for (final a in idx!.sourceAssets) a.subject};
    expect(subjects.length, greaterThanOrEqualTo(3),
        reason: 'WAL-133 D4: pipeline phải chạy ở ≥3 môn — thấy $subjects');
    for (final a in idx.sourceAssets) {
      final s = a.toAsset(); // ném AssertionError nếu provenance thiếu
      expect(s.path, startsWith('assets/pack/'));
    }
  });
}

String? get _realIndex {
  const p = 'assets/pack/lesson-index-g5.json';
  try {
    final f = File(p);
    return f.existsSync() ? f.readAsStringSync() : null;
  } catch (_) {
    return null;
  }
}
