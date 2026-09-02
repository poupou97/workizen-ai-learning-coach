import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/curriculum/pedagogical_boundary.dart';
import 'package:learning_coach/core/knowledge/provenance.dart';
import 'package:learning_coach/core/tutor/tutor_prompt.dart';

final _stage = LearningStage(
  grade: 5,
  bookSeries: 'KNTT',
  lessonId: 'B57',
  conceptsIntroduced: const {'quy-dong'},
  methodsIntroduced: const {'m-quydong', 'm-bcnn'},
  terminologyIntroduced: const {'quy đồng', 'mẫu số'},
);

final _mQuyDong = TeachingMethod(
  id: 'm-quydong',
  name: 'Quy đồng mẫu số',
  appliesToConcepts: const {'quy-dong'},
  requiresConcepts: const {},
  requiresTerminology: const {'quy đồng'},
  skillCaseId: 'B57',
  provenance: const Provenance(
    origin: KnowledgeOrigin.sourceDemonstrated,
    sourceId: 'toan-5-kntt-t2',
    extractionMethod: 'manual',
    confidence: 0.9,
    subject: 'Toán',
    grade: 5,
    pageStart: 32,
  ),
);

final _mBcnn = TeachingMethod(
  id: 'm-bcnn',
  name: 'Quy đồng bằng BCNN',
  appliesToConcepts: const {'quy-dong'},
  requiresConcepts: const {'bcnn'}, // chưa được giới thiệu
  requiresTerminology: const {},
  skillCaseId: 'B57',
);

TutorPromptRequest req({String methodId = 'm-quydong', String? cas = 'B57'}) =>
    TutorPromptRequest(
      scope: TutorScope.forProblem('quy-dong', cas, _stage, [_mQuyDong, _mBcnn]),
      methodId: methodId,
      exerciseCase: cas,
      problemText: '3/4 + 1/5 = ?',
      grade: 5,
    );

void main() {
  test('prompt hợp lệ: đúng method, đúng nguồn DEMONSTRATED, đủ luật', () {
    final p = buildTutorPrompt(req())!;
    expect(p, contains('Quy đồng mẫu số'));
    expect(p, contains('SAM làm theo ví dụ')); // không bao giờ «Theo SGK» cho demonstrated
    expect(p, contains('REVEAL gate'));
    expect(p, contains('thang ±1'));
    expect(p, contains('thông minh')); // danh sách CẤM phải nằm trong prompt
  });

  test('method ngoài phép (BCNN chưa dạy) → KHÔNG CÓ prompt — fail closed', () {
    expect(buildTutorPrompt(req(methodId: 'm-bcnn')), isNull);
  });

  test('không xác định được ca → không prompt', () {
    expect(buildTutorPrompt(req(cas: null)), isNull);
  });

  test('prompt chỉ liệt kê từ vựng CỦA STAGE — BCNN không xuất hiện', () {
    final p = buildTutorPrompt(req())!;
    expect(p, contains('mẫu số · quy đồng'));
    expect(p.toLowerCase(), isNot(contains('bcnn')));
  });
}
