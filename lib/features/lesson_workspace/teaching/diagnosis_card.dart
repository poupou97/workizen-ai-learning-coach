/// TRACK B ROUND 7 · V2 — trình bày [AnswerDiagnosis] DƯỚI lời SAM.
///
/// Lượt phản hồi theo lỗi trông thế này trên máy:
///
///   🦉 SAM (kịch bản thử nghiệm)            Câu 1/3
///   ┌───────────────────────────────────────────────┐
///   │ Con chọn «Lọc». Sách viết — Dùng để tách:      │ ← headline, NHẮC LẠI
///   │ tách chất rắn không tan ra khỏi chất lỏng.     │   lựa chọn của TRẺ
///   └───────────────────────────────────────────────┘
///   BÀI NÀY DÙNG Ở ĐÂU
///   → Lọc nước từ hỗn hợp nước lẫn đất  ✨→          ← chạm là nhảy tới
///   ┌ SAM chỉ biết chừng này ──────────────────────┐ ← chỉ ở nhánh «chưa đủ
///   │ …KHÔNG kết luận gì về việc con hiểu hay chưa │   bằng chứng»
///   └───────────────────────────────────────────────┘
///   ↺ Thử lại  con đọc lại câu hỏi, rồi soi vào…    ← vòng lặp chưa đóng
///
/// KHÔNG có: điểm, sao, phần trăm, «gần rồi», «con giỏi/kém». Không có chữ
/// nào của một bài cụ thể — widget chỉ vẽ mô hình được truyền vào.
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../views/visual_explain.dart';
import 'answer_diagnosis.dart';

class DiagnosisCard extends StatelessWidget {
  const DiagnosisCard({
    super.key,
    required this.diagnosis,
    this.onOpenLink,
    this.onShowInRead,
  });

  final AnswerDiagnosis diagnosis;

  /// Chạm một liên hệ ⇒ mở sơ đồ ấy trong Trực quan.
  final void Function(ExplainLink link)? onOpenLink;

  /// «📖 Xem trong Đọc» cho block sách của thứ trẻ chọn.
  final void Function(String blockId)? onShowInRead;

  static const rootKey = Key('tutor-diagnosis');
  static const limitKey = Key('tutor-diagnosis-limit');
  static const retryKey = Key('tutor-diagnosis-retry');
  static const linksEmptyKey = Key('tutor-diagnosis-links-empty');
  static Key kindKey(DiagnosisKind k) => Key('tutor-diagnosis-${k.name}');
  static Key factKey(String name) => Key('tutor-diagnosis-fact-$name');
  static Key linkKey(String semanticId) =>
      Key('tutor-diagnosis-link-$semanticId');

  @override
  Widget build(BuildContext context) {
    final d = diagnosis;
    return Column(
      key: rootKey,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Nhánh nào đang chạy — để test (và Founder) đọc được trên chính cây
        // widget rằng ba nhánh là THẬT, không phải một câu đổi chữ.
        SizedBox(key: kindKey(d.kind), height: 0, width: 0),
        for (final f in d.facts) ...[
          _labelled(
            f.name,
            Text(
              f.value ?? '— sách không nói ở phần này',
              key: factKey(f.name),
              style: TextStyle(
                fontSize: WalType.secondary,
                color: f.value == null ? WalColors.inkSoft : WalColors.ink,
                height: 1.45,
                fontStyle:
                    f.value == null ? FontStyle.italic : FontStyle.normal,
              ),
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        if (d.links.isNotEmpty) ...[
          _sectionLabel(explainLinksLabel),
          for (final l in d.links)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Material(
                color: Colors.white,
                borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                child: InkWell(
                  key: linkKey(l.semanticId),
                  borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                  onTap: onOpenLink == null ? null : () => onOpenLink!(l),
                  child: Padding(
                    padding: const EdgeInsets.all(WalSpacing.sm),
                    child: Row(
                      children: [
                        Expanded(
                          child: Text(
                            l.title,
                            style: const TextStyle(
                              fontSize: WalType.secondary,
                              fontWeight: FontWeight.w600,
                              color: WalColors.ink,
                              height: 1.35,
                            ),
                          ),
                        ),
                        if (onOpenLink != null)
                          const Text(
                            '✨ →',
                            style: TextStyle(
                              fontSize: WalType.secondary,
                              color: WalColors.primaryText,
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ] else if (d.linksEmptyNote != null) ...[
          _sectionLabel(explainLinksLabel),
          Text(
            d.linksEmptyNote!,
            key: linksEmptyKey,
            style: const TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.inkSoft,
              height: 1.45,
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        if (d.limitNote != null) ...[
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(WalSpacing.sm),
            decoration: BoxDecoration(
              color: LearningStateToken.insufficientEvidence.bg,
              borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'SAM CHỈ BIẾT CHỪNG NÀY',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w700,
                    letterSpacing: .6,
                    color: WalColors.inkSoft,
                  ),
                ),
                const SizedBox(height: 3),
                Text(
                  d.limitNote!,
                  key: limitKey,
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.ink,
                    height: 1.45,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: WalSpacing.sm),
        ],
        if (d.sourceBlockId != null && onShowInRead != null)
          SizedBox(
            height: WalSpacing.minTouch,
            child: TextButton(
              key: const Key('tutor-diagnosis-in-read'),
              style: TextButton.styleFrom(
                alignment: Alignment.centerLeft,
                padding: EdgeInsets.zero,
              ),
              onPressed: () => onShowInRead!(d.sourceBlockId!),
              child: const Text(
                '📖 Xem chỗ này trong sách',
                style: TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.primaryText,
                ),
              ),
            ),
          ),
        if (d.retry != null)
          Row(
            key: retryKey,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                '↺ ',
                style: TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.primaryText,
                ),
              ),
              Expanded(
                child: Text.rich(
                  TextSpan(
                    children: [
                      const TextSpan(
                        text: '$diagnosisRetryLabel — ',
                        style: TextStyle(fontWeight: FontWeight.w700),
                      ),
                      TextSpan(text: d.retry!),
                    ],
                  ),
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.primaryText,
                    height: 1.4,
                  ),
                ),
              ),
            ],
          ),
      ],
    );
  }

  static Widget _sectionLabel(String label) => Padding(
    padding: const EdgeInsets.only(bottom: 4),
    child: Text(
      label,
      style: const TextStyle(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        letterSpacing: .6,
        color: WalColors.primaryText,
      ),
    ),
  );

  static Widget _labelled(String label, Widget child) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        label,
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          letterSpacing: .4,
          color: WalColors.inkSoft,
        ),
      ),
      const SizedBox(height: 3),
      Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.sm),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        ),
        child: child,
      ),
    ],
  );
}
