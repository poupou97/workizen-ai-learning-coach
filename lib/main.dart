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
import 'features/navigation/app_shell.dart';
import 'features/navigation/sam_hub_screen.dart';
import 'features/progress/progress_screen.dart';
import 'features/settings/settings_screen.dart';
import 'core/context/learning_context.dart';
import 'core/curriculum/canonical_problem.dart';
import 'core/intent/learning_intent.dart';
import 'core/intent/next_lesson.dart';
import 'core/knowledge/provenance.dart';
import 'core/knowledge/slice_curriculum.dart' show curriculaForLearner;
import 'core/store/timetable.dart';
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
import 'features/subjects/book_shelf_screen.dart';
import 'features/subjects/subjects_screen.dart';
import 'features/subjects/subject_display.dart';
import 'features/subjects/subject_home_screen.dart';
import 'features/mission/mission_data.dart';
import 'features/onboarding/onboarding_screen.dart';
import 'app/boot_screen.dart';
import 'core/lesson_model/lesson_document.dart';
import 'core/lesson_model/workspace_catalog.dart';
import 'features/lesson_workspace/lesson_workspace_screen.dart';
import 'features/lesson_workspace/widgets/runtime_plan.dart'
    show founderNextAction;
import 'features/lesson_workspace/workspace_trace.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final dir = await getApplicationDocumentsDirectory();
  final store = await FileLearnerStore.open(
    File('${dir.path}/hoc-cung-sam/learner-store.jsonl'),
  );
  runApp(
    HocCungSamApp(
      store: store,
      ocr: MlkitEducationOcrAdapter(),
      storiesDbPath: '${dir.path}/hoc-cung-sam/sam-stories.db',
    ),
  );
}

class HocCungSamApp extends StatefulWidget {
  const HocCungSamApp({
    super.key,
    required this.store,
    this.ocr,
    this.storiesDbPath,
    this.indexLoader = LessonIndex.loadForGrade,
  });

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
  List<TimetableEntry> _timetable = const [];
  LessonIndex? _lessonIndex; // WAL-136 — null = chưa build asset, nói thật
  StoriesStore _stories = StoriesStore.open('/khong-co'); // rỗng tới khi nạp
  StoryItem? _splashQuote;

  @override
  void initState() {
    super.initState();
    _load();
  }

  /// ⭐⭐ ROUND 7 · V2 (Founder order 50) — MỌI MẠCH HỌC CÓ THẬT trên máy.
  ///
  /// Trước vòng này Home nhận ĐÚNG MỘT bài («bài của lớp con») cộng một danh
  /// sách «lát cắt nghiên cứu» tách riêng. Founder cầm máy và gọi tên hệ quả:
  /// Home thành landing page của Bài 17. Nay Home nhận CẢ HỆ — mỗi bài SAM đã
  /// xếp sẵn là một mạch học, kèm dấu vết phiên và việc tiếp theo của CHÍNH
  /// nó, và Home xếp chúng thành hàng thẻ.
  ///
  /// Thứ tự: bài của ĐÚNG LỚP trước, rồi bài sách lớp khác (thẻ tự dán nhãn
  /// «sách lớp N»). Không có bài nào ⇒ danh sách rỗng, Home không bịa thẻ.
  ///
  /// ⚠ Việc tiếp theo đến từ `founderNextAction` — ĐỘNG CƠ DUY NHẤT mà Lesson
  /// Workspace cũng gọi. Home không có luật riêng: nếu có, nút trên Home và
  /// gợi ý trong bài sẽ trỏ hai nơi khác nhau cho cùng một trạng thái.
  List<HomeLessonThread> _lessonThreads(LearnerProfile p) {
    final c = WorkspaceCatalog.shared;
    if (!c.isLoaded) return const [];
    final docs =
        [for (final book in c.booksWithWorkspace) ...c.docsForBook(book)]
          ..sort((a, b) {
            final own =
                (a.grade == p.grade ? 0 : 1) - (b.grade == p.grade ? 0 : 1);
            return own != 0 ? own : a.slotKey.compareTo(b.slotKey);
          });
    return [
      for (final d in docs)
        HomeLessonThread(
          doc: d,
          openedViews: WorkspaceTrace.session.viewsFor(d.slotKey),
          next: founderNextAction(
            d,
            seen: WorkspaceTrace.session.viewsFor(d.slotKey),
            learnerId: p.learnerId,
          ),
        ),
    ];
  }

