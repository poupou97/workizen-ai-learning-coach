/// TRACK B — MODE 1 «Đọc» (Smart Book): cấu trúc bài TRUNG THÀNH với sách.
///
/// Hybrid native + source-region (04-SMART-BOOK §4): block tin được ⇒ chữ
/// native, đổi được cỡ chữ; hình ⇒ crop vùng trang (nội bộ) + caption của
/// sách; vùng bị giữ lại ⇒ placeholder thật thà, KHÔNG BAO GIỜ là chữ.
/// Chạm một đoạn ⇒ «Hỏi SAM về đoạn này» (nhảy Mode 3 mang theo block).
///
/// ROUND 3 B2 (concept khung 4 «Đọc như sách»):
/// - ĐIỀU HƯỚNG THEO TRANG: hàng chip «Trang 60 · 61 · 62 · 63» (từ trang IN
///   của block, không bịa) + vạch «— trang N —» tại chỗ đổi trang trong thứ tự
///   đọc ⇒ trẻ/phụ huynh đối chiếu được với sách giấy trên bàn.
/// - HÌNH & CHÚ THÍCH: hình đứng cạnh nhau trong sách (block hình liên tiếp)
///   dựng thành MỘT HÀNG; chú thích liên tiếp gộp thành một cụm dưới hàng —
///   đúng bố cục trang. KHÔNG gán chú thích vào hình theo liên kết máy
///   (`captionBlockId`): liên kết của pipeline còn sai (O5) và gán sai là
///   biến điều chưa chắc thành sự thật sách.
/// - NHÃN MỤC: «MỤC TIÊU» 🎯 · «Em đã học» 📌 · «Em có biết?» 💡 — chỉ là
///   biểu tượng trang trí theo chữ có sẵn, không thêm chữ.
///
/// ROUND 4 (§6.3 readability · §6.8 crop/caption display-side):
/// - ĐOẠN VĂN là chữ liền như trang sách (không mỗi đoạn một thẻ trắng — trên
///   Nokia round 3 một trang thành 8 thẻ rời); thẻ chỉ dành cho câu hỏi,
///   hoạt động, chỗ để trống.
/// - HÌNH + CHÚ THÍCH liền kề dựng thành MỘT khối «hình» (ảnh → chú thích →
///   dòng nguồn) — vẫn theo thứ tự đọc, không theo liên kết máy.
/// - CHE MÉP ẢNH (`bleedScale`): crop pipeline còn dính chữ/chú thích hàng
///   xóm ở mép (D-R3-05); UI phóng 14 % trong hộp giữ tỉ lệ để ~6 % mỗi mép
///   ra ngoài vùng nhìn. Không sửa ảnh, không sửa bbox (Lane A-pipeline); sheet
///   «Sách viết» vẫn hiện ảnh nguyên gốc.
/// - DÒNG NGUỒN cuối bài: chỉ «SGK … · trang …»; mã pipeline của dòng nguồn
///   máy sinh rời màn trẻ đọc (nếp gấp kỹ thuật trong sheet).
///
/// Không phát sự kiện học nào: view này là hàm thuần của `LessonDocument`.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/lesson_document.dart';
import 'widgets/source_sheet.dart';
import 'widgets/withheld_card.dart';

class SmartBookView extends StatefulWidget {
  const SmartBookView({
    super.key,
    required this.doc,
    required this.fontStep,
    required this.onFontStep,
    required this.onAskSam,
    this.scrollToBlockId,
    this.header,
  });

  final LessonDocument doc;

  /// 0 = vừa (17sp), 1 = to (19sp), 2 = rất to (22sp) — thân bài ≥16sp.
  final int fontStep;
  final void Function(int step) onFontStep;
  final void Function(LessonBlock block) onAskSam;
  final String? scrollToBlockId;

  /// ⭐ ROUND 4 §6.3 (lỗi đo trên Nokia 6.1): khung CỐ ĐỊNH của workspace
  /// (breadcrumb + chip + ba tab + thẻ «SAM đề xuất») chiếm 820/1920 px —
  /// 43 % màn — nên trang sách chỉ còn hơn nửa màn để đọc. Thẻ đề xuất là LỜI
  /// KHUYÊN, không phải thanh điều hướng: ở màn Đọc nó đi vào ĐẦU vùng cuộn
  /// (vẫn là thứ đầu tiên trẻ thấy) rồi cuộn đi, trả lại chiều cao cho trang.
  /// `null` ⇒ như cũ. Không cắt chữ lý do (D-R3-03 giữ nguyên).
  final Widget? header;

