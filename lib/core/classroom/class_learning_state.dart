/// WAL-105 — ClassLearningState: teacher view = PROJECTION, không phải model.
///
/// Bất biến Founder (delta K):
/// - KHÔNG BAO GIỜ mean(mastery) toàn lớp — mean giấu ca hỏng, cùng lý do
///   min-not-mean của `ConceptMastery.derived`. Cấu trúc này KHÔNG CÓ trường
///   «điểm trung bình lớp» để mà dùng sai.
/// - UNKNOWN ≠ weak: học sinh chưa quan sát vào nhóm «chưa có dữ liệu»,
///   tuyệt đối không vào nhóm «yếu».
/// - Mọi con số truy về học sinh cụ thể (F4) — nhóm là danh sách id, không
///   phải count trần.
library;

import '../student/concept_summary.dart';

/// Một học sinh + summary MỘT khái niệm — đầu vào projection.
class StudentConceptRow {
  const StudentConceptRow({required this.studentId, required this.summary});

  final String studentId;
  final ConceptSummary summary;
}

/// Projection của MỘT khái niệm trên lớp. Bốn nhóm theo ConceptClaim —
/// danh sách id (drill-down được), không có aggregate mù.
class ClassConceptState {
  const ClassConceptState({
    required this.conceptId,
    required this.noData,
    required this.needsWork,
    required this.developing,
    required this.strong,
    required this.commonWeakCases,
    required this.unobservedByAll,
  });

  final String conceptId;

  /// noEvidence + insufficientEvidence — «chưa biết», KHÔNG phải «yếu».
  final List<String> noData;

  final List<String> needsWork;
  final List<String> developing;

  /// strongOnObserved + mastered.
  final List<String> strong;

  /// Ca yếu PHỔ BIẾN: (caseId, danh sách học sinh yếu ca đó), sắp theo số
  /// học sinh giảm dần rồi caseId — MODE, không mean; truy được từng em.
  final List<(String, List<String>)> commonWeakCases;

  /// Ca CHƯA HỌC SINH NÀO được quan sát — lỗ coverage của cả lớp.
  final List<String> unobservedByAll;
}

ClassConceptState classConceptState(
    String conceptId, List<StudentConceptRow> rows) {
  final noData = <String>[], needsWork = <String>[];
  final developing = <String>[], strong = <String>[];
  final weakBy = <String, List<String>>{};
  Set<String>? unobservedEveryone;

  for (final r in rows) {
    final s = r.summary;
    assert(s.conceptId == conceptId);
    switch (s.claim) {
      case ConceptClaim.noEvidence:
      case ConceptClaim.insufficientEvidence:
        noData.add(r.studentId);
      case ConceptClaim.needsWork:
        needsWork.add(r.studentId);
        for (final c in s.weakestObservedCases) {
          weakBy.putIfAbsent(c, () => []).add(r.studentId);
        }
      case ConceptClaim.developing:
        developing.add(r.studentId);
      case ConceptClaim.strongOnObserved:
      case ConceptClaim.mastered:
        strong.add(r.studentId);
    }
    final un = s.unobservedCases.toSet();
    unobservedEveryone =
        unobservedEveryone == null ? un : unobservedEveryone.intersection(un);
  }

  final common = weakBy.entries
      .map((e) => (e.key, e.value..sort()))
      .toList()
    ..sort((a, b) {
      if (a.$2.length != b.$2.length) return b.$2.length - a.$2.length;
      return a.$1.compareTo(b.$1);
    });

  return ClassConceptState(
    conceptId: conceptId,
    noData: noData..sort(),
    needsWork: needsWork..sort(),
    developing: developing..sort(),
    strong: strong..sort(),
    commonWeakCases: common,
    unobservedByAll: (unobservedEveryone ?? const {}).toList()..sort(),
  );
}
