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
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:path_provider/path_provider.dart';

import 'core/stories/stories_store.dart';
import 'core/store/file_store.dart';
import 'core/store/learner_profile.dart';
import 'core/store/learner_store.dart';
import 'features/camera/education_ocr_adapter.dart';
import 'features/camera/mlkit_ocr_adapter.dart';
import 'features/mission/mission_center_screen.dart';
import 'features/discovery/story_detail_screen.dart';
import 'features/parent/parent_area.dart';
import 'features/settings/settings_screen.dart';
import 'core/curriculum/canonical_problem.dart';
import 'core/knowledge/provenance.dart';
import 'core/knowledge/slice_curriculum.dart' show curriculumFor;
import 'features/learning_session/slice_flow.dart';
import 'features/assessment/assessment_screen.dart';
import 'features/assessment/learner_confirm.dart';
import 'features/assessment/assessment_result_screen.dart';
import 'features/shell/session_recorder.dart';
import 'core/store/learning_session.dart' show SessionMode, SessionTrigger;
import 'core/student/concept_summary.dart';
import 'features/discovery/splash_quote.dart';
import 'features/subjects/lesson_index.dart';
import 'app/theme/band_density_scope.dart';
import 'app/theme/wal_tokens.dart' show WalBandDensity;
import 'core/pedagogy/presentation_policy.dart' show bandForGrade;
import 'features/subjects/subjects_screen.dart';
import 'features/mission/mission_data.dart';
import 'features/onboarding/onboarding_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final dir = await getApplicationDocumentsDirectory();
  final store = await FileLearnerStore.open(
      File('${dir.path}/hoc-cung-sam/learner-store.jsonl'));
  runApp(HocCungSamApp(
      store: store,
      ocr: MlkitEducationOcrAdapter(),
      storiesDbPath: '${dir.path}/hoc-cung-sam/sam-stories.db'));
}

class HocCungSamApp extends StatefulWidget {
  const HocCungSamApp(
      {super.key,
      required this.store,
      this.ocr,
      this.storiesDbPath,
      this.indexLoader = LessonIndex.loadForGrade});

  final LearnerStore store;

  /// WAL-113 QA — inject được để test nạp index deterministic (mặc định: asset).
  final Future<LessonIndex?> Function(int grade) indexLoader;

  /// `null` (test/desktop) ⇒ nút chụp giữ flow demo cũ — không giả camera.
  final EducationOcrAdapter? ocr;

  /// WAL-152 — nơi copy sam-stories.db từ asset. `null` = không nạp kho
  /// khám phá (test cũ giữ nguyên hành vi).
  final String? storiesDbPath;

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
  LessonIndex? _lessonIndex; // WAL-136 — null = chưa build asset, nói thật
  StoriesStore _stories = StoriesStore.open('/khong-co'); // rỗng tới khi nạp
  StoryItem? _splashQuote;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _loadLessonIndex() async {
    final p = _profile;
    if (p == null) return;
    final idx = await widget.indexLoader(p.grade);
    if (mounted) setState(() => _lessonIndex = idx);
  }

  Future<void> _loadStories() async {
    final path = widget.storiesDbPath;
    if (path == null) return;
    try {
      final f = File(path);
      if (!f.existsSync()) {
        final bytes = await rootBundle.load('assets/pack/sam-stories.db');
        await f.parent.create(recursive: true);
        await f.writeAsBytes(bytes.buffer.asUint8List(), flush: true);
      }
      final s = StoriesStore.open(path);
      if (!mounted) return;
      setState(() {
        _stories = s;
        final quotes = s.loadingQuotes();
        if (quotes.isNotEmpty) {
          _splashQuote = quotes[Random(DateTime.now().day).nextInt(quotes.length)];
        }
      });
    } catch (_) {/* thiếu asset ⇒ kho rỗng, UI nói thật */}
  }

  Future<void> _load() async {
    _loadStories(); // song song — không chặn profiles
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
    _loadLessonIndex();
  }

  void _selectProfile(String learnerId) {
    final p = _profiles.where((x) => x.learnerId == learnerId).firstOrNull;
    if (p == null) return;
    setState(() {
      _profile = p;
      _refreshMission(); // mission tính lại TỪ KHO của đúng learner này
    });
    widget.store.saveActiveLearner(p.learnerId); // sống qua restart
    _loadLessonIndex(); // grade có thể khác ⇒ index khác
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
    // WAL-113 QA (Nokia walk): app khởi động CHƯA có hồ sơ ⇒ _loadLessonIndex
    // lúc _load() return sớm — phải nạp lại SAU khi onboarding tạo hồ sơ,
    // không thì Môn học trống tới lần restart sau (bug thấy trên máy trắng).
    _loadLessonIndex();
  }

