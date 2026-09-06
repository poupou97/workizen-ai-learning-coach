/// ⭐⭐ WAL-51 — Màn "HÔM NAY" (Mission Center): màn hình đầu tiên của
/// «Học cùng SAM», bám wireframe M1 (SLICE-1-WIREFRAMES.md).
///
/// Luật hiển thị (khắc từ doctrine, có widget test giữ):
/// - MỘT hành động kế tiếp, kèm `decision.reason` — lý do trẻ-đọc-được.
/// - CẤM %: không con số nào giả vờ chính xác.
/// - Ôn tới hạn: sắc thái nhẹ, KHÔNG đỏ, không đếm ngược hối thúc.
/// - Thử-thách-phủ: dạng CHƯA THỬ được nói thẳng tên.
/// - Mascot HELLO thu nhỏ — SAM chào rồi lùi lại (STEP_BACK là feature).
///
/// ROUND 4 (Lane B §6 «Home»): thẻ «BÀI HỌC SAM» và thẻ Scale trung thực là
/// MỘT vùng «Hôm nay» — một dòng SAM nói học gì tiếp và vì sao (lời trẻ), thẻ
/// chính ở trên, thẻ «còn có thể mở» ở dưới; không còn ô mic «SAM đang học
/// cách trò chuyện» (hứa chat mà không có chat — audit round 3).
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/agenda/learning_agenda.dart';
import '../../core/display/lesson_title.dart';
import '../../core/intent/next_lesson.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/next_action.dart';
import '../../core/agenda/lesson_next_action.dart' show LessonNextAction;
import '../../core/stories/stories_store.dart';
import '../../core/store/learner_profile.dart';
import '../camera/camera_demo_flow.dart';
import '../parent/parent_tonight_screen.dart';
import '../lesson_workspace/widgets/fixture_chip.dart';
import '../lesson_workspace/widgets/trust_sheet.dart';
import 'mission_data.dart';
import '../subjects/subject_display.dart';

/// «Vì sao bài này?» trên thẻ Bài học SAM — chỉ nói điều có thật trong tài
/// liệu: bài đã được xếp sẵn theo các cách học từ sách (đếm phần sách có).
String workspaceWhyLine(LessonDocument doc) {
  final ways = <String>[
    'đọc như trong sách',
    if (doc.semantic.isNotEmpty) 'xem sơ đồ / bảng',
    if (doc.tutorScript != null)
      'trả lời ${doc.tutorScript!.asks.length} câu hỏi trong sách cùng SAM',
  ];
  return 'Vì sao bài này? Đây là bài SAM đã xếp sẵn từ sách để con '
      '${ways.join(', ')} — con thử trước nhé.';
}

/// ⭐ ROUND 4 (Lane C × Lane B) — dòng giới thiệu khu LÁT CẮT NGHIÊN CỨU.
///
/// Máy của Na là máy lớp 6; lát cắt của Lane C là sách LỚP 5. Nó có mặt ở đây
/// để Founder đi tới được mà KHÔNG phải tạo hồ sơ mới — nên phải nói thật với
/// trẻ rằng đây không phải bài của lớp mình, bằng lời trẻ, không hứa hẹn gì,
/// và không đẩy trẻ vào đó (việc hôm nay vẫn ở phía trên).
const String researchAreaLine =
    'Đây không phải bài của lớp con — SAM đang tập đọc thử một cuốn sách khác. '
    'Con xem cho biết cũng được. Bài hôm nay của con ở phía trên nhé.';

class MissionCenterScreen extends StatelessWidget {
  const MissionCenterScreen({
    super.key,
    required this.data,
    this.learnerName,
    this.onStartHomework,
    this.profiles = const [],
    this.activeLearnerId,
    this.onSelectProfile,
    this.onAddProfile,
    this.onParentArea,
    this.onOpenSubjects,
    this.onReview,
    this.onAssess,
    this.onOpenSettings,
    this.todayStory,
    this.didYouKnowStory,
    this.onOpenStory,
    this.bookRecommendation,
    this.onStartRecommendation,
    this.workspaceLesson,
    this.onOpenWorkspaceLesson,
    this.researchLessons = const [],
    this.openedViews = const {},
    this.lessonNext,
  });

  final MissionData data;

  /// WAL-109 — multi-profile: danh sách hồ sơ trên máy + hồ sơ ĐANG HỌC.
  /// Switch không logout; mọi flow phía dưới bind vào activeLearnerId.
  final List<LearnerProfile> profiles;
  final String? activeLearnerId;
  final void Function(String learnerId)? onSelectProfile;
  final VoidCallback? onAddProfile;

  /// WAL-109 — khu bố mẹ qua PIN gate. `null` = flow demo cũ (test cũ giữ).
  final VoidCallback? onParentArea;

  /// WAL-136 — mở MÔN HỌC (lesson picker từ corpus). `null` = nút mờ như cũ.
  final VoidCallback? onOpenSubjects;

  /// WAL-138 — chip «Ôn luyện»: mở bài ôn THẬT (hoặc nói thật khi chưa tới hạn).
  final VoidCallback? onReview;

  /// WAL-143 — «Kiểm tra hiểu bài». `null` = máy này chưa đủ dữ liệu ⇒ chip
  /// nói thật thay vì mở màn rỗng.
  final VoidCallback? onAssess;

  /// WAL-152 — Settings/Thêm (entry Kho khám phá). `null` = ẩn icon.
  final VoidCallback? onOpenSettings;

  /// «Ngày này năm xưa» — CHỈ khi có event VERIFIED đúng ngày (§14);
  /// không có ⇒ [didYouKnowStory] với nhãn KHÁC — không giả Today.
  final StoryItem? todayStory;
  final StoryItem? didYouKnowStory;
  final void Function(StoryItem)? onOpenStory;

