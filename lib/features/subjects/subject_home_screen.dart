/// WAL-136 (#07) — SUBJECT HOME: danh sách bài THẬT (tên mined từ SGK).
/// Bài Toán có bài tập corpus ⇒ vào học thẳng (CanonicalProblem.fromCurriculum
/// — sách là nguồn, không xác nhận giả). Bài chưa nối engine ⇒ nói thật.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/context/learning_context.dart';
import '../../core/curriculum/canonical_problem.dart';
import '../../core/curriculum/subject_id.dart';
import '../../core/intent/learning_intent.dart';
import '../../core/store/timetable.dart';
import '../../core/knowledge/provenance.dart';
import '../../core/knowledge/slice_curriculum.dart';
import '../../core/tutor/teaching_provenance.dart' show sourceLineForChildOf;
import '../../core/store/learner_profile.dart';
import '../../core/store/learner_store.dart';
import '../../core/store/learning_session.dart';
import '../../core/student/learning_evidence.dart';
import '../../core/student/learning_map_state.dart';
import '../../core/tutor/learning_activity.dart';
import '../history/source_reader.dart';
import '../learning_session/slice_flow.dart';
import '../geography/map_reader_screen.dart';
import '../science/experiment_screen.dart';
import '../shell/compose_lite_screen.dart';
import '../shell/reader_screen.dart';
import '../shell/session_recorder.dart';
import 'lesson_index.dart';
import 'source_gallery_screen.dart';

class SubjectHomeScreen extends StatelessWidget {
  const SubjectHomeScreen({
    super.key,
    required this.profile,
    required this.store,
    required this.index,
    required this.subject,
    this.book,
    this.timetable = const [],
    this.reviewDueSubjects = const {},
  });

  final LearnerProfile profile;
  final LearnerStore store;
  final LessonIndex index;
  final String subject;

  /// WAL-167 — khi mở TỪ GIÁ SÁCH: màn này thành «Book Home», chỉ hiện bài của
  /// đúng cuốn đó và mang tên cuốn đó. Cùng một màn, hai lối vào — không tạo
  /// màn thứ hai cho cùng một việc.
  final BookRef? book;

  /// WAL-175 — hai tín hiệu để SAM ĐỀ NGHỊ ý định. Rỗng ⇒ SAM không đề nghị và
  /// hỏi thẳng; nó KHÔNG được bịa lý do (fail closed).
  final List<TimetableEntry> timetable;

  /// Mã môn đang có chỗ vướng / đến hạn ôn — bằng chứng thắng thời khoá biểu.
  final Set<String> reviewDueSubjects;

  List<KhoaExperiment> get _experiments =>
      index.experimentsForSubject(subject);

  /// ⭐⭐ WAL-181 — toàn bộ event của NGƯỜI HỌC NÀY, một lần, để suy trạng
  /// thái Learning Map cho mọi bài đang hiện. Không lọc theo môn trước —
  /// lineage tự lọc đúng sách+bài (WAL-178/179).
  Future<List<LearningEvent>> _allEvents() async =>
      (await store.sessions(learnerId: profile.learnerId))
          .expand((s) => s.events)
          .toList();

  /// ⭐⭐ WAL-176 (Missing #1) — Home ĐÃ đề nghị đúng bài + đúng ý định (lý do
  /// thật, không đoán); màn này KHÔNG được hỏi lại. Đi thẳng qua `_startIntent`
  /// — CÙNG một đường trẻ tự chọn cũng đi, không tạo đường thứ hai cho cùng
  /// một việc (WAL-166 §subtitle, «một luật, một chỗ»).
  ///
  /// Không thấy đúng bài/hoạt động ⇒ im lặng bỏ qua — Home lỡ đề nghị bài đã
  /// biến mất thì SAM không được ép mở một bài rỗng.
  void openLessonWithIntent(
    BuildContext context, {
    required String sourceDocumentId,
    required int lessonNo,
    required LearningIntent intent,
  }) {
    final b = (index.subjects[subject] ?? const <BookLessons>[])
        .where((x) => x.sourceDocumentId == sourceDocumentId)
        .firstOrNull;
    if (b == null) return;
    final l = b.lessons.where((x) => x.no == lessonNo).firstOrNull;
    if (l == null) return;
    final acts = index.activitiesFor(book: b.sourceDocumentId, lessonNo: l.no);
    if (acts.isEmpty) return;
    final key = LessonKey(
        sourceDocumentId: b.sourceDocumentId,
        number: l.no,
        pageStart: l.pageStart);
    _startIntent(context, b, l, acts, intent, curriculumForLesson(key));
  }

