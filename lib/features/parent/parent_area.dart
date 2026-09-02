/// WAL-109 §26 — KHU BỐ MẸ: PIN gate + «Tình hình các con» (KHÔNG xếp hạng).
///
/// Luật:
/// - PIN là RÀO CHẮN TRẺ TÒ MÒ (ghi thật — không phải bảo mật chống người lớn).
/// - Mỗi con MỘT thẻ, mọi câu trạng thái qua explainConcept (claim-gated F4);
///   KHÔNG so sánh anh chị em, không «bạn nào giỏi hơn», không %.
/// - «Tối nay cùng X» đọc từ KHO CỦA ĐÚNG X — parent projection không merge.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/adaptive/adaptive_engine.dart';
import '../../core/coach/parent_explanation.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/student/concept_summary.dart';
import '../learning_session/slice_flow.dart' show masteryFromStore;
import 'parent_tonight_screen.dart';

/// Lối vào duy nhất: PIN (đặt lần đầu / nhập) → Tình hình các con.
Future<void> openParentArea(
  BuildContext context, {
  required LearnerStore store,
  required List<LearnerProfile> profiles,
}) async {
  final nav = Navigator.of(context);
  final existing = await store.parentPin();
  final ok = await nav.push<bool>(MaterialPageRoute(
      builder: (_) => ParentPinScreen(store: store, existingPin: existing)));
  if (ok != true || !nav.mounted) return;
  nav.push(MaterialPageRoute(
      builder: (_) => ParentOverviewScreen(store: store, profiles: profiles)));
}

class ParentPinScreen extends StatefulWidget {
  const ParentPinScreen(
      {super.key, required this.store, required this.existingPin});

  final LearnerStore store;

  /// `null` = chưa đặt — màn này thành màn ĐẶT PIN (nhập 2 lần).
  final String? existingPin;

  @override
  State<ParentPinScreen> createState() => _ParentPinScreenState();
}

class _ParentPinScreenState extends State<ParentPinScreen> {
  final _pin = TextEditingController();
  String? _firstEntry;
  String? _error;

  bool get _setting => widget.existingPin == null;

  Future<void> _submit() async {
    final v = _pin.text.trim();
    if (v.length < 4) {
      setState(() => _error = 'PIN cần ít nhất 4 số.');
      return;
    }
    if (!_setting) {
      if (v == widget.existingPin) {
        Navigator.of(context).pop(true);
      } else {
        setState(() => _error = 'PIN chưa đúng.');
      }
      return;
    }
    if (_firstEntry == null) {
      setState(() {
        _firstEntry = v;
        _pin.clear();
        _error = null;
      });
      return;
    }
    if (v == _firstEntry) {
      await widget.store.saveParentPin(v);
      if (mounted) Navigator.of(context).pop(true);
    } else {
      setState(() {
        _firstEntry = null;
        _pin.clear();
        _error = 'Hai lần nhập chưa khớp — đặt lại từ đầu nhé.';
      });
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(WalSpacing.lg),
            child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text(
                    _setting
                        ? (_firstEntry == null
                            ? 'Đặt PIN cho khu bố mẹ'
                            : 'Nhập lại PIN lần nữa')
                        : 'Nhập PIN khu bố mẹ',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                        fontSize: WalType.title,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink),
                  ),
                  const SizedBox(height: WalSpacing.sm),
                  const Text(
                    'PIN giúp khu vực của bố mẹ không lẫn với chỗ con học.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: WalType.secondary, color: WalColors.inkSoft),
                  ),
                  const SizedBox(height: WalSpacing.lg),
                  TextField(
                    controller: _pin,
                    autofocus: true,
                    obscureText: true,
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    maxLength: 8,
                    style: const TextStyle(
                        fontSize: WalType.display, color: WalColors.ink),
                    decoration: InputDecoration(
                      counterText: '',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(WalSpacing.radiusButton),
                          borderSide: BorderSide.none),
                    ),
                    onSubmitted: (_) => _submit(),
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: WalSpacing.sm),
                    Text(_error!,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.inkSoft)),
                  ],
                  const SizedBox(height: WalSpacing.lg),
                  SizedBox(
                    height: WalSpacing.minTouch + 8,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                          backgroundColor: WalColors.primary500,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(
                                  WalSpacing.radiusButton))),
                      onPressed: _submit,
                      child: Text(_setting ? 'Đặt PIN' : 'Mở khu bố mẹ',
                          style: const TextStyle(fontSize: WalType.body)),
                    ),
                  ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(false),
                    child: const Text('Quay lại',
                        style: TextStyle(
                            fontSize: WalType.body,
                            color: WalColors.primaryText)),
                  ),
                ]),
          ),
        ),
      );
}

