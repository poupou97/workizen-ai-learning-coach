/// ⭐⭐ Lệnh 59 §P0 — XEM ẢNH HỌC TẬP TOÀN MÀN HÌNH, PHÓNG VÀ KÉO ĐƯỢC.
///
/// Founder: «Trên điện thoại, nếu không zoom được thì nhiều nội dung gần như
/// không thể đọc.» Sơ đồ, bản đồ, biểu đồ, hình thí nghiệm, chú thích nhỏ —
/// tất cả đều nằm trong ảnh, và ảnh inline trên máy 360 dp thì chữ trong ảnh
/// nhỏ hơn chữ của bài.
///
/// ⭐ GENERIC (§P0.4): component này KHÔNG biết gì về Bài 17, về môn, hay về
/// màn gọi nó. Nó nhận một đường dẫn asset + vài dòng chú thích, nên Đọc,
/// Trực quan, bản đồ, chân dung… đều dùng lại được.
///
/// ⭐⭐ LICENCE KHÔNG ĐỔI (§P0.5). Xem to hơn không phải là được phát hành:
///
///     CAN DISPLAY INTERNALLY  !=  CAN DISTRIBUTE
///     ZOOM CAPABILITY         !=  DISTRIBUTION RIGHT
///
/// Viewer vì thế KHÔNG có nút tải về, KHÔNG có chia sẻ, KHÔNG có sao chép —
/// và mang theo nhãn nguồn của chính ảnh. Nó chỉ đổi cách NHÌN, không đổi
/// quyền.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';

/// Mở ảnh học tập toàn màn hình.
///
/// Đẩy một route BÊN TRÊN màn đang đọc, nên màn ấy còn nguyên trong cây widget
/// — back về là ĐÚNG vị trí đang đọc, không dựng lại bài (§P0.2).
Future<void> showLearningImage(
  BuildContext context, {
  required String asset,
  double? aspect,
  String? caption,
  String? sourceLine,
  VoidCallback? onOpenSource,
  double bleedScale = 1.0,
}) => Navigator.of(context).push(
  MaterialPageRoute<void>(
    fullscreenDialog: true,
    builder: (_) => LearningImageViewer(
      asset: asset,
      aspect: aspect,
      caption: caption,
      sourceLine: sourceLine,
      onOpenSource: onOpenSource,
      // ⚠ Dòng này TỪNG THIẾU. Tham số có, nơi dùng có, chỉ mỗi chỗ truyền là
      // không — nên `showLearningImage(bleedScale: 1.14)` im lặng rơi về 1.0
      // và màn toàn màn hình vẫn lòi mép chữ, dù test vẫn xanh (test dựng
      // thẳng widget nên đi vòng qua đúng chỗ hỏng). Cùng họ với lỗi
      // `subjectLabelOf`: khai báo → truyền → KHÔNG AI ĐỌC.
      bleedScale: bleedScale,
    ),
  ),
);

class LearningImageViewer extends StatefulWidget {
  const LearningImageViewer({
    super.key,
    required this.asset,
    this.aspect,
    this.caption,
    this.sourceLine,
    this.onOpenSource,
    this.bleedScale = 1.0,
  });

  final String asset;

  /// width/height của ảnh — giữ ĐÚNG tỉ lệ, không kéo méo (§P0.3).
  final double? aspect;

  /// Chú thích trong sách, nguyên văn. `null` ⇒ không hiện gì.
  final String? caption;

  /// Dòng nguồn ngắn («SGK KHTN 6 · trang 61»).
  final String? sourceLine;

  /// Mở tờ nguồn đầy đủ — provenance không được mất khi đổi tap sang viewer.
  final VoidCallback? onOpenSource;

  /// ⭐ CHE MÉP CROP. Crop từ pipeline còn dính chữ/chú thích của hàng bên
  /// cạnh; màn Đọc đã phóng nhẹ để cắt phần dư ấy. Xem to mà KHÔNG che thì
  /// mép chữ lạ hiện ra và trẻ tưởng nó thuộc về hình — đo trên Nokia, lệnh
  /// 59. Dùng CÙNG hệ số với inline để hai chỗ là một bức ảnh.
  ///
  /// 1.0 = không che (mặc định, cho ảnh không phải crop trang sách).
  final double bleedScale;

  static const viewerKey = Key('learning-image-viewer');
  static const imageKey = Key('learning-image-viewer-image');
  static const closeKey = Key('learning-image-viewer-close');
  static const sourceKey = Key('learning-image-viewer-source');