  /// WAL-138 — chip «Ôn luyện»: bài ôn THẬT từ SGK (exercise KHÁC bài đã
  /// làm) khi có dạng đã học; chưa có gì để ôn ⇒ nói thật.
  Future<void> _openReview(BuildContext context) async {
    final p = _profile;
    final idx = _lessonIndex;
    final exs = idx?.exercisesForToan(6) ?? const [];
    if (p == null || exs.length < 2) {
      _honest(context,
          'Chưa có bài nào tới hạn ôn — con học một bài mới trước nhé!');
      return;
    }
    final log = await widget.store.evidenceFor(
        learnerId: p.learnerId, skillCaseId: 'denominator-non-divisible');
    if (log.events.isEmpty) {
      if (context.mounted) {
        _honest(context,
            'Con chưa học dạng này nên chưa có gì để ôn — vào Môn học nhé!');
      }
      return;
    }
    final e = exs[1]; // bài KHÁC bài đầu — ôn không phải làm lại y hệt
    if (!context.mounted) return;
    await openCanonicalProblem(context,
        problem: CanonicalProblem.fromCurriculum(
          exerciseLabel: 'b6-on',
          expression: e.expr,
          provenance: Provenance(
            origin: KnowledgeOrigin.sourceStated,
            sourceId: e.book,
            extractionMethod: 'qmap-v1',
            confidence: 0.9,
            grade: p.grade,
            subject: 'Toán',
            pageStart: e.page,
          ),
        ),
        profile: p,
        store: widget.store);
    if (mounted) setState(_refreshMission);
  }

  /// WAL-145 — ghi bản xuất dữ liệu của MỘT người học ra tệp trong thư mục
  /// tài liệu của app. Không gửi đi đâu: quyền lấy dữ liệu ra không được biến
  /// thành một đường dữ liệu trẻ rời máy.
  Future<String?> _saveExport(String learnerId, String jsonl) async {
    try {
      final dir = await getApplicationDocumentsDirectory();
      final f = File('${dir.path}/hoc-cung-sam/export-$learnerId.jsonl');
      await f.parent.create(recursive: true);
      await f.writeAsString(jsonl, flush: true);
      return f.path;
    } catch (_) {
      return null; // ghi không được ⇒ nói thật, không bịa đường dẫn
    }
  }

  /// WAL-137 — sửa hồ sơ xong: thay TẠI CHỖ trong danh sách và nạp lại
  /// mission + mục lục. `learnerId` không đổi nên mọi bằng chứng vẫn thuộc
  /// đúng người — đổi lớp KHÔNG đụng sổ học (bất biến 2, WAL-95).
  void _onProfileEdited(LearnerProfile saved) {
    setState(() {
      _profiles = [
        for (final p in _profiles)
          if (p.learnerId == saved.learnerId) saved else p
      ];
      if (_profile?.learnerId == saved.learnerId) _profile = saved;
      _refreshMission();
    });
    _loadLessonIndex(); // lớp có thể đã đổi ⇒ mục lục khác
  }

