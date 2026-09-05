/// WAL-210 round 3 (#7, Lane B yêu cầu) — «Hình trong sách» của Toán 6 KHÔNG
/// được trưng hình Toán 5: `sourceAssetsFor` lọc theo môn VÀ sách-thuộc-lớp
/// (sách trên giá của pack, hoặc tiền tố lớp `NN-` của định danh sách).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

String _asset(String doc, String subject) =>
    '{"asset":"a.png","subject":"$subject","sourceDocumentId":"$doc",'
    '"pagePdf":3,"bboxFrac":[0,0,1,1],"extractionVersion":"v1"}';

LessonIndex _index({required int grade, String books = '[]', required List<String> assets}) =>
    LessonIndex.fromJsonString('{"grade":$grade,"subjects":{},"toanExercises":{},'
        '"books":$books,"sourceAssets":[${assets.join(',')}]}')!;

void main() {
  test('⭐⭐ Toán 6: hình Toán 5 bị loại, hình Toán 6 giữ (tiền tố lớp)', () {
    final idx = _index(grade: 6, assets: [
      _asset('05-sgk-toan-5-tap-mot', 'Toán'),
      _asset('06-sgk-toan-6-tap-mot', 'Toán'),
    ]);
    expect(idx.sourceAssets, hasLength(2), reason: 'parse giữ cả hai (fail closed ở màn)');
    expect(idx.sourceAssetsFor('Toán').map((a) => a.sourceDocumentId),
        ['06-sgk-toan-6-tap-mot']);
  });

  test('sách nằm trên giá của pack ⇒ giữ dù định danh không mang tiền tố lớp', () {
    final idx = _index(
        grade: 6,
        books: '[{"sourceDocumentId":"khtn-6-kntt","subject":"KHTN","title":"KHTN 6",'
            '"cover":"covers/k.webp","lessonCount":1}]',
        assets: [_asset('khtn-6-kntt', 'KHTN'), _asset('05-sgk-khoa-hoc-5', 'KHTN')]);
    expect(idx.sourceAssetsFor('KHTN').map((a) => a.sourceDocumentId), ['khtn-6-kntt']);
  });

  test('⭐ không chứng minh được thuộc lớp (không tiền tố, không trên giá) ⇒ '
      'không trưng (fail closed)', () {
    final idx = _index(grade: 6, assets: [_asset('toan-x', 'Toán')]);
    expect(idx.sourceAssetsFor('Toán'), isEmpty);
  });

  test('vẫn lọc theo môn: hình Khoa học 6 không lọt sang Toán', () {
    final idx = _index(grade: 6, assets: [
      _asset('06-sgk-khoa-hoc-tu-nhien-6', 'KHTN'),
      _asset('06-sgk-toan-6-tap-mot', 'Toán'),
    ]);
    expect(idx.sourceAssetsFor('Toán'), hasLength(1));
    expect(idx.sourceAssetsFor('KHTN'), hasLength(1));
    expect(idx.sourceAssetsFor('Sử'), isEmpty);
  });
}
