/// ⭐⭐ ROUND 7 · V2 «MULTI-SUBJECT HOME» (Founder order 50) — MÔ HÌNH THẺ CỦA
/// HÀNG «HÔM NAY».
///
/// Order 50 §1: «HOME không phải LANDING PAGE CỦA BÀI 17. HOME phải là AI
/// LEARNING HOME CHO MỘT NGÀY HỌC NHIỀU MÔN.» Tệp này là phần MÁY ĐỌC ĐƯỢC
/// của điều đó: một hàm THUẦN dựng danh sách thẻ và một hàm THUẦN chọn ĐÚNG
/// MỘT thẻ để tầng «SAM GỢI Ý» trình bày.
///
/// ⛔ RÀNG BUỘC TRUNG THỰC (order 50 §9, và là lý do tệp này tồn tại)
///
/// «Không cần fake dữ liệu nếu chưa có. Nếu chỉ một số môn có real data, hiển
/// thị đúng trạng thái của chúng.»
///
/// Trên máy hôm nay có ĐÚNG HAI bài SAM đã xếp sẵn (`WorkspaceCatalog`):
/// KHTN 6 · Bài 17 (ba cách học) và LS&ĐL 5 · Bài 8 (chỉ có Đọc). Mọi thứ còn
/// lại trong `assets/pack/lesson-index-g*.json` là MỤC LỤC GIÁ SÁCH — một mục
/// trẻ giở xem được, KHÔNG phải một bài mở được cùng SAM. Nên:
///
/// - thẻ có bài thật ⇒ nói trạng thái thật của bài ấy;
/// - môn chưa có bài ⇒ VẪN CÓ THẺ, và thẻ nói thẳng «SAM chưa xếp sẵn bài nào
///   ở môn này» + con số mục lục có thật. Không bịa tiến độ để hàng thẻ trông
///   đầy hơn.
///
/// Một hàng hai thẻ thật + vài thẻ rỗng-trung-thực là kết quả ĐÚNG. Một hàng
/// năm thẻ bịa là hỏng đơn hàng.
///
/// ⛔ TỪ VỰNG TRẠNG THÁI bị khoá bằng [HomeCardState] — không có chỗ nào trong
/// tệp này sinh ra `ĐÃ HIỂU` · `70%` · `GIỎI` · `MASTERED` · sao · điểm.
///
/// ⛔ KHÔNG CÓ ĐỘNG CƠ ĐỀ XUẤT THỨ HAI. Tệp này KHÔNG gọi `founderNextAction`,
/// `nextActionFor`, `nextBestLessonAction`, và không đọc `WorkspaceTrace`. Nó
/// NHẬN [LessonNextAction] đã dựng sẵn (do chính hàm mà Lesson Workspace gọi
/// sinh ra) và chỉ TRÌNH BÀY / XẾP HẠNG chúng — cùng kỷ luật mà lớp trợ giúp
/// trong workspace phải theo. `home_multi_subject_test.dart` soi mã tệp này
/// để giữ điều đó.
library;

import '../../core/agenda/lesson_next_action.dart'
    show LessonNextAction, LessonSummary;
import '../../core/display/lesson_title.dart';
import '../../core/lesson_model/lesson_document.dart';
import '../../core/lesson_model/next_action.dart' show WorkspaceView;

/// TỪ VỰNG TRẠNG THÁI Founder cho phép (order 50 §9), nguyên văn.
///
/// Danh sách này là HỢP ĐỒNG, không phải tiện ích: mọi chữ trạng thái trên
/// một Smart Card phải đến từ đây. Thêm một trạng thái = một quyết định sản
/// phẩm, không phải một chuỗi mới trong widget.
enum HomeCardState {
  /// Trẻ đã mở NHIỀU HƠN một cách học của bài, chưa mở hết.
  dangHoc('ĐANG HỌC'),

  /// Chưa mở cách học nào — hoặc môn chưa có bài nào SAM xếp sẵn.
  chuaBatDau('CHƯA BẮT ĐẦU'),

  /// Đã mở ĐÚNG một cách học, và đó là Đọc.
  daMoDoc('ĐÃ MỞ ĐỌC'),

  /// Đã mở ĐÚNG một cách học, và đó là Trực quan.
  daXemTrucQuan('ĐÃ XEM TRỰC QUAN'),

