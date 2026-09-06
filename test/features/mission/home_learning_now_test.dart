/// ROUND 7 · V1 — MÀN ĐẦU TRẢ LỜI BA CÂU (Founder order 48 «HOME — AI FIRST»,
/// order 49 §1).
///
/// Máy thật vòng 7 lượt 1 (`round7-r1-device-walk/02-home.png`): lời chào →
/// SAM nhắc LẠI tên bài → năm chip chung chung chiếm một phần ba màn → nhãn
/// HÔM NAY → thẻ bài → nút «Mở bài học» RƠI XUỐNG DƯỚI NẾP GẤP. Không có gì
/// nói con đang học tới đâu.
///
/// Bài kiểm này giữ bốn điều, và ba trong bốn là điều Founder gọi tên:
///
/// 1. ĐANG HỌC GÌ + VIỆC TIẾP THEO ở màn đầu, nút đứng TRÊN mọi thứ phụ.
/// 2. «SAM thấy gì» là HỖ TRỢ — nó không được đứng trên Next Action.
/// 3. Tiến độ là BẰNG CHỨNG MỞ: không %, không sao, không «đã thạo»,
///    không «đã học». Số vạch = số cách học bài NÀY có, không phải 3 cố định.
/// 4. Home không có động cơ đề xuất thứ hai: nhãn nút đến từ `lessonNext`.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';
import 'package:learning_coach/features/mission/mission_center_screen.dart';
import 'package:learning_coach/features/mission/mission_data.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import '../lesson_workspace/support.dart';

const _g6 = LearnerProfile(learnerId: 'l6', displayName: 'Na', grade: 6);
const _book = '06-sgk-khoa-hoc-tu-nhien-6';

LessonIndex _khtn6() => LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"KHTN":[{"sourceDocumentId":"$_book","volume":null,
   "lessons":[{"no":17,"title":"Tách chất khỏi hỗn hợp","pageStart":60}]}]}}