  /// ⭐⭐ ROUND 7 · V2 — MÔN TRÊN GIÁ SÁCH CỦA TRẺ CHƯA CÓ BÀI NÀO SAM XẾP SẴN.
  ///
  /// Đây là chỗ đơn hàng 50 dễ bị phản bội nhất: cách nhanh để hàng thẻ trông
  /// đầy là bịa một thẻ «Toán 6 — đang học 70%». Không. Môn nào chưa có bài
  /// thì thẻ của nó NÓI THẲNG là chưa có, kèm con số mục lục THẬT lấy từ pack.
  ///
  /// Mục lục chưa nạp ⇒ rỗng: không mục lục thì không biết trẻ có sách gì, và
  /// đoán là bịa.
  List<HomeShelfSubject> _shelfSubjects() {
    final idx = _lessonIndex;
    if (idx == null) return const [];
    return [
      for (final subject in idx.subjects.keys)
        HomeShelfSubject(
          subject: subject,
          listedLessons: idx.listedLessonCountFor(subject),
          openableLessons: idx.openableLessonCountFor(subject),
        ),
    ];
  }

  Future<void> _loadLessonIndex() async {
    final p = _profile;
    if (p == null) return;
    if (!WorkspaceCatalog.shared.isLoaded) {
      // Song song với pack; xong thì Home vẽ lại để thẻ «Bài học SAM» hiện.
      WorkspaceCatalog.shared.load().then((_) {
        if (mounted) setState(() {});
      });
    }
    final idx = await widget.indexLoader(p.grade);
    if (!mounted) return;
    // ROUND 3 B5: tên sách cho dòng nguồn của Kho khám phá (mã sách → tên).
    if (idx != null) {
      knownBookTitles.addAll({
        for (final b in idx.books)
          b.sourceDocumentId: b.volumeLabel == null
              ? b.title
              : '${b.title} · ${b.volumeLabel}',
      });
    }
    setState(() {
      _lessonIndex = idx;
      // ⭐ WAL-210 G2: thẻ Home của lớp chỉ-có-Scale cần con số bài từ pack
      // — pack nạp xong thì mission tính lại, không đợi lần mở app sau.
      _refreshMission();
    });
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
          _splashQuote =
              quotes[Random(DateTime.now().day).nextInt(quotes.length)];
        }
      });
    } catch (_) {
      /* thiếu asset ⇒ kho rỗng, UI nói thật */
    }
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
      // ⭐ Lệnh 51 §1 (C-2) — tên sách là bộ nhớ TOÀN CỤC tích luỹ theo lớp đã
      // mở. Không xoá thì «Kho khám phá» (kho của toàn corpus, không lọc lớp)
      // hiện «SGK Ngữ văn 6» hay hiện mã sách trần TUỲ vào việc phiên này đã
      // mở hồ sơ lớp 6 trước hay chưa — cùng màn, cùng hồ sơ, hai kết quả.
      knownBookTitles.clear();
      _refreshMission(); // mission tính lại TỪ KHO của đúng learner này
    });
    widget.store.saveActiveLearner(p.learnerId); // sống qua restart
    _loadLessonIndex(); // grade có thể khác ⇒ index khác
  }

  void _refreshMission() {
    final p = _profile;
    _mission = p == null
        ? null
        : buildMissionFromStore(
            profile: p,
            store: widget.store,
            index: _lessonIndex,
          );
    if (p != null) {
      widget.store.timetable(p.learnerId).then((t) {
        if (mounted) setState(() => _timetable = t);
      });
    } else {
      _timetable = const [];
    }
  }

  /// Môn đang có chỗ vướng / đến hạn ôn — suy từ CHÍNH danh sách ôn đã tính,
  /// không tính lại bằng luật thứ hai. Một luật, một chỗ.
  Set<String> _reviewDueSubjects(MissionData data) => {
    for (final r in data.reviews)
      if (r.subjectId != null) r.subjectId!,
  };

  /// ⭐⭐ WAL-176 (Missing #1) — gợi ý CẤP SÁCH từ TKB, môn BẤT KỲ có bìa +
  /// hoạt động thật (không riêng Toán — `LearningAgenda`/WAL-102 chỉ phủ dòng
  /// `SliceCurriculum` DUY NHẤT hiện có). Tính lại mỗi build từ state đã nạp
  /// — cùng cách `_reviewDueSubjects` đang làm, không thêm luồng async mới.
  HomeRecommendation? _bookRecommendation() {
    final idx = _lessonIndex;
    if (idx == null) return null;
    return nextBookRecommendation(
      index: idx,
      now: DateTime.now(),
      timetable: _timetable,
    );
  }

  /// Bấm «Bắt đầu» trên thẻ gợi ý sách: mở ĐÚNG Book Home rồi tự vào thẳng
  /// bài/ý định đã đề nghị — trẻ không bị hỏi lại (SAM đã hỏi xong ở Home).
  Future<void> _startRecommendation(
    BuildContext context,
    MissionData data,
    HomeRecommendation rec,
  ) async {
    final idx = _lessonIndex;
    if (idx == null) return;
    final book = idx.books
        .where((b) => b.sourceDocumentId == rec.sourceDocumentId)
        .firstOrNull;
    if (book == null) return;
    await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (ctx) {
          final screen = SubjectHomeScreen(
            profile: _profile!,
            store: widget.store,
            index: idx,
            subject: rec.subject,
            book: book,
            timetable: _timetable,
            reviewDueSubjects: _reviewDueSubjects(data),
          );
          // ⭐ Book Home vào ĐÚNG stack (back trả về đây, không rơi thẳng về
          // Home) — rồi mới tự mở tiếp bài/ý định, không cần trẻ chạm lần hai.
          WidgetsBinding.instance.addPostFrameCallback((_) {
            if (!ctx.mounted) return;
            screen.openLessonWithIntent(
              ctx,
              sourceDocumentId: rec.sourceDocumentId,
              lessonNo: rec.lessonNo,
              intent: rec.intent,
            );
          });
          return screen;
        },
      ),
    );
    if (mounted) setState(_refreshMission);
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
      _honest(
        context,
        'Chưa có bài nào tới hạn ôn — con học một bài mới trước nhé!',
      );
      return;
    }
    final log = await widget.store.evidenceFor(
      learnerId: p.learnerId,
      skillCaseId: 'denominator-non-divisible',
    );
    if (log.events.isEmpty) {
      if (context.mounted) {
        _honest(
          context,
          'Con chưa học dạng này nên chưa có gì để ôn — vào Môn học nhé!',
        );
      }
      return;
    }
    final e = exs[1]; // bài KHÁC bài đầu — ôn không phải làm lại y hệt
    if (!context.mounted) return;
    await openCanonicalProblem(
      context,
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
      store: widget.store,
      // ⭐ WAL-210 lineage: bài ôn lấy từ `exercisesForToan(6)` ⇒ đúng
      // cuốn của bài tập + bài 6 (số bài hoá cứng cùng chỗ với danh sách).
      learningContext: LearningContext(
        learnerId: p.learnerId,
        grade: p.grade,
        subject: 'Toán',
        sourceDocumentId: e.book,
        lessonNo: 6,
        intent: LearningIntent.review,
      ),
    );
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
          if (p.learnerId == saved.learnerId) saved else p,
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
    final cs = p == null ? const [] : curriculaForLearner(p);
    final c = cs.length == 1 ? cs.single : null;
    final exs = _lessonIndex?.exercisesForToan(6) ?? const [];
    if (p == null || c == null || exs.length < 2) {
      _honest(
        context,
        'Máy này chưa nạp đủ bài để kiểm tra — con vào Môn học làm vài bài '
        'trước, rồi SAM mới kiểm tra được.',
      );
      return;
    }
    final log = await widget.store.evidenceFor(
      learnerId: p.learnerId,
      skillCaseId: 'denominator-non-divisible',
    );
    if (log.events.isEmpty) {
      if (context.mounted) {
        _honest(
          context,
          'Con chưa học dạng này nên SAM chưa kiểm tra — mình học trước đã '
          'nhé, rồi kiểm tra mới nói lên điều gì.',
        );
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
      _honest(
        context,
        'SAM đã chuyển sang sổ học của ${who.displayName} — con bấm «Kiểm '
        'tra hiểu bài» lại một lần nữa nhé.',
      );
      return;
    }
    if (!context.mounted) return;
    final nav = Navigator.of(context);
    await nav.push(
      MaterialPageRoute(
        builder: (_) => AssessmentScreen(
          items: exs.take(3).toList(),
          // ⭐ WAL-210 lineage: đề lấy từ `exercisesForToan(6)` ⇒ bài 6
          // của đúng cuốn chứa bài tập (số bài hoá cứng cùng chỗ).
          learningContext: LearningContext(
            learnerId: p.learnerId,
            grade: p.grade,
            subject: 'Toán',
            sourceDocumentId: exs.first.book,
            lessonNo: 6,
          ),
          onFinished: (events, answers) async {
            final rec = await recordSession(
              store: widget.store,
              learnerId: p.learnerId,
              subjectId: c.subjectId,
              events: events,
              trigger: SessionTrigger.assessment,
              mode: SessionMode.assess,
            );
            final m = await masteryFromStore(widget.store, p.learnerId, c);
            if (!nav.mounted) return;
            nav.pushReplacement(
              MaterialPageRoute(
                builder: (_) => AssessmentResultScreen(
                  answers: answers,
                  summary: ConceptSummary.of(
                    m,
                    knownCaseIds: {for (final k in c.cases) k.id},
                    now: DateTime.now(),
                  ),
                  violations: rec.violations,
                  onDone: () => nav.pop(),
                ),
              ),
            );
          },
        ),
      ),
    );
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
        child: Text(msg, style: const TextStyle(fontSize: 17, height: 1.5)),
      ),
    );
  }

  /// WAL-109 — thêm người học: dùng LẠI onboarding, không nhánh UI mới.
  void _addProfile(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => Scaffold(
          body: SafeArea(
            child: OnboardingScreen(
              onDone: (p) async {
                await _onboarded(p);
                if (context.mounted) Navigator.of(context).pop();
              },
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Học cùng SAM',
    debugShowCheckedModeBanner: false,
    home: BandDensityScope(
      density: WalBandDensity.forGradeBandLabel(
        bandForGrade(_profile?.grade ?? 3)?.label ?? '3-5',
      ),
      child: _homeChild(),
    ),
  );

  /// ⭐ Lệnh 52 §4 — GỐC của tab «Giá sách».
  ///
  /// Cùng MỘT cây widget mà `onOpenSubjects` đẩy — tách ra để tab và CTA cũ
  /// dùng chung, KHÔNG nhân bản màn (§9).
  ///
  /// §13: lớp là ngữ cảnh của hồ sơ, nên `profile` đi thẳng vào đây — giá sách
  /// không bao giờ hỏi lại «con học lớp mấy».
  Widget _bookshelfRoot(BuildContext context, MissionData data) {
    final idx = _lessonIndex;
    if (idx == null || idx.books.isEmpty) {
      return SubjectsScreen(
        profile: _profile!,
        store: widget.store,
        index: idx,
      );
    }
    return BookShelfScreen(
      profile: _profile!,
      index: idx,
      onOpenBook: (b) => Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => SubjectHomeScreen(
            profile: _profile!,
            store: widget.store,
            index: idx,
            subject: b.subject,
            book: b,
            timetable: _timetable,
            reviewDueSubjects: _reviewDueSubjects(data),
          ),
        ),
      ),
    );
  }

  /// Bài mà tab SAM mở: bài của ĐÚNG lớp trẻ đang học. Bài lớp khác KHÔNG
  /// được lôi vào đây — tab SAM là chỗ học, không phải chỗ trưng bày.
  LessonDocument? _samLessonDoc() {
    final p = _profile;
    if (p == null) return null;
    for (final t in _lessonThreads(p)) {
      if (t.doc.grade == p.grade) return t.doc;
    }
    return null;
  }

  /// `null` ⇒ tab SAM ẩn lối vào ấy thay vì mở một màn rỗng.
  VoidCallback? _openWorkspaceLessonFromSam(BuildContext context) {
    final doc = _samLessonDoc();
    if (doc == null) return null;
    return () async {
      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => LessonWorkspaceScreen(
            doc: doc,
            trace: WorkspaceTrace.session,
            learnerId: _profile!.learnerId,
          ),
        ),
      );
      if (mounted) setState(_refreshMission);
    };
  }

  Widget _homeChild() => _loading
      ? (_splashQuote == null
            // ROUND 3 B5 (audit O1): khung trắng lúc chờ hồ sơ ⇒ màn
            // khởi động có nhãn hiệu, nói thật «đang mở».
            ? const BootScreen(note: 'Đang mở hồ sơ của con…')
            : SplashQuoteScreen(quote: _splashQuote!))
      : _profile == null
      ? OnboardingScreen(onDone: _onboarded)
      : FutureBuilder<MissionData>(
          future: _mission,
          builder: (context, snap) {
            final data = snap.data;
            if (data == null) {
              // ROUND 3 B5 (audit O1): chờ mission tính từ kho —
              // vẫn là màn khởi động, không phải khung trắng.
              return const BootScreen(note: 'Đang xem hôm nay học gì…');
            }
            final ocr = widget.ocr;
            // ⭐ Lệnh 52 — Home nhiều môn trở thành GỐC của tab
            // «Trang chủ». Màn KHÔNG bị viết lại; chỉ đổi chỗ nó
            // đứng trong cây (§3).
            return AppShell(
              home: MissionCenterScreen(
                data: data,
                bookRecommendation: _bookRecommendation(),
                onStartRecommendation: (rec) =>
                    _startRecommendation(context, data, rec),
                // ⭐⭐ ROUND 7 · V2 — Home nhận CẢ HỆ MẠCH HỌC, mỗi
                // mạch kèm dấu vết phiên và việc tiếp theo ĐÃ DỰNG
                // SẴN, cộng danh sách môn trên giá sách chưa có bài.
                // Không phải để Home thông minh hơn: để Home và
                // workspace nói CÙNG một điều về cùng một bài, và để
                // môn chưa có bài vẫn được nói ra đúng trạng thái.
                // `founderNextAction` là động cơ duy nhất; Home chỉ
                // trình bày và xếp hạng kết quả của nó.
                learnerGrade: _profile!.grade,
                lessonThreads: _lessonThreads(_profile!),
                shelfSubjects: _shelfSubjects(),
                // ⭐ ROUND 7 · V1 — nút Home mang tên một cách học ⇒
                // mở ĐÚNG cách học ấy. Lỗi máy thật vòng 1: «📖 Đọc ▸»
                // mở ra màn hỏi «con muốn học theo cách nào?».
                onOpenWorkspaceLesson: (doc, {at}) async {
                  await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => LessonWorkspaceScreen(
                        doc: doc,
                        trace: WorkspaceTrace.session,
                        initialView: at,
                        learnerId: _profile!.learnerId,
                      ),
                    ),
                  );
                  if (mounted) setState(() {});
                },
                learnerName: _profile!.displayName,
                profiles: _profiles,
                activeLearnerId: _profile!.learnerId,
                onSelectProfile: _selectProfile,
                onAddProfile: () => _addProfile(context),
                onParentArea: () => openParentArea(
                  context,
                  store: widget.store,
                  profiles: _profiles,
                  saveExport: _saveExport,
                ),
                onReview: () => _openReview(context),
                onAssess: () => _openAssessment(context),
                onOpenSettings: () async {
                  await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => SettingsScreen(
                        stories: _stories,
                        profile: _profile,
                        store: widget.store,
                        index: _lessonIndex,
                        profiles: _profiles,
                        onProfileChanged: _onProfileEdited,
                      ),
                    ),
                  );
                  // ⭐⭐ WAL-176 — Thời khoá biểu sửa được TỪ Thêm →
                  // Cài đặt; Home đọc `_timetable` từ STATE trong bộ
                  // nhớ, không phải kho mỗi lần build. Thiếu dòng này
                  // thì gợi ý sách qua TKB đứng yên tới lần mở app
                  // sau — TKB tưởng đã lưu nhưng Home chưa "thấy".
                  if (mounted) setState(_refreshMission);
                },
                todayStory: _stories.todayEvents(DateTime.now()).firstOrNull,
                didYouKnowStory: _didYouKnow(),
                onOpenStory: (st) => Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) =>
                        StoryDetailScreen(item: st, stories: _stories),
                  ),
                ),
                // WAL-167 — cửa trước nay là GIÁ SÁCH khi máy có bìa
                // thật; chưa có bìa thì vẫn vào lưới môn như cũ
                // (không chặn việc học vì thiếu ảnh).
                // ⭐ Lệnh 52 §9 — CÙNG gốc với tab «Giá sách»
                // (`_bookshelfRoot`), không dựng bản thứ hai.
                onOpenSubjects: () async {
                  await Navigator.of(context).push(
                    MaterialPageRoute(
                      builder: (_) => _bookshelfRoot(context, data),
                    ),
                  );
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
              ),
              bookshelf: _bookshelfRoot(context, data),
              sam: SamHubScreen(
                learnerName: _profile!.displayName,
                onCapture: ocr == null
                    ? null
                    : () async {
                        await startHomeworkFlow(
                          context,
                          profile: _profile!,
                          store: widget.store,
                          ocr: ocr,
                        );
                        if (mounted) setState(_refreshMission);
                      },
                onLearnWithSam: _openWorkspaceLessonFromSam(context),
                lessonLabel: _samLessonDoc()?.title,
              ),
              achievements: ProgressScreen(
                profile: _profile!,
                store: widget.store,
              ),
              more: SettingsScreen(
                stories: _stories,
                profile: _profile,
                store: widget.store,
                index: _lessonIndex,
                profiles: _profiles,
                onProfileChanged: _onProfileEdited,
              ),
            );
          },
        );
}
