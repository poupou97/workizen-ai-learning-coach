/// WAL-128 — luật của pedagogy model giữ bằng test (không chỉ schema).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/pedagogy/pedagogical_pattern.dart';
import 'package:learning_coach/core/pedagogy/pedagogy_model.dart';
import 'package:learning_coach/core/pedagogy/source_misconception.dart';
import 'package:learning_coach/core/student/mastery.dart';

void main() {
  group('supportLevelOf — act nào ghi evidence mức nào (§32 bảo thủ)', () {
    test('act không đưa nội dung ⇒ none; trẻ vẫn được tính tự làm', () {
      for (final a in [
        TeachingAct.observeWait,
        TeachingAct.diagnosticProbe,
        TeachingAct.askExplanation,
        TeachingAct.askVerification,
        TeachingAct.reflect,
        TeachingAct.stepBack,
      ]) {
        expect(supportLevelOf(a), SupportLevel.none, reason: '$a');
      }
    });

    test('act đưa nội dung định hướng ⇒ hint — kể cả pumpRecall (bảo thủ)',
        () {
      for (final a in [
        TeachingAct.pumpRecall,
        TeachingAct.smallHint,
        TeachingAct.strategicHint,
        TeachingAct.contrastCases,
      ]) {
        expect(supportLevelOf(a), SupportLevel.hint, reason: '$a');
      }
    });

    test('làm mẫu/giảng ⇒ workedStep; revealAnswer ⇒ fullSolution (bất biến)',
        () {
      expect(supportLevelOf(TeachingAct.workedExample), SupportLevel.workedStep);
      expect(supportLevelOf(TeachingAct.demonstrateStep), SupportLevel.workedStep);
      expect(supportLevelOf(TeachingAct.revealStep), SupportLevel.workedStep);
      expect(supportLevelOf(TeachingAct.revealAnswer), SupportLevel.fullSolution,
          reason: 'lời giải trọn vẹn không bao giờ được ghi nhẹ hơn');
    });
  });

  group('rungToSupport — thang 7 nấc §17 map ĐƠN ĐIỆU xuống evidence', () {
    test('không nấc nào map NHẸ hơn nấc đứng trước', () {
      SupportLevel? prev;
      for (final r in AssistanceRung.values) {
        final s = rungToSupport(r);
        if (prev != null) {
          expect(s.index >= prev.index, isTrue,
              reason: '$r map nhẹ hơn nấc trước — «đúng sau demonstration» '
                  'sẽ lẻn xuống mức thấp');
        }
        prev = s;
      }
    });

    test('hai đầu thang cố định: independent→none, workedSolution→full', () {
      expect(rungToSupport(AssistanceRung.independent), SupportLevel.none);
      expect(
          rungToSupport(AssistanceRung.workedSolution), SupportLevel.fullSolution);
    });

    test('prompt KHÔNG phải independent — «đúng sau prompt» ≠ tự làm', () {
      expect(rungToSupport(AssistanceRung.prompt), isNot(SupportLevel.none));
    });
  });

  group('PedagogySource — thẩm quyền nguồn phải trỏ được về nguồn', () {
    test('sourceExplicit thiếu sourceDocumentId ⇒ assert nổ', () {
      expect(
        () => PedagogySource(
            authority: PedagogyAuthority.sourceExplicit,
            extractionMethod: 'manual'),
        throwsA(isA<AssertionError>()),
      );
    });

    test('externalResearch không cần doc — văn liệu ngoài hợp lệ', () {
      expect(
        const PedagogySource(
            authority: PedagogyAuthority.externalResearch,
            extractionMethod: 'research:wood-1976'),
        isA<PedagogySource>(),
      );
    });
  });

  group('SourceMisconception seed v0 — 4 mục thật từ WAL-127', () {
    test('mọi seed đủ provenance (doc + trang) và authority sourceExplicit',
        () {
      expect(sourceMisconceptionSeedV0, hasLength(4));
      for (final m in sourceMisconceptionSeedV0) {
        expect(m.source.authority, PedagogyAuthority.sourceExplicit);
        expect(m.source.sourceDocumentId, isNotNull, reason: m.id);
        expect(m.source.page, isNotNull, reason: m.id);
      }
    });

    test('skillCaseId chưa map ⇒ null giữ nguyên — không bịa mapping', () {
      // Seed v0 nói theo BÀI của SGV; map về SkillCase là việc của WAL-129
      // khi có blueprint cho đúng ca — chưa map thì phải là null.
      for (final m in sourceMisconceptionSeedV0) {
        expect(m.skillCaseId, isNull, reason: m.id);
      }
    });
  });

  test('PatternStep: minutes null hợp lệ — nguồn không nói thì không bịa số',
      () {
    const step = PatternStep(
        intent: PedagogicalIntent.activate,
        allowedActs: [TeachingAct.pumpRecall]);
    expect(step.minutes, isNull);
  });
}
