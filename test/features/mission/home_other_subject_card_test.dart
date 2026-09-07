/// ⭐⭐ FOUNDER DECISION C-1 (lệnh 54) — HOME FAIL-CLOSED THEO LỚP.
///
/// Tệp này đã đổi tiền đề HAI LẦN, và lần nào cũng do Founder cầm máy rồi
/// chốt — ghi lại cả hai để không ai tưởng test bị nới:
///
/// 1. Ban đầu (`home_research_card_test.dart`) nó đòi LS&ĐL 5 phải đứng dưới
///    khu riêng «SAM ĐANG TẬP ĐỌC SÁCH KHÁC» kèm eyebrow «LÁT CẮT NGHIÊN
///    CỨU». Order 50 §6 bác: đừng đẩy môn khác thành «sách khác».
/// 2. Rồi nó đòi bài lớp khác phải là MỘT THẺ HỌC trong hàng «HÔM NAY», mang
///    nhãn «Sách lớp 5 · không phải sách lớp con». Lệnh 54 bác luôn cách ấy:
///
///    «Grade filtering phải xảy ra TRƯỚC ranking/recommendation, không phải
///     ranking xong rồi mới gắn nhãn cảnh báo.»
///
/// Nên hôm nay bài kiểm đòi điều NGƯỢC LẠI với bản trước: bài ngoài lớp
/// KHÔNG được có mặt trên Home. Nó vẫn tồn tại trong Giá sách / Bản đồ học
/// tập — nơi trẻ CHỦ ĐỘNG đi tới — nhưng không phải nơi SAM tự đưa ra.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/features/mission/home_cards.dart';

/// Bài LS&ĐL **lớp 5** (bản synthetic, có trong git).
LessonDocument _history5() {
  final j = jsonDecode(
    File(
      'assets/fixtures/synthetic/'
      'lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json',
    ).readAsStringSync(),
  ) as Map;
  return LessonDocument.fromJson(
    j.cast<String, Object?>(),
    assetBase: FixtureSlot.syntheticDir,
  )!;
}

void main() {
  test('⭐⭐ học sinh LỚP 6 KHÔNG nhận thẻ Home của bài LỚP 5', () {
    final d = _history5();
    expect(d.grade, 5, reason: 'mẫu thử phải là bài lớp 5');

    final row = buildHomeCards(
      threads: [HomeLessonThread(doc: d)],
      learnerGrade: 6,
    );

    expect(
      row.cards.where((c) => c.isRealLesson),
      isEmpty,
      reason: 'bài lớp 5 lọt vào Home của học sinh lớp 6',
    );
  });

  test('học sinh LỚP 5 thì CHÍNH bài ấy là thẻ của em', () {
    final d = _history5();
    final row = buildHomeCards(
      threads: [HomeLessonThread(doc: d)],
      learnerGrade: 5,
    );
    expect(row.cards.where((c) => c.isRealLesson), hasLength(1));
  });

  test('⛔ ba cách gọi tên CŨ đều đã biến mất khỏi mã nguồn', () {
    final src = [
      File('lib/features/mission/home_cards.dart').readAsStringSync(),
      File(
        'lib/features/mission/mission_center_screen.dart',
      ).readAsStringSync(),
      File('lib/main.dart').readAsStringSync(),
    ].join('\n');
    for (final banned in [
      'SAM ĐANG TẬP ĐỌC SÁCH KHÁC',
      'LÁT CẮT NGHIÊN CỨU',
      'tập đọc thử một cuốn sách khác',
      'không phải sách lớp con',
      'otherGradeNote',
    ]) {
      expect(
        src.contains(banned),
        isFalse,
        reason: '«$banned» vẫn còn — lệnh 54 bỏ hẳn đường gắn nhãn này',
      );
    }
  });
}