/// Dữ liệu «Tối nay» của MỘT con — lắp từ kho của đúng con đó.
Future<({ParentExplanation explanation, AdaptiveDecision decision,
    Map<String, String> names})?> parentTonightFor(
    LearnerProfile p, LearnerStore store) async {
  final c = curriculumFor(p);
  if (c == null) return null; // ngoài slice — nói thật ở thẻ, không bịa
  final mastery = await masteryFromStore(store, p.learnerId, c);
  final names = {for (final sc in c.cases) sc.id: sc.condition};
  final summary = ConceptSummary.of(mastery,
      knownCaseIds: {...names.keys}, now: DateTime.now());
  final explanation = explainConcept(summary,
      conceptDisplayName: 'quy đồng mẫu số', caseDisplayNames: names);
  final decision = decide(
    conceptId: c.conceptId,
    exerciseCase: 'denominator-non-divisible',
    mastery: mastery,
    stage: c.stage,
    catalogue: c.catalogue,
    caseCatalogue: c.cases,
  );
  return (explanation: explanation, decision: decision, names: names);
}

/// «TÌNH HÌNH CÁC CON» — mỗi con một thẻ, KHÔNG xếp hạng (§26.9).
class ParentOverviewScreen extends StatelessWidget {
  const ParentOverviewScreen(
      {super.key, required this.store, required this.profiles});

  final LearnerStore store;
  final List<LearnerProfile> profiles;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              const Text('Tình hình các con',
                  style: TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.sm),
              const Text(
                'Mỗi con một nhịp học riêng — SAM kể chuyện từng bạn, '
                'không so sánh ai với ai.',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                    height: 1.4),
              ),
              const SizedBox(height: WalSpacing.md),
              for (final p in profiles) _ChildCard(profile: p, store: store),
            ],
          ),
        ),
      );
}

class _ChildCard extends StatelessWidget {
  const _ChildCard({required this.profile, required this.store});

  final LearnerProfile profile;
  final LearnerStore store;

  @override
  Widget build(BuildContext context) => FutureBuilder(
        future: parentTonightFor(profile, store),
        builder: (context, snap) {
          final data = snap.data;
          return Container(
            margin: const EdgeInsets.only(bottom: WalSpacing.md),
            padding: const EdgeInsets.all(WalSpacing.lg),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
            ),
            child:
                Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('${profile.displayName} · Lớp ${profile.grade}',
                  style: const TextStyle(
                      fontSize: WalType.title,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.sm),
              if (snap.connectionState != ConnectionState.done)
                const SizedBox.shrink()
              else if (data == null)
                Text(
                    'SAM chưa có nội dung lớp ${profile.grade} nên chưa thể '
                    'kể gì về phần học trong ứng dụng.',
                    style: const TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.ink,
                        height: 1.45))
              else ...[
                // claim-gated — nguồn duy nhất của câu trạng thái (F4).
                Text(data.explanation.message,
                    style: const TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.ink,
                        height: 1.45)),
                const SizedBox(height: WalSpacing.sm),
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () => Navigator.of(context).push(
                        MaterialPageRoute(
                            builder: (_) => ParentTonightScreen(
                                  childName: profile.displayName,
                                  explanation: data.explanation,
                                  decision: data.decision,
                                  caseDisplayNames: data.names,
                                ))),
                    child: Text('Tối nay cùng ${profile.displayName} ▸',
                        style: const TextStyle(
                            fontSize: WalType.body,
                            color: WalColors.primaryText)),
                  ),
                ),
              ],
            ]),
          );
        },
      );
}
