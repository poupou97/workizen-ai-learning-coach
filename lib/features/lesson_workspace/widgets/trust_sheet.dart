/// ROUND 3 B1/B5 — sheet «Nguồn & độ tin» của MỘT bài trong Workspace.
///
/// Trả lời bốn câu mà chip một dòng không đủ chỗ: chữ/hình từ đâu (và tin
/// tới đâu), sơ đồ Trực quan xếp theo LUẬT nào, SAM ở đây là gì, và có ghi
/// bằng chứng học không. Mọi câu đều đọc từ `LessonDocument` — không có câu
/// nào là lời hứa. Mã luật (`tsl-enumerated-steps-v1`) và mã pipeline nằm ở
/// ĐÂY, không nằm trên màn trẻ đọc (B5: raw ids out of the child UI).
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/content_trust.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/semantic_data.dart';
import 'runtime_plan.dart';
import '../tutor_view.dart' show TutorView;

/// Chữ trẻ/phụ huynh đọc cho từng mức tin — không dịch «đẹp» hơn sự thật.
String trustChildDescription(ContentTrust t, LessonDocument doc) => switch (t) {
  ContentTrust.trustedCorpus =>
    'Nội dung đã qua cổng kiểm của Workizen — là nội dung sản phẩm.',
  ContentTrust.fixtureFromTrustedCorpus =>
    'Chữ và hình là NGUYÊN VĂN ${doc.pageRangeLine}, máy đọc từ sách qua bộ '
        'lọc nghiên cứu. Đây là bản dựng nội bộ để nhìn thấy sản phẩm — chưa '
        'qua cổng phát hành cho trẻ; chỗ máy chưa đọc chắc thì để trống và chỉ '
        'trang, không bịa.',
  ContentTrust.fixtureSynthetic =>
    'Chữ là MẪU GIẢ LẬP (mỗi đoạn có «[MẪU]») để chạy thử giao diện — không '
        'câu nào là lời sách.',
  ContentTrust.prototype =>
    'Phần này do người viết tay cho bản thử — không phải sách, không phải '
        'sách giáo viên.',
};

Future<void> showTrustSheet(
  BuildContext context, {
  required LessonDocument doc,
  String? learnerId,
}) {
  final script = doc.tutorScript;
  final plan = planForDoc(doc, learnerId: learnerId);
  final withheld = doc.blocks.whereType<WithheldBlock>().length;
  final images = doc.blocks.whereType<ImageBlock>().length;
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: WalColors.surface,
    showDragHandle: true,
    isScrollControlled: true,
    builder: (sheet) => SafeArea(
      child: SingleChildScrollView(
        key: const Key('trust-sheet'),
        padding: const EdgeInsets.fromLTRB(
          WalSpacing.lg,
          0,
          WalSpacing.lg,
          WalSpacing.lg,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Nguồn & độ tin của bài này',
              style: TextStyle(
                fontSize: WalType.title,
                fontWeight: FontWeight.w700,
                color: WalColors.ink,
              ),
            ),
            const SizedBox(height: WalSpacing.xs),
            Text(
              '🧪 ${fixtureChipLabel(doc.trust) ?? 'Nội dung sản phẩm'}',
              style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                color: WalColors.warnText,
              ),
            ),
            const SizedBox(height: WalSpacing.md),
            _section(
              '📖 Chữ và hình trong «Đọc»',
              trustChildDescription(doc.trust, doc),
              detail:
                  '${doc.blocks.length} phần · $images hình vùng trang (nội bộ) · '
                  '$withheld chỗ giữ lại',
            ),
            _section(
              '✨ Sơ đồ trong «Trực quan»',
              doc.semantic.isEmpty
                  ? 'Bài này chưa có sơ đồ — chỉ có bảng tóm tắt lời sách.'
                  : 'SAM chỉ XẾP LẠI lời sách theo luật tất định — không thêm '
                        'bước, không thêm chữ, không có đường «bài → AI → hình».',
              detail: doc.semantic.isEmpty
                  ? null
                  : [
                      for (final s in doc.semantic)
                        '${s.shapeLabel} «${s.title}» — luật ${s.derivation}',
                    ].join('\n'),
            ),
            _section(
              '🦉 SAM trong «Học với SAM»',
              script == null
                  ? 'Bài này chưa có kịch bản — SAM không hỏi gì.'
                  : '${SamMode.prototypeScripted.childLabel}: SAM đi theo kịch '
                        'bản viết sẵn ${script.steps.length} bước, hỏi '
                        '${script.asks.length} câu nguyên văn trong sách. Khoá '
                        'đáp án là bản nháp của người viết — KHÔNG phải sách '
                        'giáo viên. Khớp/không khớp chỉ so với bản nháp đó.',
              detail: script == null
                  ? null
                  : '${TutorView.runtimeLine(plan)}\n'
                        '${script.asks.firstOrNull?.keySource ?? ''}',
            ),
            _section(
              '📝 Bằng chứng học',
              'KHÔNG ghi. Mọi thao tác trong bài này không vào hồ sơ học của '
                  'con — «Đã xem» chỉ nói con đã mở, mất khi tắt app.',
            ),
            const SizedBox(height: WalSpacing.sm),
            const Text(
              'Ranh giới (giữ bằng kiểu dữ liệu và test)',
              style: TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                color: WalColors.ink,
              ),
            ),
            const SizedBox(height: 4),
            for (final c in BoundaryClaim.values)
              Padding(
                padding: const EdgeInsets.only(bottom: 2),
                child: Text(
                  '• ${c.statement}',
                  style: const TextStyle(fontSize: 13, color: WalColors.inkSoft),
                ),
              ),
            const SizedBox(height: WalSpacing.md),
            Text(
              'Nguồn máy: ${doc.provenance.sourcePipeline} · '
              '${doc.provenance.generator}\n${doc.provenance.distribution}',
              style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
            ),
            const SizedBox(height: WalSpacing.md),
            SizedBox(
              width: double.infinity,
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: () => Navigator.of(sheet).pop(),
                child: const Text(
                  'Đã hiểu',
                  style: TextStyle(
                    fontSize: WalType.body,
                    color: WalColors.primaryText,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

Widget _section(String title, String body, {String? detail}) => Padding(
  padding: const EdgeInsets.only(bottom: WalSpacing.sm),
  child: Container(
    width: double.infinity,
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: WalType.secondary,
            fontWeight: FontWeight.w700,
            color: WalColors.ink,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          body,
          style: const TextStyle(
            fontSize: WalType.secondary,
            color: WalColors.ink,
            height: 1.4,
          ),
        ),
        if (detail != null) ...[
          const SizedBox(height: 4),
          Text(
            detail,
            style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
          ),
        ],
      ],
    ),
  ),
);

/// Dùng ở màn Trực quan: mô tả một sơ đồ cho sheet (giữ ở đây để một chỗ).
String semanticRuleLine(SemanticData s) =>
    '${s.shapeLabel} «${s.title}» — luật ${s.derivation}';
