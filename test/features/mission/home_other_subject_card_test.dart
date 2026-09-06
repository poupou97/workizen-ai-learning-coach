/// ⭐⭐ FOUNDER ORDER 50 §6 — «KHÔNG ĐẨY MÔN KHÁC THÀNH SÁCH KHÁC».
///
/// Tệp này TRƯỚC ĐÂY tên là `home_research_card_test.dart` và nó KHOÁ đúng
/// thứ Founder vừa bác bỏ. Nó đòi cho bằng được rằng LS&ĐL 5 · Bài 8 phải:
///
/// - đứng dưới một nhãn khu riêng **«SAM ĐANG TẬP ĐỌC SÁCH KHÁC»**;
/// - mang eyebrow **«LÁT CẮT NGHIÊN CỨU · SÁCH LỚP 5 · BẢN THỬ NGHIỆM»**;
/// - đi kèm một dòng bắt đầu bằng «Đây không phải bài của lớp con — SAM đang
///   **tập đọc thử một cuốn sách khác**. Con xem cho biết cũng được.»
///
/// Founder, sau khi cầm máy: «Điều này làm nó giống nội dung phụ/research.
/// Nếu đó là một lesson có thể mở, hãy trình bày như: MỘT MÔN / BÀI HỌC KHÁC
/// với trạng thái truth thích hợp.»
///
/// Nên bài kiểm đổi TIỀN ĐỀ, không nới kỳ vọng. Sự thật phải nói vẫn phải
/// nói — **đây là sách LỚP 5, không phải sách lớp con** — nhưng nó nói ở
/// đúng nơi của một bài học: **trên chính thẻ học của nó**, trong cùng hàng
/// «HÔM NAY» với bài của lớp con. Mỗi kỳ vọng dưới đây vẫn đòi một chuỗi CỤ
/// THỂ; và ba chuỗi cũ ở trên nay bị cấm bằng tên.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';

import '../lesson_workspace/support.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);

Future<MissionData> _data() => buildMissionFromStore(
  profile: _g6,
  store: JsonlLearnerStore(),
  now: DateTime(2026, 9, 5, 19),
);

LessonDocument _history() {
  final j = jsonDecode(
    File('assets/fixtures/synthetic/lesson-05-sgk-lich-su-va-dia-li-5-b8.synthetic.json')
        .readAsStringSync(),
  ) as Map;
  return LessonDocument.fromJson(
    j.cast<String, Object?>(),
    assetBase: FixtureSlot.syntheticDir,
  )!;
}

/// Một mạch học chưa mở cách nào, việc tiếp theo do ĐỘNG CƠ DUY NHẤT sinh.
HomeLessonThread _thread(LessonDocument d) =>
    HomeLessonThread(doc: d, next: founderNextAction(d, seen: const {}));

Future<void> _pump(
  WidgetTester t, {
  required List<LessonDocument> docs,
  void Function(LessonDocument)? onOpen,
}) async {
  t.view.physicalSize = const Size(1080, 5000);
  t.view.devicePixelRatio = 2.75;
  addTearDown(t.view.reset);
  await t.pumpWidget(
    fixtureHost(
      MissionCenterScreen(
        data: await _data(),
        learnerGrade: 6,
        onOpenSubjects: () {},
        lessonThreads: [for (final d in docs) _thread(d)],
        onOpenWorkspaceLesson: (d, {at}) => onOpen?.call(d),
      ),
    ),
  );
  await t.pumpAndSettle();
}