  /// ⚠ HIỆN KHÔNG ĐƯỢC SINH RA Ở ĐÂU. Founder cho phép nhãn này, nhưng bản
  /// dựng hôm nay không đo được «sẵn sàng luyện tập»: vòng luyện tập thuộc
  /// nhánh SAM teaching (`round7/v2-sam-teaching`) và chưa có tín hiệu nào
  /// trên Home. Gán nó bây giờ sẽ là suy diễn — đúng thứ §9 cấm.
  ///
  /// Giữ trong enum có chủ ý: đây là chỗ ghi rằng nhãn TỒN TẠI và VÌ SAO chưa
  /// dùng. `home_multi_subject_test.dart` khoá bằng một bài kiểm nói rõ
  /// «không thẻ nào được mang nhãn này chừng nào chưa có bằng chứng luyện
  /// tập» — ai bắt đầu gán nó sẽ phải sửa bài kiểm ấy và nói ra lý do.
  coTheLuyen('CÓ THỂ LUYỆN'),

  /// Trẻ đã mở HẾT những cách học bài này có. «Đã mở» không phải «đã hiểu» —
  /// nên nhãn là TIẾP TỤC, không phải «xong».
  tiepTuc('TIẾP TỤC');

  const HomeCardState(this.label);

  /// Chữ trẻ đọc — nguyên văn từ vựng Founder.
  final String label;
}

/// Một MẠCH HỌC có thật: một bài SAM đã xếp sẵn, dấu vết phiên của nó, và
/// việc tiếp theo do ĐỘNG CƠ DUY NHẤT sinh ra.
///
/// [next] `null` chỉ xảy ra ở môi trường test cũ chưa nối động cơ; thẻ khi ấy
/// vẫn nói đúng trạng thái, chỉ không có câu «việc tiếp theo» của SAM.
class HomeLessonThread {
  const HomeLessonThread({
    required this.doc,
    this.openedViews = const {},
    this.next,
  });

  final LessonDocument doc;

  /// Những cách học trẻ đã MỞ trong phiên này. ⚠ MỞ ≠ HIỂU: tập này chỉ được
  /// dùng để nói «đã mở gì», không bao giờ để nói «đã hiểu gì».
  final Set<WorkspaceView> openedViews;

  /// Việc tiếp theo của CHÍNH bài này, đã dựng sẵn bởi `founderNextAction`.
  final LessonNextAction? next;

  /// Những cách học bài NÀY thật sự có — đọc từ MỘT nguồn dùng chung với luật
  /// đề xuất ([LessonSummary.availableViews]), nên hàng thẻ và động cơ không
  /// thể liệt kê hai tập khác nhau.
  List<WorkspaceView> get availableViews =>
      LessonSummary.fromDocument(doc).availableViews;

  /// Giao của «đã mở» với «bài này có» — dấu vết của bài khác không bao giờ
  /// đếm vào đây.
  Set<WorkspaceView> get openedHere =>
      openedViews.where(availableViews.contains).toSet();
}

/// Một MÔN TRÊN GIÁ SÁCH của trẻ, chưa có bài nào SAM xếp sẵn.
///
/// [listedLessons] và [openableLessons] là con số THẬT đọc từ mục lục pack.
/// Chúng khác nhau và sự khác nhau ấy là điều phải nói với trẻ: mục lục liệt
/// kê được nhiều, mở ra làm được thì ít.
class HomeShelfSubject {
  const HomeShelfSubject({
    required this.subject,
    required this.listedLessons,
    required this.openableLessons,
  });

  /// Tên môn NHƯ MỤC LỤC PACK ghi («Toán», «Ngữ văn», «KHTN») — không dịch
  /// lại, không viết tắt thêm.
  final String subject;

  /// Số bài mục lục liệt kê được cho môn này.
  final int listedLessons;

  /// Số bài trong đó có ít nhất một việc trẻ làm được ở Môn học.
  final int openableLessons;
}

