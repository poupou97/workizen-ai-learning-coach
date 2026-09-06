/// ROUND 7 · WS-R — **MÂU THUẪN CỦA NEXT ACTION** (lỗi máy thật, vòng 6).
///
/// Trên Nokia 6.1, LS&ĐL 5 Bài 8: trẻ mở bài, chạm 📖 Đọc, và SAM nói
///
///     «Con đã đi qua các cách học của bài này … về mục lục chọn bài khác»
///
/// ngay phía trên hàng
///
///     «Đã mở: ● Đọc ○ Trực quan ○ Học với SAM»
///
/// **Hai câu ngược nhau trên một màn**, và câu trên bảo trẻ rời bài mình vừa
/// mở. Không test nào bắt được; một người cầm máy thật đọc ra.
///
/// HAI LỖI, MỘT MÀN — và cả hai đều là cùng một sai lầm: **coi dấu vết MỞ như
/// bằng chứng ĐÃ HỌC**, cộng với việc **liệt kê những cách học bài không có**.
///
/// 1. `viewsSeen` được đánh dấu ngay lúc mở tab (`WorkspaceTrace.markView`).
///    Bài này không có `SemanticData` và không có kịch bản, nên nó chỉ có MỘT
///    cách học; mở nó xong là `viewsSeen` phủ hết, R5 bắn, và R5 kết luận «đã
///    đi qua» rồi khuyên rời bài. `OPENED != UNDERSTOOD`.
/// 2. Hàng «Đã mở» duyệt `WorkspaceView.values` VÔ ĐIỀU KIỆN, nên nó vẽ «○»
///    cho hai cách học không tồn tại — mời trẻ đi tìm thứ không có, và cãi
///    lại câu ngay trên nó. Màn «Vào bài học» đã nói thật từ vòng 3 («Chưa có
///    sơ đồ cho bài này»); hàng này thì chưa.
///
/// TEST NÀO ĐÁNG LẼ BẮT ĐƯỢC? Test §6.7 vòng 4 ĐÃ ghim đúng chuỗi
/// «Đã mở: ● Đọc ○ Trực quan ○ Học với SAM» — nhưng nó chạy trên fixture MẪU,
/// bài CÓ ĐỦ cả ba cách học, nên chuỗi ấy đúng ở đó và mãi mãi xanh. Lỗi là
/// **quần thể thử**, không phải độ chặt: bài một-cách-học chưa bao giờ được
/// đưa vào test. Tệp này đưa vào.
///
/// BẤT BIẾN CẤU TRÚC (không phải kiểm chuỗi). Round 6 đã học rằng một canary
/// bắt từ khoá thì bắn nhầm vào chữ sách thật và không giữ gì. Nên điều được
/// ghim ở đây là: **SAM chỉ chủ động mời trẻ RỜI bài khi có bằng chứng đã
/// chấm** (`hasApprovedValidatedSuccess`, tức R1) — quét toàn bộ 8 tổ hợp
/// `viewsSeen` × 4 hình dạng bài × 4 vị thế bằng chứng.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/agenda/lesson_next_action.dart';
import 'package:learning_coach/core/context/learning_context.dart';
import 'package:learning_coach/core/curriculum/semantic_binding.dart';
import 'package:learning_coach/core/lesson_model/lesson_document.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart'
    show WorkspaceView;
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/student/evidence_validation.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/core/student/student_lesson_state.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/assist_layer.dart';
import 'package:learning_coach/features/lesson_workspace/widgets/runtime_plan.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';

import 'support.dart';

const _ref = LessonRef('05-sgk-lich-su-va-dia-li-5', 8);
const _ctx = LearningContext(
  learnerId: 'na',
  grade: 5,
  subject: 'LS&ĐL',
  sourceDocumentId: '05-sgk-lich-su-va-dia-li-5',
  lessonNo: 8,
);

/// Hình dạng của Golden #1 sau vòng 6: chữ đọc được, **không** sơ đồ,
/// **không** kịch bản — vì khối mang cả hai đang bị giữ lại.
const _oneWay = LessonSummary(
  lessonRef: _ref,
  hasReadableBlocks: true,
  hasSemanticData: false,
  hasTutorScript: false,
);