  /// WAL-108 — mở flow camera THẬT (learnerId + store xuyên suốt). `null` =
  /// môi trường chưa nối slice (test/demo cũ) ⇒ giữ flow demo.
  final VoidCallback? onStartHomework;

  /// Tên gọi từ HỒ SƠ THẬT (WAL-95). `null` ⇒ xưng hô trung tính, không bịa tên.
  final String? learnerName;

  /// ⭐⭐ WAL-176 (Missing #1) — gợi ý Ở CẤP SÁCH từ TKB (Khoa học, Sử…), khi
  /// agenda Toán (WAL-102) chưa có gì khẩn (không phải review/retrieve).
  /// `null` = không có căn cứ thật ⇒ thẻ giữ nguyên hành vi cũ, không bịa.
  final HomeRecommendation? bookRecommendation;

  /// Bấm «Bắt đầu» khi thẻ đang hiện [bookRecommendation]: đưa thẳng trẻ vào
  /// ĐÚNG sách/bài/ý định — KHÔNG hỏi lại (SAM đã hỏi xong ở Home rồi).
  final void Function(HomeRecommendation)? onStartRecommendation;

  /// ⭐ ROUND 3 B1 — bài có Lesson Workspace (ba cách học) của ĐÚNG lớp này,
  /// từ `WorkspaceCatalog`. `null` ⇒ không có thẻ (không bịa). Thẻ nói rõ đây
  /// là bản thử nghiệm; nó KHÔNG thay thẻ «Việc SAM đề xuất» (hợp đồng G2
  /// của Track A giữ nguyên) — chỉ làm sản phẩm NHÌN THẤY được từ Home.
  final LessonDocument? workspaceLesson;
  /// ⭐ ROUND 7 · V1 — [at] là CÁCH HỌC mà nút vừa hứa mở.
  ///
  /// Lỗi máy thật vòng 1: Home nói «📖 Đọc ▸», trẻ chạm, và app mở màn «Con
  /// muốn học bài này theo cách nào?» — tức HỎI LẠI đúng câu Home vừa trả lời
  /// hộ. Nút mang tên một cách học thì phải mở ĐÚNG cách học ấy. `null` (thẻ
  /// nghiên cứu, thẻ phụ) ⇒ giữ màn «Vào bài học» như cũ: ở đó SAM chưa hứa
  /// gì cả.
  final void Function(LessonDocument doc, {WorkspaceView? at})?
      onOpenWorkspaceLesson;

  /// ⭐ ROUND 4 (Lane C, Golden Slice #2) — LÁT CẮT NGHIÊN CỨU của lớp KHÁC
  /// (LS&ĐL 5 Bài 8 trên máy của học sinh lớp 6): hiện thành thẻ riêng, ghi
  /// rõ «sách lớp N», để Founder đi được tới lát cắt mà không tạo hồ sơ mới.
  /// Rỗng ⇒ không thẻ. Mở bằng cùng [onOpenWorkspaceLesson].
  final List<LessonDocument> researchLessons;

  /// ⭐⭐ ROUND 7 · V1 — DẤU VẾT PHIÊN của [workspaceLesson]: những cách học
  /// trẻ đã MỞ. Home KHÔNG tự hỏi `WorkspaceTrace` (cùng kỷ luật với lớp trợ
  /// giúp trong workspace): tầng trên dựng sẵn và truyền xuống.
  ///
  /// ⚠ MỞ ≠ HIỂU. Tập này chỉ được dùng để nói «con đã mở gì», không bao giờ
  /// để nói «con đã hiểu gì» — `home_learning_now_test.dart` giữ điều đó.
  final Set<WorkspaceView> openedViews;

  /// ⭐⭐ ROUND 7 · V1 — VIỆC TIẾP THEO của [workspaceLesson], do CHÍNH động
  /// cơ mà workspace dùng sinh ra (`founderNextAction`). Home không có động
  /// cơ đề xuất thứ hai: nếu nó tự nghĩ ra CTA, Home và workspace sẽ nói hai
  /// điều khác nhau về cùng một bài. `null` ⇒ nút mở bài như cũ.
  final LessonNextAction? lessonNext;

  static const workspaceCardKey = Key('home-workspace-card');

  /// ROUND 7 · V1 — những phần của thẻ «ĐANG HỌC».
  static const nextActionCtaKey = Key('home-next-action-cta');
  static const progressKey = Key('home-evidence-progress');
  static const samSeenKey = Key('home-sam-seen');
  static const continueRowKey = Key('home-continue-row');
  static Key continueChipKey(WorkspaceView v) =>
      Key('home-continue-${v.name}');
  static const samLineKey = Key('home-sam-line');
  static const secondaryCardKey = Key('home-secondary-card');

  /// ROUND 4 (Lane C) — thẻ lát cắt NGHIÊN CỨU, một khoá cho mỗi bài.
  static Key researchCardKey(String slotKey) =>
      Key('home-research-card-$slotKey');
  static const researchAreaLineKey = Key('home-research-area-line');