  @override
  Widget build(BuildContext context) {
    final all = index.subjects[subject] ?? const <BookLessons>[];
    final books = book == null
        ? all
        : [
            for (final b in all)
              if (b.sourceDocumentId == book!.sourceDocumentId) b
          ];
    final title = book == null
        ? '$subject · Lớp ${profile.grade}'
        : (book!.volumeLabel == null
            ? book!.title
            : '${book!.title} · ${book!.volumeLabel}');
    return Scaffold(
      backgroundColor: WalColors.surface,
      // ⭐⭐ WAL-181 — nạp event MỘT LẦN cho cả màn, không phải một truy vấn
      // riêng cho từng bài. Đang tải ⇒ danh sách hiện trước, badge tới sau
      // (progressive, không chặn màn) — rỗng khi lỗi/chưa xong cũng hợp lệ,
      // KHÔNG phải lỗi (bài chỉ tạm chưa có badge, không phải "chưa học").
      body: FutureBuilder<List<LearningEvent>>(
        future: _allEvents(),
        builder: (context, snap) {
          final allEvents = snap.data ?? const <LearningEvent>[];
          return SafeArea(
            child: ListView(
              padding: const EdgeInsets.all(WalSpacing.lg),
              children: [
                Text(title,
                    style: const TextStyle(
                        fontSize: WalType.display,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink)),
                const SizedBox(height: WalSpacing.sm),
                // WAL-144 #KHTN: mục lục Khoa học 5 chưa map bài↔trang tin cậy
                // (số bài trùng/thiếu pageStart) — thí nghiệm hiện thành mục
                // RIÊNG, KHÔNG gán bừa vào bài (nói thật hơn là đoán).
                if (_experiments.isNotEmpty) _experimentsTile(context),
                if (index.mapsForSubject(subject).isNotEmpty)
                  _mapsTile(context),
                // WAL-133: hình SGK đã crop của MÔN NÀY — chỉ hiện khi có
                // asset thật kèm đủ provenance (tầng parse đã loại thứ không
                // chứng minh được), nên tile này không bao giờ mở ra màn rỗng.
                if (index.sourceAssetsFor(subject).isNotEmpty)
                  _sourceAssetsTile(context),
                for (final b in books) ...[
                  if (book == null && (b.volume != null || books.length > 1))
                    Padding(
                      padding:
                          const EdgeInsets.symmetric(vertical: WalSpacing.sm),
                      child: Text(
                          b.volume == null ? 'Sách' : 'Tập ${b.volume}',
                          style: const TextStyle(
                              fontSize: WalType.secondary,
                              fontWeight: FontWeight.w700,
                              color: WalColors.inkSoft)),
                    ),
                  for (final l in b.lessons)
                    _lessonTile(context, b, l, allEvents),
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
                          fontSize: WalType.body,
                          color: WalColors.primaryText)),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _lessonTile(BuildContext context, BookLessons b, LessonRef l,
      List<LearningEvent> allEvents) {
    // ⭐ WAL-166: hỏi DỮ LIỆU «bài này có việc gì», không hỏi «môn tên gì».
    // Luật cũ «chỉ mở khi có dữ liệu thật» giữ nguyên — chỉ bỏ ba nhánh cứng
    // theo tên môn, thứ đang khoá Khoa học và Tiếng Anh ở ngoài.
    final acts = index.activitiesFor(book: b.sourceDocumentId, lessonNo: l.no);
    final openable = acts.isNotEmpty;
    final parts = [for (final a in acts) _countLabel(a)];
    final subtitle = parts.isNotEmpty
        ? '${parts.join(' · ')} từ SGK — vào học ngay'
        : 'SAM đang học bài này — con chụp bài tập để học cùng nhé';
    // ⭐⭐ WAL-181 — badge NHỎ trong đúng tile đã có (Founder UX Constraint
    // 2026-09-04: reuse UI, không dashboard riêng). Chữ/icon, không số/%.
    final mapState = learningMapStateFor(
        sourceDocumentId: b.sourceDocumentId,
        lessonNo: l.no,
        allEvents: allEvents);
    final (badgeIcon, badgeLabel) = childLabelFor(mapState);
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      // Material bọc ListTile — nền + ink vẽ đúng chỗ (assertion framework).
      child: Material(
        color: openable ? Colors.white : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: ListTile(
        title: Row(children: [
          Expanded(
              child: Text(
            _lessonLabel(b, l),
            style: const TextStyle(
                fontSize: WalType.body,
                fontWeight: FontWeight.w600,
                color: WalColors.ink),
          )),
          if (mapState != LearningMapState.unseen) ...[
            const SizedBox(width: WalSpacing.sm),
            Text(badgeIcon, style: const TextStyle(fontSize: WalType.body)),
          ],
        ]),
        subtitle: Text(
          mapState == LearningMapState.unseen
              ? subtitle
              : '$badgeLabel · $subtitle',
          style: const TextStyle(
              fontSize: WalType.secondary, color: WalColors.inkSoft),
        ),
        trailing: openable
            ? const Icon(Icons.chevron_right, color: WalColors.primaryText)
            : null,
          onTap: !openable ? null : () => _openLesson(context, b, l, acts),
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
                      // ⭐ Duyệt thẳng từ danh sách thí nghiệm (không qua bộ
                      // chọn ý định) — ý định CHƯA BIẾT, giữ null thật lòng
                      // thay vì suy đoán để lấp field (WAL-182).
                      _openExperiment(
                          context,
                          ex,
                          LearningContext(
                              learnerId: profile.learnerId,
                              grade: profile.grade,
                              subject: subject,
                              sourceDocumentId: ex.book,
                              lessonNo: ex.lesson));
                    },
                  ),
              ]),
            ),
          ),
        ),
      ),
    );
  }

  Widget _sourceAssetsTile(BuildContext context) {
    final assets = index.sourceAssetsFor(subject);
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        child: ListTile(
          title: const Text('🖼️ Hình trong sách',
              style: TextStyle(
                  fontSize: WalType.body,
                  fontWeight: FontWeight.w600,
                  color: WalColors.ink)),
          subtitle: Text('${assets.length} hình chụp từ SGK — phóng to xem được',
              style: const TextStyle(
                  fontSize: WalType.secondary, color: WalColors.inkSoft)),
          trailing:
              const Icon(Icons.chevron_right, color: WalColors.primaryText),
          onTap: () => Navigator.of(context).push(MaterialPageRoute(
              builder: (_) =>
                  SourceGalleryScreen(subject: subject, assets: assets))),
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

  void _openExperiment(
      BuildContext context, KhoaExperiment ex, LearningContext ctx) {
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => ExperimentScreen(
              experiment: ex,
              learningContext: ctx,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  // WAL-173: mã môn suy từ TÊN, không tra bảng cứng. Nhánh cũ
                  // dồn mọi môn lạ về 'khoa-hoc' ⇒ thêm Sinh học là bằng chứng
                  // của trẻ bị ghi SAI MÔN mà không ai báo.
                  subjectId: subjectIdOf(ex.subject),
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }

  /// Bài có NHIỀU hoạt động (đọc + viết…): cho trẻ CHỌN — không nuốt hoạt động.
  /// Phụ đề đếm việc — một chỗ, vét cạn trên `sealed`.
  /// Nhãn của một bài. Số bài LẶP LẠI trong cùng cuốn là chuyện có thật —
  /// GDTC đánh số lại theo từng chủ đề — nên khi lặp thì phải nói thêm cái gì
  /// PHÂN BIỆT ĐƯỢC, nếu không trẻ thấy hai dòng «Bài 1» y hệt và tưởng máy
  /// hỏng (đo trên Nokia, khung MAIN-n03 môn Khoa học).
  ///
  /// Thứ tự ưu tiên: tên bài (nếu miner bắt được) → trang IN. Không có cả hai
  /// thì để «Bài N» trần — KHÔNG bịa thứ tự «(1)», «(2)» vì con số đó không
  /// tồn tại trong sách.
  static String _lessonLabel(BookLessons b, LessonRef l) {
    if (l.title != null) return 'Bài ${l.no} · ${_titleCase(l.title!)}';
    final repeated = b.lessons.where((o) => o.no == l.no).length > 1;
    if (repeated && l.pageStart != null) return 'Bài ${l.no} · trang ${l.pageStart}';
    return 'Bài ${l.no}';
  }

  static String _countLabel(LessonActivity a) => switch (a) {
        ExerciseActivity(:final items) => '${items.length} bài tập',
        ReadingActivity() => '1 bài đọc',
        WritingActivity() => '1 đề viết',
        SourceActivity() => '1 tư liệu gốc',
        ExperimentActivity() => '1 thí nghiệm',
      };

  void _openLesson(BuildContext context, BookLessons b, LessonRef l,
      List<LessonActivity> acts) {
    // ⭐ WAL-170 — ĐỊNH DANH CHÍNH XÁC của bài đang mở: sách + số in + trang
    // in. Trước đây chỗ này hỏi `curriculumFor(profile)`, tức chỉ hỏi LỚP,
    // nên «Nguồn bài học» của BẤT KỲ bài nào cũng trưng ra trang 21 SGK
    // Toán 5. Nay không khớp đúng bài thì không có mục đó — fail closed.
    final key = LessonKey(
        sourceDocumentId: b.sourceDocumentId,
        number: l.no,
        pageStart: l.pageStart);
    final curriculum = curriculumForLesson(key);
    // Vét cạn trên `sealed`: thêm loại việc mới mà quên nối UI ⇒ không biên
    // dịch được, thay vì im lặng biến mất khỏi sheet.
    // ⭐⭐ WAL-175 — Ý ĐỊNH, không phải danh sách việc.
    //
    // Trước đây chỗ này hỏi «Bài này có mấy việc — con chọn nhé»: đó là từ vựng
    // của `LessonActivity` rò ra giao diện, và nó làm MẤT ý định — vào bằng
    // «học trước» hay «ôn luyện» thì cũng ra cùng một danh sách (Convergence
    // §25, khoảng cách lớn nhất giữa mã và mô hình).
    //
    // Nay: SAM ĐỀ NGHỊ một ý định kèm LÝ DO nhìn thấy được; trẻ đổi được sang
    // bất kỳ ý định nào bài này làm được. Không có căn cứ thật ⇒ SAM HỎI, không
    // bịa lý do (fail closed).
    final available = availableIntents(
      hasExercises: acts.whereType<ExerciseActivity>().isNotEmpty,
      hasAnyActivity: acts.isNotEmpty,
      hasSource: curriculum != null || acts.isNotEmpty,
    );
    if (available.isEmpty) return;

    // ⭐ KHÔNG hỏi ý định khi ý định không đổi được gì. Nếu mọi ý định bài này
    // cho ra CÙNG một chuỗi hoạt động thì bộ chọn là lựa chọn giả — thêm một
    // chạm mà không thêm nghĩa. «Cùng bài, khác ý định, khác trải nghiệm» chỉ
    // đúng khi nó thật sự khác.
    final byIntent = {
      for (final i in available)
        i: activitiesForIntent(i, acts).map((a) => a.runtimeType).toList()
    };
    final distinct = byIntent.values.map((v) => v.join('|')).toSet();
    if (distinct.length <= 1) {
      _startIntent(context, b, l, acts, available.first, curriculum);
      return;
    }

    final proposal = proposeIntent(
      subject: subject,
      now: DateTime.now(),
      available: available,
      timetable: timetable,
      reviewDue: reviewDueSubjects.contains(subjectIdOf(subject)),
    );

    showModalBottomSheet<void>(
      context: context,
      backgroundColor: WalColors.surface,
      showDragHandle: true,
      // Bọc cuộn: máy thấp / bàn phím lên thì bộ chọn vẫn tới được lựa chọn
      // CUỐI. Không bọc thì «Xem trong sách» tràn khỏi màn và KHÔNG BẤM ĐƯỢC —
      // đúng lỗi đã dính ở màn PIN (WAL-145), test bắt được ở đây.
      isScrollControlled: true,
      builder: (sheet) => SafeArea(
        child: SingleChildScrollView(
          child: Padding(
          padding: const EdgeInsets.fromLTRB(
              WalSpacing.lg, 0, WalSpacing.lg, WalSpacing.lg),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_lessonLabel(b, l),
                  style: const TextStyle(
                      fontSize: WalType.body,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.sm),
              // SAM nói lý do TRƯỚC, rồi mới tới lựa chọn. Không có lý do thì
              // hỏi thẳng — không dựng một câu cho có.
              Text(
                  proposal == null
                      ? 'Con muốn bắt đầu thế nào?'
                      : proposal.reason,
                  style: const TextStyle(
                      fontSize: WalType.secondary, color: WalColors.inkSoft)),
              const SizedBox(height: WalSpacing.md),
              for (final i in _intentOrder(available, proposal?.intent))
                _intentTile(sheet, i, proposed: i == proposal?.intent,
                    onTap: () {
                  Navigator.of(sheet).pop();
                  _startIntent(context, b, l, acts, i, curriculum);
                }),
            ],
          ),
        ),
        ),
      ),
    );
  }

  /// Ý định được đề nghị lên đầu; «xem trong sách» LUÔN xuống cuối.
  ///
  /// Tra cứu là lối ra hợp lệ (Convergence, tranh luận #1) nhưng nếu đặt ngang
  /// hàng thị giác với việc học thì nó là lựa chọn rẻ nhất về nỗ lực — trẻ sẽ
  /// chọn nó. Đây là khẳng định về TRỌNG SỐ, không phải về tính chính đáng, và
  /// nó kiểm được bằng số liệu dùng thật (Convergence U1).
  static List<LearningIntent> _intentOrder(
      Set<LearningIntent> available, LearningIntent? proposed) {
    const rank = [
      LearningIntent.review,
      LearningIntent.prepare,
      LearningIntent.practice,
      LearningIntent.lookup,
    ];
    final rest = [
      for (final i in rank)
        if (available.contains(i) && i != proposed) i
    ];
    return [?proposed, ...rest];
  }

  static (String, String) _intentText(LearningIntent i) => switch (i) {
        // Ngôn ngữ TÌNH HUỐNG của trẻ, không phải từ vựng sư phạm
        // («ôn tập», «chuẩn bị» là từ của người lớn).
        LearningIntent.prepare => ('🌱', 'Mai có tiết này'),
        LearningIntent.review => ('🔁', 'Cô dạy rồi, con ôn lại'),
        LearningIntent.practice => ('✏️', 'Con có bài tập'),
        LearningIntent.lookup => ('📖', 'Xem trong sách'),
      };

  Widget _intentTile(BuildContext sheet, LearningIntent i,
      {required bool proposed, required VoidCallback onTap}) {
    final (icon, label) = _intentText(i);
    final quiet = i == LearningIntent.lookup;
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
      child: Material(
        color: proposed
            ? WalColors.primary500
            : (quiet ? Colors.transparent : WalColors.surfaceLavender),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
          side: quiet && !proposed
              ? const BorderSide(color: WalColors.surfaceLavender)
              : BorderSide.none,
        ),
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
          child: Padding(
            padding: const EdgeInsets.symmetric(
                horizontal: WalSpacing.md, vertical: WalSpacing.md),
            child: Row(children: [
              Text(icon, style: const TextStyle(fontSize: WalType.body)),
              const SizedBox(width: WalSpacing.sm),
              Expanded(
                child: Text(label,
                    style: TextStyle(
                        fontSize: WalType.body,
                        fontWeight:
                            proposed ? FontWeight.w700 : FontWeight.w600,
                        color: proposed ? Colors.white : WalColors.ink)),
              ),
              if (proposed)
                const Icon(Icons.arrow_forward, color: Colors.white, size: 20),
            ]),
          ),
        ),
      ),
    );
  }

  /// Ý định XẾP THỨ TỰ hoạt động — cùng bài, khác ý định, khác thứ tự vào.
  ///
  /// ⭐ KHÔNG nuốt hoạt động: một bài Tiếng Việt có Đọc + Viết thì cả hai phải
  /// tới được, dù ý định nào. Bản đầu của tôi chỉ mở hoạt động ĐẦU TIÊN hợp ý
  /// định, và thế là «Luyện viết» biến mất khỏi sản phẩm — test bắt được.
  static List<LessonActivity> activitiesForIntent(
      LearningIntent intent, List<LessonActivity> acts) {
    int rank(LessonActivity a) => switch (intent) {
          // Chuẩn bị: quan sát/dự đoán trước, đọc sau, bài tập cuối.
          LearningIntent.prepare => switch (a) {
              ExperimentActivity() => 0,
              ReadingActivity() => 1,
              SourceActivity() => 2,
              WritingActivity() => 3,
              ExerciseActivity() => 4,
            },
          // Ôn / bài tập: việc sinh bằng chứng trước.
          LearningIntent.review || LearningIntent.practice => switch (a) {
              ExerciseActivity() => 0,
              ExperimentActivity() => 1,
              ReadingActivity() => 2,
              WritingActivity() => 3,
              SourceActivity() => 4,
            },
          // Tra cứu: nguồn trước, và KHÔNG mời bài tập (không sinh bằng chứng).
          LearningIntent.lookup => switch (a) {
              SourceActivity() => 0,
              ReadingActivity() => 1,
              ExperimentActivity() => 2,
              WritingActivity() => 3,
              ExerciseActivity() => 9,
            },
        };
    final out = [...acts]..sort((x, y) => rank(x).compareTo(rank(y)));
    return intent == LearningIntent.lookup
        ? [for (final a in out) if (a is! ExerciseActivity) a]
        : out;
  }

  /// Nhãn + hành động của một hoạt động. Vét cạn trên `sealed` — thêm loại việc
  /// mới mà quên nối UI thì không biên dịch được.
  ///
  /// ⭐⭐ WAL-178/182/189 — [ctx] mang sẵn sách/bài/ý định lúc gọi hàm này,
  /// và CHẢY QUA tới mọi loại hoạt động (Experiment từ đầu; Reading/Writing/
  /// Source từ WAL-189) — cùng một đường, không tạo đường context riêng cho
  /// từng loại việc. `ctx.intent == lookup` ⇒ màn con phát TRACE, không phát
  /// EVIDENCE (WAL-175: tra cứu không phải bằng chứng, dù trẻ có viết gì).
  (String, VoidCallback) _activityAction(BuildContext context, LessonRef l,
          LessonActivity a, LearningContext ctx) =>
      switch (a) {
        ExerciseActivity(:final items) => (
            '🧮 Làm bài tập',
            () => _openExercise(context, l, items.first)
          ),
        ReadingActivity(:final reading) => (
            '📖 Đọc bài',
            () => _openReading(context, reading, ctx)
          ),
        WritingActivity(:final writing) => (
            '✍️ Luyện viết',
            () => _openWriting(context, writing, ctx)
          ),
        SourceActivity(:final source) => (
            '📜 Đọc tư liệu gốc',
            () => _openSource(context, source, ctx)
          ),
        ExperimentActivity(:final experiment) => (
            '🔬 Làm thí nghiệm',
            () => _openExperiment(context, experiment, ctx)
          ),
      };

  void _startIntent(BuildContext context, BookLessons b, LessonRef l,
      List<LessonActivity> acts, LearningIntent intent, SliceCurriculum? c) {
    final ordered = activitiesForIntent(intent, acts);
    // ⭐⭐ WAL-182 — "SAM đang đứng ở đâu" TỪ ĐÂY: sách + bài + ý định đã biết
    // thật (không đoán) ngay tại điểm sắp mở Tool. Dùng chung cho mọi nhánh
    // dưới, không xây context riêng cho từng activity type.
    final ctx = LearningContext(
        learnerId: profile.learnerId,
        grade: profile.grade,
        subject: subject,
        sourceDocumentId: b.sourceDocumentId,
        lessonNo: l.no,
        intent: intent);

    // Tra cứu mà bài không có nguồn nào ⇒ «Nguồn bài học» của chương trình.
    if (intent == LearningIntent.lookup && ordered.isEmpty) {
      if (c != null) _openSourceInfo(context, c);
      return;
    }
    if (ordered.isEmpty) return;
    if (ordered.length == 1) {
      _activityAction(context, l, ordered.single, ctx).$2();
      return;
    }
    // Nhiều việc trong cùng một ý định ⇒ để trẻ chọn việc, KHÔNG tự chọn hộ.
    final actions = [
      for (final a in ordered) _activityAction(context, l, a, ctx),
      if (intent == LearningIntent.lookup && c != null)
        ('📖 Nguồn bài học', () => _openSourceInfo(context, c)),
    ];
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: WalColors.surface,
      showDragHandle: true,
      // ⭐⭐ WAL-187 — cùng lỗi WAL-145 đã bắt ở sheet ý định phía trên: thiếu
      // isScrollControlled + bọc cuộn ⇒ trên máy thật, ListTile tràn khỏi
      // vùng hit-test của sheet — VẼ RA (thấy được) nhưng KHÔNG BẤM ĐƯỢC dù
      // toạ độ đúng ngay trên chữ. Phát hiện khi đi Golden Journey thật trên
      // Nokia (Tiếng Việt Bài 2 — 2 lựa chọn Đọc bài/Luyện viết đều không
      // phản hồi chạm cho tới khi thêm dòng này).
      isScrollControlled: true,
      builder: (sheet) => SafeArea(
        child: SingleChildScrollView(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const Padding(
              padding: EdgeInsets.all(WalSpacing.md),
              child: Text('Con muốn làm phần nào trước?',
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
      ),
    );
  }

  /// WAL-141 #17 — «Nguồn bài học» từ Subject Home: các cách trong chương
  /// trình + nguồn — render qua sourceLineForChildOf (một luật, một chỗ).
  void _openSourceInfo(BuildContext context, SliceCurriculum c) {
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
  void _openWriting(BuildContext context, TvWriting w, LearningContext ctx) {
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
              learningContext: ctx,
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
  void _openReading(BuildContext context, TvReading r, LearningContext ctx) {
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
              learningContext: ctx,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  subjectId: 'tieng-viet',
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }

  /// WAL-113 B2 — Sử: TƯ LIỆU gốc → SourceReader (NGUỒN ≠ SAM ≠ EM).
  void _openSource(BuildContext context, SuSource src, LearningContext ctx) {
    Navigator.of(context).push(MaterialPageRoute(
        builder: (_) => SourceReaderScreen(
              source: src,
              learningContext: ctx,
              onFinished: (events) => recordSession(
                  store: store,
                  learnerId: profile.learnerId,
                  subjectId: 'lich-su-va-dia-li',
                  events: events,
                  trigger: SessionTrigger.manual),
            )));
  }
}