  static const fontSteps = [17.0, 19.0, 22.0];

  /// ROUND 4 §6.8 — phóng ảnh trong hộp giữ tỉ lệ để che mép dính chữ.
  static const bleedScale = 1.14;

  static Key pageChipKey(int page) => Key('smart-book-page-$page');
  static Key figureKey(String firstImageId) => Key('smart-book-figure-$firstImageId');

  /// Biểu tượng cho nhãn mục của SÁCH — chỉ trang trí theo chữ có sẵn.
  static String stageIcon(String label) {
    final l = label.trim().toLowerCase();
    if (l.startsWith('mục tiêu')) return '🎯';
    if (l.startsWith('em đã học')) return '📌';
    if (l.startsWith('em có biết')) return '💡';
    return '';
  }

  /// Trang IN của một block (hình của TSL không mang trang in ⇒ suy từ block
  /// chữ cùng trang PDF); không suy được ⇒ `null`.
  static int? pageOf(LessonDocument doc, LessonBlock b) =>
      b.sourceRef.pagePrinted ?? doc.printedPageFor(b.sourceRef.pagePdf);

  /// Các trang in của bài theo thứ tự đọc — chỉ trang CÓ block.
  static List<int> pagesOf(LessonDocument doc) {
    final out = <int>[];
    for (final b in doc.blocks) {
      if (b is SourceRefBlock) continue;
      final p = pageOf(doc, b);
      if (p != null && !out.contains(p)) out.add(p);
    }
    return out;
  }

  /// Dòng nguồn cuối bài cho trẻ: bỏ mã pipeline mà bộ sinh gắn vào đuôi
  /// («… · tc2-p1 / sdm-v2») — chỉ khi tài liệu KHAI `pipelineVersion` (dữ
  /// liệu nói, không đoán); tài liệu mẫu giữ nguyên chữ («FIXTURE MẪU»).
  static String childSourceRefText(LessonDocument doc, String text) {
    final pv = doc.provenance.pipelineVersion;
    if (pv == null) return text;
    var out = text;
    for (final tok in pv.split('/')) {
      final t = tok.trim();
      if (t.isNotEmpty) out = out.replaceAll(t, '');
    }
    out = out
        .replaceAll(RegExp(r'\s*/\s*'), ' ')
        .replaceAll(RegExp(r'(\s*·\s*)+$'), '')
        .replaceAll(RegExp(r'\s{2,}'), ' ')
        .trim();
    return out.isEmpty ? doc.pageRangeLine : out;
  }

  @override
  State<SmartBookView> createState() => _SmartBookViewState();
}

/// Một «mảnh» bố cục: một block thường, MỘT KHỐI hình (hàng ảnh + chú thích
/// liền kề), hoặc MỘT CỤM chú thích mồ côi.
sealed class _Piece {
  const _Piece();
}

final class _One extends _Piece {
  const _One(this.block);
  final LessonBlock block;
}

final class _Figure extends _Piece {
  const _Figure(this.images, this.captions);
  final List<ImageBlock> images;
  final List<CaptionBlock> captions;
}

final class _CaptionGroup extends _Piece {
  const _CaptionGroup(this.captions);
  final List<CaptionBlock> captions;
}

class _SmartBookViewState extends State<SmartBookView> {
  final Map<String, GlobalKey> _keys = {};
  final Map<int, GlobalKey> _pageKeys = {};
  final _scroll = ScrollController();

  @override
  void initState() {
    super.initState();
    _scheduleScroll();
  }

  @override
  void didUpdateWidget(SmartBookView old) {
    super.didUpdateWidget(old);
    if (old.scrollToBlockId != widget.scrollToBlockId) _scheduleScroll();
  }

