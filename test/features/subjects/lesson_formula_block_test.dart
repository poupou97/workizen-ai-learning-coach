/// WAL-239 — `FormulaSourceBlock` phải TỚI được tay trẻ.
///
/// Hồi quy cho một lỗi ĐÃ PHÁT HÀNH: pack canonical mang 2.699 khối
/// `t:"formula"`, bộ dựng GỠ chuỗi OCR mà vùng công thức sở hữu, còn parser
/// client chỉ nhận `text` · `heading` · `img` — nên khối rơi im lặng và tại
/// mỗi chỗ công thức trẻ không nhận lại gì. Đo được ở Toán 1 tr.61.
///
/// Test này chốt hai điều, và điều thứ hai mới là điều đã hỏng:
///   1. khối `formula` được đọc thành [ReadFormula]
///   2. nó KHÔNG bị lặng lẽ bỏ khi parser gặp loại khối mình chưa biết
library;

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

Map<String, Object?> _lesson(List<Object?> content) => {
      'book': '01-sgk-toan-1-tap-hai',
      'lesson': 32,
      'text': 'Phép trừ số có hai chữ số.',
      'pagePdfStart': 61,
      'pagePdfEnd': 62,
      'content': content,
    };

void main() {
  test('khối formula được đọc thành ReadFormula, không rơi im lặng', () {
    final p = LessonPages.fromJson(jsonDecode(jsonEncode(_lesson([
      {'t': 'text', 'v': 'Tính nhẩm.'},
      {
        't': 'formula',
        'id': '01-sgk-toan-1-tap-hai:p061:fml00',
        'w': 640,
        'h': 99,
        'page': 61,
        'trust': 'TRUSTED',
        'ident': null,
      },
    ]))))!;
    expect(p.content.length, 2, reason: 'khối công thức phải còn trong dòng đọc');
    final f = p.content[1];
    expect(f, isA<ReadFormula>());
    f as ReadFormula;
    expect(f.id, '01-sgk-toan-1-tap-hai:p061:fml00');
    expect(f.page, 61);
    expect(f.ident, isNull);
    // Tỉ lệ phải theo ĐÚNG vùng đã cắt, không ép vuông.
    expect(f.aspect, closeTo(640 / 99, 1e-9));
  });

  test('SỐ HIỆU IN được giữ nguyên như sách, KHÔNG bịa khi sách không in', () {
    final p = LessonPages.fromJson(jsonDecode(jsonEncode(_lesson([
      {'t': 'formula', 'id': 'b:p1:fml00', 'w': 10, 'h': 5, 'page': 1, 'ident': '3.2'},
      {'t': 'formula', 'id': 'b:p1:fml01', 'w': 10, 'h': 5, 'page': 1, 'ident': '  '},
      {'t': 'formula', 'id': 'b:p1:fml02', 'w': 10, 'h': 5, 'page': 1},
    ]))))!;
    expect(p.content.whereType<ReadFormula>().map((f) => f.ident).toList(),
        ['3.2', null, null]);
  });

  test('khối công thức HỎNG bị loại, không dựng nửa vời', () {
    final p = LessonPages.fromJson(jsonDecode(jsonEncode(_lesson([
      {'t': 'text', 'v': 'Còn chữ này.'},
      {'t': 'formula', 'id': 'b:p1:fml00', 'w': 0, 'h': 5, 'page': 1},
      {'t': 'formula', 'w': 10, 'h': 5, 'page': 1},
      {'t': 'formula', 'id': 'b:p1:fml02', 'w': 10, 'h': -5, 'page': 1},
    ]))))!;
    expect(p.content.whereType<ReadFormula>(), isEmpty);
    expect(p.content.length, 1, reason: 'chữ của sách không được mất theo');
  });

  test('THỨ TỰ ĐỌC giữ nguyên: công thức đứng đúng chỗ giữa hai đoạn chữ', () {
    final p = LessonPages.fromJson(jsonDecode(jsonEncode(_lesson([
      {'t': 'text', 'v': 'trước'},
      {'t': 'formula', 'id': 'b:p1:fml00', 'w': 10, 'h': 5, 'page': 1},
      {'t': 'text', 'v': 'sau'},
    ]))))!;
    expect(p.content.map((e) => e.runtimeType.toString()).toList(),
        ['ReadText', 'ReadFormula', 'ReadText']);
  });
}
