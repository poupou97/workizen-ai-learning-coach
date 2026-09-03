/// WAL-168 — ARCHITECTURE GATE, điểm chặn thứ nhất.
///
/// Trước đây `ProblemContextScreen` tự hỏi «bài này là phân số dạng gì»:
/// `FractionProblem.parse(...)` → `fractionCase(...)`. Nghĩa là môn nào không
/// viết được thành `a/b ± c/d` thì `exerciseCase == null` ⇒ TutorScope không
/// có phương pháp ⇒ **không dạy được gì**, dù mọi tầng trên đã trung tính.
///
/// Test này dựng một môn KHÔNG PHẢI TOÁN (chỉ tồn tại trong test) và đòi màn
/// dùng chung dạy được nó mà KHÔNG thêm một dòng runtime nào theo môn.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/canonical_problem.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/curriculum/skill_case.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/knowledge/slice_curriculum.dart';
import 'package:learning_coach/core/store/learner_profile.dart';
import 'package:learning_coach/core/store/learner_store.dart';
import 'package:learning_coach/core/student/mastery.dart';
import 'package:learning_coach/features/learning_session/slice_flow.dart';

const _p = LearnerProfile(learnerId: 'l', displayName: 'Na', grade: 4);

/// Ca của một môn tưởng tượng — chỉ dùng để kiểm RUNTIME, không bao giờ là
/// sự thật giáo dục (Founder: fixture cho UI/runtime, không cho nội dung).
const _caseId = 'quan-sat-vat-song';

/// ⭐ Classifier của «họ môn» giả định: nhận ra đề bằng CHỮ, không bằng số.
String? _observationCase(String expression) =>
    expression.toLowerCase().contains('quan sát') ? _caseId : null;

const _prov = Provenance(
  origin: KnowledgeOrigin.sourceDemonstrated,
  sourceId: '04-sgk-khoa-hoc-4',
  extractionMethod: 'test-fixture',
  confidence: 0.9,
  bookSeries: 'kntt',
  grade: 4,
  subject: 'Khoa học',
  pageStart: 10,
);

final _curriculum = SliceCurriculum(
  subjectId: 'khoa-hoc',
  conceptId: 'quan-sat',
  activityLabel: 'Khoa học 4 · Quan sát vật sống',
  classifyCase: _observationCase,
  stage: const LearningStage(
    grade: 4,
    bookSeries: 'kntt',
    lessonId: 'khoa4-quan-sat',
    conceptsIntroduced: {'quan-sat'},
    methodsIntroduced: {'observe-then-describe'},
    terminologyIntroduced: {},
  ),
  catalogue: const [
    TeachingMethod(
      id: 'observe-then-describe',
      name: 'Quan sát rồi mô tả',
      appliesToConcepts: {'quan-sat'},
      skillCaseId: _caseId,
      requiresConcepts: {'quan-sat'},
      requiresTerminology: {},
      provenance: _prov,
      hints: MethodHints(
        hint: 'Con nhìn kỹ xem có gì thay đổi không?',
        workedStep: 'Bước đầu tiên: ghi lại điều con thấy. Đến lượt con!',
        fullSolution: 'Cả bài nhé: mô tả điều quan sát được rồi so với dự đoán.',
      ),
    ),
  ],
  cases: const [
    SkillCase(
        id: _caseId,
        conceptId: 'quan-sat',
        condition: 'quan sát một vật sống rồi mô tả',
        introducedGrade: 4),
  ],
);

Future<void> _pump(WidgetTester t, String expression) async {
  await t.pumpWidget(MaterialApp(
    home: ProblemContextScreen(
      problem: CanonicalProblem.fromCurriculum(
          exerciseLabel: 'b1', expression: expression, provenance: _prov),
      profile: _p,
      store: JsonlLearnerStore(),
      curriculum: _curriculum,
      mastery: const ConceptMastery(conceptId: 'quan-sat', cases: {}),
    ),
  ));
  await t.pumpAndSettle();
}

void main() {
  testWidgets(
      '⭐⭐ môn KHÔNG PHẢI toán vẫn ra ĐÚNG dạng bài — màn dùng chung không '
      'còn tự hỏi «đây có phải phân số không»', (t) async {
    await _pump(t, 'Quan sát cây đậu sau ba ngày');
    expect(find.textContaining('quan sát một vật sống rồi mô tả'), findsOneWidget,
        reason: '⭐⭐ đột biến trả lại FractionProblem.parse trong màn ⇒ đề này '
            'không parse được ⇒ không có dạng bài ⇒ đỏ. Đây CHÍNH LÀ điểm chặn '
            'Architecture Gate.');
  });

  testWidgets('⭐ classifier không nhận ra ⇒ fail closed, không bịa dạng bài',
      (t) async {
    await _pump(t, 'Một đề lạc đề hoàn toàn');
    expect(find.textContaining('quan sát một vật sống rồi mô tả'), findsNothing,
        reason: '⭐ đột biến trả ca mặc định khi không nhận ra ⇒ đỏ');
  });

  testWidgets('⭐ lời dạy của môn này lấy từ DỮ LIỆU của chính nó', (t) async {
    await _pump(t, 'Quan sát cây đậu sau ba ngày');
    expect(find.textContaining('Quan sát rồi mô tả'), findsWidgets,
        reason: 'phương pháp của môn hiện ra, không phải phương pháp Toán');
    expect(find.textContaining('mẫu số'), findsNothing,
        reason: '⭐ đột biến rơi về catalogue Toán ⇒ đỏ');
  });
}
