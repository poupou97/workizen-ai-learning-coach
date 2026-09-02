/// WAL-136 (#07) — SUBJECT HOME: danh sách bài THẬT (tên mined từ SGK).
/// Bài Toán có bài tập corpus ⇒ vào học thẳng (CanonicalProblem.fromCurriculum
/// — sách là nguồn, không xác nhận giả). Bài chưa nối engine ⇒ nói thật.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/knowledge/provenance.dart';
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/learning_session.dart';
import '../../core/tutor/learning_activity.dart';
import '../history/source_reader.dart';
import '../learning_session/slice_flow.dart';
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
    final sources = _isSu ? index.suSourcesFor(l.no) : const <SuSource>[];
    final openable =
        exercises.isNotEmpty || readings.isNotEmpty || sources.isNotEmpty;
    final subtitle = exercises.isNotEmpty
        ? '${exercises.length} bài tập từ SGK — vào học ngay'
        : readings.isNotEmpty
            ? '${readings.length} bài đọc từ SGK — đọc rồi trả lời'
            : sources.isNotEmpty
                ? '${sources.length} tư liệu gốc từ SGK — đọc nguồn rồi tự kết luận'
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
              : () => exercises.isNotEmpty
                  ? _openExercise(context, l, exercises.first)
                  : readings.isNotEmpty
                      ? _openReading(context, readings.first)
                      : _openSource(context, sources.first),
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
