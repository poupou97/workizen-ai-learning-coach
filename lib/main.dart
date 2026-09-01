/// «Học cùng SAM» — entry.
///
/// WAL-95: app khởi động từ KHO THẬT (`LearnerStore`), không phải fixture.
/// Chưa có hồ sơ ⇒ onboarding hai câu hỏi; có rồi ⇒ vào thẳng màn HÔM NAY.
/// Kho hiện là JSONL trong bộ nhớ (ghi ra tệp là việc của tầng platform —
/// WAL-84); mọi thứ phía trên nói chuyện qua interface nên đổi engine không
/// đụng màn hình nào.
library;

import 'package:flutter/material.dart';

import 'core/store/learner_profile.dart';
import 'core/store/learner_store.dart';
import 'features/mission/mission_center_screen.dart';
import 'features/mission/mission_data.dart';
import 'features/onboarding/onboarding_screen.dart';

void main() => runApp(HocCungSamApp(store: JsonlLearnerStore()));

class HocCungSamApp extends StatefulWidget {
  const HocCungSamApp({super.key, required this.store});

  final LearnerStore store;

  @override
  State<HocCungSamApp> createState() => _HocCungSamAppState();
}

class _HocCungSamAppState extends State<HocCungSamApp> {
  LearnerProfile? _profile;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final ps = await widget.store.profiles();
    if (!mounted) return;
    setState(() {
      _profile = ps.isEmpty ? null : ps.first;
      _loading = false;
    });
  }

  Future<void> _onboarded(LearnerProfile p) async {
    await widget.store.saveProfile(p);
    if (!mounted) return;
    setState(() => _profile = p);
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Học cùng SAM',
        debugShowCheckedModeBanner: false,
        home: _loading
            ? const Scaffold(body: SizedBox.shrink())
            : _profile == null
                ? OnboardingScreen(onDone: _onboarded)
                // Nội dung học vẫn từ fixture domain (slice 1) — hồ sơ đã
                // THẬT; nối bằng chứng vào kho là bước kế của WAL-95.
                : MissionCenterScreen(
                    data: buildDemoMission(), learnerName: _profile!.displayName),
      );
}
