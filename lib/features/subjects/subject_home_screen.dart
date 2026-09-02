/// WAL-136 (#07) — SUBJECT HOME: danh sách bài THẬT (tên mined từ SGK).
/// Bài Toán có bài tập corpus ⇒ vào học thẳng (CanonicalProblem.fromCurriculum
/// — sách là nguồn, không xác nhận giả). Bài chưa nối engine ⇒ nói thật.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/knowledge/provenance.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/tutor/teaching_provenance.dart' show sourceLineForChildOf;
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/learning_session.dart';
import '../../core/tutor/learning_activity.dart';
import '../history/source_reader.dart';
import '../learning_session/slice_flow.dart';
import '../geography/map_reader_screen.dart';
import '../science/experiment_screen.dart';
import '../shell/compose_lite_screen.dart';
import '../shell/reader_screen.dart';
import '../shell/session_recorder.dart';
import 'lesson_index.dart';

class SubjectHomeScreen extends StatelessWidget {
  const SubjectHomeScreen({
    super.key,
    required this.profile,
    required this.store,
    required this.index,
    required this.subject,
  });

  final LearnerProfile profile;
  final LearnerStore store;
  final LessonIndex index;
  final String subject;

  bool get _isToan => subject == 'Toán';
  bool get _isTv => subject == 'Tiếng Việt';
  bool get _isSu => subject == 'LS&ĐL';
  List<KhoaExperiment> get _experiments =>
      index.experimentsForSubject(subject);

