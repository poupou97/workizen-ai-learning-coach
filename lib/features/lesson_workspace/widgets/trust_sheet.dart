/// ROUND 3 B1/B5 — sheet «Nguồn & độ tin» của MỘT bài trong Workspace.
///
/// Trả lời bốn câu mà chip một dòng không đủ chỗ: chữ/hình từ đâu (và tin
/// tới đâu), sơ đồ Trực quan xếp theo LUẬT nào, SAM ở đây là gì, và có ghi
/// bằng chứng học không. Mọi câu đều đọc từ `LessonDocument` — không có câu
/// nào là lời hứa.
///
/// ROUND 4 (§6.4 «trust/source explanation in child language»): sheet xếp
/// theo NGƯỜI ĐỌC — «Nói với con» (lời trẻ 11 tuổi, giải nghĩa «nguồn SGK có
/// cấu trúc, chưa kiểm định»), rồi sơ đồ / SAM / bằng chứng, rồi «Dành cho bố
/// mẹ» (cổng, giấy phép, sáu bất đẳng thức), và mã luật / mã pipeline / mã
/// runtime chỉ nằm trong nếp gấp «Chi tiết kỹ thuật» (đóng mặc định, §6.9).
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/lesson_model/content_trust.dart';
import '../../../core/lesson_model/lesson_document.dart';
import '../../../core/lesson_model/semantic_data.dart';
import '../tutor_view.dart' show TutorView;
import 'runtime_plan.dart';
import 'tech_details.dart';

/// Chữ trẻ đọc cho từng mức tin — không dịch «đẹp» hơn sự thật.
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
  // Round 4: «nguồn SGK có cấu trúc, chưa kiểm định» nói bằng lời trẻ 11 tuổi.
  ContentTrust.trustedStructuredLesson =>
    'Chữ và hình trong bài là chữ và hình của ${doc.pageRangeLine} — máy chép '
        'lại từ sách, nhớ cả số trang và chỗ đứng của từng đoạn.\n\n'
        '«Chưa kiểm định» nghĩa là: chưa có người lớn soát lại từng chữ máy '
        'chép, nên có thể còn lỗi nhỏ (một dấu, một chữ). Thấy chỗ nào lạ, con '
        'mở sách giấy ra so — số trang ghi ngay bên cạnh.\n\n'
        'Chỗ nào máy chưa chắc đọc đúng, SAM để trống và chỉ trang — không '
        'đoán.',
  ContentTrust.withheld =>
    'Phần này máy chưa đọc chắc nên KHÔNG hiện chữ — chỉ chỉ trang trong '
        'sách, không bịa.',
};

/// Dòng cho bố mẹ — cổng nào chưa qua, vì sao chip không tắt, không ghi gì.
String trustParentLine(LessonDocument doc) => switch (doc.trust) {
  ContentTrust.trustedCorpus =>
    'Nội dung đã qua cổng kiểm và có giấy phép phát hành.',
  ContentTrust.fixtureSynthetic =>
    'Bản mẫu giả lập chỉ để chạy thử giao diện — không có nội dung sách. '
        'Con làm gì trong bài này cũng không được ghi làm bằng chứng học.',
  _ =>
    'Bản dựng nội bộ để xem sản phẩm. Chữ sách trích nguyên văn qua một đường '
        'có cấu trúc (giữ trang và vị trí từng đoạn); chưa qua cổng kiểm-tin-giả '
        'và chưa có giấy phép phát hành — vì vậy chip «Bản thử nghiệm» không '
        'tắt được. Con làm gì trong bài này cũng không được ghi làm bằng chứng '
        'học; «Đã xem» chỉ nói con đã mở.',
};

/// Sự thật máy của cả bài — cho nếp gấp kỹ thuật (mã luật, pipeline, runtime).
List<String> trustTechLines(LessonDocument doc, {String? learnerId}) {
  final p = doc.provenance;
  final plan = planForDoc(doc, learnerId: learnerId);
  final script = doc.tutorScript;
  return [
    for (final s in doc.semantic) semanticRuleLine(s),
    if (script != null) 'Runtime: ${TutorView.runtimeLineTechnical(plan)}',
    if (script?.asks.firstOrNull != null)
      'Khoá đáp án: ${script!.asks.first.keySource}',
    'Nguồn máy: ${p.sourcePipeline} · ${p.generator}',
    if (p.pipelineVersion != null) 'Phiên bản pipeline: ${p.pipelineVersion}',
    if (p.sdmVersion != null) 'Mô hình: ${p.sdmVersion}',
    'Kiểm-tin-giả: ${p.auditStatus.name}'
        '${p.auditRef != null ? ' · ${p.auditRef}' : ''}',
    if (p.boundaryConfidence != null)
      'Ranh giới bài: tin cậy ${p.boundaryConfidence!.toStringAsFixed(2)}'
          '${p.boundary?.source != null ? ' · ${p.boundary!.source}' : ''}',
    if (p.sourceHash != null)
      'Băm nguồn: ${p.sourceHash!.substring(0, p.sourceHash!.length.clamp(0, 12))}…',
    p.distribution,
    'Giấy phép: ${doc.licence.name}',
  ];
}

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
              '📖 Nói với con: chữ và hình trong «Đọc»',
              trustChildDescription(doc.trust, doc),
              detail:
                  '${doc.blocks.length} phần · $images hình · '
                  '$withheld chỗ SAM để trống',
            ),
            _section(
              '✨ Sơ đồ trong «Trực quan»',
              doc.semantic.isEmpty
                  ? 'Bài này chưa có sơ đồ — chỉ có bảng tóm tắt lời sách.'
                  : 'SAM chỉ XẾP LẠI lời sách theo luật có sẵn — không thêm '
                        'bước, không thêm chữ, không có đường «bài → AI → hình».',
              detail: doc.semantic.isEmpty
                  ? null
                  : [
                      for (final s in doc.semantic) '${s.shapeLabel} «${s.title}»',
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
              detail: script == null ? null : TutorView.runtimeLine(plan),
            ),
            _section(
              '📝 Bằng chứng học',
              'KHÔNG ghi. Mọi thao tác trong bài này không vào hồ sơ học của '
                  'con — «Đã xem» chỉ nói con đã mở, mất khi tắt app.',
            ),
            _section(
              '👨‍👩‍👧 Dành cho bố mẹ',
              trustParentLine(doc),
              detail: [
                'Ranh giới (giữ bằng kiểu dữ liệu và test):',
                for (final c in BoundaryClaim.values) '• ${c.statement}',
              ].join('\n'),
            ),
            TechDetails(lines: trustTechLines(doc, learnerId: learnerId)),
            const SizedBox(height: WalSpacing.sm),
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
            style: const TextStyle(
              fontSize: 12,
              color: WalColors.inkSoft,
              height: 1.35,
            ),
          ),
        ],
      ],
    ),
  ),
);

/// Mô tả một sơ đồ kèm mã luật — CHỈ cho nếp gấp kỹ thuật.
String semanticRuleLine(SemanticData s) =>
    '${s.shapeLabel} «${s.title}» — luật ${s.derivation}';
