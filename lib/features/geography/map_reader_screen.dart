/// WAL-144 #28 Địa — MAP READER (bounded): BẢN ĐỒ THẬT từ SGK (SOURCE_ASSET
/// crop, provenance đầy đủ) + câu hỏi khai thác VERBATIM.
///
/// Bất biến:
/// - Ảnh là SOURCE_ASSET từ sách — caption in trong sách hiển thị cùng nguồn;
///   không ảnh minh hoạ AI nào ở đây (SOURCE IMAGE ≠ AI ILLUSTRATION).
/// - Câu hỏi mở «chỉ trên bản đồ» — trẻ làm bằng mắt/tay, SAM KHÔNG chấm
///   (correct=null); một sự kiện PARTICIPATION khi hoàn tất (WAL-210 /
///   Founder D1: «Con đã chỉ được» là tự báo, không phải bằng chứng tự làm),
///   policy map-reader-v1. Mang lineage sách (+ bài khi pack có) và version
///   của pack; `lookup` ⇒ không sự kiện (cùng luật WAL-189 với các màn kia).
/// - Không %, không điểm.
library;

import 'package:flutter/material.dart';

import '../../app/theme/band_density_scope.dart';
import '../../app/theme/wal_tokens.dart';
import '../../core/assets/learning_asset.dart';
import '../../core/context/learning_context.dart';
import '../../core/intent/learning_intent.dart';
import '../shell/learning_asset_image.dart';
import '../../core/knowledge/slice_curriculum.dart' show knowledgeModelVersion;
import '../../core/student/evidence_ids.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/mastery.dart';
import '../subjects/lesson_index.dart';

class MapReaderScreen extends StatefulWidget {
  const MapReaderScreen(
      {super.key,
      required this.map,
      this.learningContext,
      this.onFinished,
      this.now});

  final DiaMap map;

  /// ⭐ WAL-210 — trước đây màn này là surface DUY NHẤT không nhận context:
  /// không gate `lookup`, không lineage, không version pack. `null` = lối vào
  /// cũ (test/demo) — vẫn chạy, chỉ thiếu những gì context mới có.
  final LearningContext? learningContext;
  final void Function(List<LearningEvent> events)? onFinished;
  final DateTime Function()? now;

  @override
  State<MapReaderScreen> createState() => _MapReaderScreenState();
}

class _MapReaderScreenState extends State<MapReaderScreen> {
  // ⭐ WAL-210 (audit C1): token PHIÊN sinh một lần lúc mở màn — mở lại
  // cùng bài là phiên khác, id khác (đồng hồ máy, không ăn nhịp `now`).
  final String _token = newEvidenceSessionToken(DateTime.now());
  bool _done = false;

  DiaMap get m => widget.map;
  DateTime _at() => (widget.now ?? DateTime.now)();

