/// WAL-76 (GĐ3) — LearningObjective: tầng ngữ nghĩa trên ContentUnit.
///
/// Nguồn: mục «MỤC TIÊU» per-bài trong SGV (sourceStated — sách NÓI THẲNG
/// «Giúp HS: …»). Hai loại theo đúng cấu trúc SGV: kiến-thức-kĩ-năng và
/// phát-triển-năng-lực — không trộn, vì Coach nói về hai thứ này khác nhau.
///
/// Concept CHỈ gán khi từ khoá đặc trưng khớp; 'unmapped' giữ trung thực.
library;

import '../knowledge/provenance.dart';

enum ObjectiveKind { knowledge, competency }

class LearningObjective {
  const LearningObjective({
    required this.id,
    required this.lessonNumber,
    required this.text,
    required this.kind,
    required this.provenance,
    this.conceptId,
  });

  final String id;
  final int lessonNumber;

  /// Nguyên văn theo SGV — không diễn đạt lại (đó là việc của tầng nói).
  final String text;

  final ObjectiveKind kind;

  /// `null` = chưa quy được về concept — unmapped trung thực, không đoán.
  final String? conceptId;

  final Provenance provenance;

  /// Được nói «SGV yêu cầu con …» không — chỉ khi nguồn nói thẳng.
  bool get citable => provenance.citableAsTextbookFact;

  static LearningObjective? fromJson(Map<String, Object?> j) {
    final id = j['id'], lesson = j['lesson'], text = j['text'],
        kind = j['kind'], origin = j['origin'];
    if (id is! String || lesson is! int || text is! String) return null;
    if (origin != 'sourceStated') return null; // nguồn lạ ⇒ từ chối, không đoán
    final concept = j['conceptId'];
    return LearningObjective(
      id: id,
      lessonNumber: lesson,
      text: text,
      kind: kind == 'competency'
          ? ObjectiveKind.competency
          : ObjectiveKind.knowledge,
      conceptId:
          concept is String && concept != 'unmapped' ? concept : null,
      provenance: Provenance(
        origin: KnowledgeOrigin.sourceStated,
        sourceId: (j['book'] as String?) ?? 'unknown',
        extractionMethod:
            (j['extraction'] as String?) ?? 'sgv-muctieu-v1',
        confidence: 0.9,
        pageStart: j['pagePdf'] is int ? j['pagePdf'] as int : null,
      ),
    );
  }
}
