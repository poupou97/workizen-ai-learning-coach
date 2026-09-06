/// ⭐⭐ WAL-51 — Màn "HÔM NAY" (Mission Center): màn hình đầu tiên của
/// «Học cùng SAM».
///
/// Luật hiển thị (khắc từ doctrine, có widget test giữ):
/// - MỘT hành động kế tiếp, kèm `decision.reason` — lý do trẻ-đọc-được.
/// - CẤM %: không con số nào giả vờ chính xác.
/// - Ôn tới hạn: sắc thái nhẹ, KHÔNG đỏ, không đếm ngược hối thúc.
/// - Thử-thách-phủ: dạng CHƯA THỬ được nói thẳng tên.
/// - Mascot HELLO thu nhỏ — SAM chào rồi lùi lại (STEP_BACK là feature).
///
/// ⭐⭐ ROUND 7 · V2 — MULTI-SUBJECT HOME (Founder order 50).
///
/// Founder cầm máy thật sau vòng 1: «HOME hiện tại đang bị tối ưu quá mức cho
/// một Golden Lesson duy nhất. Đây KHÔNG đúng với hành vi học thực tế… HOME
/// phải là AI LEARNING HOME CHO MỘT NGÀY HỌC NHIỀU MÔN, không phải landing
/// page của Bài 17.»
///
/// Màn này nay có HAI TẦNG, và chỉ hai:
///
/// ```
/// CHÀO NA
/// HÔM NAY   [ Smart Card ][ Smart Card ▸ hé ]  →   ← nhiều môn, trượt ngang
/// SAM GỢI Ý [ ĐÚNG MỘT việc tiếp theo         ]   ← một hành động nổi bật
/// CÁC MÔN CỦA CON · GẦN ĐÂY · CÁCH KHÁC ĐỂ HỌC    ← thứ cấp
/// ```
///
/// MULTI-SUBJECT CONTEXT + SINGLE NEXT ACTION. Không bao giờ năm CTA tranh
/// nhau: cả màn có **đúng một** [FilledButton], và có bài kiểm đếm nó.
///
/// Mô hình thẻ + luật chọn một việc nằm ở `home_cards.dart` (hàm THUẦN, kiểm
/// được không cần dựng widget). Màn này chỉ VẼ.
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
import '../lesson_workspace/widgets/fixture_chip.dart';
import '../lesson_workspace/widgets/trust_sheet.dart';
import 'home_cards.dart';
import 'mission_data.dart';
import '../subjects/subject_display.dart';

export 'home_cards.dart'
    show HomeCard, HomeCardState, HomeLessonThread, HomeShelfSubject;

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

