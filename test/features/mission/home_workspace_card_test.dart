/// ROUND 3 B1 — Home nhìn thấy sản phẩm: bài có Lesson Workspace hiện thành
/// thẻ; không có bài ⇒ không có thẻ; nhãn thử nghiệm bắt buộc; lối vào Môn học
/// (hợp đồng G2 của Track A) không bị nuốt.
///
/// ⭐⭐ ROUND 7 · V2 (Founder order 50) — SỬA TIỀN ĐỀ, KHÔNG NỚI KỲ VỌNG.
/// «Thẻ Bài học SAM» của vòng trước là một MEGA-CARD chiếm gần hết màn đầu.
/// Founder đã bác nó (§7). Cùng những sự thật ấy nay nằm ở hai chỗ có tên:
/// Smart Card của hàng «HÔM NAY» (MÔN · BÀI · TRẠNG THÁI · VIỆC TIẾP THEO) và
/// thẻ «SAM GỢI Ý» (tên bài · nguồn · lời SAM · nút). Mỗi kỳ vọng dưới đây
/// vẫn đòi một chuỗi CỤ THỂ — chỉ đổi chỗ nó phải xuất hiện.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/fixture_chip.dart';
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

void main() {
// ⭐ ROUND 7 · WS-S — QUYẾT ĐỊNH CỦA FOUNDER: tiêu đề hiển thị NGUYÊN VĂN NGUỒN.
// Các kỳ vọng dưới đây từng ghim chuỗi ĐÃ ĐƯỢC HẠ CHỮ; nay chúng ghim đúng chuỗi
// mà fixture của chính test này mang. Sửa TIỀN ĐỀ, không nới assertion: mỗi kỳ
// vọng vẫn đòi một chuỗi CỤ THỂ, chỉ là chuỗi thật thay vì chuỗi biến đổi.

  testWidgets('⭐ có bài workspace ⇒ Smart Card «HÔM NAY» + thẻ «SAM GỢI Ý» với '
      'tên bài, chương, trang, nhãn nguồn; nút trả đúng tài liệu', (
    t,
  ) async {
    final doc = loadSyntheticDoc();
    LessonDocument? opened;
    // ROUND 4: hai thẻ xếp dọc — màn cao để ListView dựng cả hai.
    t.view.physicalSize = const Size(1080, 5000);
    t.view.devicePixelRatio = 2.75;
    addTearDown(t.view.reset);
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          learnerGrade: 6,
          // ⭐ VIỆC TIẾP THEO đến từ ĐỘNG CƠ DUY NHẤT — không truyền nó thì
          // Home KHÔNG có gì để đưa lên «SAM GỢI Ý» và rơi về thẻ đề xuất cũ
          // (fail-closed có chủ ý: Home không tự nghĩ ra một đề xuất).
          lessonThreads: [
            HomeLessonThread(doc: doc, next: founderNextAction(doc, seen: const {})),
          ],
          onOpenWorkspaceLesson: (d, {at}) => opened = d,
        ),
      ),
    );
    await t.pumpAndSettle();
    // TẦNG 1 — Smart Card của chính bài này, khoá theo slot (không còn một
    // «thẻ bài học» duy nhất của cả màn).
    expect(
      find.byKey(MissionCenterScreen.smartCardKey(doc.slotKey)),
      findsOneWidget,
    );
    // Trạng thái là TỪ VỰNG Founder, và nó nói đúng sự thật: chưa mở gì.
    expect(find.text('CHƯA BẮT ĐẦU'), findsOneWidget);
    // TẦNG 2 — nhãn nguồn thành chip gọn, cùng widget và cùng bộ chữ với
    // workspace. Nó KHÔNG được mất khi màn sắp lại.
    expect(find.byKey(MissionCenterScreen.samSuggestionKey), findsOneWidget);
    expect(
      find.descendant(
        of: find.byKey(MissionCenterScreen.samSuggestionKey),
        matching: find.byKey(FixtureChip.chipKey),
      ),
      findsOneWidget,
    );
    final inCard = find.descendant(
      of: find.byKey(MissionCenterScreen.samSuggestionKey),
      matching: find.textContaining('Bài 17 · TÁCH CHẤT'),
    );
    expect(inCard, findsOneWidget);
    expect(find.textContaining('Chương IV'), findsOneWidget);
    expect(find.textContaining('trang 60–63'), findsOneWidget);
    // ROUND 7 V1: ba cách học không còn là MỘT DÒNG CHỮ trong thẻ — mỗi cách
    // còn lại là một nút bấm được ở hàng «CÓ THỂ LÀM TIẾP».
    expect(find.byKey(MissionCenterScreen.continueRowKey), findsOneWidget);
    expect(find.textContaining('Học với SAM'), findsWidgets);
    // Lối vào Môn học (G2 của Track A) vẫn còn — ROUND 7 V2: dưới nhãn «CÁC
    // MÔN CỦA CON», nút VIỀN, không tranh CTA với «SAM GỢI Ý».
    expect(find.byKey(MissionCenterScreen.secondaryCardKey), findsOneWidget);
    expect(find.text('CÁC MÔN CỦA CON'), findsOneWidget);
    expect(find.text('Vào Môn học ▸'), findsOneWidget);
    // Nhãn nút là NGUYÊN VĂN nhãn của động cơ (R2 ⇒ «📖 Đọc»), không phải một
    // chuỗi Home tự đặt.
    await t.ensureVisible(find.text('📖 Đọc ▸'));
    await t.pumpAndSettle();
    await t.tap(find.text('📖 Đọc ▸'));
    expect(opened?.slotKey, doc.slotKey);
  });

  testWidgets('không có bài workspace ⇒ không có thẻ (không bịa)', (t) async {
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(data: await _data(), onOpenSubjects: () {}),
      ),
    );
    await t.pumpAndSettle();
    expect(find.byKey(MissionCenterScreen.todayRowKey), findsNothing);
    expect(find.textContaining('BÀI HỌC SAM'), findsNothing);
    expect(find.textContaining('Bài 17'), findsNothing);
  });

  testWidgets('thẻ không có %, sao, «đã học»', (t) async {
    await t.pumpWidget(
      fixtureHost(
        MissionCenterScreen(
          data: await _data(),
          onOpenSubjects: () {},
          learnerGrade: 6,
          lessonThreads: [
            HomeLessonThread(
              doc: loadSyntheticDoc(),
              next: founderNextAction(loadSyntheticDoc(), seen: const {}),
            ),
          ],
          onOpenWorkspaceLesson: (_, {at}) {},
        ),
      ),
    );
    await t.pumpAndSettle();
    final card = find.descendant(
      of: find.byKey(MissionCenterScreen.samSuggestionKey),
      matching: find.byType(Text),
    );
    for (final e in card.evaluate()) {
      final s = ((e.widget as Text).data ?? '').toLowerCase();
      expect(s, isNot(contains('%')));
      expect(s, isNot(contains('★')));
      expect(s, isNot(contains('đã học')));
    }
  });
}
