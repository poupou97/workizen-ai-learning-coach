/// WAL-167 — GIÁ SÁCH: trẻ nhận ra ĐÚNG CUỐN SÁCH mình đang học.
///
/// Vì sao đây là màn đáng có, không phải trang trí: ở Việt Nam **sách giấy vẫn
/// là trung tâm trên lớp** (điện thoại bị siết trong trường), nên thứ nối lớp
/// học với màn hình là cuốn sách cụ thể trên bàn. Nhật Bản (Lentrance mở ra
/// 本棚 hiện bìa sách) và cả hai cổng SGK số của VN (Hành Trang Số, hoc10
/// «Tủ sách») đều chọn thế có chủ đích.
///
/// ⭐ Nhưng bìa là BIỂN CHỈ ĐƯỜNG, không phải nội dung: bấm vào sách KHÔNG mở
/// PDF lật trang — nó vào trải nghiệm phần mềm (Bài → Học → Bằng chứng). Đây
/// là chỗ khác IXL, nơi 336 bìa sách chỉ dẫn tới bảng ánh xạ kỹ năng.
///
/// QA Nokia n91: bản đầu nhóm theo môn với tiêu đề môn riêng. Pack lớp 5 hầu
/// hết MỘT cuốn / một môn ⇒ mỗi nhóm chỉ đủ một ô, thành ra 13 cuốn xếp thành
/// 13 hàng: muốn tới Toán phải cuộn qua gần hết giá. Cùng họ lỗi WAL-142 n64
/// (dữ liệu đúng nhưng CHÔN mất điều màn này sinh ra để nói). Sửa: một lưới
/// duy nhất, ô rộng theo bề ngang máy — tên môn đã nằm ngay dưới mỗi bìa nên
/// bỏ tiêu đề nhóm không mất thông tin nào.
///
/// ⭐ ROUND 5 B: khung concept 1 («GIÁ SÁCH») có Ô TÌM và hàng chip lọc mà
/// bản này chưa có — đó là phần lớn khoảng cách còn lại của màn (65–75 %).
/// Vòng 5 thêm hai thứ đó, và CHỈ hai thứ đó, vì chúng không phát biểu điều
/// gì mới: tìm là so khớp chuỗi trong tên sách / tên môn ĐÃ CÓ trong mục lục;
/// chip lọc là tập môn có thật trong mục lục cộng một chip «có bài học SAM»
/// đếm từ `WorkspaceCatalog`. Không xếp hạng sách, không «gợi ý», không lưu
/// gì (khung concept có «Yêu thích» — thứ đó cần ghi hồ sơ, nằm ngoài ranh
/// giới không-ghi của Track B, nên KHÔNG dựng).
///
/// ⭐ TRACK B (WAL-210): cuốn nào có ÍT NHẤT một bài có Lesson Workspace
/// (fixture trong `WorkspaceCatalog`) thì mở `BookScreen` mới (bìa → Chương →
/// Bài → Workspace); cuốn khác giữ nguyên hành vi cũ qua [onOpenBook]. Đường
/// cũ vẫn tới được từ trong `BookScreen` (một chạm) — không mất lối nào.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/lesson_model/workspace_catalog.dart';
import '../../core/store/learner_profile.dart';
import '../lesson_workspace/book_screen.dart';
import '../lesson_workspace/workspace_trace.dart';
import 'lesson_index.dart';

class BookShelfScreen extends StatefulWidget {
  const BookShelfScreen({
    super.key,
    required this.profile,
    required this.index,
    required this.onOpenBook,
    this.catalog,
    this.trace,
  });

  final LearnerProfile profile;
  final LessonIndex? index;

  /// Mở một cuốn — tầng trên dựng Book Home (cùng màn với Subject Home, lọc
  /// theo sách), nên giá sách không biết gì về điều hướng.
  final void Function(BookRef book) onOpenBook;

  /// Bài nào có workspace. `null` ⇒ dùng catalog chung của app (nạp lười).
  final WorkspaceCatalog? catalog;