LessonNextAction _act({
  LessonSummary lesson = _oneWay,
  Set<WorkspaceView> seen = const {},
  StudentLessonState? state,
}) => nextBestLessonAction(
  state: state ?? StudentLessonState.unseen(_ref),
  context: _ctx,
  lesson: lesson,
  viewsSeen: seen,
);

LearningEvent _ev(EvidenceKind k, {bool? correct, EvidenceValidation? v}) =>
    LearningEvent(
      eventId: 'e-${k.name}-$correct-${v?.validatorId}',
      skillCaseId: 'lsdl5-b8-case',
      kind: k,
      correct: correct,
      at: DateTime(2026, 9, 6),
      sourceDocumentId: _ref.sourceDocumentId,
      lessonNo: 8,
      validation: v,
    );

/// Fixture MẪU với `semantic` và `tutorScript` bị lấy đi — đúng hình dạng
/// Golden #1 mà không cần `assets/fixtures/real/` (gitignore ⇒ clone sạch).
LessonDocument _oneWayDoc() {
  final j = (jsonDecode(File(syntheticPath).readAsStringSync()) as Map)
      .cast<String, Object?>();
  j['semantic'] = <Object?>[];
  j.remove('tutorScript');
  final d = LessonDocument.fromJson(j, assetBase: FixtureSlot.syntheticDir);
  if (d == null) throw StateError('fixture mẫu không parse được');
  return d;
}