/// Trần số thẻ của hàng «HÔM NAY».
///
/// Đây là quyết định TRÌNH BÀY, không phải giấu dữ liệu: order 50 §4 nói hàng
/// này là «learning context switcher», không phải mục lục — sáu thẻ vẫn lướt
/// hết bằng ngón cái. Giá sách đầy đủ nằm sau một chạm ở «CÁC MÔN CỦA CON», và
/// màn hình PHẢI nói ra khi có môn không lọt vào hàng (xem
/// `MissionCenterScreen`). Đổi số này = đổi một hằng, có test đếm.
const int kHomeCardLimit = 6;

/// Một Smart Card của hàng «HÔM NAY».
///
/// Order 50 §3: thẻ chỉ trả lời bốn câu — MÔN · BÀI · TRẠNG THÁI · VIỆC TIẾP
/// THEO. Mọi thứ khác (chương, số trang, chip nguồn, lời SAM, tiến độ) là
/// SECONDARY và không được lên thẻ.
class HomeCard {
  const HomeCard({
    required this.id,
    required this.subjectLine,
    required this.state,
    required this.detailLine,
    required this.nextLabel,
    this.lessonLine,
    this.otherGradeNote,
    this.thread,
  });

  /// Khoá ổn định cho widget key — `slotKey` của bài, hoặc `shelf:<môn>`.
  final String id;

  /// MÔN — «KHTN 6», «LS&ĐL 5», «Toán».
  final String subjectLine;

  /// BÀI — «Bài 17 · TÁCH CHẤT KHỎI HỖN HỢP»; `null` khi môn chưa có bài nào.
  final String? lessonLine;

  /// TRẠNG THÁI — từ vựng Founder, không có gì khác.
  final HomeCardState state;

  /// Một dòng nói thêm điều CÓ THẬT: đã mở cách học nào, hoặc vì sao môn này
  /// còn trống và giá sách đang có gì.
  final String detailLine;

  /// VIỆC TIẾP THEO — nhãn nút. Với thẻ có bài, nhãn đến NGUYÊN VĂN từ động
  /// cơ ([LessonNextAction.label]); với thẻ rỗng, đó là việc thật duy nhất
  /// làm được: giở giá sách.
  final String nextLabel;

  /// «Sách lớp 5 · không phải sách lớp con» — sự thật BẮT BUỘC nói khi bài
  /// thuộc lớp khác (order 50 §6: vẫn phải nói, nhưng nói như MỘT MÔN / BÀI
  /// HỌC KHÁC, không phải như phế phẩm nghiên cứu).
  final String? otherGradeNote;

  /// `null` ⇒ thẻ RỖNG-TRUNG-THỰC: môn có trên giá sách, chưa có bài SAM.
  final HomeLessonThread? thread;

  bool get isRealLesson => thread != null;

  LessonDocument? get doc => thread?.doc;

  LessonNextAction? get next => thread?.next;
}

/// ⭐ Trạng thái của một mạch học — LUẬT TẤT ĐỊNH, đọc được thành lời:
///
/// - chưa mở cách nào              ⇒ CHƯA BẮT ĐẦU
/// - đã mở HẾT cách bài này có     ⇒ TIẾP TỤC   («đã mở» ≠ «xong»)
/// - đã mở đúng một cách, là Đọc   ⇒ ĐÃ MỞ ĐỌC
/// - đã mở đúng một cách, Trực quan⇒ ĐÃ XEM TRỰC QUAN
/// - còn lại (nhiều hơn một, chưa hết) ⇒ ĐANG HỌC
///
/// Luật đọc ĐÚNG MỘT tín hiệu — dấu vết «đã mở tab» — và không suy ra gì
/// ngoài nó. Ví dụ của chính Founder ở §3 (đã mở Đọc + Trực quan, còn Học với
/// SAM ⇒ «ĐANG HỌC») rơi đúng vào nhánh cuối.
HomeCardState lessonCardState(HomeLessonThread thread) {
  final ways = thread.availableViews;
  final opened = thread.openedHere;
  if (opened.isEmpty) return HomeCardState.chuaBatDau;
  if (ways.isNotEmpty && opened.length == ways.length) {
    return HomeCardState.tiepTuc;
  }
  if (opened.length == 1) {
    if (opened.single == WorkspaceView.read) return HomeCardState.daMoDoc;
    if (opened.single == WorkspaceView.visual) {
      return HomeCardState.daXemTrucQuan;
    }
  }
  return HomeCardState.dangHoc;
}

