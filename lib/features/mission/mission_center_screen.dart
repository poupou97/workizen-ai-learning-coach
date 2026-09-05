/// ⭐⭐ WAL-51 — Màn "HÔM NAY" (Mission Center): màn hình đầu tiên của
/// «Học cùng SAM», bám wireframe M1 (SLICE-1-WIREFRAMES.md).
///
/// Luật hiển thị (khắc từ doctrine, có widget test giữ):
/// - MỘT hành động kế tiếp, kèm `decision.reason` — lý do trẻ-đọc-được.
/// - CẤM %: không con số nào giả vờ chính xác.
/// - Ôn tới hạn: sắc thái nhẹ, KHÔNG đỏ, không đếm ngược hối thúc.
/// - Thử-thách-phủ: dạng CHƯA THỬ được nói thẳng tên.
/// - Mascot HELLO thu nhỏ — SAM chào rồi lùi lại (STEP_BACK là feature).
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/agenda/learning_agenda.dart';
import '../../core/intent/next_lesson.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/next_action.dart';
import '../../core/stories/stories_store.dart';
import '../../core/store/learner_profile.dart';
import '../camera/camera_demo_flow.dart';
import '../parent/parent_tonight_screen.dart';
import 'mission_data.dart';

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
  final void Function(LessonDocument)? onOpenWorkspaceLesson;

  static const workspaceCardKey = Key('home-workspace-card');

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.md),
          children: [
            _greeting(),
            const SizedBox(height: WalSpacing.md),
            _askSamBar(),
            const SizedBox(height: WalSpacing.sm),
            _intentChips(),
            const SizedBox(height: WalSpacing.md),
            _nextActionCard(),
            if (workspaceLesson != null) ...[
              const SizedBox(height: WalSpacing.sm),
              _workspaceCard(workspaceLesson!),
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

  Widget _nextActionCard() {
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
    final reason = rec != null
        ? rec.reason
        : (data.agenda?.reason ??
            data.nextActionReason ??
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
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
        color: WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        if (hasProposal) ...[
          const Text('VIỆC SAM ĐỀ XUẤT',
              style: TextStyle(
                  fontSize: WalType.secondary,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 1.1,
                  color: WalColors.inkSoft)),
          const SizedBox(height: 4),
        ],
        Text(title,
            style: const TextStyle(
                fontSize: WalType.title,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText)),
        const SizedBox(height: WalSpacing.sm),
        Text(reason,
            style: const TextStyle(
                fontSize: WalType.body, color: WalColors.ink, height: 1.45)),
        if (showButton) ...[
          const SizedBox(height: WalSpacing.md),
          SizedBox(
            height: WalSpacing.minTouch,
            child: FilledButton(
              style: FilledButton.styleFrom(
                  backgroundColor: WalColors.primary500,
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: onPressed,
              child: const Text('Bắt đầu',
                  style: TextStyle(
                      fontSize: WalType.body, fontWeight: FontWeight.w700)),
            ),
          ),
        ],
      ]),
    );
  }

  /// ROUND 3 B1 — thẻ «Bài học SAM»: một bài, ba cách học, từ Home một chạm.
  /// Mọi chữ đọc từ tài liệu bài (tên, chương, trang); nhãn thử nghiệm bắt
  /// buộc vì `doc.isFixture`.
  Widget _workspaceCard(LessonDocument doc) {
    final where = doc.chapter == null
        ? doc.pageRangeLine
        : '${doc.chapter!.label} · ${doc.pageRangeLine}';
    return Container(
      key: MissionCenterScreen.workspaceCardKey,
      padding: const EdgeInsets.all(WalSpacing.lg),
      decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
          border: Border.all(color: WalColors.primary500.withValues(alpha: 0.35))),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(
            doc.isFixture
                ? 'BÀI HỌC SAM · BẢN THỬ NGHIỆM'
                : 'BÀI HỌC SAM',
            style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.1,
                color: WalColors.inkSoft)),
        const SizedBox(height: 4),
        Text('✨ ${doc.lessonLabel}',
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

  /// Ô hỏi SAM (home1) — TRẠNG THÁI TRUNG THỰC: voice/chat chưa mở (WAL-123),
  /// không render một chat giả.
  Widget _askSamBar() => Container(
        padding: const EdgeInsets.symmetric(
            horizontal: WalSpacing.md, vertical: WalSpacing.sm),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
        ),
        child: Row(children: [
          const Icon(Icons.mic_none, color: WalColors.inkSoft, size: 20),
          const SizedBox(width: WalSpacing.sm),
          Expanded(
            child: Text('SAM đang học cách trò chuyện — con bấm thẻ bên dưới nhé',
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ),
        ]),
      );

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
            Text(st.sourceLine,
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
