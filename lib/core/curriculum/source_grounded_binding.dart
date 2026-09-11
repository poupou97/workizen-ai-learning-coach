/// ⭐ BINDING SUY TỪ NGUỒN — một đường, không phải một tệp mỗi bài.
///
/// Nguyên mẫu `khtn6_bai17.dart` chứng minh hình dạng: mọi trường của một
/// binding giải được đều **CỤC BỘ TRONG BÀI**. Không cần mô hình chương trình
/// xuyên bài, vì các cổng tiên quyết của [eligibilityOf] đúng một cách
/// **TỰ THAM CHIẾU**:
///
/// - `requiresConcepts ⊆ stage.conceptsIntroduced` — cả hai là {khái niệm của
///   chính bài này}
/// - `requiresTerminology ⊆ stage.terminologyIntroduced` — vế trái RỖNG
/// - `stage.methodsIntroduced ∋ method.id` — bài này in ra quy tắc ấy
///
/// ⛔ KHÔNG BỊA TIÊN QUYẾT. `requiresTerminology` để RỖNG là cố ý: sách không
/// in ra «phương pháp này đòi những thuật ngữ nào». Khai bừa là bịa một quan
/// hệ phụ thuộc mà nguồn không nói.
///
/// ⛔ KHÔNG CÓ KHỐI QUY TẮC IN ⇒ KHÔNG CÓ BINDING. Đo được: 18/33 bài có câu
/// quy tắc («Em đã học» / «Ghi nhớ» / «Kết luận» / «Kiến thức cốt lõi») in
/// kèm trang. 15 bài còn lại fail closed — `runtimeGuidedReady = false`.
///
/// Dữ liệu riêng từng bài: ĐƯỢC. Logic riêng từng bài: KHÔNG. Tệp này không
/// có một nhánh `if book == …` nào.
library;

import '../knowledge/provenance.dart';
import 'concept.dart';
import 'pedagogical_boundary.dart';
import 'semantic_binding.dart';
import 'skill_case.dart';

/// Ngữ nghĩa chương trình đã được bộ dựng trích NGUYÊN VĂN từ khối quy tắc.
class SourceCurriculum {
  const SourceCurriculum({
    required this.conceptId,
    required this.canonicalName,
    required this.textbookTerms,
    required this.skillCaseId,
    required this.condition,
    required this.methodId,
    required this.methodName,
    required this.ruleBlockId,
    required this.pagePdf,
    required this.pagePrinted,
    required this.extractionMethod,
  });

  final String conceptId;
  final String canonicalName;
  final List<String> textbookTerms;
  final String skillCaseId;

  /// CÂU QUY TẮC NGUYÊN VĂN — không diễn đạt lại.
  final String condition;
  final String methodId;
  final String methodName;
  final String ruleBlockId;
  final int pagePdf;
  final int? pagePrinted;
  final String extractionMethod;

  /// `null` khi thiếu bất kỳ trường bắt buộc nào — fail closed, không đoán.
  static SourceCurriculum? fromJson(Object? v) {
    if (v is! Map) return null;
    final m = v.cast<String, Object?>();
    final terms = [
      for (final t in (m['textbookTerms'] as List? ?? const []))
        if (t is String && t.isNotEmpty) t,
    ];
    final id = m['conceptId'], name = m['canonicalName'];
    final caseId = m['skillCaseId'], cond = m['condition'];
    final mid = m['methodId'], mname = m['methodName'];
    final blk = m['ruleBlockId'], pg = m['pagePdf'], ex = m['extractionMethod'];
    if (id is! String || name is! String || caseId is! String) return null;
    if (cond is! String || cond.trim().isEmpty) return null;
    if (mid is! String || mname is! String || blk is! String) return null;
    if (pg is! num || ex is! String || terms.isEmpty) return null;
    // ⚠ `origin` phải là `sourceStated`. Bất kỳ giá trị nào khác ⇒ từ chối:
    // không có đường nào nâng UNKNOWN lên sourceStated ở đây.
    if (m['origin'] != 'sourceStated') return null;
    return SourceCurriculum(
      conceptId: id, canonicalName: name, textbookTerms: terms,
      skillCaseId: caseId, condition: cond, methodId: mid, methodName: mname,
      ruleBlockId: blk, pagePdf: pg.toInt(),
      pagePrinted: (m['pagePrinted'] as num?)?.toInt(),
      extractionMethod: ex,
    );
  }
}

/// Dựng cặp (curriculum, binding) cho MỘT bài — rồi giao cho [resolveBinding]
/// đã có. Không runtime thứ hai, không luật tin cậy thứ hai.
({BindingCurriculum curriculum, SemanticBinding binding}) bindingFor(
  SourceCurriculum c, {
  required String book,
  required int lessonNo,
  required int grade,
  required String bookSeries,
  required String activityId,
}) {
  final lessonId = '$book:b$lessonNo';
  final prov = Provenance(
    origin: KnowledgeOrigin.sourceStated,
    sourceId: book,
    extractionMethod: '${c.extractionMethod} · block ${c.ruleBlockId}',
    confidence: 0.9,
    bookSeries: bookSeries,
    grade: grade,
    // ⭐ `citableAsTextbookFact` đòi `pageStart != null`. Trang IN nếu dò được,
    // nếu không thì trang PDF — vẫn là một trang CÓ THẬT tra ngược được.
    pageStart: c.pagePrinted ?? c.pagePdf,
    pageEnd: c.pagePrinted ?? c.pagePdf,
  );
  final method = TeachingMethod(
    id: c.methodId,
    name: c.methodName,
    appliesToConcepts: {c.conceptId},
    skillCaseId: c.skillCaseId,
    requiresConcepts: {c.conceptId},
    requiresTerminology: const {},
    provenance: prov,
  );
  return (
    curriculum: BindingCurriculum(
      conceptId: c.conceptId,
      cases: [
        SkillCase(
            id: c.skillCaseId,
            conceptId: c.conceptId,
            condition: c.condition,
            introducedGrade: grade),
      ],
      stage: LearningStage(
        grade: grade,
        bookSeries: bookSeries,
        lessonId: lessonId,
        conceptsIntroduced: {c.conceptId},
        methodsIntroduced: {c.methodId},
        terminologyIntroduced: c.textbookTerms.toSet(),
      ),
      catalogue: [method],
    ),
    binding: SemanticBinding(
      activityId: activityId,
      lessonRef: LessonRef(book, lessonNo),
      conceptId: c.conceptId,
      skillCaseId: c.skillCaseId,
      methodIds: [c.methodId],
      bindingSource: BindingSource.derived,
      confidence: 0.9,
      provenance: const BindingProvenance(
        curatedBy: 'source-rule-block-v1',
        basis: 'khối quy tắc in trong chính bài (Em đã học / Ghi nhớ / '
            'Kết luận / Kiến thức cốt lõi)',
      ),
    ),
  );
}

/// Khái niệm của bài — chỉ dùng chữ của chính bài, không thêm từ ngoài.
Concept conceptOf(SourceCurriculum c,
        {required int grade,
        required String bookSeries,
        required String lessonId,
        required int page}) =>
    Concept(
      id: c.conceptId,
      canonicalName: c.canonicalName,
      exposures: [
        ConceptExposure(
            grade: grade,
            bookSeries: bookSeries,
            lessonId: lessonId,
            role: ExposureRole.introduces,
            pageStart: page),
      ],
      textbookTerms: {grade: c.textbookTerms.toSet()},
    );