  /// WAL-143 — «Kiểm tra hiểu bài»: cùng engine, luật `AssistancePolicy
  /// .assessment` (không gợi ý, không chữa giữa chừng, mode assess).
  ///
  /// ⭐ KHÔNG THI ĐIỀU CHƯA DẠY: chưa có bằng chứng nào về dạng này ⇒ nói
  /// thật và mời học trước. Kiểm tra một đứa trẻ về thứ nó chưa được học
  /// không sinh ra bằng chứng, chỉ sinh ra một con số.
  Future<void> _openAssessment(BuildContext context) async {
    final p = _profile;
    final c = p == null ? null : curriculumFor(p);
    final exs = _lessonIndex?.exercisesForToan(6) ?? const [];
    if (p == null || c == null || exs.length < 2) {
      _honest(context,
          'Máy này chưa nạp đủ bài để kiểm tra — con vào Môn học làm vài bài '
          'trước, rồi SAM mới kiểm tra được.');
      return;
    }
    final log = await widget.store.evidenceFor(
        learnerId: p.learnerId, skillCaseId: 'denominator-non-divisible');
    if (log.events.isEmpty) {
      if (context.mounted) {
        _honest(context,
            'Con chưa học dạng này nên SAM chưa kiểm tra — mình học trước đã '
            'nhé, rồi kiểm tra mới nói lên điều gì.');
      }
      return;
    }
    if (!context.mounted) return;
    // ⭐ Máy của chung: hỏi cho chắc TRƯỚC khi sinh bằng chứng độc lập.
    final who = await confirmLearner(context, profiles: _profiles, active: p);
    if (who == null) return; // đóng sheet = đổi ý, không ghi gì
    if (who.learnerId != p.learnerId) {
      _selectProfile(who.learnerId);
      if (!context.mounted) return;
      _honest(context,
          'SAM đã chuyển sang sổ học của ${who.displayName} — con bấm «Kiểm '
          'tra hiểu bài» lại một lần nữa nhé.');
      return;
    }
    if (!context.mounted) return;
    final nav = Navigator.of(context);
    await nav.push(MaterialPageRoute(
        builder: (_) => AssessmentScreen(
              items: exs.take(3).toList(),
              onFinished: (events, answers) async {
                final rec = await recordSession(
                  store: widget.store,
                  learnerId: p.learnerId,
                  subjectId: c.subjectId,
                  events: events,
                  trigger: SessionTrigger.assessment,
                  mode: SessionMode.assess,
                );
                final m = await masteryFromStore(
                    widget.store, p.learnerId, c);
                if (!nav.mounted) return;
                nav.pushReplacement(MaterialPageRoute(
                    builder: (_) => AssessmentResultScreen(
                          answers: answers,
                          summary: ConceptSummary.of(m,
                              knownCaseIds: {for (final k in c.cases) k.id},
                              now: DateTime.now()),
                          violations: rec.violations,
                          onDone: () => nav.pop(),
                        )));
              },
            )));
    if (mounted) setState(_refreshMission);
  }

  /// «Bạn có biết?» — một mục VERIFIED bất kỳ, ổn định trong ngày.
  StoryItem? _didYouKnow() {
    if (_stories.isEmpty) return null;
    final pool = [
      ..._stories.byType('EVENT'),
      ..._stories.byType('INVENTION_DISCOVERY'),
      ..._stories.byType('PERSON'),
    ];
    if (pool.isEmpty) return null;
    return pool[Random(DateTime.now().day).nextInt(pool.length)];
  }

  void _honest(BuildContext context, String msg) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(24, 0, 24, 32),
        child: Text(msg,
            style: const TextStyle(fontSize: 17, height: 1.5)),
      ),
    );
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
        home: BandDensityScope(
          density: WalBandDensity.forGradeBandLabel(
              bandForGrade(_profile?.grade ?? 3)?.label ?? '3-5'),
          child: _homeChild(),
        ),
      );

  Widget _homeChild() => _loading
            ? (_splashQuote == null
                ? const Scaffold(body: SizedBox.shrink())
                : SplashQuoteScreen(quote: _splashQuote!))
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
                            store: widget.store,
                            profiles: _profiles,
                            saveExport: _saveExport),
                        onReview: () => _openReview(context),
                        onAssess: () => _openAssessment(context),
                        onOpenSettings: () => Navigator.of(context).push(
                            MaterialPageRoute(
                                builder: (_) =>
                                    SettingsScreen(
                                  stories: _stories,
                                  profile: _profile,
                                  store: widget.store,
                                  index: _lessonIndex,
                                  profiles: _profiles,
                                  onProfileChanged: _onProfileEdited))),
                        todayStory: _stories
                            .todayEvents(DateTime.now())
                            .firstOrNull,
                        didYouKnowStory: _didYouKnow(),
                        onOpenStory: (st) => Navigator.of(context).push(
                            MaterialPageRoute(
                                builder: (_) => StoryDetailScreen(
                                    item: st, stories: _stories))),
                        onOpenSubjects: () async {
                          await Navigator.of(context).push(MaterialPageRoute(
                              builder: (_) => SubjectsScreen(
                                  profile: _profile!,
                                  store: widget.store,
                                  index: _lessonIndex)));
                          if (mounted) setState(_refreshMission);
                        },
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
                  );
}
