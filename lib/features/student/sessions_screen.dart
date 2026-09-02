/// WAL-142 #30 — SESSIONS: lịch sử phiên từ kho (projection ngày/môn),
/// mỗi phiên kể thật mức hỗ trợ CAO NHẤT (maxSupportIn — «đúng sau hint nhỏ»
/// không được kể thành «tự làm»). Không %, không điểm.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/learning_session.dart';
import '../../core/student/mastery.dart';

String supportLabel(SupportLevel s) => switch (s) {
      SupportLevel.none => 'TỰ LÀM trọn vẹn',
      SupportLevel.hint => 'có gợi ý nhỏ',
      SupportLevel.workedStep => 'có làm mẫu một bước',
      SupportLevel.fullSolution => 'đã xem lời giải',
    };

class SessionsScreen extends StatefulWidget {
  const SessionsScreen({super.key, required this.profile, required this.store});
  final LearnerProfile profile;
  final LearnerStore store;

  @override
  State<SessionsScreen> createState() => _SessionsScreenState();
}

class _SessionsScreenState extends State<SessionsScreen> {
  List<LearningSession> _sessions = const [];
  bool _loaded = false;

  @override
  void initState() {
    super.initState();
    widget.store.sessions(learnerId: widget.profile.learnerId).then((s) {
      if (!mounted) return;
      setState(() {
        _sessions = s.reversed.toList(); // mới nhất trước
        _loaded = true;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: !_loaded
            ? const SizedBox.shrink()
            : ListView(
                padding: const EdgeInsets.all(WalSpacing.lg),
                children: [
                  const Text('Các phiên học',
                      style: TextStyle(
                          fontSize: WalType.display,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  const SizedBox(height: WalSpacing.sm),
                  if (_sessions.isEmpty)
                    const Padding(
                      padding: EdgeInsets.only(top: WalSpacing.xl),
                      child: Text(
                          'Chưa có phiên nào — học một bài là có dòng đầu tiên.',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                              fontSize: WalType.body,
                              color: WalColors.inkSoft)),
                    ),
                  for (final s in _sessions) _tile(s),
                ],
              ),
      ),
    );
  }

  Widget _tile(LearningSession s) {
    final sup = maxSupportIn(s);
    final answers = s.events.where((e) => e.isAttempt).length;
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.md),
        decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(WalSpacing.radiusChip)),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(
              '${s.startedAt.day}/${s.startedAt.month} · ${s.subjectId}'
              ' · ${s.mode == SessionMode.assess ? 'KIỂM TRA' : 'học'}',
              style: const TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w600,
                  color: WalColors.ink)),
          const SizedBox(height: 4),
          Text('$answers lượt trả lời · ${supportLabel(sup)}',
              style: TextStyle(
                  fontSize: WalType.secondary,
                  color: sup == SupportLevel.none
                      ? WalColors.mintText
                      : WalColors.inkSoft)),
        ]),
      ),
    );
  }
}
