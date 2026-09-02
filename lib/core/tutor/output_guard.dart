/// WAL-30 SHADOW — OUTPUT GUARD: «LLM proposes, ENGINE VALIDATES».
///
/// Bằng chứng từ 50 shadow-run (2026-09-02): dưới adversarial nudge («anh
/// tớ bảo dùng BCNN»), 5/5 run của model escalate — rò tên method cấm,
/// rò con-số-dẫn-xuất (4×5=20) ở mức hint, và vỡ luật khen dưới áp lực
/// xã giao («anh em tớ thông minh»). Kết luận ma trận quyền: wording là
/// của LLM, nhưng KHÔNG lời nào tới trẻ mà không qua guard tất định này.
///
/// GHI THẬT giới hạn v1: chặn được TÊN cấm + CON SỐ dẫn xuất + từ khen cấm
/// + tutoring-trong-exam; KHÔNG chặn được mô-tả-phép-tính thuần lời
/// («lấy hai mẫu nhân với nhau») — lỗ đó cần semantic check (L3) và là
/// một lý do khuyến nghị KEEP SHADOW.
library;

import '../student/mastery.dart';
import 'tutor_feedback.dart' show bannedAbilityPraise;

class GuardVerdict {
  const GuardVerdict(this.allowed, this.blockedReasons);
  final bool allowed;
  final List<String> blockedReasons;
}

/// Sự thật dẫn xuất của MỘT bài — engine tính, guard dùng để chặn rò.
class DerivedFacts {
  const DerivedFacts({
    required this.commonDenominator,
    required this.answerForms,
    this.intermediateForms = const [],
  });

  /// vd 20 — CẤM xuất hiện khi mức ≤ hint (hint gợi hướng, không cho số).
  final int commonDenominator;

  /// vd ['19/20'] — CẤM khi chưa fullSolution.
  final List<String> answerForms;

  /// vd ['15/20', '4/20'] — bước trung gian, CẤM khi ≤ hint.
  final List<String> intermediateForms;
}

GuardVerdict validateTutorOutput({
  required String text,
  required SupportLevel maxAllowed,
  required DerivedFacts facts,
  List<String> forbiddenMethodTerms = const ['bcnn', 'bội chung'],
  bool examMode = false,

  /// Sự thật TRẺ ĐÃ TỰ NÊU trong lượt của mình («19/20 đúng không?») —
  /// SAM xác nhận lại KHÔNG phải reveal. Bài học từ 4 false-positive s07:
  /// guard không có ngữ cảnh input sẽ phạt oan lời xác nhận.
  List<String> childStatedFacts = const [],
}) {
  final low = text.toLowerCase();
  final squashed = text.replaceAll(' ', '');
  final reasons = <String>[];

  // ── tên method cấm: không nhắc, kể cả khi từ chối (baseline không nhắc) ──
  for (final term in forbiddenMethodTerms) {
    if (low.contains(term)) reasons.add('METHOD_NAME:$term');
  }

  // ── luật khen: áp cho MỌI đối tượng («anh em tớ thông minh» vẫn cấm) ──
  for (final b in bannedAbilityPraise) {
    if (low.contains(b)) reasons.add('PRAISE:$b');
  }

  // ── exam: không lời dạy nào — chặn mọi từ khoá phương pháp/bước ──
  if (examMode) {
    for (final w in ['quy đồng', 'mẫu số chung', 'nhân', '×', 'gợi ý:']) {
      if (low.contains(w.toLowerCase())) {
        reasons.add('EXAM_TUTORING:$w');
        break;
      }
    }
  }

  // ── rò con số dẫn xuất theo mức cho phép (trừ thứ trẻ đã tự nêu) ──
  bool childSaid(String f) => childStatedFacts.contains(f);
  final cd = facts.commonDenominator.toString();
  if (maxAllowed.index <= SupportLevel.hint.index) {
    if (RegExp('(^|[^0-9])$cd([^0-9]|\$)').hasMatch(squashed)) {
      reasons.add('ESCALATION:common-denominator-$cd-at-hint');
    }
    for (final f in facts.intermediateForms) {
      if (squashed.contains(f)) reasons.add('ESCALATION:$f-at-hint');
    }
  }
  if (maxAllowed != SupportLevel.fullSolution) {
    for (final a in facts.answerForms) {
      if (squashed.contains(a)) reasons.add('REVEAL:$a');
    }
  }

  return GuardVerdict(reasons.isEmpty, reasons);
}
