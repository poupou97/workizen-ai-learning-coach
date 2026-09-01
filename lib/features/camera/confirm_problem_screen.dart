/// ⭐⭐ WAL-52 — Màn "TỚ ĐỌC ĐƯỢC THẾ NÀY": RANH GIỚI AN TOÀN của Camera Tutor.
///
/// Bám wireframe C2 + bất biến WAL-64 (do KIỂU giữ): perception chưa xác nhận
/// KHÔNG có đường vào evidence — màn này là nơi DUY NHẤT sinh [ConfirmedProblem].
///
/// Ba lối ra, không lối tắt:
///   ✓ Đúng rồi   → ConfirmedProblem (confirmedAsIs)
///   ✏️ Sửa       → ConfirmedProblem (corrected) — hypothesis máy GIỮ NGUYÊN,
///                  mỗi lần sửa là một nhãn đo Student-Correction-Rate (#5 WAL-63)
///   📷 Chụp lại  → quay về camera
/// Không đọc được đề (hypothesis == null): SAM ADMIT_UNCERTAINTY — "chưa chắc"
/// là câu trả lời hợp lệ; trẻ chụp lại hoặc TỰ GÕ đề (→ CanonicalProblem man:).
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/perception/perception_provenance.dart';

class ConfirmProblemScreen extends StatefulWidget {
  const ConfirmProblemScreen({
    super.key,
    required this.hypothesis,
    required this.onConfirmed,
    required this.onRetake,
    this.now,
  });

  /// `null` = pipeline không ghép được biểu thức (caseUnknown) — fail closed.
  final PerceptionHypothesis? hypothesis;

  /// Lối ra DUY NHẤT về phía domain — nhận CanonicalProblem, không nhận chuỗi thô.
  final void Function(CanonicalProblem problem) onConfirmed;
  final VoidCallback onRetake;
  final DateTime? now;

  @override
  State<ConfirmProblemScreen> createState() => _ConfirmProblemScreenState();
}

class _ConfirmProblemScreenState extends State<ConfirmProblemScreen> {
  bool _editing = false;
  bool _manualEntry = false;
  late final TextEditingController _controller = TextEditingController(
      text: widget.hypothesis?.expression ?? '');

  DateTime get _now => widget.now ?? DateTime.now();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final h = widget.hypothesis;
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(WalSpacing.lg),
          child: h == null && !_manualEntry
              ? _uncertainView()
              : _confirmView(h),
        ),
      ),
    );
  }

  // ── không đọc được đề: nói thật, không đoán ────────────────────────────
  Widget _uncertainView() => Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const SizedBox(height: WalSpacing.xl),
          Center(child: _samChip('assets/mascot/sam-admit-uncertainty.png', 96)),
          const SizedBox(height: WalSpacing.md),
          const Text(
            'Tớ chưa chắc mình đọc đúng đề — con chụp gần hơn giúp tớ nhé?',
            textAlign: TextAlign.center,
            style: TextStyle(
                fontSize: WalType.title,
                fontWeight: FontWeight.w600,
                color: WalColors.ink,
                height: 1.4),
          ),
          const SizedBox(height: WalSpacing.xl),
          _primaryButton('Chụp lại', widget.onRetake),
          const SizedBox(height: WalSpacing.sm),
          _outlineButton('Gõ đề vào đây ✎',
              () => setState(() => _manualEntry = true)),
        ],
      );

  // ── xác nhận / sửa ─────────────────────────────────────────────────────
  Widget _confirmView(PerceptionHypothesis? h) {
    final manual = h == null;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Row(children: [
          _samChip('assets/mascot/sam-think.png', 44),
          const SizedBox(width: WalSpacing.sm),
          Expanded(
            child: Text(
              manual ? 'Con gõ đề bài vào đây nhé:' : 'Tớ đọc được thế này:',
              style: const TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink),
            ),
          ),
        ]),
        const SizedBox(height: WalSpacing.lg),
        Container(
          padding: const EdgeInsets.all(WalSpacing.lg),
          decoration: BoxDecoration(
            color: WalColors.surfaceLavender,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
          ),
          child: (_editing || manual)
              ? TextField(
                  controller: _controller,
                  autofocus: true,
                  style: const TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.primaryText),
                  textAlign: TextAlign.center,
                  decoration: const InputDecoration(
                      border: InputBorder.none, hintText: 'vd: 3/4 + 2/5'),
                )
              : Text(
                  h.expression,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.primaryText),
                ),
        ),
        const SizedBox(height: WalSpacing.sm),
        if (!manual)
          const Text('Đúng đề bài của con chưa?',
              textAlign: TextAlign.center,
              style: TextStyle(
                  fontSize: WalType.body, color: WalColors.inkSoft)),
        const SizedBox(height: WalSpacing.lg),
        _primaryButton('✓ Đúng rồi', () => _confirm(h)),
        const SizedBox(height: WalSpacing.sm),
        if (!manual && !_editing)
          _outlineButton('✏️ Sửa', () => setState(() => _editing = true)),
        if (!manual && !_editing) const SizedBox(height: WalSpacing.sm),
        _outlineButton('📷 Chụp lại', widget.onRetake),
      ],
    );
  }

  void _confirm(PerceptionHypothesis? h) {
    final text = _controller.text.trim();
    if (h != null) {
      // Đường camera: ĐI QUA ConfirmedProblem — sửa của trẻ thành bản ghi mới,
      // hypothesis máy còn nguyên (WAL-64).
      final confirmed = ConfirmedProblem.confirm(
        h,
        correctedExpression: (_editing && text.isNotEmpty) ? text : null,
        at: _now,
      );
      widget.onConfirmed(CanonicalProblem.fromConfirmedPerception(confirmed));
    } else if (text.isNotEmpty) {
      // Đường tự gõ: nguồn là chính trẻ — mint man:, không xác nhận giả.
      widget.onConfirmed(
          CanonicalProblem.fromManualInput(expression: text, at: _now));
    }
  }

  Widget _primaryButton(String label, VoidCallback onTap) => SizedBox(
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: onTap,
          child: Text(label,
              style: const TextStyle(
                  fontSize: WalType.body, fontWeight: FontWeight.w700)),
        ),
      );

  Widget _outlineButton(String label, VoidCallback onTap) => SizedBox(
        height: WalSpacing.minTouch + 8,
        child: OutlinedButton(
          style: OutlinedButton.styleFrom(
              foregroundColor: WalColors.primaryText,
              side: const BorderSide(color: WalColors.primary500),
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: onTap,
          child: Text(label, style: const TextStyle(fontSize: WalType.body)),
        ),
      );

  Widget _samChip(String asset, double size) => ClipOval(
        child: Image.asset(asset,
            width: size,
            height: size,
            fit: BoxFit.cover,
            errorBuilder: (_, e, s) => Container(
                width: size, height: size, color: WalColors.surfaceLavender)),
      );
}