void main() {
  group('LUẬT — bài chỉ có MỘT cách học', () {
    test('mở Đọc xong ⇒ Ở LẠI BÀI, và SAM nói bài chỉ có một cách học', () {
      final a = _act(seen: {WorkspaceView.read});
      expect(a.rule, 'R5');
      expect(a.kind, LessonNextKind.keepGoing);
      expect(a.label, 'Xem tiếp bài này');
      expect(a.reason, contains('chỉ có một cách học'));
      expect(a.reason, contains('Đọc'));
      expect(a.basis, contains('seen.allAvailable=1'));
    });

    test('KHÔNG câu nào bảo trẻ rời bài mình vừa mở', () {
      final a = _act(seen: {WorkspaceView.read});
      expect(a.reason, isNot(contains('về mục lục')));
      expect(a.reason, isNot(contains('bài khác')));
      expect(a.reason, isNot(contains('đi qua')));
    });

    test('chưa mở gì ⇒ vẫn là R2 «đọc bài trong sách»', () {
      expect(_act().rule, 'R2');
      expect(_act().view, WorkspaceView.read);
    });
  });

  group('BẤT BIẾN CẤU TRÚC — rời bài CHỈ khi đã có bằng chứng được chấm', () {
    const shapes = <String, LessonSummary>{
      'một cách (Golden #1)': _oneWay,
      'đọc + sơ đồ': LessonSummary(
        lessonRef: _ref,
        hasReadableBlocks: true,
        hasSemanticData: true,
        hasTutorScript: false,
      ),
      'đọc + kịch bản': LessonSummary(
        lessonRef: _ref,
        hasReadableBlocks: true,
        hasSemanticData: false,
        hasTutorScript: true,
      ),
      'đủ ba': LessonSummary(
        lessonRef: _ref,
        hasReadableBlocks: true,
        hasSemanticData: true,
        hasTutorScript: true,
      ),
    };

    test('không tổ hợp «đã mở» nào mở khoá lời khuyên rời bài', () {
      final states = <String, StudentLessonState>{
        'chưa học gì': StudentLessonState.unseen(_ref),
        'tự báo': StudentLessonState.fromEvents(_ref, [
          _ev(EvidenceKind.participation),
        ]),
        'xin gợi ý': StudentLessonState.fromEvents(_ref, [
          _ev(EvidenceKind.hintRequested),
        ]),
        'đúng nhưng KHÔNG dấu validator': StudentLessonState.fromEvents(_ref, [
          _ev(EvidenceKind.independentAttempt, correct: true),
        ]),
      };
      var checked = 0;
      for (final shape in shapes.entries) {
        for (final st in states.entries) {
          for (final seen in _subsets(WorkspaceView.values.toSet())) {
            final a = _act(lesson: shape.value, seen: seen, state: st.value);
            checked++;
            expect(
              a.kind,
              isNot(LessonNextKind.backToContents),
              reason: '${shape.key} / ${st.key} / $seen ⇒ ${a.rule} ${a.reason}',
            );
            expect(a.kind, isNot(LessonNextKind.nextLesson));
          }
        }
      }
      expect(checked, 4 * 4 * 8, reason: 'quét đủ mọi tổ hợp, không lấy mẫu');
    });

    test('CÓ dấu validator ⇒ R1 mới mời sang bài khác — đường DUY NHẤT', () {
      const v = EvidenceValidation(
        validatorId: 'fraction-check-v1',
        validatorVersion: '1',
      );
      final ok = StudentLessonState.fromEvents(_ref, [
        _ev(EvidenceKind.independentAttempt, correct: true, v: v),
      ]);
      for (final seen in _subsets(WorkspaceView.values.toSet())) {
        final a = _act(seen: seen, state: ok);
        expect(a.rule, 'R1');
        expect(a.kind, LessonNextKind.backToContents);
      }
    });

    test('bài KHÔNG đọc được gì vẫn nói thật và vẫn trả trẻ về SGK', () {
      // Ở lại một bài trống không giúp được ai — đây là kết cục «rời bài»
      // đúng, và nó không dựa vào dấu vết mở tab nào cả.
      const empty = LessonSummary(
        lessonRef: _ref,
        hasReadableBlocks: false,
        hasSemanticData: false,
        hasTutorScript: false,
      );
      final a = _act(lesson: empty);
      expect(a.kind, LessonNextKind.backToContents);
      expect(a.reason, contains('chưa đọc được phần nào'));
    });
  });

  group('TRÊN MÀN — hai dòng phải NÓI CÙNG MỘT ĐIỀU', () {
    setUp(WorkspaceTrace.session.reset);

    testWidgets('hàng «Đã mở» không chào mời cách học bài này không có', (
      t,
    ) async {
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      final doc = _oneWayDoc();
      expect(availableViewsOf(doc), [WorkspaceView.read]);
      final trace = WorkspaceTrace();
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: doc,
            trace: trace,
            initialView: WorkspaceView.read,
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();

      final row = t.widget<Text>(find.byKey(AssistPeek.seenKey)).data!;
      // ⭐ ĐÚNG CHUỖI trẻ thấy trên máy — chỗ mâu thuẫn được sinh ra.
      expect(row, startsWith('Đã mở: ● Đọc'));
      expect(row, isNot(contains('○')), reason: 'không có gì để mở thêm');
      expect(row, contains('Bài này chưa có Trực quan, Học với SAM'));

      // và số chấm phải ĐÚNG BẰNG số cách học bài này có — kiểm ĐẾM, không
      // kiểm từ khoá (round 6: canary từ khoá bắn nhầm vào chữ sách thật).
      final marks = '●○'.split('').fold<int>(
        0,
        (n, c) => n + c.allMatches(row).length,
      );
      expect(marks, availableViewsOf(doc).length);
    });

    testWidgets('SAM KHÔNG bảo trẻ rời bài mình vừa mở', (t) async {
      t.view.physicalSize = const Size(1080, 1920);
      t.view.devicePixelRatio = 2.75;
      addTearDown(t.view.reset);
      final doc = _oneWayDoc();
      await t.pumpWidget(
        fixtureHost(
          LessonWorkspaceScreen(
            doc: doc,
            trace: WorkspaceTrace(),
            initialView: WorkspaceView.read,
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.text('SAM gợi ý: Về mục lục'), findsNothing);
      expect(find.text('SAM gợi ý: Xem tiếp bài này'), findsOneWidget);
      await t.tap(find.byKey(AssistPeek.peekKey));
      await t.pumpAndSettle();
      expect(find.textContaining('về mục lục chọn bài khác'), findsNothing);
      expect(find.textContaining('đã đi qua các cách học'), findsNothing);
      expect(find.textContaining('chỉ có một cách học'), findsOneWidget);
      // đường về vẫn có — nhưng là nút ← của trẻ, không phải lời SAM khuyên
      expect(find.byTooltip('Về mục lục'), findsOneWidget);
    });
  });
}

/// Mọi tập con của [all] — 2^n, để test quét chứ không lấy mẫu.
Iterable<Set<WorkspaceView>> _subsets(Set<WorkspaceView> all) sync* {
  final xs = all.toList();
  for (var mask = 0; mask < (1 << xs.length); mask++) {
    yield {
      for (var i = 0; i < xs.length; i++)
        if (mask & (1 << i) != 0) xs[i],
    };
  }
}
