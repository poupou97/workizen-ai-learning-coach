/// WAL-239 — KHỐI CANONICAL → CÓ NHÁNH Ở CLIENT → **THẬT SỰ HIỆN RA**.
///
/// Bất biến kỹ thuật Founder chốt sau lỗi công thức:
///
///     CANONICAL TYPED BLOCK PRODUCED
///     → CLIENT CONSUMER EXISTS
///     → LEARNER PATH RENDERS IT.
///
/// Hai chặng đầu đã có chốt (`tool/tests/test_block_types_reach_client.py`).
/// Chặng thứ ba là bộ này: dựng ĐÚNG widget của sản phẩm, với DỮ LIỆU PACK
/// THẬT và ẢNH THẬT lấy từ `figures-g*.db`, rồi hỏi «có hiện ra không».
///
/// ⚠ ĐÂY KHÔNG PHẢI KIỂM MÁY THẬT. Nó chứng minh đường dựng widget, không
/// chứng minh trải nghiệm trên máy Android. Kiểm máy thật vẫn còn nợ.
///
/// Danh sách khối được CẮT NGẮN quanh khối cần soi vì `ListView.builder` không
/// dựng mục ngoài màn hình — nhưng chính khối ấy là dữ liệu pack nguyên vẹn,
/// không sửa một chữ.
///
/// `assets/pack/` và `poc-out/packs/` đều gitignore ⇒ clone sạch thì **skip**,
/// và nói rõ vì sao.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pack/lesson_figure_store.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';
import 'package:learning_coach/features/subjects/lesson_pages_screen.dart';

const _packDir = 'assets/pack';
const _figDir = 'poc-out/packs/figures';

/// Bài đầu tiên trong lớp `g` có khối thoả [where], kèm chỉ số khối ấy.
({Map<String, Object?> lesson, int at})? _find(
    int g, bool Function(Map) where) {
  final f = File('$_packDir/lesson-index-g$g.json');
  if (!f.existsSync()) return null;
  final d = jsonDecode(f.readAsStringSync()) as Map<String, Object?>;
  for (final r in (d['lessonReadings'] as List? ?? const []).whereType<Map>()) {
    final c = (r['content'] as List? ?? const []).whereType<Map>().toList();
    final i = c.indexWhere(where);
    if (i >= 0) {
      return (lesson: Map<String, Object?>.from(r), at: i);
    }
  }
  return null;
}

/// Cắt `content` còn một cửa sổ quanh `at` để mục nằm trong màn hình.
LessonPages _trim(Map<String, Object?> lesson, int at, {int before = 1}) {
  final c = (lesson['content'] as List).whereType<Map>().toList();
  final lo = (at - before).clamp(0, c.length);
  final hi = (at + 2).clamp(0, c.length);
  return LessonPages.fromJson({...lesson, 'content': c.sublist(lo, hi)})!;
}

Future<void> _pump(WidgetTester t, LessonPages p, LessonFigureStore s) async {
  await t.pumpWidget(MaterialApp(
      home: LessonPagesScreen(
          pages: p, lessonLabel: 'Bài ${p.lesson}', figures: s)));
  await t.pump(const Duration(milliseconds: 50));
}

void main() {
  final havePack = Directory(_packDir).existsSync() &&
      File('$_packDir/lesson-index-g12.json').existsSync();
  const why = 'assets/pack chưa dựng trên máy này (gitignore) — '
      'dựng pack rồi chạy lại';

  testWidgets('KHỐI CÔNG THỨC hiện thành ẢNH TRANG IN, không rơi im lặng',
      (tester) async {
    if (!havePack) return markTestSkipped(why);
    int? grade;
    ({Map<String, Object?> lesson, int at})? hit;
    for (final g in [1, 10, 11, 12]) {
      hit = _find(g, (e) => e['t'] == 'formula');
      if (hit != null) {
        grade = g;
        break;
      }
    }
    expect(hit, isNotNull, reason: 'pack phải có khối formula để soi');
    final store = LessonFigureStore.open('$_figDir/figures-g$grade.db');
    expect(store.isEmpty, isFalse, reason: 'cần kho ảnh lớp $grade');

    final block = (hit!.lesson['content'] as List)[hit.at] as Map;
    final id = block['id'] as String;
    expect(store.jpeg(id), isNotNull, reason: 'ảnh của $id phải có trong kho');

    final pages = _trim(hit.lesson, hit.at);
    expect(pages.content.whereType<ReadFormula>(), isNotEmpty,
        reason: '⛔ parser bỏ mất khối formula — đúng lỗi đã phát hành');

    await _pump(tester, pages, store);
    expect(find.byType(Image), findsWidgets,
        reason: '⛔ khối formula không dựng ra ảnh nào — trẻ thấy khoảng trống');
  });

  testWidgets('KHỐI MÃ hiện ĐỦ DÒNG và ĐÚNG THỨ TỰ trên đường đọc', (tester) async {
    if (!havePack) return markTestSkipped(why);
    int? grade;
    ({Map<String, Object?> lesson, int at})? hit;
    for (final g in [12, 11, 10]) {
      hit = _find(
          g,
          (e) =>
              e['t'] == 'text' &&
              (e['v'] as String? ?? '').contains('\n') &&
              (e['v'] as String? ?? '').contains('def '));
      if (hit != null) {
        grade = g;
        break;
      }
    }
    expect(hit, isNotNull, reason: 'pack phải có khối mã nhiều dòng để soi');
    final src = (hit!.lesson['content'] as List)[hit.at]['v'] as String;
    final lines = src.split('\n');
    expect(lines.length, greaterThanOrEqualTo(2));

    final store = LessonFigureStore.open('$_figDir/figures-g$grade.db');
    final pages = _trim(hit.lesson, hit.at);
    await _pump(tester, pages, store);

    // Chữ phải hiện NGUYÊN VẸN, kể cả ranh giới dòng.
    final shown = tester
        .widgetList<SelectableText>(find.byType(SelectableText))
        .map((w) => w.data ?? '')
        .join('\u0000');
    expect(shown.contains(src), isTrue,
        reason: '⛔ khối mã không hiện nguyên văn.\nmong đợi:\n$src');
    for (final ln in lines) {
      expect(shown.contains(ln.trim()), isTrue, reason: 'mất dòng «$ln»');
    }
  });
}