  /// Bài học SAM là VIỆC CHÍNH của «Hôm nay» khi có bài cho lớp này và không
  /// có việc Toán khẩn vì bằng chứng thật (review/retrieve thắng — Convergence
  /// §10) và không có gợi ý sách theo TKB đang lên tiếng.
  bool get _workspaceIsPrimary =>
      workspaceLesson != null &&
      !_agendaIsEvidenceUrgent &&
      _effectiveRecommendation == null;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.md),
          children: [
            _greeting(),
            // ⭐⭐ ROUND 7 · V1 — MÀN ĐẦU TRẢ LỜI BA CÂU, KHÔNG PHẢI LÀ MỘT
            // BỆ PHÓNG. Founder order 49 §1: «Một màn đầu phải nổi bật: ĐANG
            // HỌC GÌ + VIỆC TIẾP THEO. SAM thấy gì là hỗ trợ, không tranh
            // hierarchy với Next Action.»
            //
            // Máy thật (`round7-r1-device-walk/02-home.png`) cho thấy thứ tự
            // cũ: chào → SAM nhắc LẠI tên bài → 5 chip chung chung (một phần
            // ba màn) → nhãn HÔM NAY → thẻ bài → nút «Mở bài học» RƠI XUỐNG
            // DƯỚI NẾP GẤP. Trẻ mở app và thấy… một bảng nút.
            //
            // Thứ tự mới khi có bài đang học: ĐANG HỌC (nổi bật, có việc tiếp
            // theo trong chính thẻ) → CÓ THỂ LÀM TIẾP (những cách học còn
            // lại) → SAM ĐÃ THẤY GÌ (nhỏ, phụ) → rồi mới tới phần còn lại.
            // Dòng SAM nhắc lại tên bài bị XOÁ khỏi đường này: nó lặp đúng
            // cái tiêu đề nằm ngay dưới nó, và nó đẩy nút xuống.
            if (_workspaceIsPrimary) ...[
              const SizedBox(height: WalSpacing.sm),
              _learningNowCard(workspaceLesson!),
              const SizedBox(height: WalSpacing.sm),
              _continueRow(workspaceLesson!),
              const SizedBox(height: WalSpacing.sm),
              _samSeenCard(workspaceLesson!),
              const SizedBox(height: WalSpacing.lg),
              _sectionLabel('HÔM NAY'),
              _nextActionCard(secondary: true),
            ] else ...[
              const SizedBox(height: WalSpacing.sm),
              _samLine(),
              const SizedBox(height: WalSpacing.sm),
              _intentChips(),
              const SizedBox(height: WalSpacing.md),
              _sectionLabel('HÔM NAY'),
              _nextActionCard(),
              if (workspaceLesson != null) ...[
                const SizedBox(height: WalSpacing.sm),
                _workspaceCard(workspaceLesson!, primary: false),
              ],
            ],
            // ⭐ ROUND 4 (Lane C × Lane B) — lát cắt NGHIÊN CỨU đứng NGOÀI khu
            // «Hôm nay», dưới nhãn riêng: một bài sách lớp khác không được
            // trôi vào việc hôm nay của trẻ lớp 6 như nội dung bình thường.
            if (researchLessons.isNotEmpty) ...[
              const SizedBox(height: WalSpacing.lg),
              _sectionLabel('SAM ĐANG TẬP ĐỌC SÁCH KHÁC'),
              Padding(
                padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                child: Text(researchAreaLine,
                    key: MissionCenterScreen.researchAreaLineKey,
                    style: const TextStyle(
                        fontSize: WalType.secondary,
                        color: WalColors.inkSoft,
                        height: 1.4)),
              ),
              for (final d in researchLessons) ...[
                _workspaceCard(d, research: true),
                const SizedBox(height: WalSpacing.sm),
              ],
            ],
            if (data.upcomingSubjects.isNotEmpty) ...[
              const SizedBox(height: WalSpacing.sm),
              _upcomingRow(),
            ],
            if (todayStory != null || didYouKnowStory != null) ...[
              const SizedBox(height: WalSpacing.md),
              _discoveryCard(),
            ],
            const SizedBox(height: WalSpacing.lg),
            if (data.reviews.isNotEmpty) ...[
              _sectionLabel('Ôn lại'),
              for (final r in data.reviews) _reviewTile(r),
              const SizedBox(height: WalSpacing.md),
            ],
            if (data.unobservedCaseNames.isNotEmpty) ...[
              _sectionLabel('Thử dạng mới'),
              for (final name in data.unobservedCaseNames) _unseenTile(name),
            ],
            // ROUND 7 · V1 — 5 chip ý định chung chung KHÔNG còn ăn một phần
            // ba màn đầu khi trẻ đang có bài dở. Chúng vẫn còn, đủ xa để
            // không tranh chỗ với việc tiếp theo.
            if (_workspaceIsPrimary) ...[
              const SizedBox(height: WalSpacing.lg),
              _sectionLabel('CÁCH KHÁC ĐỂ HỌC'),
              _intentChips(),
            ],
            const SizedBox(height: WalSpacing.xl),
            _bottomActions(),
          ],
        ),
      ),
    );
  }

  Widget _greeting() => Builder(
      builder: (context) => Row(children: [
            _samChip('assets/mascot/sam-hello.png', size: 44),
            const SizedBox(width: WalSpacing.sm),
            Expanded(
              child: InkWell(
                onTap: onSelectProfile == null
                    ? null
                    : () => _showSwitcher(context),
                child: Text('Chào ${learnerName ?? data.studentName}!',
                    style: const TextStyle(
                        fontSize: WalType.title,
                        fontWeight: FontWeight.w700,
                        color: WalColors.ink)),
              ),
            ),
            // WAL-109 — switcher là CÔNG DÂN HẠNG NHẤT (§26): máy của chung,
            // đổi người học phải dễ như đổi hồ sơ Netflix — và không logout.
            if (onSelectProfile != null)
              IconButton(
                tooltip: 'Đổi người học',
                onPressed: () => _showSwitcher(context),
                icon: const Icon(Icons.switch_account_outlined,
                    color: WalColors.primaryText),
              ),
            if (onOpenSettings != null)
              IconButton(
                tooltip: 'Thêm',
                onPressed: onOpenSettings,
                icon: const Icon(Icons.more_horiz,
                    color: WalColors.primaryText),
              ),
          ]));

  void _showSwitcher(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: WalColors.surface,
      builder: (ctx) => SafeArea(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Padding(
            padding: EdgeInsets.all(WalSpacing.sm),
            child: Text('Ai đang học?',
                style: TextStyle(
                    fontSize: WalType.title,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
          ),
          for (final p in profiles)
            ListTile(
              leading: CircleAvatar(
                  backgroundColor: p.learnerId == activeLearnerId
                      ? WalColors.primary500
                      : WalColors.surfaceLavender,
                  child: Text(p.displayName.characters.first,
                      style: TextStyle(
                          color: p.learnerId == activeLearnerId
                              ? Colors.white
                              : WalColors.ink))),
              title: Text('${p.displayName} · Lớp ${p.grade}',
                  style: const TextStyle(
                      fontSize: WalType.body, color: WalColors.ink)),
              trailing: p.learnerId == activeLearnerId
                  ? const Icon(Icons.check, color: WalColors.primaryText)
                  : null,
              onTap: () {
                Navigator.of(ctx).pop();
                if (p.learnerId != activeLearnerId) {
                  onSelectProfile?.call(p.learnerId);
                }
              },
            ),
          if (onAddProfile != null)
            ListTile(
              leading: const CircleAvatar(
                  backgroundColor: WalColors.surfaceLavender,
                  child:
                      Icon(Icons.add, color: WalColors.primaryText)),
              title: const Text('Thêm người học',
                  style: TextStyle(
                      fontSize: WalType.body, color: WalColors.ink)),
              onTap: () {
                Navigator.of(ctx).pop();
                onAddProfile?.call();
              },
            ),
          const SizedBox(height: WalSpacing.sm),
        ]),
      ),
    );
  }

  /// Toán (WAL-102) đang có việc do BẰNG CHỨNG thúc — bậc cao nhất trong thứ
  /// tự đã chốt (Convergence §10: bằng chứng → TKB → làm dở → không có gì).
  bool get _agendaIsEvidenceUrgent =>
      data.agenda?.kind == AgendaActionKind.review ||
      data.agenda?.kind == AgendaActionKind.retrieve;

  /// ⭐⭐ WAL-176 — gợi ý sách qua TKB chỉ được lên tiếng khi Toán KHÔNG đang
  /// khẩn vì bằng chứng thật. Nó ĐƯỢC PHÉP thay «nghỉ» của Toán: `rest` chỉ
  /// có nghĩa «Toán hôm nay không có gì mới», không phải «cả ngày không có gì
  /// để làm» — một tiết Khoa học thật ngày mai là lý do khác, không phải SAM
  /// nói lại cùng một việc.
  HomeRecommendation? get _effectiveRecommendation =>
      _agendaIsEvidenceUrgent ? null : bookRecommendation;

  Widget _nextActionCard({bool secondary = false}) {
    final rec = _effectiveRecommendation;
    final hasProposal = rec != null || data.agenda != null;
    final title = rec != null
        ? '${rec.subject} · Bài ${rec.lessonNo}'
        : (data.agenda == null
            ? data.nextActionTitle
            : _agendaTitle(data.agenda!.kind));
    // ⭐ reason đến từ resolver (agenda hoặc HomeRecommendation) — hiển thị
    // NGUYÊN VĂN, UI không suy diễn thêm. Lớp chỉ có đường Scale (WAL-210
    // G2): lý do do buildMissionFromStore viết từ con số thật của pack.
    // ROUND 4: khi bài học SAM là việc chính, thẻ Scale KHÔNG nói «SAM chưa
    // có bài dạy riêng cho lớp 6» nữa (mâu thuẫn với thẻ ngay trên) — chỉ nói
    // điều còn đúng: ở Môn học con mở được N bài từ sách (N thật của pack).
    final reason = rec != null
        ? rec.reason
        : (data.agenda?.reason ??
            (secondary && data.scaleLessonCount > 0
                ? 'Ở Môn học con mở được ${data.scaleLessonCount} bài từ '
                    'sách giáo khoa — đọc, làm thí nghiệm, viết.'
                : data.nextActionReason) ??
            data.decision.reason);
    final showButton =
        rec != null || data.agenda?.kind != AgendaActionKind.rest;
    // ⭐ WAL-210 G2: không agenda + có bài Scale ⇒ «Bắt đầu» mở MÔN HỌC (giá
    // sách), KHÔNG mở camera — camera là đường của nội dung Deep (chip 📷 +
    // nút «Chụp bài tập» vẫn giữ nguyên cho nó).
    final onPressed = rec != null
        ? (onStartRecommendation == null
            ? null
            : () => onStartRecommendation!(rec))
        : (_startForAgenda() ??
            (data.scaleLessonCount > 0 ? onOpenSubjects : null) ??
            onStartHomework ??
            () {});
    return Container(
      key: secondary ? MissionCenterScreen.secondaryCardKey : null,
      padding: EdgeInsets.all(secondary ? WalSpacing.md : WalSpacing.lg),
      decoration: BoxDecoration(
        color: secondary ? Colors.white : WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (hasProposal || secondary) ...[
          Text(secondary ? 'CÒN CÓ THỂ MỞ' : 'VIỆC SAM ĐỀ XUẤT',
              style: const TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.1,
                  color: WalColors.inkSoft)),
          const SizedBox(height: 4),
        ],
        Text(title,
            style: TextStyle(
                fontSize: secondary ? WalType.body + 1 : WalType.title,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText)),
        const SizedBox(height: WalSpacing.sm),
        Text(reason,
            style: TextStyle(
                fontSize: secondary ? WalType.secondary : WalType.body,
                color: WalColors.ink,
                height: 1.45)),
        if (showButton) ...[
          const SizedBox(height: WalSpacing.md),
          SizedBox(
            height: WalSpacing.minTouch,
            child: secondary
                ? OutlinedButton(
                    style: OutlinedButton.styleFrom(
                        foregroundColor: WalColors.primaryText,
                        side: const BorderSide(color: WalColors.primary500),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(
                                WalSpacing.radiusButton))),
                    onPressed: onPressed,
                    child: const Text('Vào Môn học ▸',
                        style: TextStyle(
                            fontSize: WalType.body,
                            fontWeight: FontWeight.w700)),
                  )
                : FilledButton(
                    style: FilledButton.styleFrom(
                        backgroundColor: WalColors.primary500,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(
                                WalSpacing.radiusButton))),
                    onPressed: onPressed,
                    child: const Text('Bắt đầu',
                        style: TextStyle(
                            fontSize: WalType.body,
                            fontWeight: FontWeight.w700)),
                  ),
          ),
        ],
      ]),
    );
  }

  // ── ROUND 7 · V1 — «ĐANG HỌC» + «VIỆC TIẾP THEO» ───────────────────────

  /// Những cách học bài này thật sự CÓ (một nguồn với luật đề xuất).
  List<WorkspaceView> _waysOf(LessonDocument doc) => [
        if (doc.blocks.any((b) => b is! WithheldBlock)) WorkspaceView.read,
        if (doc.semantic.isNotEmpty) WorkspaceView.visual,
        if (doc.tutorScript != null) WorkspaceView.tutor,
      ];

  /// Đã mở bao nhiêu trong số cách học bài NÀY có. Giao với [_waysOf] để một
  /// dấu vết của bài khác không bao giờ đếm vào đây.
  int _openedCount(LessonDocument doc) =>
      _waysOf(doc).where(openedViews.contains).length;

  /// ⭐⭐ THẺ «ĐANG HỌC» — thẻ nổi bật nhất của màn đầu.
  ///
  /// Nó trả lời cả hai câu Founder yêu cầu trong MỘT khối: đang học gì (tên
  /// bài, sách, trang) và việc tiếp theo (nút, nhãn lấy từ [lessonNext] — tức
  /// từ CHÍNH động cơ workspace dùng, không phải một luật thứ hai của Home).
  ///
  /// Tiến độ là BẰNG CHỨNG MỞ, không phải mastery: N vạch cho N cách học bài
  /// này có, tô những cách đã mở. Không %, không sao, không «đã thạo».
  Widget _learningNowCard(LessonDocument doc) {
    final ways = _waysOf(doc);
    final opened = _openedCount(doc);
    final where = doc.chapter == null
        ? doc.pageRangeLine
        : '${doc.chapter!.label} · ${doc.pageRangeLine}';
    final next = lessonNext;
    final ctaLabel = next == null
        ? 'Mở bài học'
        : (next.view == null ? 'Xem tiếp bài này ▸' : '${next.label} ▸');
    return Container(
      key: MissionCenterScreen.workspaceCardKey,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
        color: WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        // ROUND 7 · V1 lượt 2 (máy thật, 01-home.png): một dòng nhãn ba vế
        // IN HOA 15sp XUỐNG HAI DÒNG và át cả tên bài. Nhãn «bản thử nghiệm»
        // là BẮT BUỘC — nhưng nó là một SỰ THẬT VỀ NGUỒN, không phải tiêu đề
        // của khu. Tách ra: eyebrow một từ, nhãn nguồn thành chip gọn dưới
        // dòng trang, dùng LẠI `FixtureChip` của workspace (một bộ chữ, một
        // đường mở sheet «Nguồn & độ tin»).
        const Text('ĐANG HỌC',
            style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.1,
                color: WalColors.inkSoft)),
        const SizedBox(height: 2),
        Text(displayLessonLabel(doc.lessonNo, doc.title),
            style: const TextStyle(
                fontSize: WalType.title,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText,
                height: 1.2)),
        const SizedBox(height: 2),
        Text(where,
            style: const TextStyle(
                fontSize: WalType.secondary, color: WalColors.inkSoft)),
        if (doc.isFixture) ...[
          const SizedBox(height: WalSpacing.sm),
          Builder(
            builder: (context) => FixtureChip(
              trust: doc.trust,
              compact: true,
              onTap: () => showTrustSheet(context, doc: doc),
            ),
          ),
        ],
        const SizedBox(height: WalSpacing.md),
        _evidenceBar(ways.length, opened),
        const SizedBox(height: WalSpacing.sm),
        // SAM nói — NGUYÊN VĂN lý do của động cơ, Home không viết lại.
        Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _samChip('assets/mascot/sam-explain.png', size: 30),
          const SizedBox(width: WalSpacing.sm),
          Expanded(
            child: Text(next?.reason ?? workspaceWhyLine(doc),
                key: const Key('home-workspace-why'),
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.ink,
                    height: 1.4)),
          ),
        ]),
        const SizedBox(height: WalSpacing.md),
        SizedBox(
          width: double.infinity,
          height: WalSpacing.minTouch,
          child: FilledButton(
            key: MissionCenterScreen.nextActionCtaKey,
            style: FilledButton.styleFrom(
                backgroundColor: WalColors.primary500,
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton))),
            onPressed: onOpenWorkspaceLesson == null
                ? null
                : () => onOpenWorkspaceLesson!(doc, at: next?.view),
            child: Text(ctaLabel,
                style: const TextStyle(
                    fontSize: WalType.body, fontWeight: FontWeight.w700)),
          ),
        ),
      ]),
    );
  }

  /// N vạch cho N cách học bài này CÓ; tô những cách đã mở. Chú thích nói
  /// đúng nó là gì: «đã mở», không phải «đã xong».
  Widget _evidenceBar(int total, int opened) => Row(
        key: MissionCenterScreen.progressKey,
        children: [
          for (var i = 0; i < total; i++) ...[
            if (i > 0) const SizedBox(width: 5),
            Expanded(
              child: Container(
                height: 7,
                decoration: BoxDecoration(
                  color: i < opened
                      ? WalColors.primary500
                      : WalColors.primary500.withValues(alpha: 0.18),
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
            ),
          ],
          const SizedBox(width: WalSpacing.sm),
          Text('đã mở $opened/$total cách học',
              style: const TextStyle(
                  fontSize: 13, color: WalColors.inkSoft)),
        ],
      );

  /// «CÓ THỂ LÀM TIẾP» — những cách học của CHÍNH bài này, không phải năm
  /// chip chung chung. Cách học SAM đang đề xuất không lặp lại ở đây (nút của
  /// nó đã ở trên); cách học bài không có thì không được mời.
  Widget _continueRow(LessonDocument doc) {
    final rest = [
      for (final v in _waysOf(doc))
        if (v != lessonNext?.view) v,
    ];
    if (rest.isEmpty) return const SizedBox.shrink();
    return Column(
      key: MissionCenterScreen.continueRowKey,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionLabel('CÓ THỂ LÀM TIẾP'),
        Row(children: [
          for (var i = 0; i < rest.length; i++) ...[
            if (i > 0) const SizedBox(width: WalSpacing.sm),
            Expanded(
              child: SizedBox(
                height: WalSpacing.minTouch,
                child: OutlinedButton(
                  key: MissionCenterScreen.continueChipKey(rest[i]),
                  style: OutlinedButton.styleFrom(
                      backgroundColor: Colors.white,
                      foregroundColor: WalColors.ink,
                      side: BorderSide(
                          color: WalColors.primary500.withValues(alpha: 0.3)),
                      padding: const EdgeInsets.symmetric(horizontal: 6),
                      shape: RoundedRectangleBorder(
                          borderRadius:
                              BorderRadius.circular(WalSpacing.radiusChip))),
                  onPressed: onOpenWorkspaceLesson == null
                      ? null
                      : () => onOpenWorkspaceLesson!(doc, at: rest[i]),
                  child: FittedBox(
                    fit: BoxFit.scaleDown,
                    child: Text('${rest[i].icon} ${rest[i].label}',
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w600)),
                  ),
                ),
              ),
            ),
          ],
        ]),
      ],
    );
  }

  /// «SAM ĐÃ THẤY GÌ» — HỖ TRỢ, không tranh hierarchy với việc tiếp theo
  /// (Founder order 49 §1). Nền trắng phẳng, chữ nhỏ, không nút, không mascot.
  ///
  /// ⚠ Nó nói ĐÚNG một điều: trẻ đã MỞ gì. Và nó nói thẳng rằng mở không phải
  /// hiểu — vì đây là chỗ duy nhất trên Home có hình dạng của «tiến độ», nên
  /// nó cũng là chỗ dễ bị đọc nhầm thành mastery nhất.
  Widget _samSeenCard(LessonDocument doc) {
    final total = _waysOf(doc).length;
    final opened = _openedCount(doc);
    final line = opened == 0
        ? 'Con chưa mở cách học nào của bài này trong phiên này. '
            'SAM chưa chấm phần nào — mở bài không phải là hiểu bài.'
        : 'Con đã mở $opened trong $total cách học. '
            'SAM chưa chấm phần nào — mở bài không phải là hiểu bài.';
    return Container(
      key: MissionCenterScreen.samSeenKey,
      width: double.infinity,
      padding: const EdgeInsets.symmetric(
          horizontal: WalSpacing.md, vertical: WalSpacing.sm + 2),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('SAM ĐÃ THẤY GÌ',
            style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w700,
                letterSpacing: .8,
                color: WalColors.inkSoft)),
        const SizedBox(height: 3),
        Text(line,
            style: const TextStyle(
                fontSize: 13, color: WalColors.ink, height: 1.4)),
      ]),
    );
  }

  /// ROUND 3 B1 — thẻ «Bài học SAM»: một bài, ba cách học, từ Home một chạm.
  /// Mọi chữ đọc từ tài liệu bài (tên, chương, trang); nhãn thử nghiệm bắt
  /// buộc vì `doc.isFixture`.
  /// ROUND 4: [primary] ⇒ thẻ chính của «Hôm nay» (nền lavender, dòng «vì sao
  /// bài này» bằng lời trẻ); không ⇒ thẻ trắng viền như round 3.
  /// [research] (Lane C) ⇒ lát cắt NGHIÊN CỨU của lớp khác: KHÔNG BAO GIỜ là
  /// thẻ chính, luôn nằm ngoài khu «Hôm nay», và nhãn nói rõ sách lớp mấy.
  Widget _workspaceCard(LessonDocument doc,
      {bool primary = false, bool research = false}) {
    assert(!(primary && research), 'lát cắt nghiên cứu không được làm thẻ chính');
    final where = doc.chapter == null
        ? doc.pageRangeLine
        : '${doc.chapter!.label} · ${doc.pageRangeLine}';
    return Container(
      key: research
          ? MissionCenterScreen.researchCardKey(doc.slotKey)
          : MissionCenterScreen.workspaceCardKey,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
          color: primary ? WalColors.surfaceLavender : Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
          border: primary
              ? null
              : Border.all(
                  color: WalColors.primary500.withValues(alpha: 0.35))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(
            research
                ? 'LÁT CẮT NGHIÊN CỨU · SÁCH LỚP ${doc.grade} · BẢN THỬ NGHIỆM'
                : doc.isFixture
                    ? 'BÀI HỌC SAM · BẢN THỬ NGHIỆM'
                    : 'BÀI HỌC SAM',
            style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.1,
                color: WalColors.inkSoft)),
        const SizedBox(height: 4),
        Text('✨ ${displayLessonLabel(doc.lessonNo, doc.title)}',
            style: const TextStyle(
                fontSize: WalType.title,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText)),
        const SizedBox(height: 2),
        Text(where,
            style: const TextStyle(
                fontSize: WalType.secondary, color: WalColors.inkSoft)),
        const SizedBox(height: WalSpacing.sm),
        Text(
            [for (final v in WorkspaceView.values) '${v.icon} ${v.label}']
                .join('  ·  '),
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.4)),
        if (primary) ...[
          const SizedBox(height: WalSpacing.sm),
          // «Vì sao bài này» — lời trẻ, không hứa gì ngoài điều có thật:
          // bài đã được xếp sẵn các cách học từ sách.
          Text(workspaceWhyLine(doc),
              key: const Key('home-workspace-why'),
              style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.inkSoft,
                  height: 1.4)),
        ],
        const SizedBox(height: WalSpacing.md),
        SizedBox(
          height: WalSpacing.minTouch,
          child: FilledButton(
            style: FilledButton.styleFrom(
                backgroundColor: WalColors.primary500,
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton))),
            onPressed: onOpenWorkspaceLesson == null
                ? null
                : () => onOpenWorkspaceLesson!(doc),
            child: const Text('Mở bài học',
                style: TextStyle(
                    fontSize: WalType.body, fontWeight: FontWeight.w700)),
          ),
        ),
      ]),
    );
  }

  /// REST không có nút (nghỉ là nghỉ); review → onReview; còn lại → Môn học.
  VoidCallback? _startForAgenda() => switch (data.agenda?.kind) {
        null => null,
        AgendaActionKind.rest => null,
        AgendaActionKind.review ||
        AgendaActionKind.retrieve =>
          onReview ?? onOpenSubjects,
        _ => onOpenSubjects ?? onStartHomework,
      };

  static String _agendaTitle(AgendaActionKind k) => switch (k) {
        AgendaActionKind.learn => 'Học bài mới cùng SAM',
        AgendaActionKind.practice => 'Luyện thêm cho chắc tay',
        AgendaActionKind.review => 'Tới lúc ôn lại rồi',
        AgendaActionKind.retrieve => 'Tự làm lại — không cần SAM',
        AgendaActionKind.explain => 'Giảng lại cho SAM nghe',
        AgendaActionKind.transfer => 'Thử bài dạng khác',
        AgendaActionKind.assess => 'Kiểm tra nhỏ xem sao',
        AgendaActionKind.rest => 'Hôm nay nghỉ ngơi nhé',
      };

  /// ROUND 4 — dòng SAM nói «hôm nay học gì, vì sao» bằng lời trẻ. Thay ô mic
  /// «SAM đang học cách trò chuyện» (round 3, WAL-123 trạng thái trung thực):
  /// không mic, không hứa chat — SAM Tutor ≠ chat; Home chỉ có thẻ để bấm.
  Widget _samLine() => Container(
        key: MissionCenterScreen.samLineKey,
        width: double.infinity,
        padding: const EdgeInsets.symmetric(
            horizontal: WalSpacing.md, vertical: WalSpacing.sm + 2),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        ),
        child: Text(samTodayLine(),
            style: const TextStyle(
                fontSize: WalType.secondary,
                color: WalColors.ink,
                height: 1.4)),
      );

  /// Câu SAM nói ở đầu Home — TẤT ĐỊNH từ dữ liệu, không bịa phút/%.
  String samTodayLine() {
    if (_workspaceIsPrimary) {
      return 'Hôm nay mình học '
          '${displayLessonLabel(workspaceLesson!.lessonNo, workspaceLesson!.title)}'
          ' nhé — bài này '
          'SAM đã xếp sẵn ba cách học từ sách. Bấm «Mở bài học» là vào.';
    }
    if (_effectiveRecommendation != null || data.agenda != null) {
      return data.agenda?.kind == AgendaActionKind.rest &&
              _effectiveRecommendation == null
          ? 'Hôm nay không có việc mới — nghỉ cũng là một phần của học. Con '
              'xem thẻ bên dưới nhé.'
          : 'Hôm nay SAM có một việc gợi ý cho con — xem thẻ bên dưới nhé.';
    }
    return 'Con chọn một thẻ bên dưới để bắt đầu nhé.';
  }

  /// 5 Learning Intent chips (home1) — chip dẫn FLOW THẬT hoặc nói thật.
  Widget _intentChips() => Builder(
        builder: (context) => Wrap(
          spacing: WalSpacing.sm,
          runSpacing: WalSpacing.sm,
          children: [
            _chip('📘 Học trước', onOpenSubjects),
            _chip('🔁 Ôn luyện', onReview),
            _chip('📷 Làm bài tập', onStartHomework),
            _chip('🧭 Học phương pháp',
                () => _honestSheet(context,
                    'Mỗi bài học có mục «Vì sao cách này?» kèm nguồn SGK — '
                    'con vào một bài trong Môn học để xem nhé. SAM đang xây '
                    'thư viện phương pháp riêng.')),
            _chip(
                '✅ Kiểm tra hiểu bài',
                onAssess ??
                    () => _honestSheet(context,
                        'Máy này chưa nạp đủ bài để kiểm tra — con vào Môn học '
                        'làm vài bài trước, rồi SAM mới kiểm tra được.')),
          ],
        ),
      );

  Widget _chip(String label, VoidCallback? onTap) => ActionChip(
        onPressed: onTap,
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
            side: BorderSide.none),
        label: Text(label,
            style: const TextStyle(
                fontSize: WalType.secondary, color: WalColors.ink)),
      );

  void _honestSheet(BuildContext context, String message) {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      backgroundColor: WalColors.surface,
      builder: (_) => Padding(
        padding: const EdgeInsets.fromLTRB(
            WalSpacing.lg, 0, WalSpacing.lg, WalSpacing.xl),
        child: Text(message,
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.5)),
      ),
    );
  }

  /// WAL-152 — thẻ khám phá trên Home: Today THẬT hoặc «Bạn có biết?» —
  /// hai nhãn KHÁC nhau, không bao giờ giả «ngày này năm xưa» (§14).
  Widget _discoveryCard() {
    final st = todayStory ?? didYouKnowStory!;
    final isToday = todayStory != null;
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      child: InkWell(
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        onTap: onOpenStory == null ? null : () => onOpenStory!(st),
        child: Padding(
          padding: const EdgeInsets.all(WalSpacing.md),
          child:
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(isToday ? '📅 NGÀY NÀY NĂM XƯA' : '💡 BẠN CÓ BIẾT?',
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1.05,
                    color: WalColors.primaryText)),
            const SizedBox(height: 6),
            Text(st.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                    fontSize: WalType.body,
                    fontWeight: FontWeight.w600,
                    color: WalColors.ink)),
            const SizedBox(height: 2),
            Text(storySourceLine(sourceDocumentId: st.sourceDocumentId, pagePdf: st.pagePdf),
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ]),
        ),
      ),
    );
  }

  Widget _upcomingRow() => Text(
        'Sắp tới ở trường: ${data.upcomingSubjects.join(' · ')}',
        style: const TextStyle(
            fontSize: WalType.secondary, color: WalColors.inkSoft),
      );

  Widget _sectionLabel(String t) => Padding(
        padding: const EdgeInsets.only(bottom: WalSpacing.sm),
        child: Text(t,
            style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                color: WalColors.inkSoft)),
      );

  /// WAL-164: câu chữ đến TỪ RESOLVER, màn không tự chế. Trước đây mọi mục
  /// ôn đều nói cùng một câu «Tới lúc gặp lại rồi» — kể cả khi lý do thật là
  /// «con làm được nhờ SAM giúp» hoặc «một câu lỡ tay». Nói chung chung như
  /// thế là bỏ mất đúng phần có ích cho trẻ.
  Widget _reviewTile(ReviewItem r) => _tile(
        chip: _samChip('assets/mascot/sam-review-due.png'),
        title: r.displayName,
        subtitle:
            r.reason.isEmpty ? 'Tới lúc gặp lại rồi' : r.reason, // KHÔNG hối thúc
        state: LearningStateToken.reviewDue,
      );

  Widget _unseenTile(String name) => _tile(
        chip: _samChip('assets/mascot/sam-probe.png'),
        title: 'Dạng "$name"',
        subtitle: 'Mình chưa thử dạng này', // nói thẳng, không nói mơ hồ
        state: LearningStateToken.insufficientEvidence,
      );

  Widget _tile({
    required Widget chip,
    required String title,
    required String subtitle,
    required LearningStateToken state,
  }) =>
      Container(
        margin: const EdgeInsets.only(bottom: WalSpacing.sm),
        padding: const EdgeInsets.all(WalSpacing.md),
        constraints: const BoxConstraints(minHeight: WalSpacing.minTouch),
        decoration: BoxDecoration(
          color: state.bg,
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
        ),
        child: Row(children: [
          chip,
          const SizedBox(width: WalSpacing.md),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(title,
                  style: TextStyle(
                      fontSize: WalType.body,
                      fontWeight: FontWeight.w600,
                      color: state.fg)),
              Text(subtitle,
                  style: const TextStyle(
                      fontSize: WalType.secondary, color: WalColors.inkSoft)),
            ]),
          ),
        ]),
      );

  Widget _bottomActions() => Builder(builder: (context) => Row(children: [
        Expanded(
          child: SizedBox(
            height: WalSpacing.minTouch + 8,
            child: FilledButton.icon(
              style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: onStartHomework ?? () => openCameraDemo(context),
              icon: const Icon(Icons.photo_camera_outlined),
              label: const Text('Chụp bài tập',
                  style: TextStyle(fontSize: WalType.body)),
            ),
          ),
        ),
        const SizedBox(width: WalSpacing.sm),
        SizedBox(
          height: WalSpacing.minTouch + 8,
          child: OutlinedButton(
            style: OutlinedButton.styleFrom(
                foregroundColor: WalColors.primaryText,
                side: const BorderSide(color: WalColors.primary500),
                shape: RoundedRectangleBorder(
                    borderRadius:
                        BorderRadius.circular(WalSpacing.radiusButton))),
            onPressed: onOpenSubjects,
            child: const Text('Môn học ▸',
                style: TextStyle(fontSize: WalType.body)),
          ),
        ),
        const SizedBox(width: WalSpacing.sm),
        SizedBox(
          height: WalSpacing.minTouch,
          child: TextButton(
            // WAL-109: có onParentArea ⇒ đi PIN gate thật; không có ⇒ demo cũ.
            onPressed: onParentArea ??
                () => Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => buildDemoParentTonight())),
            child: const Text('Bố mẹ ▸',
                style: TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ),
        ),
      ]));

  Widget _samChip(String asset, {double size = 36}) => ClipOval(
        child: Image.asset(asset,
            width: size,
            height: size,
            fit: BoxFit.cover,
            errorBuilder: (_, e, s) => Container(
                width: size, height: size, color: WalColors.surfaceLavender)),
      );
}
