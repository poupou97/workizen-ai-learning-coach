/// ⭐⭐ TRACK B — CỔNG RANH GIỚI (Founder 2026-09-05):
/// MOCK ≠ EVIDENCE · FIXTURE ≠ TRUSTED CORPUS · UI COMPLETION ≠ MASTERY ·
/// TAP ≠ COMPETENCE · PROTOTYPE SAM ≠ PROVEN PEDAGOGY · SCREEN EXISTS ≠
/// CAPABILITY PROVEN.
///
/// Ba lớp kiểm:
/// 1. MÃ NGUỒN: `lib/features/lesson_workspace/**` + `lib/core/lesson_model/**`
///    không import kho/bằng chứng/recorder, không gọi `recordSession`/
///    `appendSession`, không import LLM/prompt.
/// 2. RUNTIME: đi hết hành trình với một `LearnerStore` GIẢ NÉM khi bị ghi —
///    không ném là chưa có ai ghi. (Workspace không nhận store theo cấu trúc;
///    test này ghim rằng cả entry point giá sách cũng không lôi store vào.)
/// 3. GIT: fixture thật không lọt vào git; pubspec khai báo đủ thư mục.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/next_action.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/store/learning_session.dart';
import 'package:learning_coach/core/store/timetable.dart';
import 'package:learning_coach/core/student/learning_evidence.dart';
import 'package:learning_coach/features/lesson_workspace/lesson_workspace_screen.dart';
import 'package:learning_coach/features/lesson_workspace/workspace_trace.dart';
import 'package:learning_coach/features/subjects/book_shelf_screen.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

import 'support.dart';

/// Kho GIẢ: đọc trả rỗng, GHI thì ném — bất kỳ đường nào ghi bằng chứng qua
/// workspace sẽ làm test đỏ ngay tại chỗ ghi.
class _ThrowingStore implements LearnerStore {
  Never _boom(String op) =>
      throw StateError('⭐⭐ BOUNDARY VIOLATION: workspace ghi kho qua $op');

  @override
  Future<void> appendSession(LearningSession s) async => _boom('appendSession');
  @override
  Future<void> saveProfile(LearnerProfile p) async => _boom('saveProfile');
  @override
  Future<void> saveTimetable(String l, List<TimetableEntry> e) async =>
      _boom('saveTimetable');
  @override
  Future<void> saveParentPin(String pin) async => _boom('saveParentPin');
  @override
  Future<void> saveActiveLearner(String l) async => _boom('saveActiveLearner');
  @override
  Future<int> deleteLearner(String l) async => _boom('deleteLearner');

  @override
  Future<List<LearnerProfile>> profiles({String? guardianId}) async => const [];
  @override
  Future<LearnerProfile?> profile(String learnerId) async => null;
  @override
  Future<List<LearningSession>> sessions({
    required String learnerId,
    DateTime? onDay,
    String? subjectId,
    String? skillCaseId,
  }) async => const [];
  @override
  Future<EvidenceLog> evidenceFor({
    required String learnerId,
    required String skillCaseId,
  }) async => EvidenceLog.empty(skillCaseId);
  @override
  Future<List<TimetableEntry>> timetable(String learnerId) async => const [];
  @override
  Future<String?> parentPin() async => null;
  @override
  Future<String?> activeLearnerId() async => null;
  @override
  Future<String> exportLearner(String learnerId) async => '';
}

const _p = LearnerProfile(learnerId: 'na', displayName: 'Na', grade: 6);

Iterable<File> _dartFiles(String dir) => Directory(dir)
    .listSync(recursive: true)
    .whereType<File>()
    .where((f) => f.path.endsWith('.dart'));

