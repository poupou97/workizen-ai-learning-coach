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

    // ⭐⭐ ROUND 7 · WS-S — HAI TEST DƯỚI ĐÂY BỊ ĐẢO CHIỀU BỞI QUYẾT ĐỊNH CỦA
    // FOUNDER, và cả hai được sửa TIỀN ĐỀ chứ không bị xoá: chúng vẫn ghim đúng
    // hai sự thật, chỉ khác kết luận.
    test('⭐ tiêu đề IN HOA cũng giữ NGUYÊN VĂN (đảo chiều hành vi vòng 3–6)', () {
      // Vòng 3–6 trả «Hỗn hợp. Tách chất ra khỏi hỗn hợp». Phép ấy an toàn với
      // ĐÚNG chuỗi này và phá tên riêng ở 107 chuỗi khác của cùng pack, nên nó
      // không còn chạy. Cái giá được ghim ở đây, không giấu: màn hình hiện IN
      // HOA.
      expect(displayTitle('HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP'),
          'HỖN HỢP. TÁCH CHẤT RA KHỎI HỖN HỢP');
      expect(displayTitle('TÁCH CHẤT KHỎI HỖN HỢP'), 'TÁCH CHẤT KHỎI HỖN HỢP');
      expect(displayTitle(''), '');
    });

    test('GIỚI HẠN ĐÃ BIẾT, ghim để không ai tưởng đã chữa: nguồn IN HOA thì '
        'danh từ riêng KHÔNG khôi phục được', () {
      // Thông tin hoa/thường đã mất ở NGUỒN, và **hiển thị không chữa được dữ
      // liệu**. Vòng 6 trả «Thời kĩ bắc thuộc» — sai tên riêng. Vòng 7 trả
      // nguyên văn IN HOA — vẫn KHÔNG khôi phục «Bắc thuộc», chỉ thôi khẳng
      // định một cách viết sai. Đường chữa duy nhất là DỮ LIỆU: `lesson-title-v1`
      // lấy tên từ mục lục in.
      expect(displayTitle('THỜI KĨ BẮC THUỘC'), 'THỜI KĨ BẮC THUỘC');
      expect(displayTitle('THỜI KĨ BẮC THUỘC'), isNot(contains('Bắc thuộc')),
          reason: 'không phép hiển thị nào khôi phục được hoa/thường đã mất');
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

  _acronyms();

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

/// ROUND 7 · WS-R — VIẾT TẮT KHÔNG PHẢI TIÊU ĐỀ BỊ HÉT.
///
/// Đo trên `assets/pack/lesson-index-*.json` đang phát hành: 175 trên 2 623
/// tiêu đề là IN HOA, và **67 trong số đó chỉ có MỘT từ có chữ cái** —
/// «GDTC 5», «GDKT&PL 10», «TN&XH 1». Luật cũ hạ chúng thành «Gdtc 5»: một
/// cái tên bị làm hỏng. Để nguyên thì chỉ hơi to tiếng.
void _acronyms() {
  group('viết tắt giữ nguyên', () {
    test('một từ in hoa ⇒ nguyên văn', () {
      for (final s in ['GDTC 5', 'GDKT&PL 10', 'TN&XH 1', 'KHTN', 'SGK']) {
        expect(displayTitle(s), s, reason: s);
      }
    });
    // ⭐ ROUND 7 · WS-S — TIỀN ĐỀ NÀY ĐÃ BỊ FOUNDER BÁC, và test được sửa chứ
    // không bị nới. Bản trước khẳng định «từ hai từ trở lên vẫn được viết hoa
    // lại» và tự viết ra bằng chứng chống lại chính nó ở dòng cuối:
    //     displayTitle('ĐẤT NƯỚC VÀ CON NGƯỜI VIỆT NAM')
    //         → 'Đất nước và con người việt nam'
    // — tên nước bị hạ chữ, ghim thành hành vi ĐÚNG. Quyết định vòng 7 là GIỮ
    // NGUYÊN VĂN NGUỒN: không chuẩn hoá khi phép biến đổi có thể làm hỏng một
    // danh từ riêng. Mức hỏng đo trên quần thể thật: 107/107.
    test('⭐⭐ IN HOA NHIỀU TỪ cũng giữ nguyên văn — 108 tiêu đề của pack', () {
      for (final s in const [
        'MỞ ĐẦU',
        'TẾ BÀO',
        'ĐẤT NƯỚC VÀ CON NGƯỜI VIỆT NAM',
        'ASEAN AND VIET NAM',
        'CHIẾN TRANH VÀ HOA BÌNH TRONG THẾ KỈ XX',
      ]) {
        expect(displayTitle(s), s, reason: s);
      }
      // và nói thẳng cái giá: «MỞ ĐẦU» vẫn hiện IN HOA trên màn. Đó là chốt an
      // toàn về độ trung thực, không phải UX cuối cùng — xem điều kiện bật ở
      // lib/core/display/lesson_title.dart.
      expect(displayTitle('MỞ ĐẦU'), isNot('Mở đầu'));
    });
  });
}