void main() {
  testWidgets('⭐⭐ bài của lớp KHÁC là MỘT THẺ HỌC trong cùng hàng «HÔM NAY» — '
      'không còn khu «lát cắt nghiên cứu» riêng', (t) async {
    final b17 = loadSyntheticDoc();
    final b8 = _history();
    expect(WorkspaceCatalog.isResearchSlot(b8), isTrue);
    expect(WorkspaceCatalog.isResearchSlot(b17), isFalse);

    LessonDocument? opened;
    await _pump(t, docs: [b17, b8], onOpen: (d) => opened = d);

    // ① Cả hai bài đều là thẻ của hàng «HÔM NAY», cùng một loại khoá.
    expect(find.byKey(MissionCenterScreen.todayRowKey), findsOneWidget);
    expect(
      find.byKey(MissionCenterScreen.smartCardKey(b17.slotKey)),
      findsOneWidget,
    );
    expect(
      find.byKey(MissionCenterScreen.smartCardKey(b8.slotKey)),
      findsOneWidget,
    );

    // ② ⛔ Ba chuỗi Founder bác bỏ KHÔNG được quay lại — bằng tên.
    expect(find.textContaining('SAM ĐANG TẬP ĐỌC SÁCH KHÁC'), findsNothing);
    expect(find.textContaining('LÁT CẮT NGHIÊN CỨU'), findsNothing);
    final all = t
        .widgetList<Text>(find.byType(Text))
        .map((w) => w.data ?? '')
        .join(' | ');
    expect(all, isNot(contains('tập đọc thử một cuốn sách khác')));
    expect(all, isNot(contains('Con xem cho biết cũng được')));

    // ③ Nhưng SỰ THẬT VẪN PHẢI NÓI — và nó nói trên chính thẻ ấy, bằng lời
    //    trẻ, không mã máy, không %.
    final note = find.descendant(
      of: find.byKey(MissionCenterScreen.smartCardKey(b8.slotKey)),
      matching: find.text('Sách lớp 5 · không phải sách lớp con'),
    );
    expect(note, findsOneWidget);
    final noteText = t.widget<Text>(note).data!;
    expect(noteText, isNot(contains('%')));
    expect(noteText, isNot(matches(RegExp(r'[a-z]+-[a-z]+-v\d'))));

    // ④ Thẻ của lớp con KHÔNG mang dòng ấy.
    expect(
      find.descendant(
        of: find.byKey(MissionCenterScreen.smartCardKey(b17.slotKey)),
        matching: find.textContaining('không phải sách lớp con'),
      ),
      findsNothing,
    );

    // ⑤ TRƯỢT sang thẻ 2 rồi chạm ⇒ mở ĐÚNG tài liệu ấy. Đây chính là bước
    //    «swipe sang card 2 · chuyển sang một môn khác» của order 50 §10, đo
    //    bằng cử chỉ thật chứ không phải bằng gọi callback.
    await t.drag(
      find.byKey(MissionCenterScreen.todayRowKey),
      const Offset(-400, 0),
    );
    await t.pumpAndSettle();
    await t.tap(find.byKey(MissionCenterScreen.smartCardKey(b8.slotKey)));
    await t.pumpAndSettle();
    expect(opened?.slotKey, b8.slotKey);
  });

  testWidgets('⭐⭐ SÁCH LỚP KHÁC KHÔNG BAO GIỜ thành việc hôm nay: «SAM GỢI Ý» '
      'chọn bài của ĐÚNG LỚP con, kể cả khi bài lớp khác đứng trước', (t) async {
    final b17 = loadSyntheticDoc();
    final b8 = _history();
    // Cố ý ĐẢO thứ tự: nếu luật chọn chỉ là «thẻ đầu tiên» thì bài lớp 5 sẽ
    // thắng — đó là điều bậc «đúng lớp» tồn tại để chặn.
    await _pump(t, docs: [b8, b17]);
    final cta = find.descendant(
      of: find.byKey(MissionCenterScreen.nextActionCtaKey),
      matching: find.byType(Text),
    );
    expect(cta, findsOneWidget);
    final suggestion = find.byKey(MissionCenterScreen.samSuggestionKey);
    expect(
      find.descendant(of: suggestion, matching: find.textContaining('Bài 17')),
      findsOneWidget,
    );
    expect(
      find.descendant(of: suggestion, matching: find.textContaining('Bài 8')),
      findsNothing,
    );
  });

  testWidgets('chỉ có bài của lớp con ⇒ một thẻ, không có dòng «sách lớp»',
      (t) async {
    await _pump(t, docs: [loadSyntheticDoc()]);
    expect(find.textContaining('không phải sách lớp con'), findsNothing);
    expect(find.textContaining('LÁT CẮT NGHIÊN CỨU'), findsNothing);
  });
}
