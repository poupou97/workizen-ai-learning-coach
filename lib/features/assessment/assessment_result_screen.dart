/// WAL-143 #22 — KẾT QUẢ KIỂM TRA: kể BẰNG CHỨNG, không quy ra điểm.
///
/// Ba luật màn này giữ:
/// 1. KHÔNG tỉ số/điểm/% — «2/3 đúng» là một con điểm đội lốt. Màn kể từng
///    câu đúng hay chưa đúng (sự việc), rồi để `explainConcept` nói câu kết
///    luận (suy luận có gác cổng).
/// 2. LÀM ĐÚNG HẾT KHÔNG THÀNH «GIỎI»: câu kết luận đi qua `ConceptSummary`
///    nên vài câu đúng vẫn chỉ ra «chưa đủ để kết luận» — bài kiểm tra không
///    được phép vượt quyền bằng chứng.
/// 3. PHIÊN THI PHẢI SẠCH: nếu `tutoringViolationsInExam` không rỗng thì màn
///    NÓI RA, không im lặng nuốt — một bài thi bị nhiễm dạy học thì kết luận
///    rút ra từ nó không dùng được.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/coach/parent_explanation.dart';
import '../../core/student/concept_summary.dart';
import '../../core/student/learning_evidence.dart';
import 'assessment_screen.dart' show AssessmentAnswer;

class AssessmentResultScreen extends StatelessWidget {
  const AssessmentResultScreen({
    super.key,
    required this.answers,
    required this.summary,
    this.violations = const [],
    this.onDone,
  });

  final List<AssessmentAnswer> answers;

  /// Đọc LẠI từ kho sau khi phiên đã ghi — không phải đếm tại chỗ.
  final ConceptSummary summary;
  final List<LearningEvent> violations;
  final VoidCallback? onDone;

  @override
  Widget build(BuildContext context) {
    final exp = explainConcept(summary,
        conceptDisplayName: 'cộng, trừ phân số khác mẫu số',
        caseDisplayNames: const {
          'denominator-divisible': 'một mẫu số chia hết cho mẫu số còn lại',
          'denominator-non-divisible': 'hai mẫu số không chia hết cho nhau',
        });
    final tok = switch (summary.claim) {
      ConceptClaim.mastered => LearningStateToken.mastered,
      ConceptClaim.strongOnObserved => LearningStateToken.strongOnObserved,
      ConceptClaim.developing => LearningStateToken.developing,
      ConceptClaim.needsWork => LearningStateToken.needsWork,
      ConceptClaim.insufficientEvidence =>
        LearningStateToken.insufficientEvidence,
      ConceptClaim.noEvidence => LearningStateToken.noEvidence,
    };
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            const Text('Con đã làm xong',
                style: TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.md),
            if (violations.isNotEmpty) ...[
              _card(
                Text(
                    'Phiên này có ${violations.length} lượt hỗ trợ lọt vào — '
                    'SAM KHÔNG dùng nó để kết luận con đã chắc hay chưa.',
                    style: const TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.ink,
                        height: 1.45)),
                color: LearningStateToken.needsWork.bg,
              ),
              const SizedBox(height: WalSpacing.md),
            ],
            const Text('TỪNG CÂU',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                    color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.sm),
            _card(Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  for (final a in answers) ...[
                    Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Text(
                          '${a.expr}  →  con trả lời ${a.raw}'
                          '${a.correct ? ' · đúng' : ' · chưa đúng'}',
                          style: const TextStyle(
                              fontSize: WalType.body,
                              color: WalColors.ink,
                              height: 1.4)),
                    ),
                  ],
                ])),
            const SizedBox(height: WalSpacing.md),
            // «Remediation SAU» — policy assessment KHÔNG cho chữa giữa chừng
            // (reviewAfter=false), nên chỗ này chỉ NÓI RA câu chưa chắc và
            // chỉ đúng đường đã có thật (chip «Ôn luyện» phát bài khác cùng
            // dạng). Không hứa một lịch mà máy không thực sự giữ.
            if (answers.any((a) => !a.correct)) ...[
              const Text('CÒN CHƯA CHẮC CHỖ NÀO',
                  style: TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.6,
                      color: WalColors.inkSoft)),
              const SizedBox(height: WalSpacing.sm),
              _card(Text(
                  'Câu ${answers.where((a) => !a.correct).map((a) => a.expr).join(', ')} '
                  'con làm chưa đúng. Khi nào con bấm «Ôn luyện», SAM cho con '
                  'làm lại một bài khác cùng dạng — sai một câu chưa nói lên '
                  'điều gì, làm thêm mới biết.',
                  style: const TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.45))),
              const SizedBox(height: WalSpacing.md),
            ],
            const Text('SAM KẾT LUẬN ĐƯỢC GÌ',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 0.6,
                    color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.sm),
            _card(
              Text(exp.message,
                  style: const TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.ink,
                      height: 1.5)),
              color: tok.bg,
            ),
            const SizedBox(height: WalSpacing.lg),
            SizedBox(
              height: WalSpacing.minTouch + 8,
              child: FilledButton(
                style: FilledButton.styleFrom(
                    backgroundColor: WalColors.primary500),
                onPressed: onDone ?? () => Navigator.of(context).pop(),
                child: const Text('Về Hôm nay',
                    style: TextStyle(fontSize: WalType.body)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _card(Widget child, {Color color = Colors.white}) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );
}
