/// ROUND 7 · WS-R — **DANH TỪ RIÊNG LỊCH SỬ BỊ HẠ CHỮ THƯỜNG** (lỗi máy thật).
///
/// Vòng 6, LS&ĐL 5 Bài 8 trên Nokia 6.1: fixture mang tiêu đề **đúng chính tả**
/// «Đấu tranh giành độc lập thời kì **B**ắc thuộc» — `lesson-title-v1` lấy
/// nguyên từ mục lục in — còn màn hình hiện «thời kì **b**ắc thuộc».
/// **Lỗi HIỂN THỊ, không phải lỗi dữ liệu**, và **không một test nào bắt được**:
/// một người cầm máy thật đọc ra.
///
/// VÌ SAO KHÔNG TEST NÀO BẮT ĐƯỢC. Test cũ của `titleCase` chỉ nạp chuỗi IN
/// HOA («HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP»), tức **chỉ nạp đúng cái tiền đề
/// mà phép biến đổi giả định**. Một hàm hạ-chữ-thường-toàn-chuỗi luôn xanh khi
/// đầu vào vốn đã không có chữ thường nào để phá. Đây là **lỗi chọn quần thể
/// thử**, cùng hạng với hai holdout vòng 6 «đo nhầm quần thể»: không phải test
/// yếu, mà là test chưa bao giờ được cho ăn dữ liệu có thể làm nó đỏ.
///
/// TEST NÀY CÓ BẮT ĐƯỢC KHÔNG? **Có** — và đó là điều kiện để nó tồn tại. Nó
/// nạp đúng chuỗi tiêu đề thật (hằng số dưới đây, sao nguyên văn từ fixture) và
/// đọc **chữ đã render trên màn**, không phải giá trị hàm. Bất biến nó ghim
/// không phải «hàm trả về chuỗi X» mà **«mọi chữ hoa của sách còn nguyên trên
/// màn»** — nên nó vẫn đỏ nếu ai đó đổi cách viết hoa theo một kiểu khác.
///
/// ĐIỀU NÓ **KHÔNG** BẮT ĐƯỢC, NÓI THẲNG: tiêu đề **thật sự IN HOA** ở nguồn
/// («THỜI KĨ BẮC THUỘC» — chính là tiêu đề pipeline của bài này) đã mất thông
/// tin hoa/thường **trước khi tới app**. Không test hiển thị nào chữa được;
/// xem `displayTitle` và `docs/research/ROUND6-DEBT-TRIAGE.md` mục R-3.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/display/lesson_title.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

/// Nguyên văn tiêu đề Golden #1, `titleDerivation.source = 'toc'`. Hằng ở đây
/// để test chạy được trên clone sạch: `assets/fixtures/real/` là gitignore.
const goldenTitle = 'Đấu tranh giành độc lập thời kì Bắc thuộc';

/// Mọi chữ hoa của chuỗi nguồn, theo thứ tự — bất biến mà màn phải giữ.
List<String> _uppers(String s) =>
    s.split('').where((c) => c != c.toLowerCase() && c == c.toUpperCase()).toList();

LessonDocument _docWithTitle(String title) {
  final j = (jsonDecode(File(syntheticPath).readAsStringSync()) as Map)
      .cast<String, Object?>();
  j['title'] = title;
  final d = LessonDocument.fromJson(j, assetBase: FixtureSlot.syntheticDir);
  if (d == null) throw StateError('fixture mẫu không parse được');
  return d;
}

void main() {
  group('displayTitle — sửa TIỀN ĐỀ, không nới cổng', () {
    test('tiêu đề ĐÃ có chữ thường được giữ NGUYÊN TỪNG KÝ TỰ', () {
      expect(displayTitle(goldenTitle), goldenTitle);
      // và cụ thể là danh từ riêng lịch sử
      expect(displayTitle(goldenTitle), contains('Bắc thuộc'));
      expect(displayTitle(goldenTitle), isNot(contains('bắc thuộc')));
    });

    test('tiêu đề IN HOA vẫn được viết hoa lại như vòng 3–6 (Nokia n1 D1)', () {
      expect(
        displayTitle('HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP'),
        'Hỗn hợp. Tách chất ra khỏi hỗn hợp',
      );
      expect(displayTitle('TÁCH CHẤT KHỎI HỖN HỢP'), 'Tách chất khỏi hỗn hợp');
      expect(displayTitle(''), '');
    });

    test('GIỚI HẠN ĐÃ BIẾT, ghim để không ai tưởng đã chữa: nguồn IN HOA thì '
        'danh từ riêng KHÔNG khôi phục được', () {
      // Thông tin hoa/thường đã mất ở NGUỒN. Ghim sự thật ấy, đừng che nó.
      expect(displayTitle('THỜI KĨ BẮC THUỘC'), 'Thời kĩ bắc thuộc');
    });

    test('không ký tự nào bị bịa: độ dài và chuỗi chữ-thường luôn bằng nguồn', () {
      for (final s in [
        goldenTitle,
        'HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP',
        'Ngô Quyền và chiến thắng Bạch Đằng năm 938',
        'Bài học 1. Em và bạn bè',
      ]) {
        expect(displayTitle(s).length, s.length, reason: s);
        expect(displayTitle(s).toLowerCase(), s.toLowerCase(), reason: s);
      }
    });
  });

  group('trên MÀN — chữ trẻ đọc, không phải giá trị hàm', () {
    setUp(WorkspaceTrace.session.reset);

    testWidgets('tiêu đề bài giữ nguyên mọi chữ hoa của sách', (t) async {
      final doc = _docWithTitle(goldenTitle);
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(doc: doc, trace: WorkspaceTrace.session),
        ),
      );
      await t.pumpAndSettle();

      final header = find.textContaining('Bài ${doc.lessonNo} ·');
      expect(header, findsWidgets);
      final shown = (t.widget<Text>(header.first)).data!;
      expect(
        _uppers(shown.split('·').last),
        _uppers(goldenTitle),
        reason: 'mọi chữ hoa của sách phải còn trên màn: $shown',
      );
      expect(shown, contains('Bắc thuộc'));
      expect(shown, isNot(contains('bắc thuộc')));
    });
  });

  group('MỘT luật duy nhất — có test soi mã', () {
    test('không tệp nào ngoài lib/core/lesson_model/ gọi thẳng '
        'LessonDocument.titleCase', () {
      // Vòng 6 có BẢY chỗ hiển thị tiêu đề: SÁU gọi thẳng `titleCase` (hạ chữ
      // vô điều kiện) và MỘT (`source_sheet._humanCase`) kiểm `s ==
      // s.toUpperCase()` trước. Luật đúng đã tồn tại trong repo và ở sai chỗ.
      // Hai luật cho một câu hỏi là cách lỗi này quay lại.
      final offenders = <String>[];
      for (final f in Directory('lib').listSync(recursive: true)) {
        if (f is! File || !f.path.endsWith('.dart')) continue;
        if (f.path.startsWith('lib/core/lesson_model/')) continue;
        if (f.path.endsWith('lib/core/display/lesson_title.dart')) continue;
        if (f.readAsStringSync().contains('titleCase(')) offenders.add(f.path);
      }
      expect(
        offenders,
        isEmpty,
        reason: 'dùng displayTitle() — xem lib/core/display/lesson_title.dart',
      );
    });
  });
}
