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
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/store/learner_profile.dart';
import 'lesson_index.dart';

class BookShelfScreen extends StatelessWidget {
  const BookShelfScreen(
      {super.key,
      required this.profile,
      required this.index,
      required this.onOpenBook});

  final LearnerProfile profile;
  final LessonIndex? index;

  /// Mở một cuốn — tầng trên dựng Book Home (cùng màn với Subject Home, lọc
  /// theo sách), nên giá sách không biết gì về điều hướng.
  final void Function(BookRef book) onOpenBook;

  /// Số cột theo bề ngang CÒN LẠI (đã trừ lề). Nokia 6.1 (~392dp) ⇒ 3 cột,
  /// ô rộng ~109dp; máy hẹp 320dp ⇒ 2 cột. Sàn ~96dp là ngưỡng trẻ còn NHẬN
  /// RA bìa sách — đó là lý do có clamp, không phải thẩm mỹ.
  static int columnsFor(double width) => (width / 110).floor().clamp(2, 5);

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
        ...group
          ..sort((a, b) {
            final v = (a.volume ?? 0).compareTo(b.volume ?? 0);
            return v != 0 ? v : at[a]!.compareTo(at[b]!);
          }),
    ];
  }

  @override
  Widget build(BuildContext context) {
    final books = shelfOrder(index?.books ?? const <BookRef>[]);
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: LayoutBuilder(builder: (context, box) {
          final cols = columnsFor(box.maxWidth - WalSpacing.lg * 2);
          final tile =
              (box.maxWidth - WalSpacing.lg * 2 - WalSpacing.md * (cols - 1)) /
                  cols;
          return ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              Text('Sách của con · Lớp ${profile.grade}',
                  style: const TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink)),
              const SizedBox(height: WalSpacing.md),
              if (books.isEmpty)
                const Text(
                    'Máy này chưa nạp sách nào — SAM chưa mở được giá sách.',
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.inkSoft))
              else
                Wrap(
                  spacing: WalSpacing.md,
                  runSpacing: WalSpacing.lg,
                  children: [
                    for (final b in books) _bookTile(context, b, tile),
                  ],
                ),
            ],
          );
        }),
      ),
    );
  }

  Widget _bookTile(BuildContext context, BookRef b, double width) => SizedBox(
        width: width,
        child: InkWell(
          onTap: () => onOpenBook(b),
          borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
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
                    child: Text(b.title,
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                            color: WalColors.ink)),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 6),
            Text(b.volumeLabel == null ? b.title : '${b.title} · ${b.volumeLabel}',
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                    fontSize: WalType.secondary,
                    fontWeight: FontWeight.w700,
                    color: WalColors.ink)),
            Text('${b.lessonCount} bài',
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ]),
        ),
      );
}