  /// Trace phiên (trong bộ nhớ). `null` ⇒ trace chung của app.
  final WorkspaceTrace? trace;

  /// Số cột theo bề ngang CÒN LẠI (đã trừ lề). Nokia 6.1 (~392dp) ⇒ 3 cột,
  /// ô rộng ~109dp; máy hẹp 320dp ⇒ 2 cột. Sàn ~96dp là ngưỡng trẻ còn NHẬN
  /// RA bìa sách — đó là lý do có clamp, không phải thẩm mỹ.
  static int columnsFor(double width) => (width / 110).floor().clamp(2, 5);

  static const searchKey = Key('shelf-search');
  static const emptyKey = Key('shelf-empty');
  static Key filterKey(String id) => Key('shelf-filter-$id');

  /// Chip «có bài học SAM» — id riêng để test và mã đọc được.
  static const samFilter = '__sam__';

  /// Dấu tiếng Việt theo NHÓM chữ gốc — viết thành nhóm để không thể lệch
  /// một ký tự như hai chuỗi song song (lỗi bắt được ngay ở test đầu tiên).
  static const _marks = <String, String>{
    'a': 'àáảãạăằắẳẵặâầấẩẫậ',
    'd': 'đ',
    'e': 'èéẻẽẹêềếểễệ',
    'i': 'ìíỉĩị',
    'o': 'òóỏõọôồốổỗộơờớởỡợ',
    'u': 'ùúủũụưừứửữự',
    'y': 'ỳýỷỹỵ',
  };

  /// Bỏ dấu + thường hoá để trẻ gõ «toan» vẫn ra «Toán» — thuần hàm, không
  /// từ điển, không đoán ý.
  static String fold(String s) {
    final b = StringBuffer();
    for (final ch in s.toLowerCase().runes) {
      final c = String.fromCharCode(ch);
      var out = c;
      for (final e in _marks.entries) {
        if (e.value.contains(c)) {
          out = e.key;
          break;
        }
      }
      b.write(out);
    }
    return b.toString();
  }

  /// Lọc TẤT ĐỊNH: chuỗi tìm khớp tên sách hoặc tên môn; chip môn khớp môn;
  /// chip SAM khớp cuốn có workspace. Không có kết quả ⇒ nói thật.
  static List<BookRef> filtered(
    List<BookRef> books, {
    String query = '',
    String? subject,
    bool samOnly = false,
    bool Function(BookRef)? hasWorkspace,
  }) {
    final q = fold(query.trim());
    return [
      for (final b in books)
        if ((subject == null || b.subject == subject) &&
            (!samOnly || (hasWorkspace?.call(b) ?? false)) &&
            (q.isEmpty ||
                fold(b.shelfLabel).contains(q) ||
                fold(b.subject).contains(q)))
          b,
    ];
  }

  /// Thứ tự MÔN giữ nguyên mục lục — SAM không xếp hạng môn nào quan trọng
  /// hơn. Trong cùng một môn thì theo TẬP TĂNG DẦN: mục lục xếp theo mã tài
  /// liệu nên `…tap-hai` đứng trước `…tap-mot`, và trên máy thật (n93) trẻ
  /// thấy «Tập 2» trước «Tập 1» ở cả Toán, Tiếng Việt, Tiếng Anh — đúng chuỗi,
  /// sai cuốn sách đang nằm trên bàn.
  static List<BookRef> shelfOrder(List<BookRef> books) {
    final at = {for (var i = 0; i < books.length; i++) books[i]: i};
    final bySubject = <String, List<BookRef>>{};
    for (final b in books) {
      bySubject.putIfAbsent(b.subject, () => []).add(b);
    }
    return [
      for (final group in bySubject.values)
        ...group..sort((a, b) {
          final v = (a.volume ?? 0).compareTo(b.volume ?? 0);
          return v != 0 ? v : at[a]!.compareTo(at[b]!);
        }),
    ];
  }

  @override
  State<BookShelfScreen> createState() => _BookShelfScreenState();
}

