/// WAL-70 — Diagnostic Probe: khi chẩn đoán BẤT ĐỊNH, hỏi-vì-THÔNG-TIN.
///
/// Vòng khép kín: `attributionUnresolved` → [nextProbe] chọn MỘT bài ngắn
/// chỉ chạm MỘT ca → trẻ trả lời → bằng chứng vào log ca đó → gọi lại
/// `attributeFailure` → hoặc cô lập được (delegated teaching) hoặc probe tiếp.
///
/// Prior art (docs/research/DIAGNOSTIC-PROBE-LOOP.md — KHÔNG bịa công thức):
/// - CDA/Q-matrix (DINA): item đơn-thuộc-tính nhận diện thuộc tính tốt nhất.
/// - CAT item selection / active learning: hỏi nơi BẤT ĐỊNH lớn nhất. Proxy
///   của ta là ĐẾM bằng chứng độc lập (ít nhất = bất định nhất) — trung thực
///   với việc chưa có tham số item hiệu chuẩn, không giả vờ có entropy.
/// - Model tracing: kiểm MÓNG trước — hoà thì ca dạy sớm hơn trong chương
///   trình đi trước.
library;

import '../curriculum/exercise_skill_map.dart';
import '../curriculum/skill_case.dart';
import '../student/mastery.dart';
import 'multi_skill_diagnosis.dart';

/// Một câu hỏi chẩn đoán được chọn — kèm lý do đọc được (doctrine F4).
class ProbeRequest {
  const ProbeRequest({
    required this.exerciseId,
    required this.skillCaseId,
    required this.conceptId,
    required this.reason,
  });

  final String exerciseId;
  final String skillCaseId;
  final String conceptId;
  final String reason;
}

/// Chọn probe kế tiếp. Trả `null` khi KHÔNG probe được — và khi đó chẩn đoán
/// GIỮ NGUYÊN `attributionUnresolved`: không có bài cô lập thì thà nói "chưa
/// biết con vướng đâu" còn hơn đoán một ca để dạy (doctrine: quy lỗi sai địa
/// chỉ tệ hơn không quy lỗi).
///
/// Luật chọn — tất định, kiểm toán được:
///   ① chỉ hoạt động khi `attributionUnresolved` (≥2 nghi phạm);
///   ② probe phải là bài CHỈ CHẠM MỘT ca, và ca đó trong danh sách nghi phạm;
///   ③ nghi phạm ÍT bằng chứng độc lập nhất trước (bất định lớn nhất);
///      hoà ⇒ `introducedGrade` THẤP hơn trước (kiểm móng trước);
///      hoà nữa ⇒ id từ điển (tất định tuyệt đối).
ProbeRequest? nextProbe(
  MultiSkillDecision d, {
  required List<ExerciseSkillMap> exercisePool,
  required Map<String, ConceptMastery> masteryByConcept,
  List<SkillCase> caseCatalogue = const [],
}) {
  if (d.diagnosis != DiagnosticOutcome.attributionUnresolved) return null;

  // ② bài đơn-kỹ-năng theo ca — bản đồ ca → exercise cô lập được nó
  final isolating = <String, ExerciseSkillMap>{};
  for (final e in exercisePool) {
    if (e.requirements.length == 1) {
      // bài đầu tiên theo thứ tự pool; pool là dữ liệu, thứ tự của nó là của
      // người soạn — không tự xáo.
      isolating.putIfAbsent(e.requirements.single.skillCaseId, () => e);
    }
  }

  final byId = {for (final c in caseCatalogue) c.id: c};
  int evidenceOf(String caseId) {
    for (final m in masteryByConcept.values) {
      final c = m.cases[caseId];
      if (c != null) return c.evidenceCount;
    }
    return 0;
  }

  final candidates =
      d.implicatedCases.where(isolating.containsKey).toList()
        ..sort((a, b) {
          final ea = evidenceOf(a), eb = evidenceOf(b);
          if (ea != eb) return ea.compareTo(eb); // ③ ít bằng chứng trước
          final ga = byId[a]?.introducedGrade ?? 1 << 30;
          final gb = byId[b]?.introducedGrade ?? 1 << 30;
          if (ga != gb) return ga.compareTo(gb); // móng trước
          return a.compareTo(b);
        });
  if (candidates.isEmpty) return null; // fail closed — không đoán

  final target = candidates.first;
  final ex = isolating[target]!;
  final req = ex.requirements.single;
  return ProbeRequest(
    exerciseId: ex.exerciseId,
    skillCaseId: target,
    conceptId: req.conceptId,
    reason: 'Trong ${d.implicatedCases.length} kỹ năng bị nghi, '
        '"$target" có ít bằng chứng con tự làm nhất '
        '(${evidenceOf(target)} lần) — hỏi một bài NGẮN chỉ chạm kỹ năng này '
        'cho SAM biết chắc, thay vì đoán.',
  );
}