''')!;

Future<MissionData> _data() => buildMissionFromStore(
  profile: _g6,
  store: JsonlLearnerStore(),
  now: DateTime(2026, 9, 6, 19),
  index: _khtn6(),
);

Future<void> _pump(
  WidgetTester t, {
  Set<WorkspaceView> opened = const {},
  LessonDocument? doc,
  void Function(LessonDocument)? onOpen,
}) async {
  final d = doc ?? loadSyntheticDoc();
  await t.pumpWidget(
    fixtureHost(
      MissionCenterScreen(
        data: await _data(),
        onOpenSubjects: () {},
        workspaceLesson: d,
        onOpenWorkspaceLesson: onOpen ?? (_) {},
        openedViews: opened,
        lessonNext: founderNextAction(d, seen: opened),
      ),
    ),
  );
  await t.pumpAndSettle();
}

void main() {
  testWidgets('⭐⭐ 1. màn đầu: ĐANG HỌC + VIỆC TIẾP THEO, nút TRÊN mọi thứ phụ',
      (t) async {
    await _pump(t);
    double y(Finder f) => t.getTopLeft(f).dy;
    final card = find.byKey(MissionCenterScreen.workspaceCardKey);
    final cta = find.byKey(MissionCenterScreen.nextActionCtaKey);
    expect(card, findsOneWidget);
    expect(cta, findsOneWidget);
    // «đang học gì»: tên bài + sách/trang, trong thẻ
    expect(
      find.descendant(of: card, matching: find.textContaining('Bài 17')),
      findsOneWidget,
    );
    expect(find.textContaining('trang 60–63'), findsOneWidget);
    // nút việc-tiếp-theo đứng trên hàng «có thể làm tiếp», trên «SAM thấy gì»,
    // và trên cả 5 chip chung chung.
    expect(y(cta), lessThan(y(find.byKey(MissionCenterScreen.continueRowKey))));
    expect(y(cta), lessThan(y(find.byKey(MissionCenterScreen.samSeenKey))));
    // ⭐ NÚT PHẢI Ở TRONG MÀN ĐẦU — đây chính là lỗi máy thật vòng 1.
    expect(
      y(cta) + 48,
      lessThan(t.view.physicalSize.height / t.view.devicePixelRatio),
      reason: 'CTA rơi xuống dưới nếp gấp — lỗi 02-home.png',
    );
  });

  testWidgets('⭐ 2. «SAM thấy gì» là HỖ TRỢ: nhỏ hơn, đứng SAU Next Action, '
      'không có nút riêng', (t) async {
    await _pump(t, opened: {WorkspaceView.read, WorkspaceView.visual});
    final seen = find.byKey(MissionCenterScreen.samSeenKey);
    expect(seen, findsOneWidget);
    expect(
      t.getTopLeft(find.byKey(MissionCenterScreen.nextActionCtaKey)).dy,
      lessThan(t.getTopLeft(seen).dy),
    );
    // không có nút nào trong thẻ hỗ trợ — nó không tranh hành động
    expect(
      find.descendant(of: seen, matching: find.byType(ButtonStyleButton)),
      findsNothing,
    );
    final text = t
        .widgetList<Text>(find.descendant(of: seen, matching: find.byType(Text)))
        .map((w) => w.data ?? '')
        .join(' ');
    expect(text, contains('Con đã mở 2 trong 3 cách học'));
    expect(text, contains('mở bài không phải là hiểu bài'));
  });

  testWidgets('⭐⭐ 3. tiến độ là BẰNG CHỨNG MỞ — không %, sao, «đã thạo», '
      '«đã học»', (t) async {
    await _pump(t, opened: {WorkspaceView.read});
    final bar = find.byKey(MissionCenterScreen.progressKey);
    expect(bar, findsOneWidget);
    expect(
      find.descendant(of: bar, matching: find.text('đã mở 1/3 cách học')),
      findsOneWidget,
    );
    // quét CẢ MÀN: không chữ nào hứa mastery
    final all = t
        .widgetList<Text>(find.byType(Text))
        .map((w) => (w.data ?? '').toLowerCase())
        .join(' | ');
    for (final banned in [
      '%',
      'đã thạo',
      'thành thạo',
      'hoàn thành bài',
      'điểm số',
      '⭐',
      '★',
    ]) {
      expect(all, isNot(contains(banned)), reason: 'Home hứa mastery: $banned');
    }
  });

  testWidgets('⭐ 3b. số vạch = số cách học bài NÀY có, không phải 3 cố định', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    // Bài chỉ có phần đọc: không sơ đồ, không kịch bản.
    final readOnly = LessonDocument(
      schema: d.schema,
      book: d.book,
      bookTitle: d.bookTitle,
      subject: d.subject,
      grade: d.grade,
      lessonNo: d.lessonNo,
      title: d.title,
      provenance: d.provenance,
      blocks: d.blocks,
      evidencePolicy: EvidencePolicy.none,
    );
    await _pump(t, doc: readOnly);
    expect(find.textContaining('đã mở 0/1 cách học'), findsOneWidget);
    // và KHÔNG mời trẻ đi tìm hai cách học bài này không có
    expect(find.byKey(MissionCenterScreen.continueRowKey), findsNothing);
  });

  testWidgets('⭐⭐ 4. nhãn nút đến từ ĐỘNG CƠ, không phải luật riêng của Home',
      (t) async {
    // chưa mở gì ⇒ R2 (Đọc)
    await _pump(t);
    expect(find.textContaining('📖 Đọc'), findsWidgets);
    final cta = find.descendant(
      of: find.byKey(MissionCenterScreen.nextActionCtaKey),
      matching: find.byType(Text),
    );
    expect(t.widget<Text>(cta).data, '📖 Đọc ▸');

    // đã mở Đọc + Trực quan ⇒ R4 (Học với SAM)
    await _pump(t, opened: {WorkspaceView.read, WorkspaceView.visual});
    expect(t.widget<Text>(cta).data, '🦉 Học với SAM ▸');

    // đã mở hết ⇒ R5 «ở lại bài», KHÔNG bảo trẻ rời bài
    await _pump(
      t,
      opened: {
        WorkspaceView.read,
        WorkspaceView.visual,
        WorkspaceView.tutor,
      },
    );
    expect(t.widget<Text>(cta).data, 'Xem tiếp bài này ▸');
    expect(find.textContaining('về mục lục'), findsNothing);
  });

  testWidgets('lý do SAM nói trên Home là NGUYÊN VĂN lý do của động cơ', (
    t,
  ) async {
    final d = loadSyntheticDoc();
    const opened = {WorkspaceView.read};
    await _pump(t, opened: opened);
    final expected = founderNextAction(d, seen: opened).reason;
    final why = t.widget<Text>(find.byKey(const Key('home-workspace-why')));
    expect(why.data, expected, reason: 'Home không được viết lại lời động cơ');
  });

  testWidgets('«CÓ THỂ LÀM TIẾP» chỉ nêu cách học bài NÀY có, và không lặp '
      'cách SAM đang đề xuất', (t) async {
    await _pump(t);
    // đề xuất là Đọc ⇒ hàng còn lại là Trực quan + Học với SAM
    expect(
      find.byKey(MissionCenterScreen.continueChipKey(WorkspaceView.read)),
      findsNothing,
    );
    expect(
      find.byKey(MissionCenterScreen.continueChipKey(WorkspaceView.visual)),
      findsOneWidget,
    );
    expect(
      find.byKey(MissionCenterScreen.continueChipKey(WorkspaceView.tutor)),
      findsOneWidget,
    );
  });

  testWidgets('chạm nút việc-tiếp-theo mở ĐÚNG tài liệu bài', (t) async {
    LessonDocument? opened;
    await _pump(t, onOpen: (d) => opened = d);
    await t.tap(find.byKey(MissionCenterScreen.nextActionCtaKey));
    expect(opened?.slotKey, loadSyntheticDoc().slotKey);
  });

  testWidgets('nhãn «BẢN THỬ NGHIỆM» không mất khi màn được sắp lại', (t) async {
    await _pump(t);
    expect(find.textContaining('BẢN THỬ NGHIỆM'), findsWidgets);
  });
}
