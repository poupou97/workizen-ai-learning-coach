/// Bài phân số "a/b ± c/d" đã bóc số — đầu vào rule-based của slice Toán 5.
///
/// WAL-168: chuyển từ `features/tutor` xuống `core/curriculum`. Đây là tri thức
/// MIỀN (bóc số, chấm đáp án), không phải UI — và tầng chương trình phải trỏ
/// được tới nó mà không đi ngược lên features.
library;

import 'problem_applicability.dart';
import 'solvable_problem.dart';

class FractionProblem implements SolvableProblem {
  const FractionProblem(this.a, this.b, this.op, this.c, this.d);
  final int a, b, c, d;
  final String op; // '+' | '-'

  /// null nếu không phải dạng "a/b ± c/d" — tầng trên phải fail closed.
  static FractionProblem? parse(String expr) {
    final m = RegExp(
            r'^\s*(\d{1,3})\s*/\s*(\d{1,3})\s*([+\-−])\s*(\d{1,3})\s*/\s*(\d{1,3})\s*$')
        .firstMatch(expr);
    if (m == null) return null;
    return FractionProblem(
        int.parse(m.group(1)!),
        int.parse(m.group(2)!),
        m.group(3)! == '−' ? '-' : m.group(3)!,
        int.parse(m.group(4)!),
        int.parse(m.group(5)!));
  }

  int get resultNum => op == '+' ? a * d + c * b : a * d - c * b;
  int get resultDen => b * d;

  /// Đáp án của trẻ dạng "x/y" hoặc số nguyên; chấp nhận phân số CHƯA rút gọn
  /// có cùng giá trị (SGK Toán 5 chấp nhận cả hai dạng ở bước quy đồng).
  @override
  bool checkAnswer(String raw) {
    final f = RegExp(r'^\s*(-?\d{1,6})\s*(?:/\s*(\d{1,6})\s*)?$').firstMatch(raw);
    if (f == null) return false;
    final n = int.parse(f.group(1)!);
    final d0 = f.group(2) == null ? 1 : int.parse(f.group(2)!);
    if (d0 == 0) return false;
    return n * resultDen == resultNum * d0;
  }

  @override
  Map<String, String> get slots => {
        'a': '$a',
        'b': '$b',
        'c': '$c',
        'd': '$d',
        'op': op,
        // mẫu số chung khi lấy TÍCH hai mẫu — cách của Bài 6.
        'product': '${b * d}',
        'aOverProduct': '${a * d}',
        'cOverProduct': '${c * b}',
        'resultNum': '$resultNum',
      };
}

/// ⭐ Phân loại ca cho HỌ MÔN «cộng/trừ phân số» — dùng chung cho MỌI bài
/// thuộc họ này, không riêng bài nào. Thêm một bài phân số = thêm dòng dữ liệu
/// trỏ tới đúng hàm này, KHÔNG thêm mã runtime (Architecture Gate, WAL-168).
///
/// Không đọc được thành phân số ⇒ `null` ⇒ tầng trên fail closed: SAM nhận
/// «chưa chắc», không dạy bừa một cách của môn khác.
String? fractionSumCase(String expression) {
  final fp = FractionProblem.parse(expression);
  return fp == null ? null : analyzeFractionPair(fp.b, fp.d)?.skillCase;
}