/// Dòng «đã mở gì» — chỉ liệt kê cách học bài NÀY có và trẻ ĐÃ mở.
String openedDetailLine(HomeLessonThread thread) {
  final opened = [
    for (final v in thread.availableViews)
      if (thread.openedHere.contains(v)) v.label,
  ];
  if (opened.isEmpty) {
    final ways = thread.availableViews;
    if (ways.isEmpty) return 'SAM chưa đọc được phần nào của bài này.';
    return 'SAM đã xếp sẵn ${ways.length} cách học · con chưa mở cách nào.';
  }
  return 'Đã mở: ${opened.join(' · ')}';
}

/// Thẻ cho một mạch học có thật.
HomeCard cardForThread(HomeLessonThread thread, {int? learnerGrade}) {
  final d = thread.doc;
  final otherGrade = learnerGrade != null && d.grade != learnerGrade;
  return HomeCard(
    id: d.slotKey,
    subjectLine: d.bookTitle,
    lessonLine: displayLessonLabel(d.lessonNo, d.title),
    state: lessonCardState(thread),
    detailLine: openedDetailLine(thread),
    // NGUYÊN VĂN nhãn của động cơ. Home không đặt tên việc tiếp theo.
    nextLabel: thread.next?.label ?? 'Mở bài học',
    otherGradeNote: otherGrade
        ? 'Sách lớp ${d.grade} · không phải sách lớp con'
        : null,
    thread: thread,
  );
}

/// Thẻ RỖNG-TRUNG-THỰC cho một môn trên giá sách.
///
/// Nó nói ba điều, cả ba kiểm được: SAM chưa xếp bài nào ở môn này · giá sách
/// liệt kê bao nhiêu · trong đó mở ra làm được bao nhiêu. Khi số mở được là 0
/// thì câu KHÔNG được nói «bài», nó phải nói «mục lục» — đó chính là khác biệt
/// giữa một mục giá sách và một bài học cùng SAM.
HomeCard cardForShelfSubject(HomeShelfSubject s) {
  final detail = s.openableLessons > 0
      ? 'SAM chưa xếp sẵn bài nào ở môn này. Giá sách có '
            '${s.openableLessons} bài con mở làm được.'
      : 'SAM chưa xếp sẵn bài nào ở môn này. Giá sách mới có mục lục '
            '${s.listedLessons} bài.';
  return HomeCard(
    id: 'shelf:${s.subject}',
    subjectLine: s.subject,
    lessonLine: null,
    state: HomeCardState.chuaBatDau,
    detailLine: detail,
    nextLabel: s.openableLessons > 0 ? 'Mở giá sách' : 'Xem mục lục',
  );
}

/// ⭐⭐ HÀNG «HÔM NAY» — thứ tự TẤT ĐỊNH, ghi ra được thành luật:
///
/// 1. Bài SAM đã xếp sẵn **của đúng lớp con** — theo thứ tự [threads] truyền
///    vào (thứ tự catalog).
/// 2. Bài SAM đã xếp sẵn **của lớp khác** — vẫn là thẻ học bình thường, kèm
///    dòng sự thật «sách lớp N» (order 50 §6).
/// 3. Môn trên giá sách **chưa có bài nào**, xếp theo: số bài mở làm được
///    (giảm dần) → số bài mục lục liệt kê (giảm dần) → tên môn (để hai lần
///    dựng không bao giờ ra hai thứ tự).
///
/// Cắt ở [limit] thẻ. Số môn bị cắt trả về ở [HomeCardRow.hiddenSubjects] để
/// màn hình NÓI RA, không lặng lẽ giấu.
HomeCardRow buildHomeCards({
  required List<HomeLessonThread> threads,
  List<HomeShelfSubject> shelf = const [],
  int? learnerGrade,
  int limit = kHomeCardLimit,
}) {
  final own = <HomeCard>[];
  final other = <HomeCard>[];
  final seenSubjects = <String>{};
  for (final t in threads) {
    final card = cardForThread(t, learnerGrade: learnerGrade);
    seenSubjects.add(t.doc.subject);
    (card.otherGradeNote == null ? own : other).add(card);
  }

  final rest =
      [
        for (final s in shelf)
          if (!seenSubjects.contains(s.subject)) s,
      ]..sort((a, b) {
        final byOpenable = b.openableLessons.compareTo(a.openableLessons);
        if (byOpenable != 0) return byOpenable;
        final byListed = b.listedLessons.compareTo(a.listedLessons);
        if (byListed != 0) return byListed;
        return a.subject.compareTo(b.subject);
      });

  final all = [...own, ...other, for (final s in rest) cardForShelfSubject(s)];
  final shown = all.length <= limit ? all : all.sublist(0, limit);
  return HomeCardRow(cards: shown, totalSubjects: all.length);
}

