import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/adaptive/transfer_probe.dart';
import 'package:learning_coach/core/student/mastery.dart';

CaseMastery cm(double p, {int evidence = 5}) => CaseMastery(
      skillCaseId: 'B57',
      pMastery: p,
      evidenceCount: evidence,
      independentCorrect: evidence,
      lastIndependentEvidenceAt: DateTime(2026, 9, 1),
    );

TransferCandidate cand(String id,
        {String caseId = 'B57',
        SurfaceFamily surface = SurfaceFamily.bareExpression,
        String template = 't-x',
        bool single = true}) =>
    TransferCandidate(
        exerciseId: id,
        skillCaseId: caseId,
        surface: surface,
        templateId: template,
        singleSkill: single);

void main() {
  group('kích hoạt — cả ba điều kiện, hà tiện', () {
    test('chưa gần claim mạnh → KHÔNG probe (không biến mọi bài thành thi)',
        () {
      expect(
          shouldTransferProbe(
              mastery: cm(0.7), recentIndependentTemplates: {'t1'}),
          false);
    });

    test('bằng chứng đã đa dạng khuôn → KHÔNG probe', () {
      expect(
          shouldTransferProbe(
              mastery: cm(0.9), recentIndependentTemplates: {'t1', 't2'}),
          false);
    });

    test('mạnh + một màu khuôn → probe', () {
      expect(
          shouldTransferProbe(
              mastery: cm(0.9), recentIndependentTemplates: {'t1'}),
          true);
    });

    test('chưa có bằng chứng → không probe (UNKNOWN không bị thi)', () {
      expect(
          shouldTransferProbe(
              mastery: cm(0.9, evidence: 0), recentIndependentTemplates: {}),
          false);
    });
  });

  group('chọn bài — tất định, fail closed', () {
    test('không có bài khác-khuôn cùng ca → null, không đoán', () {
      expect(
          nextTransferProbe(
            skillCaseId: 'B57',
            dominantSurface: SurfaceFamily.bareExpression,
            seenTemplates: {'t-x'},
            pool: [cand('e1'), cand('e2', caseId: 'B53', template: 't-moi')],
          ),
          isNull);
    });

    test('near (cùng family, khuôn mới) thắng far', () {
      final r = nextTransferProbe(
        skillCaseId: 'B57',
        dominantSurface: SurfaceFamily.bareExpression,
        seenTemplates: {'t-cu'},
        pool: [
          cand('e-word',
              surface: SurfaceFamily.wordProblem, template: 't-w'),
          cand('e-near', template: 't-moi'),
        ],
      );
      expect(r!.exerciseId, 'e-near');
      expect(r.distance, 0);
    });

    test('bảng khoảng cách: wordProblem = 2, family khác = 1, cùng = 0', () {
      expect(
          transferDistance(
              SurfaceFamily.bareExpression, SurfaceFamily.wordProblem),
          2);
      expect(
          transferDistance(
              SurfaceFamily.wordProblem, SurfaceFamily.comparison),
          2);
      expect(
          transferDistance(
              SurfaceFamily.bareExpression, SurfaceFamily.comparison),
          1);
      expect(
          transferDistance(
              SurfaceFamily.visualModel, SurfaceFamily.visualModel),
          0);
    });

    test('distance thắng id từ điển: bài wordProblem id NHỎ vẫn thua', () {
      final r = nextTransferProbe(
        skillCaseId: 'B57',
        dominantSurface: SurfaceFamily.bareExpression,
        seenTemplates: {'t-cu'},
        pool: [
          cand('a-word', surface: SurfaceFamily.wordProblem, template: 't-w'),
          cand('z-so', surface: SurfaceFamily.comparison, template: 't-c'),
        ],
      );
      expect(r!.exerciseId, 'z-so');
    });

    test('wordProblem xa hơn comparison (bảng khoảng cách cố định)', () {
      final r = nextTransferProbe(
        skillCaseId: 'B57',
        dominantSurface: SurfaceFamily.bareExpression,
        seenTemplates: {'t-cu'},
        pool: [
          cand('e-word', surface: SurfaceFamily.wordProblem, template: 't-w'),
          cand('e-so', surface: SurfaceFamily.comparison, template: 't-c'),
        ],
      );
      expect(r!.exerciseId, 'e-so');
      expect(r.distance, 1);
    });

    test('cùng khoảng cách: đơn-kỹ-năng trước, rồi id từ điển', () {
      final r = nextTransferProbe(
        skillCaseId: 'B57',
        dominantSurface: SurfaceFamily.bareExpression,
        seenTemplates: {'t-cu'},
        pool: [
          cand('e-b', template: 't1', single: false),
          cand('e-c', template: 't2'),
          cand('e-a', template: 't3'),
        ],
      );
      expect(r!.exerciseId, 'e-a'); // single=true nhóm trước, 'e-a' < 'e-c'
    });

    test('khuôn ĐÃ GẶP không bao giờ được chọn làm transfer', () {
      final r = nextTransferProbe(
        skillCaseId: 'B57',
        dominantSurface: SurfaceFamily.bareExpression,
        seenTemplates: {'t-cu'},
        pool: [cand('e1', template: 't-cu'), cand('e2', template: 't-moi')],
      );
      expect(r!.exerciseId, 'e2');
    });

    test('mọi probe kèm lý do đọc được (F4)', () {
      final r = nextTransferProbe(
        skillCaseId: 'B57',
        dominantSurface: SurfaceFamily.bareExpression,
        seenTemplates: {},
        pool: [cand('e1', template: 't-moi')],
      );
      expect(r!.reason, isNotEmpty);
    });
  });
}
