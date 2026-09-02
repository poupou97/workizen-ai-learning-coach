/// ⭐ WAL-129 — LearningExperienceBlueprint: HỢP ĐỒNG SƯ PHẠM first-class.
///
/// Blueprint KHÔNG phải prompt. Nó nói: với SkillCase này, trải nghiệm học
/// gồm chuỗi intent/act nào, hỗ trợ tối đa tới đâu, bằng chứng nào bắt buộc,
/// nguồn nào cho phép — để engine THI HÀNH và QA KIỂM được (không phải lời
/// khuyên trong tài liệu).
///
/// Tách 5 tầng (§7 Founder Order): SOURCE (PedagogySource) ≠ KNOWLEDGE
/// (concept/case/method ids — trỏ vào curriculum) ≠ PEDAGOGY (sequence, cap,
/// evidence) ≠ PRESENTATION (HOÃN — WAL-132, không có field UI nào ở đây)
/// ≠ REALIZATION (LLM contract — WAL-131; blueprint không chứa prompt).
///
/// KHÔNG generic fixed sequence cho mọi SkillCase (F2/F3): sequence là DATA
/// per-blueprint, lấy từ pattern đo được.
library;

import '../student/learning_evidence.dart';
import '../student/mastery.dart';
import 'pedagogical_pattern.dart';
import 'pedagogy_model.dart';

const String blueprintVersion = 'blueprint-v0';

class LearningExperienceBlueprint {
  const LearningExperienceBlueprint({
    required this.blueprintId,
    required this.subject,
    required this.grade,
    required this.lessonId,
    required this.conceptIds,
    required this.skillCaseIds,
    required this.methodIds,
    required this.sequence,
    required this.assistanceCap,
    required this.evidenceRequired,
    required this.source,
    this.misconceptionIds = const [],
    this.transferRequired = false,
    this.reflectionRequired = false,
    this.learnerFirst = false,
    this.version = blueprintVersion,
  });

  final String blueprintId;
  final String subject;
  final int grade;

  /// KNOWLEDGE — trỏ vào curriculum, không sao chép nội dung.
  final String lessonId;
  final List<String> conceptIds;
  final List<String> skillCaseIds;
  final List<String> methodIds;

  /// PEDAGOGY — chuỗi khuyến nghị (intent + act được phép, pacing nếu nguồn
  /// nói). Đây là DATA per-SkillCase, không phải khuôn cứng dùng chung.
  final List<PatternStep> sequence;

  /// Trần assistance của TOÀN blueprint — map một chiều xuống SupportLevel
  /// khi đối chiếu evidence ([rungToSupport]).
  final AssistanceRung assistanceCap;

  /// Bằng chứng BẮT BUỘC phải xuất hiện trong một phiên đạt (vd: phải có
  /// independentAttempt — không có thì phiên chỉ là xem-làm-mẫu).
  final List<EvidenceKind> evidenceRequired;

  /// Trỏ [SourceMisconception.id] — SGV cảnh báo gì cho bài này.
  final List<String> misconceptionIds;

  /// §19 — mastery cần transfer/reflection; cơ chế dùng kernel có sẵn
  /// (TransferProbe WAL-103), blueprint chỉ YÊU CẦU.
  final bool transferRequired;
  final bool reflectionRequired;

  /// WAL-130 finding #1 → rule v0.1: TRẺ ĐI TRƯỚC. Blueprint quan-sát/sử-liệu
  /// đòi hành động đầu tiên là của TRẺ — mọi sự kiện mang hỗ trợ ≥ workedStep
  /// đứng TRƯỚC lần trả lời đầu tiên là vi phạm (demo-trước-quan-sát).
  /// Mặc định false: blueprint DẠY BÀI MỚI (vd B6 Khám phá) được làm mẫu trước.
  final bool learnerFirst;

  final PedagogySource source;
  final String version;
}

/// ⭐ Blueprint PHẢI kiểm được: đối chiếu MỘT PHIÊN THẬT (EvidenceLog) với
/// hợp đồng. Trả danh sách vi phạm — rỗng = phiên tuân thủ. Đây là mầm của
/// Pedagogy QA harness (WAL-131): assert bằng dữ liệu, không bằng lời.
List<String> blueprintViolations(
    LearningExperienceBlueprint bp, EvidenceLog log) {
  final out = <String>[];
  final cap = rungToSupport(bp.assistanceCap);

  for (final e in log.events) {
    final s = e.support;
    if (s != null && s.index > cap.index) {
      out.add('ASSISTANCE_OVER_CAP: ${e.eventId} ${s.name} > ${cap.name}');
    }
    if (e.skillCaseId.isNotEmpty &&
        !bp.skillCaseIds.contains(e.skillCaseId)) {
      out.add('CASE_OUT_OF_BLUEPRINT: ${e.eventId} ${e.skillCaseId}');
    }
  }

  if (bp.learnerFirst) {
    for (final e in log.events) {
      // Trẻ ĐÃ tự đi một bước (không hỗ trợ) — từ đây scaffold là hợp lệ.
      if (e.kind == EvidenceKind.independentAttempt ||
          e.kind == EvidenceKind.selfCorrection) {
        break;
      }
      // Mọi sự kiện (kể cả câu trả lời CÓ hỗ trợ) mang support ≥ workedStep
      // trước lần tự-làm đầu tiên = demo-trước-quan-sát.
      final s = e.support;
      if (s != null && s.index >= SupportLevel.workedStep.index) {
        out.add('LEARNER_FIRST_VIOLATED: ${e.eventId} ${s.name} trước lần tự làm đầu');
      }
    }
  }

  // Phiên CÓ TRẢ LỜI mới bị đòi evidenceRequired — phiên bỏ dở trước khi
  // trả lời không phải vi phạm hợp đồng (nó chỉ chưa hoàn thành).
  final answered = log.events.any((e) => e.isAttempt);
  if (answered) {
    for (final kind in bp.evidenceRequired) {
      if (!log.events.any((e) => e.kind == kind)) {
        out.add('EVIDENCE_MISSING: ${kind.name}');
      }
    }
  }
  return out;
}
