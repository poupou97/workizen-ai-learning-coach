/// «Học cùng SAM» — entry.
///
/// WAL-95: app khởi động từ KHO THẬT (`LearnerStore`), không fixture hồ sơ.
/// WAL-108: kho nay RA ĐĨA ([FileLearnerStore]) — dữ liệu sống qua restart;
/// màn «Hôm nay» sinh từ BẰNG CHỨNG trong kho ([buildMissionFromStore]);
/// nút chụp mở flow camera thật (OCR on-device qua Education Adapter).
///
/// Test/preview vẫn tiêm store bộ nhớ + bỏ trống `ocr` — không đường nào
/// phụ thuộc platform trong widget tree.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

import 'core/store/file_store.dart';
import 'core/store/learner_profile.dart';
import 'core/store/learner_store.dart';
import 'features/camera/education_ocr_adapter.dart';
import 'features/camera/mlkit_ocr_adapter.dart';
import 'features/learning_session/slice_flow.dart';
import 'features/mission/mission_center_screen.dart';
import 'features/parent/parent_area.dart';
import 'features/mission/mission_data.dart';
import 'features/onboarding/onboarding_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final dir = await getApplicationDocumentsDirectory();
  final store = await FileLearnerStore.open(
      File('${dir.path}/hoc-cung-sam/learner-store.jsonl'));
  runApp(HocCungSamApp(store: store, ocr: MlkitEducationOcrAdapter()));
}

class HocCungSamApp extends StatefulWidget {
  const HocCungSamApp({super.key, required this.store, this.ocr});

  final LearnerStore store;

  /// `null` (test/desktop) ⇒ nút chụp giữ flow demo cũ — không giả camera.
  final EducationOcrAdapter? ocr;

  @override
  State<HocCungSamApp> createState() => _HocCungSamAppState();
}

class _HocCungSamAppState extends State<HocCungSamApp> {
  // WAL-109 — DEVICE ≠ USER: máy giữ NHIỀU hồ sơ; mọi flow bind vào
  // _profile (active learner). Switch không logout, không mất state ai cả.
  List<LearnerProfile> _profiles = const [];
  LearnerProfile? _profile;
  bool _loading = true;
  Future<MissionData>? _mission;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final ps = await widget.store.profiles();
    // WAL-109: máy của chung mở lại phải về ĐÚNG người học gần nhất.
    final activeId = await widget.store.activeLearnerId();
    if (!mounted) return;
    setState(() {
      _profiles = ps;
      _profile = ps.isEmpty
          ? null
          : ps.where((p) => p.learnerId == activeId).firstOrNull ?? ps.first;
      _loading = false;
      _refreshMission();
    });
  }

  void _selectProfile(String learnerId) {
    final p = _profiles.where((x) => x.learnerId == learnerId).firstOrNull;
    if (p == null) return;
    setState(() {
      _profile = p;
      _refreshMission(); // mission tính lại TỪ KHO của đúng learner này
    });
    widget.store.saveActiveLearner(p.learnerId); // sống qua restart
  }

  void _refreshMission() {
    final p = _profile;
    _mission = p == null
        ? null
        : buildMissionFromStore(profile: p, store: widget.store);
  }

  Future<void> _onboarded(LearnerProfile p) async {
    await widget.store.saveProfile(p);
    if (!mounted) return;
    setState(() {
      _profiles = [..._profiles, p];
      _profile = p; // hồ sơ mới thành active — người vừa được thêm là người học
      _refreshMission();
    });
  }

  /// WAL-109 — thêm người học: dùng LẠI onboarding, không nhánh UI mới.
  void _addProfile(BuildContext context) {
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => Scaffold(
              body: SafeArea(
                child: OnboardingScreen(onDone: (p) async {
                  await _onboarded(p);
                  if (context.mounted) Navigator.of(context).pop();
                }),
              ),
            )));
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Học cùng SAM',
        debugShowCheckedModeBanner: false,
        home: _loading
            ? const Scaffold(body: SizedBox.shrink())
            : _profile == null
                ? OnboardingScreen(onDone: _onboarded)
                : FutureBuilder<MissionData>(
                    future: _mission,
                    builder: (context, snap) {
                      final data = snap.data;
                      if (data == null) {
                        return const Scaffold(body: SizedBox.shrink());
                      }
                      final ocr = widget.ocr;
                      return MissionCenterScreen(
                        data: data,
                        learnerName: _profile!.displayName,
                        profiles: _profiles,
                        activeLearnerId: _profile!.learnerId,
                        onSelectProfile: _selectProfile,
                        onAddProfile: () => _addProfile(context),
                        onParentArea: () => openParentArea(context,
                            store: widget.store, profiles: _profiles),
                        onStartHomework: ocr == null
                            ? null
                            : () async {
                                await startHomeworkFlow(
                                  context,
                                  profile: _profile!,
                                  store: widget.store,
                                  ocr: ocr,
                                );
                                // Về Hôm nay ⇒ mission tính LẠI từ kho —
                                // vòng khép kín nhìn thấy được trên màn.
                                if (mounted) setState(_refreshMission);
                              },
                      );
                    },
                  ),
      );
}