/// Kết quả dựng hàng: những thẻ được hiện + tổng số môn có thật, để màn hình
/// nói «đang xem N trong M môn» thay vì im lặng cắt bớt.
class HomeCardRow {
  const HomeCardRow({required this.cards, required this.totalSubjects});

  final List<HomeCard> cards;
  final int totalSubjects;

  int get hiddenSubjects => totalSubjects - cards.length;
}

/// ⭐⭐ TẦNG 2 — CHỌN ĐÚNG MỘT VIỆC TIẾP THEO (order 50 §5, §12 D).
///
/// Đây KHÔNG phải động cơ đề xuất thứ hai. Mỗi bài đã có việc tiếp theo của
/// riêng nó, do `founderNextAction` sinh ra. Hàm này chỉ trả lời một câu HẸP
/// HƠN: trong nhiều bài, **thẻ nào được đưa lên «SAM GỢI Ý»**. Nó không tính
/// ra việc phải làm — nó xếp hạng những việc đã được tính.
///
/// Bậc thang, bậc trên thắng tuyệt đối:
///
/// | # | Bậc | Vì sao |
/// |---|---|---|
/// | 1 | Có bài thật (`thread != null`) và có việc tiếp theo | thẻ rỗng-trung-thực KHÔNG có việc tiếp theo để nêu; đẩy nó lên tầng 2 là bịa ra một đề xuất |
/// | 2 | Sách ĐÚNG LỚP của con | SAM không lấy sách lớp khác làm việc hôm nay, dù bài ấy đang dở |
/// | 3 | Việc tiếp theo mở được một CÁCH HỌC (`view != null`) | «về mục lục» / «xem tiếp» là câu trả lời thật, nhưng một cách học cụ thể dẫn trẻ đi xa hơn |
/// | 4 | Bài ĐANG DỞ (đã mở ≥ 1 cách) | tiếp việc đang làm trước khi mở việc mới |
/// | 5 | Thứ tự trong hàng | tất định — hai lần dựng ra cùng một kết quả |
///
/// Trả về chỉ số trong [cards], hoặc `null` khi KHÔNG thẻ nào đủ tư cách —
/// lúc ấy màn hình rơi về đề xuất cũ của «Hôm nay» và không bịa gì.
int? promotedCardIndex(List<HomeCard> cards) {
  int? best;
  List<int>? bestScore;
  for (var i = 0; i < cards.length; i++) {
    final c = cards[i];
    final t = c.thread;
    final n = c.next;
    if (t == null || n == null) continue; // bậc 1
    final score = <int>[
      c.otherGradeNote == null ? 0 : 1, // bậc 2
      n.view != null ? 0 : 1, // bậc 3
      t.openedHere.isEmpty ? 1 : 0, // bậc 4
      i, // bậc 5
    ];
    if (bestScore == null || _less(score, bestScore)) {
      best = i;
      bestScore = score;
    }
  }
  return best;
}

bool _less(List<int> a, List<int> b) {
  for (var i = 0; i < a.length; i++) {
    if (a[i] != b[i]) return a[i] < b[i];
  }
  return false;
}

// ═══════════════════════════════════════════════════════════════════════════
// Concept «05 Home» — hai dải ngang còn lại. Ba dải có NGỮ NGHĨA KHÁC NHAU và
// không được lẫn: SẮP TỚI = thời khoá biểu từ mai (xem `home_upcoming.dart`);
// CÁC MÔN CỦA CON = cửa vào Giá sách; TIẾP TỤC HỌC = bài đang học DỞ.
// ═══════════════════════════════════════════════════════════════════════════