  void _finish() {
    if (_done) return;
    setState(() => _done = true);
    final ctx = widget.learningContext;
    // ⭐⭐ WAL-189 — tra cứu sinh TRACE, không sinh EVIDENCE.
    if (ctx?.intent == LearningIntent.lookup) {
      widget.onFinished?.call(const []);
      return;
    }
    widget.onFinished?.call([
      LearningEvent(
        eventId: evidenceEventId(
            exerciseId: '${m.book}:p${m.page}:map',
            sessionToken: _token,
            seq: 0),
        skillCaseId: 'dia-doc-ban-do',
        kind: EvidenceKind.participation, // D1: «đã chỉ được» = tự báo
        correct: null, // chỉ-trên-bản-đồ là việc của mắt/tay — SAM không chấm
        exerciseId: '${m.book}:p${m.page}:map',
        conceptIds: const ['dia-ban-do'],
        at: _at(),
        support: SupportLevel.none,
        policyId: 'map-reader-v1',
        knowledgeVersion: ctx?.knowledgeModelVersion ?? knowledgeModelVersion,
        // ⭐⭐ WAL-210 lineage: sách là sự thật của chính bản đồ; số bài lấy
        // từ pack (`DiaMap.lesson`) hoặc từ context — không có thì null, và
        // khi ấy bài này KHÔNG hiện trên Learning Map (không đoán).
        sourceDocumentId: m.book,
        lessonNo: m.lesson ?? ctx?.lessonNo,
      )
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: _done
              ? [
                  Center(
                      child: Image.asset(
                          'assets/mascot/sam-celebrate-independence.png',
                          width: densityOf(context).mascotHero,
                          height: densityOf(context).mascotHero)),
                  const SizedBox(height: WalSpacing.md),
                  _card(const Text(
                      'Tớ ghi lại là con đã đọc bản đồ và tự chỉ ra rồi nhé — '
                      'tớ không chấm; con kể cho thầy cô nghe con tìm thấy gì.',
                      style: TextStyle(
                          fontSize: WalType.body,
                          color: WalColors.ink,
                          height: 1.45))),
                  const SizedBox(height: WalSpacing.lg),
                  _primary('Về danh sách bài',
                      () => Navigator.of(context).maybePop()),
                ]
              : [
                  _samRow(
                      'sam-think.png',
                      'Bài này có vị trí trên bản đồ, SAM cho con xem đúng '
                      'bản đồ trong sách để con tự chỉ ra nhé.'),
                  const SizedBox(height: WalSpacing.md),
                  _card(Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('BẢN ĐỒ TRONG SÁCH',
                            style: TextStyle(
                                fontSize: WalType.secondary,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.6,
                                color: WalColors.inkSoft)),
                        const SizedBox(height: WalSpacing.sm),
                        // Phóng to/di chuyển được — bản đồ là để soi.
                        SizedBox(
                          height: 420,
                          child: InteractiveViewer(
                            maxScale: 6,
                            // WAL-133: đi qua MÔ HÌNH TÀI SẢN — dựng được
                            // `SourceAsset` nghĩa là provenance crop đầy đủ;
                            // thiếu thì `DiaMap` đã bị loại từ tầng parse.
                            // Nhãn + cách hỏng khi thiếu tệp do model quyết,
                            // không do màn này tự chế.
                            child: LearningAssetImage(
                                asset: SourceAsset(
                                  path: 'assets/pack/${m.asset}',
                                  sourceDocumentId: m.book,
                                  pagePdf: m.pagePdf,
                                  pagePrinted: m.page,
                                  bboxFrac: m.bboxFrac,
                                  extractionVersion: m.extractionVersion,
                                  printedCaption: m.caption,
                                ),
                                fit: BoxFit.contain),
                          ),
                        ),
                        const SizedBox(height: WalSpacing.sm),
                        Text(m.caption,
                            style: const TextStyle(
                                fontSize: WalType.secondary,
                                color: WalColors.inkSoft)),
                      ])),
                  const SizedBox(height: WalSpacing.md),
                  _card(Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('NHÌN TRÊN BẢN ĐỒ, EM HÃY:',
                            style: TextStyle(
                                fontSize: WalType.secondary,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 0.6,
                                color: WalColors.inkSoft)),
                        const SizedBox(height: WalSpacing.sm),
                        for (final q in m.questions)
                          Padding(
                            padding:
                                const EdgeInsets.only(bottom: WalSpacing.sm),
                            child: Text('• $q',
                                style: const TextStyle(
                                    fontSize: WalType.body,
                                    color: WalColors.ink,
                                    height: 1.5)),
                          ),
                      ])),
                  const SizedBox(height: WalSpacing.md),
                  _primary('Con đã chỉ được trên bản đồ ✅', _finish),
                  const SizedBox(height: WalSpacing.md),
                  Text('Nguồn: SGK ${m.subject} 5 · tr. ${m.page}',
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft)),
                ],
        ),
      ),
    );
  }

  Widget _primary(String label, VoidCallback onPressed) => SizedBox(
        width: double.infinity,
        height: WalSpacing.minTouch + 8,
        child: FilledButton(
          style: FilledButton.styleFrom(
              backgroundColor: WalColors.primary500,
              shape: RoundedRectangleBorder(
                  borderRadius:
                      BorderRadius.circular(WalSpacing.radiusButton))),
          onPressed: onPressed,
          child: Text(label, style: const TextStyle(fontSize: WalType.body)),
        ),
      );

  /// ⭐⭐ WAL-185 — SAM không chỉ chọn ĐÚNG hình thức trình bày (bản đồ thật
  /// thay vì đoạn văn) mà còn NÓI RA lý do — order Founder §18: "SAM should
  /// not merely decorate visualization. SAM can use it intentionally."
  Widget _samRow(String asset, String text) => Row(children: [
        Image.asset('assets/mascot/$asset',
            width: densityOf(context).mascotChip,
            height: densityOf(context).mascotChip),
        const SizedBox(width: WalSpacing.md),
        Expanded(
            child: Text(text,
                style: const TextStyle(
                    fontSize: WalType.body, color: WalColors.ink))),
      ]);

  Widget _card(Widget child) => Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.lg),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard)),
        child: child,
      );
}