  @override
  Widget build(BuildContext context) {
    final books = index.subjects[subject] ?? const <BookLessons>[];
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            Text('$subject · Lớp ${profile.grade}',
                style: const TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            const SizedBox(height: WalSpacing.sm),
            // WAL-144 #KHTN: mục lục Khoa học 5 chưa map bài↔trang tin cậy
            // (số bài trùng/thiếu pageStart) — thí nghiệm hiện thành mục RIÊNG,
            // KHÔNG gán bừa vào bài (nói thật hơn là đoán).
            if (_experiments.isNotEmpty) _experimentsTile(context),
            if (index.mapsForSubject(subject).isNotEmpty)
              _mapsTile(context),
            for (final b in books) ...[
              if (b.volume != null || books.length > 1)
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: WalSpacing.sm),
                  child: Text(
                      b.volume == null ? 'Sách' : 'Tập ${b.volume}',
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          fontWeight: FontWeight.w700,
                          color: WalColors.inkSoft)),
                ),
              for (final l in b.lessons) _lessonTile(context, b, l),
            ],
            if (books.isEmpty)
              const Padding(
                padding: EdgeInsets.only(top: WalSpacing.xl),
                child: Text(
                  'SAM chưa có mục lục môn này trên máy.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.inkSoft),
                ),
              ),
            const SizedBox(height: WalSpacing.md),
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('◂ Môn học',
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.primaryText)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _lessonTile(BuildContext context, BookLessons b, LessonRef l) {
    final exercises =
        _isToan ? index.exercisesForToan(l.no) : const <CorpusExercise>[];
    // WAL-113: TV mở bằng bài đọc thật; Sử mở bằng TƯ LIỆU gốc — cùng luật
    // «chỉ mở khi có dữ liệu thật», không surface nào bịa nội dung.
    final readings = _isTv
        ? index.readingsForTv(b.sourceDocumentId, l.no)
        : const <TvReading>[];
    final writings = _isTv
        ? index.writingsForTv(b.sourceDocumentId, l.no)
        : const <TvWriting>[];
    final sources = _isSu ? index.suSourcesFor(l.no) : const <SuSource>[];
    final openable = exercises.isNotEmpty ||
        readings.isNotEmpty ||
        writings.isNotEmpty ||
        sources.isNotEmpty;
    final parts = <String>[
      if (exercises.isNotEmpty) '${exercises.length} bài tập',
      if (readings.isNotEmpty) '${readings.length} bài đọc',
      if (writings.isNotEmpty) '${writings.length} đề viết',
      if (sources.isNotEmpty) '${sources.length} tư liệu gốc',
    ];
    final subtitle = parts.isNotEmpty
        ? '${parts.join(' · ')} từ SGK — vào học ngay'
        : 'SAM đang học bài này — con chụp bài tập để học cùng nhé';
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      // Material bọc ListTile — nền + ink vẽ đúng chỗ (assertion framework).
      child: Material(
        color: openable ? Colors.white : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: ListTile(
        title: Text(
          l.title == null ? 'Bài ${l.no}' : 'Bài ${l.no} · ${_titleCase(l.title!)}',
          style: const TextStyle(
              fontSize: WalType.body,
              fontWeight: FontWeight.w600,
              color: WalColors.ink),
        ),
        subtitle: Text(
          subtitle,
          style: const TextStyle(
              fontSize: WalType.secondary, color: WalColors.inkSoft),
        ),
        trailing: openable
            ? const Icon(Icons.chevron_right, color: WalColors.primaryText)
            : null,
          onTap: !openable
              ? null
              : () => _openLesson(
                  context, l, exercises, readings, writings, sources),
        ),
      ),
    );
  }

  /// «CỘNG, TRỪ HAI PHÂN SỐ…» → «Cộng, trừ hai phân số…» — tiêu đề mined in hoa.
  static String _titleCase(String upper) {
    final low = upper.toLowerCase();
    return low.isEmpty ? low : low[0].toUpperCase() + low.substring(1);
  }

  void _openExercise(BuildContext context, LessonRef l, CorpusExercise e) {
    // Sách là NGUỒN TIN: bài tập in trong SGK ⇒ sourceStated, có trang.
    final problem = CanonicalProblem.fromCurriculum(
      exerciseLabel: 'b${l.no}',
      expression: e.expr,
      provenance: Provenance(
        origin: KnowledgeOrigin.sourceStated,
        sourceId: e.book,
        extractionMethod: 'qmap-v1',
        confidence: 0.9,
        grade: index.grade,
        subject: subject,
        pageStart: e.page,
      ),
    );
    openCanonicalProblem(context,
        problem: problem, profile: profile, store: store);
  }

  Widget _experimentsTile(BuildContext context) {
    final n = _experiments.length;
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: ListTile(
          title: const Text('🔬 Thí nghiệm trong sách',
              style: TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w600,
                  color: WalColors.ink)),
          subtitle: Text('$n thí nghiệm từ SGK — dự đoán rồi làm thử',
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
          trailing:
              const Icon(Icons.chevron_right, color: WalColors.primaryText),
          onTap: () => showModalBottomSheet<void>(
            context: context,
            backgroundColor: WalColors.surface,
            builder: (sheet) => SafeArea(
              child: ListView(shrinkWrap: true, children: [
                for (final ex in _experiments)
                  ListTile(
                    title: Text(ex.title,
                        style: const TextStyle(
                            fontSize: WalType.body, color: WalColors.ink)),
                    subtitle: Text('tr. ${ex.page}',
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.inkSoft)),
                    onTap: () {
                      Navigator.of(sheet).pop();
                      _openExperiment(context, ex);
                    },
                  ),
              ]),
            ),
          ),
        ),
      ),
    );
  }

  Widget _mapsTile(BuildContext context) {
    final maps = index.mapsForSubject(subject);
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: ListTile(
          title: const Text('🗺️ Bản đồ trong sách',
              style: TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w600,
                  color: WalColors.ink)),
          subtitle: Text(
              '${maps.length} bản đồ từ SGK — nhìn rồi chỉ ra',
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
          trailing:
              const Icon(Icons.chevron_right, color: WalColors.primaryText),
          onTap: () => Navigator.of(context).push(MaterialPageRoute(
              builder: (_) => MapReaderScreen(
                    map: maps.first,
                    onFinished: (events) => recordSession(
                        store: store,
                        learnerId: profile.learnerId,
                        subjectId: 'dia-li',
                        events: events,
                        trigger: SessionTrigger.manual),
                  ))),
        ),
      ),
    );
  }

  void _openExperiment(BuildContext context, KhoaExperiment ex) {
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ExperimentScreen(
              experiment: ex,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  subjectId: switch (ex.subject) {
                    'Vật lí' => 'vat-li',
                    'Hoá học' => 'hoa-hoc',
                    _ => 'khoa-hoc',
                  },
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }

  /// Bài có NHIỀU hoạt động (đọc + viết…): cho trẻ CHỌN — không nuốt hoạt động.
  void _openLesson(
      BuildContext context,
      LessonRef l,
      List<CorpusExercise> exercises,
      List<TvReading> readings,
      List<TvWriting> writings,
      List<SuSource> sources) {
    final actions = <(String, VoidCallback)>[
      if (exercises.isNotEmpty)
        ('🧮 Làm bài tập', () => _openExercise(context, l, exercises.first)),
      if (exercises.isNotEmpty && _isToan)
        ('📖 Nguồn bài học', () => _openSourceInfo(context)),
      if (readings.isNotEmpty)
        ('📖 Đọc bài', () => _openReading(context, readings.first)),
      if (writings.isNotEmpty)
        ('✍️ Luyện viết', () => _openWriting(context, writings.first)),
      if (sources.isNotEmpty)
        ('📜 Đọc tư liệu gốc', () => _openSource(context, sources.first)),
    ];
    if (actions.length == 1) {
      actions.single.$2();
      return;
    }
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: WalColors.surface,
      builder: (sheet) => SafeArea(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Padding(
            padding: EdgeInsets.all(WalSpacing.md),
            child: Text('Bài này có mấy việc — con chọn nhé',
                style: TextStyle(
                    fontSize: WalType.body,
                    fontWeight: FontWeight.w600,
                    color: WalColors.ink)),
          ),
          for (final a in actions)
            ListTile(
              title: Text(a.$1,
                  style: const TextStyle(
                      fontSize: WalType.body, color: WalColors.ink)),
              onTap: () {
                Navigator.of(sheet).pop();
                a.$2();
              },
            ),
          const SizedBox(height: WalSpacing.sm),
        ]),
      ),
    );
  }

  /// WAL-141 #17 — «Nguồn bài học» từ Subject Home: các cách trong chương
  /// trình + nguồn — render qua sourceLineForChildOf (một luật, một chỗ).
  void _openSourceInfo(BuildContext context) {
    final c = curriculumFor(profile);
    if (c == null) return;
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: WalColors.surface,
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(
            WalSpacing.lg, 0, WalSpacing.lg, WalSpacing.xl),
        child: ListView(shrinkWrap: true, children: [
          const Text('Nguồn bài học',
              style: TextStyle(
                  fontSize: WalType.title,
                  fontWeight: FontWeight.w700,
                  color: WalColors.ink)),
          const SizedBox(height: WalSpacing.sm),
          for (final m in c.catalogue) ...[
            const SizedBox(height: WalSpacing.sm),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(WalSpacing.md),
              decoration: BoxDecoration(
                  color: WalColors.white,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusChip)),
              child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('«${m.name}»',
                        style: const TextStyle(
                            fontSize: WalType.body,
                            fontWeight: FontWeight.w600,
                            color: WalColors.ink)),
                    const SizedBox(height: 4),
                    Text(sourceLineForChildOf(m.provenance),
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            color: WalColors.primaryText,
                            height: 1.4)),
                  ]),
            ),
          ],
        ]),
      ),
    );
  }

  /// WAL-144 — TV: đề VIẾT thật → Compose (dàn ý → nháp → góp ý → sửa;
  /// SAM KHÔNG viết hộ — không tồn tại chỗ chứa bài mẫu). Evidence một chỗ ghi.
  void _openWriting(BuildContext context, TvWriting w) {
    final activity = LearningActivity(
      activityId: '${w.book}:l${w.lesson}:viet',
      prompt: w.prompt,
      response: ResponseKind.compose,
      conceptId: 'tv-viet',
      sourceBook: w.book,
      sourcePage: w.page,
    );
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ComposeLiteScreen(
              activity: activity,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  subjectId: 'tieng-viet',
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }

  /// WAL-113 B1 — TV: đoạn văn + câu hỏi NGUYÊN VĂN từ units (textbookVerbatim).
  /// SGK không in đáp án ⇒ activity KHÔNG có options — Reader chạy chế độ câu
  /// hỏi mở, KHÔNG chấm (UNKNOWN ≠ SAI). Evidence ghi MỘT LẦN qua recordSession.
  void _openReading(BuildContext context, TvReading r) {
    final q = r.questions.first;
    final activity = LearningActivity(
      activityId: '${r.book}:l${r.lesson}:doc-hieu',
      prompt: q.prompt,
      response: ResponseKind.readRespond,
      conceptId: 'tv-doc-hieu',
      passage: r.passage,
      sourceBook: r.book,
      sourcePage: q.page ?? r.page,
    );
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ReaderScreen(
              activity: activity,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  subjectId: 'tieng-viet',
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }

  /// WAL-113 B2 — Sử: TƯ LIỆU gốc → SourceReader (NGUỒN ≠ SAM ≠ EM).
  void _openSource(BuildContext context, SuSource src) {
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => SourceReaderScreen(
              source: src,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  subjectId: 'lich-su-va-dia-li',
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }
}