/// ⭐ «TIẾP TỤC HỌC» — bài trẻ đã mở nhưng CHƯA mở hết cách học.
///
/// «Đang học dở» là điều duy nhất ở đây đo được: trẻ đã mở ít nhất một cách
/// học, và còn cách chưa mở. Nó KHÔNG nói trẻ hiểu tới đâu.
///
/// ⭐⭐ VÌ SAO KHÔNG CÓ PHẦN TRĂM. Concept vẽ «60%», «40%», «20%». Không có
/// phép đo nào trong sản phẩm này sinh ra được những con số ấy: số cách học đã
/// mở chia cho số cách học có KHÔNG phải mức hiểu bài — nó là tỉ lệ MỞ. Hiện
/// một con số phần trăm bên cạnh chữ «học» là nói với trẻ và bố mẹ rằng SAM đo
/// được sự hiểu, trong khi `OPENED != UNDERSTOOD`. Thẻ vì thế nói **đã mở gì
/// và còn gì chưa mở** — cùng lượng thông tin, không mượn thẩm quyền.
List<HomeLessonThread> continueLearning(
  List<HomeLessonThread> threads, {
  required int learnerGrade,
}) => [
  for (final t in threads)
    // ⭐ Bài của LỚP KHÁC không bao giờ là «việc con đang học dở». Đo trên
    // Nokia (lệnh 53): hồ sơ lớp 5 hiện thẻ «KHTN 6 · Bài 17», vì dải này
    // nhận mọi bài trong catalog mà không lọc lớp.
    if (t.doc.grade == learnerGrade &&
        t.openedHere.isNotEmpty &&
        t.openedHere.length < t.availableViews.length)
      t,
];

/// Một ô trong dải «CÁC MÔN CỦA CON» — cửa vào Giá sách của môn ấy.
///
/// ⭐ Cố ý NGHÈO: tên môn và có/không có bài SAM xếp sẵn. Concept vẽ thêm nhãn
/// «Tốt», «Ôn tập» dưới mỗi môn — đó là lời tuyên bố về NĂNG LỰC, và sản phẩm
/// này chỉ được nói điều có bằng chứng. Order 50 §5 đã liệt kê nhãn cấm:
/// ĐÃ HIỂU / 70% / GIỎI / MASTERED. «Tốt» thuộc đúng họ ấy.
class HomeSubjectChip {
  const HomeSubjectChip({
    required this.subject,
    required this.hasSamLesson,
    this.coverAsset,
  });

  final String subject;

  /// ⭐ BÌA SÁCH THẬT của môn (`assets/pack/covers/…`) — cùng ảnh Giá sách đang
  /// dùng, không phải icon vẽ thêm. `null` = pack chưa có bìa cho môn này ⇒ ô
  /// rơi về chữ cái đầu, KHÔNG bịa một hình khác.
  final String? coverAsset;

  /// Môn này có ít nhất một bài SAM đã xếp sẵn (khác với «có sách trên giá»).
  final bool hasSamLesson;
}

/// Dải «CÁC MÔN CỦA CON»: MỌI môn trên giá sách của trẻ, theo thứ tự mục lục.
///
/// Gộp hai nguồn về một danh sách duy nhất, không lặp: môn có bài SAM xếp sẵn
/// ([threads]) và môn chỉ có sách ([shelf]). Trẻ không cần biết hai nguồn ấy
/// khác nhau — nhưng ô nào có bài thì nói được là có.
List<HomeSubjectChip> homeSubjectChips({
  required List<HomeLessonThread> threads,
  required List<HomeShelfSubject> shelf,
  required int learnerGrade,
  Map<String, String> coverBySubject = const {},
}) {
  final withLesson = <String>{
    for (final t in threads)
      // Bài lớp KHÁC không làm cho môn của lớp NÀY thành «có bài».
      if (t.doc.grade == learnerGrade) t.doc.subject,
  };
  final out = <HomeSubjectChip>[];
  final seen = <String>{};
  for (final s in shelf) {
    if (!seen.add(s.subject)) continue;
    out.add(
      HomeSubjectChip(
        subject: s.subject,
        hasSamLesson: withLesson.contains(s.subject),
        coverAsset: coverBySubject[s.subject],
      ),
    );
  }
  // Môn có bài SAM nhưng vắng mặt trên giá (mục lục chưa nạp) vẫn phải có ô.
  for (final s in withLesson) {
    if (seen.add(s)) {
      out.add(
        HomeSubjectChip(
          subject: s,
          hasSamLesson: true,
          coverAsset: coverBySubject[s],
        ),
      );
    }
  }
  return out;
}