class _BookShelfScreenState extends State<BookShelfScreen> {
  WorkspaceCatalog get _catalog => widget.catalog ?? WorkspaceCatalog.shared;

  final _search = TextEditingController();

  /// `null` = «Tất cả»; `BookShelfScreen.samFilter` = chỉ cuốn có bài học SAM;
  /// còn lại là tên môn có thật trong mục lục.
  String? _filter;

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    // Nạp lười, không chặn giá sách: chưa nạp xong thì cuốn mở theo lối cũ.
    if (!_catalog.isLoaded) {
      _catalog.load().then((_) {
        if (mounted) setState(() {});
      });
    }
  }

  /// Mục lục thật của cuốn (từ pack) để BookScreen xếp theo chương.
  List<LessonRef> _lessonsOf(BookRef b) {
    final idx = widget.index;
    if (idx == null) return const [];
    for (final books in idx.subjects.values) {
      for (final bl in books) {
        if (bl.sourceDocumentId == b.sourceDocumentId) return bl.lessons;
      }
    }
    return const [];
  }

  void _open(BuildContext context, BookRef b) {
    final docs = _catalog.docsForBook(b.sourceDocumentId);
    if (docs.isEmpty) {
      widget.onOpenBook(b);
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => BookScreen(
          book: b,
          lessons: _lessonsOf(b),
          docs: docs,
          trace: widget.trace ?? WorkspaceTrace.session,
          onOpenLegacy: () => widget.onOpenBook(b),
          learnerId: widget.profile.learnerId,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final profile = widget.profile;
    final books = BookShelfScreen.shelfOrder(
      widget.index?.books ?? const <BookRef>[],
    );
    final subjects = <String>[];
    for (final b in books) {
      if (!subjects.contains(b.subject)) subjects.add(b.subject);
    }
    final shown = BookShelfScreen.filtered(
      books,
      query: _search.text,
      subject: _filter == null || _filter == BookShelfScreen.samFilter
          ? null
          : _filter,
      samOnly: _filter == BookShelfScreen.samFilter,
      hasWorkspace: (b) => _catalog.hasWorkspaceFor(b.sourceDocumentId),
    );
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, box) {
            final cols = BookShelfScreen.columnsFor(
              box.maxWidth - WalSpacing.lg * 2,
            );
            final tile =
                (box.maxWidth -
                    WalSpacing.lg * 2 -
                    WalSpacing.md * (cols - 1)) /
                cols;
            return ListView(
              padding: const EdgeInsets.all(WalSpacing.lg),
              children: [
                Text(
                  'Sách của con · Lớp ${profile.grade}',
                  style: const TextStyle(
                    fontSize: WalType.display,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink,
                  ),
                ),
                if (books.isNotEmpty) ...[
                  const SizedBox(height: WalSpacing.md),
                  _searchField(),
                  const SizedBox(height: WalSpacing.sm),
                  _filterRow(subjects),
                ],
                const SizedBox(height: WalSpacing.md),
                if (books.isEmpty)
                  const Text(
                    'Máy này chưa nạp sách nào — SAM chưa mở được giá sách.',
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.inkSoft,
                    ),
                  )
                else if (shown.isEmpty)
                  const Text(
                    'Không có cuốn nào khớp — con thử xoá bớt chữ tìm, hoặc '
                    'bấm «Tất cả» nhé.',
                    key: BookShelfScreen.emptyKey,
                    style: TextStyle(
                      fontSize: WalType.body,
                      color: WalColors.inkSoft,
                    ),
                  )
                else
                  Wrap(
                    spacing: WalSpacing.md,
                    runSpacing: WalSpacing.lg,
                    children: [
                      for (final b in shown) _bookTile(context, b, tile),
                    ],
                  ),
              ],
            );
          },
        ),
      ),
    );
  }

  Widget _searchField() => SizedBox(
    height: WalSpacing.minTouch,
    child: TextField(
      key: BookShelfScreen.searchKey,
      controller: _search,
      onChanged: (_) => setState(() {}),
      textInputAction: TextInputAction.search,
      style: const TextStyle(fontSize: WalType.body, color: WalColors.ink),
      decoration: InputDecoration(
        hintText: 'Tìm sách, môn học…',
        hintStyle: const TextStyle(
          fontSize: WalType.body,
          color: WalColors.inkSoft,
        ),
        prefixIcon: const Icon(Icons.search, color: WalColors.inkSoft),
        suffixIcon: _search.text.isEmpty
            ? null
            : IconButton(
                tooltip: 'Xoá chữ tìm',
                icon: const Icon(Icons.close, color: WalColors.inkSoft),
                onPressed: () => setState(_search.clear),
              ),
        filled: true,
        fillColor: Colors.white,
        contentPadding: const EdgeInsets.symmetric(vertical: 0),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(WalSpacing.radiusButton),
          borderSide: BorderSide.none,
        ),
      ),
    ),
  );

  Widget _filterRow(List<String> subjects) => SizedBox(
    height: WalSpacing.minTouch,
    child: ListView(
      scrollDirection: Axis.horizontal,
      children: [
        _filterChip(null, 'Tất cả', 'all'),
        if (_catalog.isLoaded && _catalog.booksWithWorkspace.isNotEmpty)
          _filterChip(BookShelfScreen.samFilter, '✨ Có bài học SAM', 'sam'),
        for (final s in subjects) _filterChip(s, s, s),
      ],
    ),
  );

  Widget _filterChip(String? value, String label, String id) => Padding(
    padding: const EdgeInsets.only(right: WalSpacing.sm),
    child: ChoiceChip(
      key: BookShelfScreen.filterKey(id),
      label: Text(
        label,
        style: TextStyle(
          fontSize: WalType.secondary,
          fontWeight: FontWeight.w600,
          color: _filter == value ? Colors.white : WalColors.ink,
        ),
      ),
      selected: _filter == value,
      selectedColor: WalColors.primary500,
      backgroundColor: Colors.white,
      showCheckmark: false,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
      ),
      onSelected: (_) => setState(() => _filter = value),
    ),
  );

  Widget _bookTile(BuildContext context, BookRef b, double width) => SizedBox(
    width: width,
    child: InkWell(
      onTap: () => _open(context, b),
      borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(WalSpacing.radiusBookCover),
            child: AspectRatio(
              aspectRatio: 3 / 4,
              child: Image.asset(
                'assets/pack/${b.cover}',
                fit: BoxFit.cover,
                // Máy dựng bản build thiếu bìa ⇒ vẫn vào sách được bằng TÊN,
                // không chặn việc học vì thiếu một tấm ảnh.
                errorBuilder: (_, _, _) => Container(
                  color: WalColors.surfaceLavender,
                  alignment: Alignment.center,
                  padding: const EdgeInsets.all(WalSpacing.sm),
                  child: Text(
                    b.title,
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink,
                    ),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            b.shelfLabel,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              fontSize: WalType.secondary,
              fontWeight: FontWeight.w700,
              color: WalColors.ink,
            ),
          ),
          Text(
            '${b.lessonCount} bài',
            style: const TextStyle(
              fontSize: WalType.secondary,
              color: WalColors.inkSoft,
            ),
          ),
          // TRACK B: cuốn có Lesson Workspace được đánh dấu để Founder
          // nhận ra ngay trên giá — nhãn nhỏ, không xếp hạng sách.
          // ROUND 4: cùng một chữ «✨ N bài học SAM» từ giá → sách → chương
          // (đếm từ catalog, không bịa).
          if (_catalog.hasWorkspaceFor(b.sourceDocumentId))
            Text(
              '✨ ${_catalog.docsForBook(b.sourceDocumentId).length} bài học SAM',
              style: const TextStyle(
                fontSize: WalType.secondary,
                fontWeight: FontWeight.w600,
                color: WalColors.primaryText,
              ),
            ),
        ],
      ),
    ),
  );
}