  /// Mức phóng khi chạm hai lần. Đủ để đọc chữ trong sơ đồ, chưa tới mức lạc
  /// mất bối cảnh.
  static const doubleTapScale = 2.5;
  static const maxScale = 5.0;

  @override
  State<LearningImageViewer> createState() => _LearningImageViewerState();
}

class _LearningImageViewerState extends State<LearningImageViewer>
    with SingleTickerProviderStateMixin {
  final _controller = TransformationController();
  late final AnimationController _anim = AnimationController(
    vsync: this,
    duration: const Duration(milliseconds: 180),
  );
  Animation<Matrix4>? _tween;
  TapDownDetails? _lastTap;

  @override
  void dispose() {
    _anim.dispose();
    _controller.dispose();
    super.dispose();
  }

  bool get _zoomed => _controller.value.getMaxScaleOnAxis() > 1.01;

  void _animateTo(Matrix4 target) {
    _tween = Matrix4Tween(begin: _controller.value, end: target).animate(
      CurvedAnimation(parent: _anim, curve: Curves.easeOut),
    )..addListener(() => _controller.value = _tween!.value);
    _anim.forward(from: 0);
  }

  /// Chạm hai lần: chưa phóng ⇒ phóng vào ĐÚNG điểm vừa chạm; đang phóng ⇒ về.
  void _onDoubleTap() {
    if (_zoomed) {
      _animateTo(Matrix4.identity());
      return;
    }
    final p = _lastTap?.localPosition;
    const s = LearningImageViewer.doubleTapScale;
    final m = p == null
        ? (Matrix4.identity()..scaleByDouble(s, s, 1, 1))
        : (Matrix4.identity()
            ..translateByDouble(-p.dx * (s - 1), -p.dy * (s - 1), 0, 1)
            ..scaleByDouble(s, s, 1, 1));
    _animateTo(m);
  }

  @override
  Widget build(BuildContext context) {
    final caption = widget.caption;
    final source = widget.sourceLine;
    return Scaffold(
      key: LearningImageViewer.viewerKey,
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            Positioned.fill(
              child: GestureDetector(
                onDoubleTapDown: (d) => _lastTap = d,
                onDoubleTap: _onDoubleTap,
                child: InteractiveViewer(
                  transformationController: _controller,
                  minScale: 1,
                  maxScale: LearningImageViewer.maxScale,
                  // Kéo được cả khi chưa phóng: ảnh cao hơn màn vẫn xem hết.
                  panEnabled: true,
                  child: Center(
                    child: AspectRatio(
                      aspectRatio: widget.aspect ?? 1,
                      child: ClipRect(
                        child: Transform.scale(
                          scale: widget.bleedScale,
                          child: Image.asset(
                            widget.asset,
                            key: LearningImageViewer.imageKey,
                            fit: BoxFit.contain,
                            // Thiếu tệp ⇒ nói thật, không màn đen câm (§P7).
                            errorBuilder: (_, _, _) => const Center(
                              child: Text(
                                'Máy này chưa có ảnh của bài.',
                                style: TextStyle(color: Colors.white70),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
            Positioned(
              top: WalSpacing.sm,
              left: WalSpacing.sm,
              child: IconButton(
                key: LearningImageViewer.closeKey,
                tooltip: 'Đóng',
                icon: const Icon(Icons.close, color: Colors.white),
                onPressed: () => Navigator.of(context).maybePop(),
              ),
            ),
            if (caption != null || source != null)
              Positioned(
                left: 0,
                right: 0,
                bottom: 0,
                child: Container(
                  padding: const EdgeInsets.all(WalSpacing.md),
                  color: Colors.black.withValues(alpha: 0.55),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (caption != null)
                        Text(
                          caption,
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: WalType.secondary,
                            height: 1.35,
                          ),
                        ),
                      if (source != null) ...[
                        const SizedBox(height: WalSpacing.xs),
                        // Nguồn đi THEO ảnh, kể cả khi phóng to: quyền dùng
                        // không đổi vì ảnh to hơn (§P0.5).
                        InkWell(
                          key: LearningImageViewer.sourceKey,
                          onTap: widget.onOpenSource,
                          child: Text(
                            widget.onOpenSource == null
                                ? source
                                : '$source · Nguồn ▸',
                            style: const TextStyle(
                              color: Colors.white70,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