/// ⭐ Lệnh 53 §2 — ẢNH ĐẠI DIỆN của MỘT BÀI, chọn TẤT ĐỊNH.
///
/// Ảnh phải đến từ CHÍNH bài ấy: `doc.blocks` chỉ chứa hình của bài này, nên
/// không có đường nào để ảnh bài khác lọt vào.
///
/// ⭐⭐ LUẬT CHỌN (đo được, không «đẹp/xấu»), theo đúng thứ tự:
///
/// 1. LOẠI ảnh quá hẹp hoặc quá dẹt — `aspect` ngoài [minAspect, maxAspect].
///    Ảnh dẹt như dải trang trí (aspect ~3.0) làm hero thì cắt mất nội dung;
///    ảnh cao gầy thì nhồi vào thẻ ngang cũng vậy.
/// 2. LOẠI ảnh quá nhỏ — diện tích bbox dưới [minArea] phần trang. Đây là cách
///    đo «icon / logo / bảng con» mà KHÔNG cần đoán ngữ nghĩa: một hình chiếm
///    dưới 2% trang không phải hình minh hoạ chính của bài.
/// 3. Trong số còn lại, chọn DIỆN TÍCH LỚN NHẤT. Hoà thì ưu tiên hình CÓ CHÚ
///    THÍCH ĐÁNH SỐ (`labels > 0`): sách đánh số lên hình khi hình mang nghĩa.
/// 4. Vẫn hoà thì theo `id` tăng dần — để cùng một bài LUÔN cho cùng một ảnh,
///    mọi lần chạy, mọi máy.
///
/// Không ảnh nào qua được ⇒ `null`, và thẻ vẽ dạng KHÔNG ẢNH. Không bịa hình.
///
/// ⚠ Ảnh crop là nội dung SGK: INTERNAL / RESEARCH ONLY. Chúng nằm ngoài git
/// (`assets/fixtures/real/crops/`) và chỉ hiện trong app trên máy nghiên cứu —
/// đúng như màn Đọc đang làm. Đây KHÔNG phải quyết định phát hành.
class LessonHeroImage {
  const LessonHeroImage({required this.asset, required this.aspect});

  /// Đường dẫn asset đầy đủ, đã gắn `assetBase` của tài liệu.
  final String asset;

  /// width/height — để thẻ giữ chỗ đúng tỉ lệ, không kéo méo ảnh.
  final double aspect;
}

/// Ảnh quá cao/quá dẹt không dùng làm hero được.
const double kHeroMinAspect = 0.5;
const double kHeroMaxAspect = 2.5;

/// Dưới 2% diện tích trang ⇒ icon/bảng con, không phải hình của bài.
const double kHeroMinArea = 0.02;

LessonHeroImage? lessonHeroImage(LessonDocument doc) {
  ({ImageBlock b, double area})? best;
  for (final blk in doc.blocks) {
    if (blk is! ImageBlock) continue;
    final aspect = blk.aspect;
    if (aspect == null) continue; // không biết tỉ lệ ⇒ không dám làm hero
    if (aspect < kHeroMinAspect || aspect > kHeroMaxAspect) continue;
    // `bbox` là hằng 4 số (assert trong SourceRef) — rộng × cao đã chuẩn hoá
    // theo trang, nên diện tích là PHẦN TRANG mà hình chiếm.
    final bbox = blk.sourceRef.bbox;
    final area = bbox[2] * bbox[3];
    if (area < kHeroMinArea) continue;
    if (best == null ||
        area > best.area ||
        (area == best.area &&
            (blk.labels > best.b.labels ||
                (blk.labels == best.b.labels &&
                    blk.id.compareTo(best.b.id) < 0)))) {
      best = (b: blk, area: area);
    }
  }
  if (best == null) return null;
  return LessonHeroImage(
    asset: '${doc.assetBase}${best.b.crop}',
    aspect: best.b.aspect!,
  );
}
