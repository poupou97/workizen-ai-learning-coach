/// WAL-133 — mô hình tài sản: ba loại, luật nào cũng có chỗ đỡ.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/assets/learning_asset.dart';
import 'package:learning_coach/features/shell/learning_asset_image.dart';

SourceAsset _src() => SourceAsset(
      path: 'assets/pack/map-x.png',
      sourceDocumentId: '05-sgk-lich-su-va-dia-li-5',
      pagePdf: 12,
      pagePrinted: 10,
      bboxFrac: const [0.07, 0.05, 0.93, 0.9],
      extractionVersion: 'map-crop-v1',
      printedCaption: 'Hình 1. Bản đồ tự nhiên Việt Nam',
    );

void main() {
  test('⭐ SourceAsset PHẢI nằm trong vùng không-commit (WAL-43)', () {
    expect(
        () => SourceAsset(
              path: 'assets/mascot/map-x.png', // vùng ĐƯỢC commit
              sourceDocumentId: 'b',
              pagePdf: 1,
              bboxFrac: const [0, 0, 1, 1],
              extractionVersion: 'v1',
              printedCaption: 'c',
            ),
        throwsA(isA<AssertionError>()),
        reason: '⭐ crop từ SGK lọt vào vùng commit ⇒ vi phạm bản quyền im lặng');
  });

  test('⭐ crop không truy lại được (thiếu khung/phiên bản) ⇒ không dựng nổi',
      () {
    expect(
        () => SourceAsset(
              path: 'assets/pack/x.png',
              sourceDocumentId: 'b',
              pagePdf: 1,
              bboxFrac: const [0, 0, 1], // thiếu một số
              extractionVersion: 'v1',
              printedCaption: 'c',
            ),
        throwsA(isA<AssertionError>()));
    expect(
        () => SourceAsset(
              path: 'assets/pack/x.png',
              sourceDocumentId: 'b',
              pagePdf: 1,
              bboxFrac: const [0, 0, 1, 1],
              extractionVersion: '', // không biết cắt kiểu gì
              printedCaption: 'c',
            ),
        throwsA(isA<AssertionError>()));
  });

  test('⭐ CHỈ ảnh nguồn mới có dòng nguồn — hình SAM vẽ KHÔNG mượn được', () {
    expect(sourceLineOf(_src()), contains('trang 10'));
    expect(
        sourceLineOf(
            const SamGeneratedAsset(path: 'assets/pack/d.png', what: 'sơ đồ')),
        isNull,
        reason: '⭐ hình SAM vẽ mượn dòng nguồn của sách = nói dối');
    expect(sourceLineOf(const UiDecorativeAsset(path: 'assets/mascot/s.png')),
        isNull);
  });

  test('trang IN chưa dò được ⇒ KHÔNG bịa số trang', () {
    final a = SourceAsset(
      path: 'assets/pack/x.png',
      sourceDocumentId: 'sach-x',
      pagePdf: 3,
      bboxFrac: const [0, 0, 1, 1],
      extractionVersion: 'v1',
      printedCaption: 'c',
    );
    expect(sourceLineOf(a), 'sach-x');
    expect(sourceLineOf(a), isNot(contains('trang')));
  });

  test('nhãn bắt buộc: chỉ hình SAM vẽ mới có, và luôn có', () {
    expect(mandatoryLabelOf(_src()), isNull);
    expect(
        mandatoryLabelOf(
            const SamGeneratedAsset(path: 'assets/pack/d.png', what: 'sơ đồ')),
        'Minh hoạ của SAM');
  });

  test('thiếu tệp: ảnh nguồn NÓI, trang trí IM (hậu quả khác nhau)', () {
    expect(missingNoticeOf(_src()), contains('chưa có ảnh'));
    expect(missingNoticeOf(const UiDecorativeAsset(path: 'assets/mascot/s.png')),
        isNull);
  });

  testWidgets('⭐ hình SAM vẽ LUÔN đeo nhãn — không tham số nào tắt được',
      (t) async {
    await t.pumpWidget(const MaterialApp(
        home: Scaffold(
            body: LearningAssetImage(
                asset: SamGeneratedAsset(
                    path: 'assets/pack/khong-co.png', what: 'sơ đồ quy đồng')))));
    await t.pump();
    expect(find.text('Minh hoạ của SAM'), findsOneWidget,
        reason: '⭐ đột biến giấu nhãn ⇒ trẻ tưởng hình SAM vẽ là hình trong '
            'sách');
  });

  testWidgets('trang trí thiếu tệp ⇒ im lặng, không làm trẻ lo', (t) async {
    await t.pumpWidget(const MaterialApp(
        home: Scaffold(
            body: LearningAssetImage(
                asset: UiDecorativeAsset(path: 'assets/mascot/khong-co.png')))));
    await t.pump();
    expect(find.byType(Text), findsNothing);
  });

  test('⭐⭐ WAL-43 THẬT: không file ảnh nào của pack bị git theo dõi', () {
    final r = Process.runSync('git', ['ls-files', 'assets/pack/']);
    final tracked = (r.stdout as String)
        .split('\n')
        .where((l) => l.trim().isNotEmpty)
        .toList();
    final images = tracked
        .where((f) => RegExp(r'\.(png|jpg|jpeg|webp|db|json)$').hasMatch(f))
        .toList();
    expect(images, isEmpty,
        reason: '⭐⭐ crop SGK / pack dữ liệu lọt vào git: $images');
    expect(File('.gitignore').readAsStringSync(), contains('assets/pack/*.png'),
        reason: 'luật gitignore biến mất ⇒ lần commit tới là lọt');
  });
}
