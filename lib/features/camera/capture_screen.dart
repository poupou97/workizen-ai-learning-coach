/// WAL-108 — màn CHỤP THẬT (real Camera capability, §3 Master Order).
///
/// Ảnh KHÔNG rời máy: chụp → OCR on-device qua [EducationOcrAdapter] →
/// [PerceptionHypothesis]. Không có đường tắt sang evidence — kết quả luôn
/// phải qua màn xác nhận «tớ đọc được thế này» (WAL-64).
///
/// Camera hỏng/không cấp quyền KHÔNG chặn việc học: lối «Gõ đề thay ✎» trả
/// [CaptureOutcome] với hypothesis `null` — tầng trên mở đường tự gõ
/// (CanonicalProblem `man:`), cùng đường với «không đọc được đề».
library;

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/perception/perception_provenance.dart';
import 'education_ocr_adapter.dart';
import 'precapture_advisor.dart';

/// Giá trị pop của màn chụp. Phân biệt ba lối ra:
/// - pop(null)                      → trẻ bấm quay lại, huỷ flow;
/// - pop(CaptureOutcome(null))      → đã chụp nhưng KHÔNG đọc được (hoặc chọn
///                                    gõ tay) — đi tiếp tới ADMIT_UNCERTAINTY;
/// - pop(CaptureOutcome(hypothesis))→ có giả thuyết, đi tới màn xác nhận.
class CaptureOutcome {
  const CaptureOutcome(this.hypothesis);
  final PerceptionHypothesis? hypothesis;
}

class CaptureScreen extends StatefulWidget {
  const CaptureScreen({super.key, required this.ocr});

  final EducationOcrAdapter ocr;

