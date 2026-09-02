import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/learning_objective.dart';

Map<String, Object?> row({String origin = 'sourceStated', Object? concept}) =>
    {
      'id': 'sgv5:obj:1:0001',
      'lesson': 1,
      'book': '05-sgv-toan-5',
      'pagePdf': 19,
      'kind': 'knowledge',
      'text': 'Đọc, viết, so sánh được các số tự nhiên.',
      'origin': origin,
      'conceptId': concept ?? 'so-tu-nhien',
    };

void main() {
  test('objective sourceStated: parse được, citable, giữ nguyên văn', () {
    final o = LearningObjective.fromJson(row())!;
    expect(o.citable, true);
    expect(o.text, 'Đọc, viết, so sánh được các số tự nhiên.');
    expect(o.conceptId, 'so-tu-nhien');
    expect(o.lessonNumber, 1);
  });

  test('origin lạ (llmInferred) → từ chối parse, không đoán', () {
    expect(LearningObjective.fromJson(row(origin: 'llmInferred')), isNull);
  });

  test("'unmapped' thành null — không có concept giả", () {
    final o = LearningObjective.fromJson(row(concept: 'unmapped'))!;
    expect(o.conceptId, isNull);
  });

  test('thiếu trường bắt buộc → null, không nửa vời', () {
    final j = row()..remove('lesson');
    expect(LearningObjective.fromJson(j), isNull);
  });
}