void main() {
  test('⭐⭐ MÃ: workspace + lesson_model không import kho/bằng chứng/LLM, không '
      'gọi recordSession/appendSession', () {
    const forbiddenImports = [
      'core/store/learner_store.dart',
      'core/store/learning_session.dart',
      'core/student/learning_evidence.dart',
      'core/student/mastery.dart',
      'core/student/evidence_validator.dart',
      'shell/session_recorder.dart',
      'core/tutor/tutor_prompt.dart',
      'core/tutor/output_guard.dart',
      'package:http',
      'dart:io',
    ];
    const forbiddenCalls = [
      'recordSession(',
      'appendSession(',
      'LearningEvent(',
      'EvidenceKind.',
      'LearnerStore',
    ];
    final files = [
      ..._dartFiles('lib/features/lesson_workspace'),
      ..._dartFiles('lib/core/lesson_model'),
    ];
    expect(files, isNotEmpty);
    // Bỏ dòng chú thích: chú thích được phép NHẮC tên kho để nói «không dùng».
    String code(File f) => f
        .readAsLinesSync()
        .where((l) => !l.trimLeft().startsWith('//'))
        .join('\n');
    for (final f in files) {
      final src = code(f);
      for (final imp in forbiddenImports) {
        expect(src, isNot(contains(imp)), reason: '${f.path} import $imp');
      }
      for (final call in forbiddenCalls) {
        expect(src, isNot(contains(call)), reason: '${f.path} dùng $call');
      }
    }
  });

  test('MÃ: sáu bất đẳng thức nằm trong kiểu, không chỉ trong tài liệu', () {
    final src = File(
      'lib/core/lesson_model/content_trust.dart',
    ).readAsStringSync();
    for (final s in [
      'MOCK ≠ EVIDENCE',
      'FIXTURE ≠ TRUSTED CORPUS',
      'UI COMPLETION ≠ MASTERY',
      'TAP ≠ COMPETENCE',
      'PROTOTYPE SAM ≠ PROVEN PEDAGOGY',
      'SCREEN EXISTS ≠ CAPABILITY PROVEN',
    ]) {
      expect(src, contains(s));
    }
  });

  testWidgets(
    '⭐⭐ RUNTIME: đi hết Giá sách → Sách → Chương → Workspace → 3 View '
    '→ trả lời SAM sai & đúng → thẻ kết, với kho GIẢ NÉM khi ghi',
    (t) async {
      final store = _ThrowingStore();
      // Kho được đưa cho ĐƯỜNG CŨ (SubjectHome) như main.dart làm; workspace
      // không có tham số kho — nếu ai đó nối kho vào workspace, test này là chỗ
      // phải đổi, và reviewer sẽ thấy.
      var legacyOpened = 0;
      final idx = LessonIndex.fromJsonString('''
{"grade":6,"subjects":{"KHTN":[{"sourceDocumentId":"06-sgk-khoa-hoc-tu-nhien-6",
 "lessons":[{"no":17,"title":"TÁCH CHẤT KHỎI HỖN HỢP","pageStart":60}]}]},
 "toanExercises":{},
 "books":[{"sourceDocumentId":"06-sgk-khoa-hoc-tu-nhien-6","subject":"KHTN",
 "grade":6,"title":"KHTN 6","cover":"covers/k.webp","lessonCount":1}]}''')!;
      await t.pumpWidget(
        fixtureHost(
          BookShelfScreen(
            profile: _p,
            index: idx,
            catalog: WorkspaceCatalog.withDocs([loadSyntheticDoc()]),
            trace: WorkspaceTrace(),
            onOpenBook: (_) async {
              legacyOpened++;
              await store.sessions(
                learnerId: 'na',
              ); // đường cũ đọc kho — hợp lệ
            },
          ),
        ),
      );
      await t.pumpAndSettle();
      await t.tap(find.text('KHTN 6'));
      await t.pumpAndSettle();
      await t.tap(find.textContaining('Chương IV'));
      await t.pumpAndSettle();
      await t.tap(find.textContaining('Bài 17 · Tách chất'));
      await t.pumpAndSettle();
      expect(find.byType(LessonWorkspaceScreen), findsOneWidget);
      // ba View
      await t.tap(find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.read)));
      await t.pumpAndSettle();
      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.visual)),
      );
      await t.pumpAndSettle();
      await t.tap(
        find.byKey(LessonWorkspaceScreen.tabKey(WorkspaceView.tutor)),
      );
      await t.pumpAndSettle();
      await t.ensureVisible(find.text('Tiếp ▸'));
    await t.tap(find.text('Tiếp ▸'));
    await t.pumpAndSettle();
    final wrong = find.widgetWithText(FilledButton, 'Lọc');
    await t.ensureVisible(wrong);
    await t.tap(wrong); // sai
    await t.pumpAndSettle();
    final right = find.widgetWithText(FilledButton, 'Cô cạn');
    await t.ensureVisible(right);
    await t.tap(right); // đúng
    await t.pumpAndSettle();
    final field = find.byKey(const Key('tutor-answer-field'));
    await t.ensureVisible(field);
    await t.enterText(field, 'nặng hơn');
    await t.tap(find.byKey(const Key('tutor-send')));
    await t.pumpAndSettle();
    expect(find.text('Con đã học cùng SAM phần này'), findsOneWidget);
      // về tận giá sách (nút trong thẻ kết của SAM, không phải thẻ đề xuất)
      final back = find.widgetWithText(TextButton, 'Về mục lục');
    await t.ensureVisible(back);
    await t.tap(back);
      await t.pumpAndSettle();
      await t.tap(find.byTooltip('Về sách'));
      await t.pumpAndSettle();
      await t.tap(find.byTooltip('Về giá sách'));
      await t.pumpAndSettle();
      expect(find.text('Sách của con · Lớp 6'), findsOneWidget);
      expect(legacyOpened, 0, reason: 'hành trình mới không rẽ sang đường cũ');
      // Không ném ⇒ không ai ghi kho. (Kho giả ném ở MỌI hàm ghi.)
    },
  );

  test('⭐ GIT: fixture thật không lọt vào git (chỉ .gitkeep)', () {
    final r = Process.runSync('git', ['ls-files', 'assets/fixtures/real']);
    final tracked = (r.stdout as String)
        .split('\n')
        .where((l) => l.trim().isNotEmpty)
        .toList();
    expect(
      tracked,
      everyElement(endsWith('.gitkeep')),
      reason: '⭐⭐ chữ SGK / crop trang lọt git ⇒ đỏ: $tracked',
    );
    expect(
      tracked,
      containsAll([
        'assets/fixtures/real/.gitkeep',
        'assets/fixtures/real/crops/.gitkeep',
      ]),
    );
  });

  test('pubspec khai báo đủ 4 thư mục fixture (khai báo không đệ quy)', () {
    final lines = File('pubspec.yaml')
        .readAsLinesSync()
        .map((l) => l.trim())
        .where((l) => l.startsWith('- '))
        .map((l) => l.substring(2).trim())
        .toSet();
    expect(
      lines,
      containsAll([
        'assets/fixtures/real/',
        'assets/fixtures/real/crops/',
        'assets/fixtures/synthetic/',
        'assets/fixtures/synthetic/crops/',
      ]),
    );
    for (final d in [
      'assets/fixtures/real/crops',
      'assets/fixtures/synthetic/crops',
    ]) {
      expect(Directory(d).existsSync(), isTrue, reason: '$d phải tồn tại');
    }
  });

  test('fixture MẪU không chứa chữ nào giống lời sách (mọi đoạn có [MẪU])', () {
    final d = loadSyntheticDoc();
    final src = File(syntheticPath).readAsStringSync();
    expect(src, isNot(contains('Đãi cát tìm vàng')));
    expect(src, isNot(contains('phễu chiết một cách từ từ')));
    for (final b in d.blocks) {
      final txt = b.toJson()['text'];
      if (txt is String && b.toJson()['type'] == 'paragraph') {
        expect(txt, contains('[MẪU]'), reason: txt);
      }
    }
  });
}
