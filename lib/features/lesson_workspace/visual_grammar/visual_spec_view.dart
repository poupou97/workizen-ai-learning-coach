/// ⭐ LANE E2 (round 5) — MÀN HÌNH chủ cho `VisualSpec`: Lane B gắn được ngay.
///
/// Widget này KHÔNG thay `visual_view.dart` của Lane B. Nó là thứ Lane B có
/// thể gắn vào khi muốn: nhận một spec đã dựng sẵn, một hàm tra trang, một
/// hàm mở sheet nguồn — và không nhận `LessonDocument`, nên bản thân nó cũng
/// không rẽ nhánh theo bài được.
///
/// Cách gắn (6 dòng, không đổi file nào của Lane B):
/// ```dart
/// VisualSpecView(
///   spec: spec,                                   // nạp từ artefact
///   pageLabel: (id) {                             // mã máy → lời trẻ
///     final b = doc.blockById(id);
///     return b == null ? 'sách' : doc.sourceLineForBlock(b);
///   },
///   onOpenSource: (ref) => showSourceSheet(context, doc: doc,
///       block: doc.blockById(ref.primaryBlockId)!, onShowInRead: …),
/// )
/// ```
///
/// FAIL CLOSED ở ba chỗ, mỗi chỗ nói VÌ SAO bằng lời trẻ:
/// 1. không có spec (bài chưa có hình nào dựng được);
/// 2. họ hình chưa có renderer — SAM có dữ liệu nhưng chưa biết vẽ kiểu đó;
/// 3. renderer từ chối vì dữ liệu sai hình dạng.
/// Không chỗ nào rơi xuống «vẽ tạm một hình khác cho có».
library;

import 'package:flutter/material.dart';

import '../../../app/theme/wal_tokens.dart';
import '../../../core/visual_spec/derivation_lexicon.dart';
import '../../../core/visual_spec/visual_spec.dart';
import 'visual_family_renderer.dart';
import 'visual_registry.dart';

class VisualSpecView extends StatefulWidget {
  const VisualSpecView({
    super.key,
    required this.spec,
    required this.pageLabel,
    required this.onOpenSource,
    this.registry = defaultVisualRegistry,
  });

  /// `null` ⇒ bài này không dựng được hình nào — nói thật, không vẽ.
  final VisualSpec? spec;
  final PageLabelLookup pageLabel;
  final OpenSourceCallback onOpenSource;
  final VisualRendererRegistry registry;

  static const rootKey = Key('visual-spec-view');
  static const emptyKey = Key('visual-spec-empty');
  static const unsupportedKey = Key('visual-spec-unsupported');
  static const whyKey = Key('visual-spec-why');
  static Key sectionTabKey(String id) => Key('visual-spec-tab-$id');

  @override
  State<VisualSpecView> createState() => _VisualSpecViewState();
}

class _VisualSpecViewState extends State<VisualSpecView> {
  int _index = 0;

  @override
  Widget build(BuildContext context) {
    final spec = widget.spec;
    if (spec == null) return _failClosed(VisualSpecView.emptyKey, _noSpecLine);
    final sections = spec.sections;
    final current = sections[_index.clamp(0, sections.length - 1)];
    return SingleChildScrollView(
      key: VisualSpecView.rootKey,
      padding: const EdgeInsets.all(WalSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // COMPOSITION: hình chính trước, hình phụ sau — một bài có thể cần
          // dòng thời gian + nhân quả + phân cấp cùng lúc.
          if (sections.length > 1)
            Wrap(
              spacing: WalSpacing.sm,
              runSpacing: WalSpacing.xs,
              children: [
                for (var i = 0; i < sections.length; i++)
                  ChoiceChip(
                    key: VisualSpecView.sectionTabKey(sections[i].id),
                    label: Text(_tabLabel(sections[i])),
                    selected: _index == i,
                    showCheckmark: false,
                    onSelected: (_) => setState(() => _index = i),
                  ),
              ],
            ),
          const SizedBox(height: WalSpacing.sm),
          Text(
            current.title,
            style: const TextStyle(
              fontSize: WalType.title,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
            ),
          ),
          if (current.childSummary != null)
            Padding(
              padding: const EdgeInsets.only(top: 2),
              child: Text(
                current.childSummary!,
                style: const TextStyle(
                  fontSize: 13,
                  color: WalColors.inkSoft,
                ),
              ),
            ),
          const SizedBox(height: WalSpacing.sm),
          _body(current),
          const SizedBox(height: WalSpacing.md),
          _why(current),
        ],
      ),
    );
  }

  String _tabLabel(VisualSection s) {
    final b = widget.registry.bindingFor(s.family);
    // Họ chưa có renderer vẫn phải có tab — để trẻ thấy SAM có dữ liệu mà
    // chưa vẽ được, thay vì tab biến mất không lời giải thích.
    return b == null ? '❓ ${s.title}' : '${b.icon} ${b.childShapeLabel}';
  }

  Widget _body(VisualSection s) {
    final binding = widget.registry.bindingFor(s.family);
    if (binding == null) {
      return _failClosed(VisualSpecView.unsupportedKey, _noRendererLine);
    }
    final why = binding.renderer.unsupportedReason(s);
    if (why != null) {
      return _failClosed(VisualSpecView.unsupportedKey, _badShapeLine);
    }
    return binding.renderer.build(
      context,
      VisualRenderContext(
        section: s,
        pageLabel: widget.pageLabel,
        onOpenSource: widget.onOpenSource,
      ),
    );
  }

  /// «Vì sao SAM vẽ thế này» — tra theo LUẬT SINH, không theo kiểu Dart.
  Widget _why(VisualSection s) => Container(
    key: VisualSpecView.whyKey,
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: WalColors.surfaceLavender,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Vì sao SAM vẽ thế này',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.w700,
            color: WalColors.primaryText,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          childExplanationForRules(s.derivationRules),
          style: const TextStyle(
            fontSize: WalType.secondary,
            color: WalColors.ink,
            height: 1.4,
          ),
        ),
        if (s.hasInferredEdge)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              InferenceStatus.inferred.childNote!,
              style: const TextStyle(fontSize: 12, color: WalColors.inkSoft),
            ),
          ),
      ],
    ),
  );

  Widget _failClosed(Key key, String line) => Container(
    key: key,
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: WalColors.surface,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: Text(
      line,
      style: const TextStyle(
        fontSize: WalType.body,
        color: WalColors.ink,
        height: 1.4,
      ),
    ),
  );
}

// Ba câu fail-closed — lời trẻ, không mã máy, nói ĐÚNG lý do khác nhau.
const String _noSpecLine =
    'Bài này SAM chưa vẽ được sơ đồ nào. SAM chỉ vẽ khi tìm được đúng chỗ '
    'sách viết; bài này SAM chưa tìm được nên không tự vẽ — con đọc sách '
    'hoặc học cùng SAM nhé.';

const String _noRendererLine =
    'SAM có dữ liệu của phần này nhưng chưa biết vẽ thành hình. SAM không vẽ '
    'đại một hình khác đâu — con đọc trong sách nhé.';

const String _badShapeLine =
    'Phần này chưa đủ để SAM vẽ thành hình (SAM cần ít nhất hai ý và biết ý '
    'nào trước ý nào). Con đọc trong sách nhé.';