  @override
  State<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends State<CaptureScreen> {
  CameraController? _controller;
  String? _error;
  bool _busy = false;

  /// WAL-140 — gate chất lượng WAL-65 chạy TRÊN KHUNG SỐNG. Nhắc trước khi
  /// chụp, vì gate SAU chụp (confidence) đã đo được là vô dụng: PHONE-SIM cho
  /// thấy ảnh suy giảm vừa phải làm recall 5/5 → 0/5 mà Vision vẫn BỊA biểu
  /// thức với conf≈1.00.
  final _advisor = PrecaptureAdvisor();
  bool _streaming = false;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      final cams = await availableCameras();
      if (cams.isEmpty) throw StateError('no camera');
      final back = cams.firstWhere(
          (c) => c.lensDirection == CameraLensDirection.back,
          orElse: () => cams.first);
      final c = CameraController(back, ResolutionPreset.high,
          enableAudio: false, imageFormatGroup: ImageFormatGroup.jpeg);
      await c.initialize();
      if (!mounted) {
        await c.dispose();
        return;
      }
      setState(() => _controller = c);
      _startPreviewChecks(c);
    } catch (e) {
      if (mounted) setState(() => _error = '$e');
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  /// Bơm khung preview qua gate chất lượng. Máy nào không cho stream thì
  /// thôi — màn giữ nguyên câu hướng dẫn chung, KHÔNG chặn việc chụp.
  void _startPreviewChecks(CameraController c) {
    try {
      c.startImageStream((image) {
        if (!mounted || _busy || image.planes.isEmpty) return;
        final now = DateTime.now();
        if (!_advisor.shouldAssess(now)) return;
        final p = image.planes.first;
        final a = _advisor.offer(
            downsampleLuma(
              width: image.width,
              height: image.height,
              yPlane: p.bytes,
              bytesPerRow: p.bytesPerRow,
            ),
            now);
        if (a != null && mounted) setState(() {});
      });
      _streaming = true;
    } catch (_) {
      _streaming = false; // không stream được ⇒ mất lời nhắc, không mất tính năng
    }
  }

  Future<void> _shoot() async {
    final c = _controller;
    if (c == null || _busy) return;
    setState(() => _busy = true);
    PerceptionHypothesis? hyp;
    try {
      // Dừng stream trước khi chụp: nhiều máy Android không cho chạy đồng thời.
      if (_streaming) {
        await c.stopImageStream();
        _streaming = false;
      }
      final shot = await c.takePicture();
      hyp = await widget.ocr.recognizeExpression(shot.path);
    } catch (_) {
      hyp = null; // lỗi chụp/OCR ⇒ cùng đường với «không đọc được» — nói thật
    }
    if (!mounted) return;
    Navigator.of(context).pop(CaptureOutcome(hyp));
  }

  @override
  Widget build(BuildContext context) {
    final c = _controller;
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: _error != null
            ? _fallback()
            : c == null
                ? const Center(
                    child: CircularProgressIndicator(
                        color: WalColors.primary500))
                : Column(children: [
                    Padding(
                      padding: const EdgeInsets.all(WalSpacing.md),
                      child: Text(
                        _advisor.message,
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            fontSize: WalType.body,
                            height: 1.35,
                            // Nền màn này là ĐEN ⇒ phải dùng cặp màu của
                            // bảng TỐI; vàng của bảng sáng (0xFFB45309) đặt
                            // trên đen là chữ tối trên nền tối.
                            color: _advisor.needsFixing
                                ? WalColorsDark.warnText
                                : Colors.white),
                      ),
                    ),
                    // Viền khung đổi màu theo lời nhắc — trẻ thấy bằng mắt
                    // trước khi đọc chữ.
                    Expanded(
                      child: Container(
                        margin: const EdgeInsets.symmetric(
                            horizontal: WalSpacing.md),
                        decoration: BoxDecoration(
                          border: Border.all(
                              color: _advisor.needsFixing
                                  ? WalColorsDark.warnText
                                  : Colors.white24,
                              width: _advisor.needsFixing ? 3 : 1),
                          borderRadius:
                              BorderRadius.circular(WalSpacing.radiusCard),
                        ),
                        child: ClipRRect(
                          borderRadius:
                              BorderRadius.circular(WalSpacing.radiusCard),
                          child: CameraPreview(c),
                        ),
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(WalSpacing.lg),
                      child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            TextButton(
                              onPressed: () => Navigator.of(context)
                                  .pop(const CaptureOutcome(null)),
                              child: const Text('Gõ đề thay ✎',
                                  style: TextStyle(
                                      fontSize: WalType.body,
                                      color: Colors.white70)),
                            ),
                            GestureDetector(
                              onTap: _shoot,
                              child: Container(
                                width: 72,
                                height: 72,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: _busy
                                      ? WalColors.inkSoft
                                      : WalColors.primary500,
                                  border: Border.all(
                                      color: Colors.white, width: 4),
                                ),
                                child: _busy
                                    ? const Padding(
                                        padding: EdgeInsets.all(20),
                                        child: CircularProgressIndicator(
                                            color: Colors.white,
                                            strokeWidth: 3))
                                    : null,
                              ),
                            ),
                            TextButton(
                              onPressed: () => Navigator.of(context).pop(),
                              child: const Text('Quay lại',
                                  style: TextStyle(
                                      fontSize: WalType.body,
                                      color: Colors.white70)),
                            ),
                          ]),
                    ),
                  ]),
      ),
    );
  }

  Widget _fallback() => Padding(
        padding: const EdgeInsets.all(WalSpacing.lg),
        child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Tớ không mở được camera trên máy này.\nMình gõ đề bài vào cũng được nhé!',
                textAlign: TextAlign.center,
                style: TextStyle(
                    fontSize: WalType.title,
                    color: Colors.white,
                    height: 1.4),
              ),
              const SizedBox(height: WalSpacing.xl),
              SizedBox(
                height: WalSpacing.minTouch + 8,
                child: FilledButton(
                  style: FilledButton.styleFrom(
                      backgroundColor: WalColors.primary500),
                  onPressed: () => Navigator.of(context)
                      .pop(const CaptureOutcome(null)),
                  child: const Text('Gõ đề vào đây ✎',
                      style: TextStyle(fontSize: WalType.body)),
                ),
              ),
              const SizedBox(height: WalSpacing.sm),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Quay lại',
                    style: TextStyle(
                        fontSize: WalType.body, color: Colors.white70)),
              ),
            ]),
      );
}