class MissionCenterScreen extends StatelessWidget {
  const MissionCenterScreen({
    super.key,
    required this.data,
    this.learnerName,
    this.learnerGrade,
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
    this.lessonThreads = const [],
    this.shelfSubjects = const [],
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

  /// ⭐ ROUND 7 · V2 — LỚP của trẻ, để thẻ nói thật khi một bài thuộc SÁCH LỚP
  /// KHÁC (order 50 §6). `null` ⇒ không so được ⇒ không dán nhãn lớp nào.
  final int? learnerGrade;

  /// ⭐⭐ WAL-176 (Missing #1) — gợi ý Ở CẤP SÁCH từ TKB (Khoa học, Sử…), khi
  /// agenda Toán (WAL-102) chưa có gì khẩn (không phải review/retrieve).
  /// `null` = không có căn cứ thật ⇒ thẻ giữ nguyên hành vi cũ, không bịa.
  final HomeRecommendation? bookRecommendation;

  /// Bấm «Bắt đầu» khi thẻ đang hiện [bookRecommendation]: đưa thẳng trẻ vào
  /// ĐÚNG sách/bài/ý định — KHÔNG hỏi lại (SAM đã hỏi xong ở Home rồi).
  final void Function(HomeRecommendation)? onStartRecommendation;

  /// ⭐⭐ ROUND 7 · V2 — MẠCH HỌC CÓ THẬT: mọi bài SAM đã xếp sẵn trên máy,
  /// mỗi bài kèm dấu vết phiên và việc tiếp theo ĐÃ DỰNG SẴN.
  ///
  /// Hôm nay tập này có ĐÚNG HAI phần tử (KHTN 6 · Bài 17 và LS&ĐL 5 · Bài 8)
  /// — và đó là toàn bộ sự thật. Home không nhân bản chúng ra thành năm thẻ.
  ///
  /// ⚠ Home KHÔNG tự hỏi `WorkspaceTrace` và KHÔNG tự gọi động cơ đề xuất:
  /// tầng trên dựng sẵn và truyền xuống, để Home và Lesson Workspace không thể
  /// nói hai điều khác nhau về cùng một bài.
  final List<HomeLessonThread> lessonThreads;

  /// ⭐⭐ ROUND 7 · V2 — MÔN TRÊN GIÁ SÁCH của trẻ chưa có bài nào SAM xếp sẵn.
  /// Chúng vẫn được một thẻ, và thẻ NÓI THẲNG là chưa có bài — «không cần fake
  /// dữ liệu nếu chưa có» (order 50 §2).
  final List<HomeShelfSubject> shelfSubjects;

  /// [at] là CÁCH HỌC mà nút vừa hứa mở. Nút mang tên một cách học thì phải mở
  /// ĐÚNG cách học ấy (lỗi máy thật vòng 1: «📖 Đọc ▸» mở ra màn hỏi lại).
  final void Function(LessonDocument doc, {WorkspaceView? at})?
      onOpenWorkspaceLesson;

  // ── KHOÁ WIDGET ─────────────────────────────────────────────────────────
  /// TẦNG 1 — hàng Smart Card trượt ngang.
  static const todayRowKey = Key('home-today-row');
  static Key smartCardKey(String id) => Key('home-smart-card-$id');
  static const rowOverflowKey = Key('home-row-overflow');

  /// TẦNG 2 — ĐÚNG MỘT việc tiếp theo.
  static const samSuggestionKey = Key('home-sam-suggestion');
  static const nextActionCtaKey = Key('home-next-action-cta');

  static const progressKey = Key('home-evidence-progress');
  static const samSeenKey = Key('home-sam-seen');
  static const continueRowKey = Key('home-continue-row');
  static Key continueChipKey(WorkspaceView v) => Key('home-continue-${v.name}');
  static const samLineKey = Key('home-sam-line');
  static const secondaryCardKey = Key('home-secondary-card');

  /// Hàng thẻ đã dựng — MỘT lần cho cả màn (thứ tự và trần thẻ là luật thuần
  /// ở `home_cards.dart`, không phải quyết định rải trong widget).
  HomeCardRow get cardRow => buildHomeCards(
        threads: lessonThreads,
        shelf: shelfSubjects,
        learnerGrade: learnerGrade,
      );

  /// Toán (WAL-102) đang có việc do BẰNG CHỨNG thúc — bậc cao nhất trong thứ
  /// tự đã chốt (Convergence §10: bằng chứng → TKB → làm dở → không có gì).
  bool get _agendaIsEvidenceUrgent =>
      data.agenda?.kind == AgendaActionKind.review ||
      data.agenda?.kind == AgendaActionKind.retrieve;

  /// ⭐⭐ WAL-176 — gợi ý sách qua TKB chỉ được lên tiếng khi Toán KHÔNG đang
  /// khẩn vì bằng chứng thật.
  HomeRecommendation? get _effectiveRecommendation =>
      _agendaIsEvidenceUrgent ? null : bookRecommendation;

  /// ⭐⭐ TẦNG 2 — thẻ được đưa lên «SAM GỢI Ý», hoặc `null` ⇒ rơi về đề xuất
  /// cũ của «Hôm nay».
  ///
  /// BẰNG CHỨNG THẬT VẪN THẮNG BÀI FIXTURE: khi Toán đang khẩn vì bằng chứng
  /// đã chấm (review/retrieve), việc ấy là việc hôm nay — một bài thử nghiệm
  /// không được chen lên trên nó. Đây là thứ tự đã chốt từ Convergence §10,
  /// order 50 không đụng tới.
  HomeCard? _promoted(HomeCardRow row) {
    if (_agendaIsEvidenceUrgent) return null;
    final i = promotedCardIndex(row.cards);
    return i == null ? null : row.cards[i];
  }

  @override
  Widget build(BuildContext context) {
    final row = cardRow;
    final promoted = _promoted(row);
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.symmetric(vertical: WalSpacing.md),
          children: [
            _pad(_greeting()),
            if (row.cards.isNotEmpty) ...[
              // ── TẦNG 1: NHIỀU MÔN ───────────────────────────────────────
              const SizedBox(height: WalSpacing.sm),
              _pad(_sectionLabel('HÔM NAY')),
              _SmartCardRow(
                key: MissionCenterScreen.todayRowKey,
                cards: row.cards,
                promotedId: promoted?.id,
                onOpenLesson: onOpenWorkspaceLesson,
                onOpenShelf: onOpenSubjects,
              ),
              if (row.hiddenSubjects > 0)
                _pad(Padding(
                  padding: const EdgeInsets.only(top: WalSpacing.sm),
                  child: Text(
                    'Con còn ${row.hiddenSubjects} môn nữa trên giá sách — '
                    'mở «Môn học» để xem hết.',
                    key: MissionCenterScreen.rowOverflowKey,
                    style: const TextStyle(
                        fontSize: 13, color: WalColors.inkSoft, height: 1.4),
                  ),
                )),
              // ── TẦNG 2: ĐÚNG MỘT VIỆC ──────────────────────────────────
              //
              // Khoảng cách md (không phải lg): hai tầng PHẢI cùng nằm trong
              // màn đầu của Nokia 6.1 (360×640 dp). `home_multi_subject_test`
              // đo đúng điều đó ở đúng kích thước ấy.
              const SizedBox(height: WalSpacing.md),
              _pad(_sectionLabel('SAM GỢI Ý')),
              _pad(promoted == null
                  ? _nextActionCard()
                  : _oneNextActionCard(promoted)),
              if (promoted?.thread != null) ...[
                const SizedBox(height: WalSpacing.sm),
                _pad(_continueRow(promoted!.thread!)),
                const SizedBox(height: WalSpacing.sm),
                _pad(_samSeenCard(promoted.thread!)),
              ],
              // ── THỨ CẤP ────────────────────────────────────────────────
              const SizedBox(height: WalSpacing.lg),
              _pad(_sectionLabel('CÁC MÔN CỦA CON')),
              _pad(_shelfCard()),
            ] else ...[
              const SizedBox(height: WalSpacing.sm),
              _pad(_samLine()),
              const SizedBox(height: WalSpacing.sm),
              _pad(_intentChips()),
              const SizedBox(height: WalSpacing.md),
              _pad(_sectionLabel('HÔM NAY')),
              _pad(_nextActionCard()),
            ],
            if (data.upcomingSubjects.isNotEmpty) ...[
              const SizedBox(height: WalSpacing.sm),
              _pad(_upcomingRow()),
            ],
            if (todayStory != null || didYouKnowStory != null) ...[
              const SizedBox(height: WalSpacing.md),
              _pad(_discoveryCard()),
            ],
            const SizedBox(height: WalSpacing.lg),
            if (data.reviews.isNotEmpty) ...[
              _pad(_sectionLabel('Ôn lại')),
              for (final r in data.reviews) _pad(_reviewTile(r)),
              const SizedBox(height: WalSpacing.md),
            ],
            if (data.unobservedCaseNames.isNotEmpty) ...[
              _pad(_sectionLabel('Thử dạng mới')),
              for (final name in data.unobservedCaseNames) _pad(_unseenTile(name)),
            ],
            if (row.cards.isNotEmpty) ...[
              const SizedBox(height: WalSpacing.lg),
              _pad(_sectionLabel('CÁCH KHÁC ĐỂ HỌC')),
              _pad(_intentChips()),
            ],
            const SizedBox(height: WalSpacing.xl),
            _pad(_bottomActions()),
          ],
        ),
      ),
    );
  }

  /// Lề ngang của màn. Hàng Smart Card KHÔNG dùng nó — nó phải chạm được mép
  /// để thẻ kế bên hé ra (order 50 §4).
  Widget _pad(Widget child) => Padding(
        padding: const EdgeInsets.symmetric(horizontal: WalSpacing.md),
        child: child,
      );

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

  // ── TẦNG 2 — ĐÚNG MỘT VIỆC TIẾP THEO ───────────────────────────────────

  /// ⭐⭐ «SAM GỢI Ý» — thẻ hành động DUY NHẤT của Home.
  ///
  /// ROUND 7 · V2, order 50 §7 «GIẢM KÍCH THƯỚC HERO»: thẻ này KHÔNG còn là
  /// mega-card của vòng 1. Nó giữ đúng bốn thứ — tên bài · một dòng nguồn ·
  /// lời SAM · nút. Thanh bằng chứng («đã mở N/M») đã chuyển xuống thẻ «SAM ĐÃ
  /// THẤY GÌ», đúng chỗ của nó: nó là bằng chứng, không phải lời mời.
  ///
  /// Mọi chữ về việc tiếp theo đến NGUYÊN VĂN từ [LessonNextAction] —
  /// `founderNextAction` là động cơ duy nhất, Home chỉ trình bày.
  Widget _oneNextActionCard(HomeCard card) {
    final t = card.thread!;
    final doc = t.doc;
    final next = t.next;
    final where = doc.chapter == null
        ? doc.pageRangeLine
        : '${doc.chapter!.label} · ${doc.pageRangeLine}';
    return Container(
      key: MissionCenterScreen.samSuggestionKey,
      padding: const EdgeInsets.all(WalSpacing.md),
      decoration: BoxDecoration(
        color: WalColors.surfaceLavender,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('${card.subjectLine} · ${card.lessonLine}',
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
                fontSize: WalType.body + 1,
                fontWeight: FontWeight.w700,
                color: WalColors.primaryText,
                height: 1.25)),
        const SizedBox(height: 2),
        Text(
            card.otherGradeNote == null
                ? where
                : '$where · ${card.otherGradeNote}',
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
                fontSize: 13, color: WalColors.inkSoft)),
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
            child: Text('${card.nextLabel} ▸',
                style: const TextStyle(
                    fontSize: WalType.body, fontWeight: FontWeight.w700)),
          ),
        ),
      ]),
    );
  }

  /// Thẻ đề xuất CŨ (agenda / gợi ý sách theo TKB / đường Scale) — dùng khi
  /// KHÔNG có bài nào đủ tư cách lên «SAM GỢI Ý». Vẫn là MỘT nút.
  Widget _nextActionCard() {
    final rec = _effectiveRecommendation;
    final hasProposal = rec != null || data.agenda != null;
    final title = rec != null
        ? '${rec.subject} · Bài ${rec.lessonNo}'
        : (data.agenda == null
            ? data.nextActionTitle
            : _agendaTitle(data.agenda!.kind));
    final reason = rec != null
        ? rec.reason
        : (data.agenda?.reason ?? data.nextActionReason ?? data.decision.reason);
    final showButton =
        rec != null || data.agenda?.kind != AgendaActionKind.rest;
    // ⭐ WAL-210 G2: không agenda + có bài Scale ⇒ «Bắt đầu» mở MÔN HỌC (giá
    // sách), KHÔNG mở camera.
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
              key: MissionCenterScreen.nextActionCtaKey,
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

  /// «CÁC MÔN CỦA CON» — lối vào giá sách. THỨ CẤP: viền, không tô đặc, để cả
  /// màn chỉ có ĐÚNG MỘT nút hành động chính (order 50 §5).
  Widget _shelfCard() => Container(
        key: MissionCenterScreen.secondaryCardKey,
        width: double.infinity,
        padding: const EdgeInsets.all(WalSpacing.md),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(
              data.scaleLessonCount > 0
                  ? 'Ở Môn học con mở được ${data.scaleLessonCount} bài từ '
                      'sách giáo khoa — đọc, làm thí nghiệm, viết.'
                  : 'Giá sách của con có mục lục các môn — SAM chưa xếp sẵn '
                      'bài nào ngoài những bài ở trên.',
              style: const TextStyle(
                  fontSize: WalType.secondary,
                  color: WalColors.ink,
                  height: 1.4)),
          const SizedBox(height: WalSpacing.sm),
          SizedBox(
            height: WalSpacing.minTouch,
            child: OutlinedButton(
              style: OutlinedButton.styleFrom(
                  foregroundColor: WalColors.primaryText,
                  side: const BorderSide(color: WalColors.primary500),
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: onOpenSubjects,
              child: const Text('Vào Môn học ▸',
                  style: TextStyle(
                      fontSize: WalType.body, fontWeight: FontWeight.w700)),
            ),
          ),
        ]),
      );

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

  /// «CÓ THỂ LÀM TIẾP» — những cách học của CHÍNH bài đang được đề xuất. Cách
  /// học SAM đang đề xuất không lặp lại ở đây (nút của nó đã ở trên); cách học
  /// bài không có thì không được mời.
  Widget _continueRow(HomeLessonThread t) {
    final rest = [
      for (final v in t.availableViews)
        if (v != t.next?.view) v,
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
                      : () => onOpenWorkspaceLesson!(t.doc, at: rest[i]),
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
  Widget _samSeenCard(HomeLessonThread t) {
    final total = t.availableViews.length;
    final opened = t.openedHere.length;
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
        const SizedBox(height: 6),
        if (total > 0) ...[
          _evidenceBar(total, opened),
          const SizedBox(height: 6),
        ],
        Text(line,
            style: const TextStyle(
                fontSize: 13, color: WalColors.ink, height: 1.4)),
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

  /// ROUND 4 — dòng SAM nói «hôm nay học gì, vì sao» bằng lời trẻ. Chỉ còn
  /// trên đường KHÔNG có thẻ nào (máy chưa nạp bài, chưa nạp mục lục).
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

  /// WAL-164: câu chữ đến TỪ RESOLVER, màn không tự chế.
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

  /// ⭐ ROUND 7 · V2 — hàng cuối KHÔNG còn nút tô đặc. «Chụp bài tập» là một
  /// lối vào, không phải việc SAM đề xuất hôm nay; để nó tô đặc là dựng CTA
  /// thứ hai tranh với «SAM GỢI Ý» (order 50 §5). Bài kiểm đếm: cả màn đúng
  /// MỘT `FilledButton`.
  Widget _bottomActions() => Builder(builder: (context) => Row(children: [
        Expanded(
          child: SizedBox(
            height: WalSpacing.minTouch,
            child: OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                  foregroundColor: WalColors.primaryText,
                  side: const BorderSide(color: WalColors.primary500),
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.circular(WalSpacing.radiusButton))),
              onPressed: onStartHomework ?? () => openCameraDemo(context),
              icon: const Icon(Icons.photo_camera_outlined, size: 20),
              label: const Text('Chụp bài tập',
                  style: TextStyle(fontSize: WalType.secondary)),
            ),
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

/// ⭐⭐ TẦNG 1 — HÀNG SMART CARD TRƯỢT NGANG (order 50 §2 · §4).
///
/// «Card không chiếm toàn bộ chiều ngang. Cho thấy một phần card kế tiếp để
/// trẻ hiểu rằng có thể swipe. Ưu tiên: 1 card chính khoảng 75–85% viewport +
/// peek card kế bên. Không tạo carousel banner marketing. Đây là learning
/// context switcher.»
///
/// Nên: `PageView` với [viewportFraction] = .82, KHÔNG tự chạy, KHÔNG lặp
/// vòng, KHÔNG hiệu ứng — thẻ đứng yên tới khi ngón tay trẻ đẩy nó.
class _SmartCardRow extends StatefulWidget {
  const _SmartCardRow({
    super.key,
    required this.cards,
    this.promotedId,
    this.onOpenLesson,
    this.onOpenShelf,
  });

  final List<HomeCard> cards;

  /// Thẻ đang được «SAM GỢI Ý» nêu — đánh dấu nhẹ để trẻ nối được hai tầng.
  final String? promotedId;

  final void Function(LessonDocument doc, {WorkspaceView? at})? onOpenLesson;
  final VoidCallback? onOpenShelf;

  @override
  State<_SmartCardRow> createState() => _SmartCardRowState();
}

class _SmartCardRowState extends State<_SmartCardRow> {
  static const double viewportFraction = .82;
  /// Chiều cao thẻ — cố định để hàng không nhảy khi thẻ này dài hơn thẻ kia.
  /// Con số đến từ phép đo: bốn dòng bắt buộc + dòng «sách lớp N» của thẻ
  /// lớp khác, ở 360 dp. Cao hơn nữa thì tầng 2 rơi xuống dưới nếp gấp.
  static const double cardHeight = 172;

  late final PageController _controller =
      PageController(viewportFraction: viewportFraction);
  int _page = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      SizedBox(
        height: cardHeight,
        child: PageView.builder(
          controller: _controller,
          padEnds: false,
          onPageChanged: (i) => setState(() => _page = i),
          itemCount: widget.cards.length,
          itemBuilder: (_, i) => Padding(
            padding: EdgeInsets.only(
                left: WalSpacing.md,
                right: i == widget.cards.length - 1 ? WalSpacing.md : 0),
            child: _SmartCard(
              card: widget.cards[i],
              promoted: widget.cards[i].id == widget.promotedId,
              onTap: () {
                final t = widget.cards[i].thread;
                if (t == null) {
                  widget.onOpenShelf?.call();
                } else {
                  widget.onOpenLesson?.call(t.doc, at: t.next?.view);
                }
              },
            ),
          ),
        ),
      ),
      if (widget.cards.length > 1) ...[
        const SizedBox(height: WalSpacing.sm),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: [
          for (var i = 0; i < widget.cards.length; i++) ...[
            if (i > 0) const SizedBox(width: 6),
            Container(
              width: i == _page ? 18 : 6,
              height: 6,
              decoration: BoxDecoration(
                color: i == _page
                    ? WalColors.primary500
                    : WalColors.primary500.withValues(alpha: 0.25),
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ],
        ]),
      ],
    ]);
  }
}

/// Một Smart Card. Order 50 §3: nó trả lời ĐÚNG bốn câu —
/// **MÔN · BÀI · TRẠNG THÁI HIỆN TẠI · VIỆC TIẾP THEO** — và không gì khác.
/// Chương, số trang, chip nguồn, lời SAM, thanh bằng chứng đều là thứ cấp và
/// nằm ở tầng dưới.
class _SmartCard extends StatelessWidget {
  const _SmartCard({
    required this.card,
    required this.promoted,
    required this.onTap,
  });

  final HomeCard card;
  final bool promoted;
  final VoidCallback onTap;

  /// Màu trạng thái — TỪ TOKEN HỌC, không phải trang trí.
  ///
  /// ⛔ `LearningStateToken.mastered` (xanh «đầy + ấm») KHÔNG BAO GIỜ được
  /// dùng ở đây: nó là màu của một tuyên bố đã thạo, và không thẻ nào trên
  /// Home có bằng chứng cho tuyên bố ấy.
  LearningStateToken get _token => switch (card.state) {
        HomeCardState.chuaBatDau => LearningStateToken.noEvidence,
        HomeCardState.dangHoc ||
        HomeCardState.daMoDoc ||
        HomeCardState.daXemTrucQuan ||
        HomeCardState.coTheLuyen =>
          LearningStateToken.strongOnObserved,
        HomeCardState.tiepTuc => LearningStateToken.reviewDue,
      };

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      child: InkWell(
        key: MissionCenterScreen.smartCardKey(card.id),
        onTap: onTap,
        borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
        child: Container(
          padding: const EdgeInsets.all(WalSpacing.md),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
            border: Border.all(
                color: promoted
                    ? WalColors.primary500
                    : WalColors.primary500.withValues(alpha: 0.16),
                width: promoted ? 2 : 1),
          ),
          child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // MÔN
                Row(children: [
                  Expanded(
                    child: Text(card.subjectLine.toUpperCase(),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.0,
                            color: WalColors.primaryText)),
                  ),
                  // Dấu nối hai tầng: thẻ nào đang được «SAM GỢI Ý» nêu.
                  // Chữ KHÁC nhãn của tầng 2 có chủ ý — hai chỗ, hai vai.
                  if (promoted)
                    const Text('ĐANG GỢI Ý',
                        style: TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                            letterSpacing: .8,
                            color: WalColors.primary500)),
                ]),
                const SizedBox(height: 3),
                // BÀI — hoặc sự thật «chưa có bài»
                Text(card.lessonLine ?? 'SAM chưa xếp sẵn bài nào',
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                        fontSize: WalType.body - .5,
                        fontWeight: FontWeight.w700,
                        height: 1.2,
                        color: card.lessonLine == null
                            ? WalColors.inkSoft
                            : WalColors.ink)),
                if (card.otherGradeNote != null) ...[
                  const SizedBox(height: 2),
                  Text(card.otherGradeNote!,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 12, color: WalColors.warnText)),
                ],
                const SizedBox(height: WalSpacing.sm),
                // TRẠNG THÁI
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: WalSpacing.sm, vertical: 3),
                  decoration: BoxDecoration(
                    color: _token.bg,
                    borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
                  ),
                  child: Text(card.state.label,
                      style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w700,
                          letterSpacing: .6,
                          color: _token.fg)),
                ),
                const SizedBox(height: 5),
                Expanded(
                  child: Text(card.detailLine,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                          fontSize: 12.5,
                          color: WalColors.inkSoft,
                          height: 1.3)),
                ),
                // VIỆC TIẾP THEO
                Text('Tiếp theo: ${card.nextLabel} →',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        fontSize: 13.5,
                        fontWeight: FontWeight.w700,
                        color: WalColors.primaryText)),
              ]),
        ),
      ),
    );
  }
}
