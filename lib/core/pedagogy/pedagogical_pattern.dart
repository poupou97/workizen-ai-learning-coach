/// WAL-128 — PedagogicalPattern: khuôn tổ chức việc học TRÍCH TỪ NGUỒN,
/// versioned, có thẩm quyền. KHÔNG hard-code schema kiểu «đủ mọi field» —
/// prototype các trường CÓ DỮ LIỆU THẬT từ WAL-127; trường chưa có evidence
/// thì CHƯA CÓ MẶT (không bịa field — §3/§5 Founder Order).
///
/// Pattern ≠ Blueprint: pattern là KHUÔN theo (family × band × intent),
/// blueprint (WAL-129) là HỢP ĐỒNG cho một SkillCase cụ thể, lắp từ pattern.
library;

import 'pedagogy_model.dart';

/// Xuất xứ một mảnh pedagogy — trỏ về SGV thật (doc, trang, bài) hoặc văn
/// liệu ngoài. Mọi trường quan trọng required — quên khai là không biên dịch.
class PedagogySource {
  const PedagogySource({
    required this.authority,
    required this.extractionMethod,
    this.sourceDocumentId,
    this.page,
    this.lesson,
    this.note,
  }) : assert(
          authority == PedagogyAuthority.externalResearch ||
              authority == PedagogyAuthority.experimental ||
              sourceDocumentId != null,
          'thẩm quyền từ nguồn thì phải trỏ được về nguồn',
        );

  final PedagogyAuthority authority;

  /// `sgv-pedagogy-v1` · `sgv-pedagogy-en-v1` · `manual` · `research:<ref>`
  final String extractionMethod;
  final String? sourceDocumentId;
  final int? page;
  final int? lesson;
  final String? note;
}

/// Một bước trong khuôn — intent + act được phép + pacing nếu nguồn nói.
class PatternStep {
  const PatternStep({
    required this.intent,
    required this.allowedActs,
    this.minutes,
    this.organization,
  });

  final PedagogicalIntent intent;
  final List<TeachingAct> allowedActs;

  /// Thời lượng SGV ghi (THCS: 584 cấu phần có phút — WAL-127 §2b).
  /// `null` = nguồn không nói — không bịa số.
  final int? minutes;

  /// Ghi chú tổ chức GỐC (nhóm/cặp/lớp) — để trích INTENT khi chuyển
  /// 1-learner (§4: không copy activity 1:1).
  final String? organization;
}

class PedagogicalPattern {
  const PedagogicalPattern({
    required this.patternId,
    required this.subjectFamily,
    required this.gradeBand,
    required this.steps,
    required this.source,
    this.misconceptionIds = const [],
    this.version = pedagogyModelVersion,
  });

  final String patternId;

  /// TOAN · TV-VAN · KHOA · SU · NN · KHAC — đúng family đã đo coverage.
  final String subjectFamily;

  /// '1-2' · '3-5' · '6-9' · '10-12'.
  final String gradeBand;

  /// Chuỗi intent CÓ THỨ TỰ — từ chuỗi đo được (ACTIVATE→DISCOVER 45 bài…),
  /// KHÔNG một sequence chung cho mọi môn (F2 có evidence).
  final List<PatternStep> steps;

  final PedagogySource source;

  /// Trỏ tới [SourceMisconception.id] liên quan (nếu nguồn có).
  final List<String> misconceptionIds;

  final String version;
}