  void _scheduleScroll() {
    final id = widget.scrollToBlockId;
    if (id == null) return;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final ctx = _keys[id]?.currentContext;
      if (ctx != null && mounted) {
        // Round 3 n1 D-R3-10: 0.08 để nhãn «Em đã học» bị cắt sát mép trên
        // thân View trên Nokia — neo thấp hơn một chút cho block đứng trọn.
        Scrollable.ensureVisible(
          ctx,
          alignment: 0.14,
          duration: WalMotion.stage,
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _jumpToPage(int page) {
    final ctx = _pageKeys[page]?.currentContext;
    if (ctx == null) return;
    Scrollable.ensureVisible(
      ctx,
      alignment: 0.0,
      duration: WalMotion.stage,
      curve: Curves.easeOut,
    );
  }

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  double get _body => SmartBookView.fontSteps[widget.fontStep.clamp(0, 2)];

  /// Gộp block liên tiếp: hàng ảnh + chú thích ngay sau ⇒ một khối hình; chú
  /// thích không có ảnh trước ⇒ cụm mồ côi. Thứ tự đọc giữ nguyên.
  static List<_Piece> piecesOf(List<LessonBlock> blocks) {
    final out = <_Piece>[];
    var i = 0;
    while (i < blocks.length) {
      final b = blocks[i];
      if (b is ImageBlock) {
        final images = <ImageBlock>[];
        while (i < blocks.length && blocks[i] is ImageBlock) {
          images.add(blocks[i] as ImageBlock);
          i++;
        }
        final captions = <CaptionBlock>[];
        while (i < blocks.length && blocks[i] is CaptionBlock) {
          captions.add(blocks[i] as CaptionBlock);
          i++;
        }
        out.add(_Figure(images, captions));
        continue;
      }
      if (b is CaptionBlock) {
        final run = <CaptionBlock>[];
        while (i < blocks.length && blocks[i] is CaptionBlock) {
          run.add(blocks[i] as CaptionBlock);
          i++;
        }
        out.add(_CaptionGroup(run));
        continue;
      }
      out.add(_One(b));
      i++;
    }
    return out;
  }

  LessonBlock _firstBlockOf(_Piece p) => switch (p) {
    _One(:final block) => block,
    _Figure(:final images) => images.first,
    _CaptionGroup(:final captions) => captions.first,
  };

  @override
  Widget build(BuildContext context) {
    final doc = widget.doc;
    final pages = SmartBookView.pagesOf(doc);
    final pieces = piecesOf(doc.blocks);
    int? lastPage;
    final children = <Widget>[];
    for (final p in pieces) {
      final first = _firstBlockOf(p);
      final page = first is SourceRefBlock
          ? null
          : SmartBookView.pageOf(doc, first);
      if (page != null && page != lastPage) {
        children.add(
          KeyedSubtree(
            key: _pageKeys.putIfAbsent(page, GlobalKey.new),
            child: _pageDivider(page, first: lastPage == null),
          ),
        );
        lastPage = page;
      }
      children.add(_piece(p));
      children.add(
        SizedBox(
          height: switch (first) {
            HeadingBlock() => WalSpacing.xs,
            ParagraphBlock() => WalSpacing.sm - 2,
            _ => WalSpacing.sm,
          },
        ),
      );
    }
    return SingleChildScrollView(
      controller: _scroll,
      padding: const EdgeInsets.fromLTRB(
        WalSpacing.md,
        WalSpacing.sm,
        WalSpacing.md,
        WalSpacing.xl,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (widget.header != null) ...[
            widget.header!,
            const SizedBox(height: WalSpacing.sm),
          ],
          if (pages.length > 1) _pageChips(pages),
          _fontControl(),
          const SizedBox(height: WalSpacing.sm),
          ...children,
          const SizedBox(height: WalSpacing.md),
          Text(
            'Hết bài · ${doc.pageRangeLine}',
            textAlign: TextAlign.center,
            style: const TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.inkSoft,
            ),
          ),
        ],
      ),
    );
  }

  Widget _pageChips(List<int> pages) => Padding(
    padding: const EdgeInsets.only(bottom: WalSpacing.xs),
    child: Row(
      children: [
        const Text(
          'Trang',
          style: TextStyle(
            fontSize: WalType.secondary,
            color: WalColors.inkSoft,
          ),
        ),
        const SizedBox(width: WalSpacing.sm),
        Expanded(
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                for (final p in pages)
                  Padding(
                    padding: const EdgeInsets.only(right: WalSpacing.xs),
                    child: SizedBox(
                      height: WalSpacing.minTouch,
                      child: TextButton(
                        key: SmartBookView.pageChipKey(p),
                        onPressed: () => _jumpToPage(p),
                        style: TextButton.styleFrom(
                          backgroundColor: Colors.white,
                          foregroundColor: WalColors.primaryText,
                          minimumSize: const Size(WalSpacing.minTouch, 0),
                          padding: const EdgeInsets.symmetric(
                            horizontal: WalSpacing.sm + 2,
                          ),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(
                              WalSpacing.radiusChip,
                            ),
                          ),
                        ),
                        child: Text(
                          '$p',
                          style: const TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
      ],
    ),
  );

  Widget _fontControl() => Row(
    children: [
      const Text(
        'Cỡ chữ',
        style: TextStyle(fontSize: WalType.secondary, color: WalColors.inkSoft),
      ),
      const Spacer(),
      for (var i = 0; i < SmartBookView.fontSteps.length; i++)
        SizedBox(
          width: WalSpacing.minTouch,
          height: WalSpacing.minTouch,
          child: TextButton(
            onPressed: () => widget.onFontStep(i),
            style: TextButton.styleFrom(
              backgroundColor: widget.fontStep == i
                  ? WalColors.primary500
                  : Colors.white,
              foregroundColor: widget.fontStep == i
                  ? Colors.white
                  : WalColors.ink,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              ),
            ),
            child: Text(
              'A',
              style: TextStyle(fontSize: 13.0 + i * 3, height: 1),
            ),
          ),
        ),
    ],
  );

  /// «— trang N —»: mốc đối chiếu với sách giấy; trang đầu là dòng mở bài.
  Widget _pageDivider(int page, {required bool first}) => Padding(
    padding: EdgeInsets.only(top: first ? 0 : WalSpacing.md, bottom: 2),
    child: Row(
      children: [
        Expanded(child: Divider(color: WalColors.inkSoft.withValues(alpha: 0.3))),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: WalSpacing.sm),
          child: Text(
            'trang $page',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w700,
              color: WalColors.inkSoft,
              letterSpacing: 0.5,
            ),
          ),
        ),
        Expanded(child: Divider(color: WalColors.inkSoft.withValues(alpha: 0.3))),
      ],
    ),
  );

  Widget _piece(_Piece p) => switch (p) {
    _One(:final block) => KeyedSubtree(
      key: _keys.putIfAbsent(block.id, GlobalKey.new),
      child: _block(block),
    ),
    _Figure(:final images, :final captions) => _figure(images, captions),
    _CaptionGroup(:final captions) => _captionGroup(captions),
  };

  Widget _block(LessonBlock b) => switch (b) {
    HeadingBlock() => _heading(b),
    // ROUND 4: đoạn văn là chữ liền như trang sách — không thẻ.
    ParagraphBlock(:final text) => _tappable(
      b,
      child: Padding(
        padding: const EdgeInsets.symmetric(
          horizontal: WalSpacing.xs,
          vertical: 2,
        ),
        child: Text(text, style: _bodyStyle()),
      ),
    ),
    ImageBlock() => _figure([b], const []),
    CaptionBlock() => _captionGroup([b]),
    TableBlock() => _table(b),
    QuestionBlock(:final text) => _tappable(
      b,
      child: _card(
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('❓', style: TextStyle(fontSize: 18)),
            const SizedBox(width: WalSpacing.sm),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(text, style: _bodyStyle()),
                  const SizedBox(height: 4),
                  const Text(
                    'Câu hỏi trong sách · chạm để hỏi SAM',
                    style: TextStyle(
                      fontSize: 12,
                      color: WalColors.primaryText,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        color: WalColors.surfaceLavender,
      ),
    ),
    ActivityBlock() => _activity(b),
    WithheldBlock() => WithheldCard(doc: widget.doc, block: b),
    SourceRefBlock(:final text) => Padding(
      padding: const EdgeInsets.only(top: WalSpacing.md),
      child: InkWell(
        onTap: () => showSourceSheet(context, doc: widget.doc, block: b),
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: Text(
          SmartBookView.childSourceRefText(widget.doc, text),
          textAlign: TextAlign.center,
          style: const TextStyle(
            fontSize: 13,
            color: WalColors.inkSoft,
            height: 1.4,
          ),
        ),
      ),
    ),
  };

  TextStyle _bodyStyle({Color color = WalColors.ink}) =>
      TextStyle(fontSize: _body, color: color, height: 1.55);

  Widget _heading(HeadingBlock b) {
    final style = switch (b.level) {
      1 => TextStyle(
        fontSize: _body + 5,
        fontWeight: FontWeight.w700,
        color: WalColors.ink,
        height: 1.3,
      ),
      2 => TextStyle(
        fontSize: _body + 2,
        fontWeight: FontWeight.w700,
        color: WalColors.primaryText,
        height: 1.3,
      ),
      _ => TextStyle(
        fontSize: _body,
        fontWeight: FontWeight.w700,
        color: WalColors.ink,
        height: 1.3,
      ),
    };
    return Padding(
      padding: EdgeInsets.only(
        top: b.level == 1 ? WalSpacing.md : WalSpacing.sm,
        left: WalSpacing.xs,
        right: WalSpacing.xs,
      ),
      child: Text(b.text, style: style),
    );
  }

  /// MỘT khối hình: hàng ảnh (1 ảnh = cả bề ngang; ≥2 ảnh cạnh nhau như trên
  /// trang) → chú thích liền kề («Hình N» đậm) → dòng nguồn. Mỗi ảnh / chú
  /// thích vẫn có key riêng (neo cuộn «Xem trong Đọc»).
  Widget _figure(List<ImageBlock> images, List<CaptionBlock> captions) {
    final line = widget.doc.sourceLineForBlock(images.first);
    return Container(
      key: SmartBookView.figureKey(images.first.id),
      padding: const EdgeInsets.all(WalSpacing.sm),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
      ),
      child: Column(
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              for (var i = 0; i < images.length; i++) ...[
                if (i > 0) const SizedBox(width: WalSpacing.sm),
                Expanded(
                  child: KeyedSubtree(
                    key: _keys.putIfAbsent(images[i].id, GlobalKey.new),
                    child: _imageBox(images[i]),
                  ),
                ),
              ],
            ],
          ),
          if (captions.isNotEmpty) ...[
            const SizedBox(height: WalSpacing.xs),
            _captionGroup(captions),
          ],
          const SizedBox(height: 2),
          Text(
            'Hình trong sách · $line · chạm hình để xem ảnh gốc',
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 11, color: WalColors.inkSoft),
          ),
        ],
      ),
    );
  }

  Widget _imageBox(ImageBlock b) {
    final line = widget.doc.sourceLineForBlock(b);
    return InkWell(
      onTap: () => showSourceSheet(context, doc: widget.doc, block: b),
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
      // Giữ chỗ theo tỉ lệ ảnh: bố cục không nở ra sau khi ảnh giải mã,
      // nên neo cuộn («Xem trong Đọc») đứng đúng chỗ (Nokia n1 D4).
      child: _fixedAspect(
        b.aspect,
        ClipRRect(
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          // ROUND 4 §6.8 — che mép dính chữ: phóng trong hộp, phần dư bị cắt.
          child: Transform.scale(
            scale: SmartBookView.bleedScale,
            child: Image.asset(
              '${widget.doc.assetBase}${b.crop}',
              fit: BoxFit.contain,
              // Máy không có crop (bản clone sạch) ⇒ nói thật, không ô trắng.
              errorBuilder: (_, _, _) => Container(
                height: 96,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: WalColors.surfaceLavender,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
                ),
                child: Text(
                  'Hình trong sách · $line\n(máy này chưa có ảnh)',
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Hộp ảnh CỐ ĐỊNH theo tỉ lệ crop, nhưng KHÔNG cao quá ~45 % màn: ảnh
  /// đứng (Hình 17.1) ở bề ngang máy xoay ngang từng cao ~2 600 px và nuốt
  /// cả bài (Nokia n2 D5). Hộp giữ chỗ ⇒ neo cuộn không trượt (D4).
  static Widget _fixedAspect(double? aspect, Widget child) {
    if (aspect == null) return child;
    return LayoutBuilder(
      builder: (ctx, c) {
        final maxH = MediaQuery.sizeOf(ctx).height * 0.45;
        final w = c.maxWidth.isFinite ? c.maxWidth : 360.0;
        var h = w / aspect;
        if (h > maxH) h = maxH;
        return Center(
          child: SizedBox(width: h * aspect, height: h, child: child),
        );
      },
    );
  }

  /// Cụm chú thích in — nguyên văn, nghiêng, giữa; mỗi dòng vẫn có key.
  Widget _captionGroup(List<CaptionBlock> captions) => Container(
    padding: const EdgeInsets.symmetric(
      horizontal: WalSpacing.md,
      vertical: WalSpacing.xs,
    ),
    child: Column(
      children: [
        for (final c in captions)
          KeyedSubtree(
            key: _keys.putIfAbsent(c.id, GlobalKey.new),
            child: Text(
              c.text,
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: WalType.secondary,
                fontStyle: FontStyle.italic,
                fontWeight: RegExp(r'^Hình\s*\d').hasMatch(c.text)
                    ? FontWeight.w700
                    : FontWeight.w400,
                color: WalColors.inkSoft,
                height: 1.35,
              ),
            ),
          ),
      ],
    ),
  );

  Widget _table(TableBlock b) {
    if (!b.safe) {
      return _card(
        Text(
          'Bảng trong sách — SAM chưa đọc chắc từng ô, con xem '
          '${widget.doc.sourceLineForBlock(b)} nhé.',
          style: _bodyStyle(color: WalColors.inkSoft),
        ),
        color: WalColors.surface,
      );
    }
    return _card(
      Table(
        border: TableBorder.all(
          color: WalColors.inkSoft.withValues(alpha: 0.3),
          width: 1,
        ),
        children: [
          for (var r = 0; r < b.rows.length; r++)
            TableRow(
              decoration: BoxDecoration(
                color: r < b.headerRows ? WalColors.surfaceLavender : null,
              ),
              children: [
                for (final c in b.rows[r])
                  Padding(
                    padding: const EdgeInsets.all(WalSpacing.sm),
                    child: Text(
                      c,
                      style: TextStyle(
                        fontSize: WalType.secondary,
                        fontWeight: r < b.headerRows
                            ? FontWeight.w700
                            : FontWeight.w400,
                        color: WalColors.ink,
                      ),
                    ),
                  ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _activity(ActivityBlock b) => switch (b.kind) {
    ActivityKind.stageLabel => Padding(
      padding: const EdgeInsets.only(top: WalSpacing.md),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Container(
          padding: const EdgeInsets.symmetric(
            horizontal: WalSpacing.md,
            vertical: 6,
          ),
          decoration: BoxDecoration(
            color: LearningStateToken.needsWork.bg,
            borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
          ),
          child: Text(
            SmartBookView.stageIcon(b.text).isEmpty
                ? b.text
                : '${SmartBookView.stageIcon(b.text)} ${b.text}',
            style: const TextStyle(
              fontSize: WalType.secondary,
              fontWeight: FontWeight.w700,
              color: WalColors.warnText,
            ),
          ),
        ),
      ),
    ),
    ActivityKind.objective => _tappable(
      b,
      child: _card(
        Text(b.text, style: _bodyStyle()),
        color: WalColors.surfaceLavender,
      ),
    ),
    ActivityKind.instruction => _tappable(
      b,
      child: _card(
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('🧪', style: TextStyle(fontSize: 18)),
            const SizedBox(width: WalSpacing.sm),
            Expanded(child: Text(b.text, style: _bodyStyle())),
          ],
        ),
        color: LearningStateToken.mastered.bg,
      ),
    ),
    ActivityKind.sidebar => _tappable(
      b,
      child: _card(
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('ⓘ', style: TextStyle(fontSize: 18)),
            const SizedBox(width: WalSpacing.sm),
            Expanded(child: Text(b.text, style: _bodyStyle())),
          ],
        ),
        color: LearningStateToken.mastered.bg,
      ),
    ),
  };

  /// Chạm một đoạn ⇒ hai việc: hỏi SAM về đoạn này, hoặc tra cứu sách.
  Widget _tappable(LessonBlock b, {required Widget child}) => InkWell(
    onTap: () => _blockActions(b),
    borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    child: child,
  );

  Future<void> _blockActions(LessonBlock b) => showModalBottomSheet<void>(
    context: context,
    backgroundColor: WalColors.surface,
    showDragHandle: true,
    builder: (sheet) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(
          WalSpacing.lg,
          0,
          WalSpacing.lg,
          WalSpacing.lg,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SizedBox(
              width: double.infinity,
              height: WalSpacing.minTouch + 8,
              child: FilledButton(
                style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(
                      WalSpacing.radiusButton,
                    ),
                  ),
                ),
                onPressed: () {
                  Navigator.of(sheet).pop();
                  widget.onAskSam(b);
                },
                child: const Text(
                  '🦉 Hỏi SAM về đoạn này',
                  style: TextStyle(fontSize: WalType.body),
                ),
              ),
            ),
            const SizedBox(height: WalSpacing.sm),
            SizedBox(
              width: double.infinity,
              height: WalSpacing.minTouch,
              child: TextButton(
                onPressed: () {
                  Navigator.of(sheet).pop();
                  showSourceSheet(context, doc: widget.doc, block: b);
                },
                child: Text(
                  '📖 Tra cứu · ${widget.doc.sourceLineForBlock(b)}',
                  style: const TextStyle(
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

  Widget _card(Widget child, {Color color = Colors.white}) => Container(
    width: double.infinity,
    padding: const EdgeInsets.all(WalSpacing.md),
    decoration: BoxDecoration(
      color: color,
      borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
    ),
    child: child,
  );
}
