/// TRANG SÁCH CỦA BÀI — màn đọc source-faithful, chữ VÀ hình của chính sách.
///
/// Vì sao có màn riêng thay vì dùng `ReaderScreen`: Reader đòi PHẢI có câu hỏi
/// (`_hasPassage && _hasQuestion`), còn trang sách của một bài thì không có câu
/// hỏi nào cả. Nhét nó vào Reader nghĩa là phải bịa ra một câu hỏi và một chỗ
/// trả lời — tức là bịa cho trẻ một bài tập mà sách không ra.
///
/// ⭐ ĐA PHƯƠNG THỨC, THEO ĐÚNG THỨ TỰ SÁCH. Founder dogfood bản chỉ-có-chữ và
/// nói thẳng: bài mở được không có nghĩa là bài đọc được. Hình đứng ĐÚNG CHỖ nó
/// thuộc về (chèn theo toạ độ y thật), không gom hết xuống cuối bài — gom xuống
/// cuối thì trẻ đọc xong mới thấy hình và không biết hình nào nói về đoạn nào.
///
/// Ba điều màn này KHÔNG làm, vì làm là nói dối:
/// - KHÔNG chấm, KHÔNG hỏi, KHÔNG %. Không có chìa khoá đáp án nào ở đây.
/// - KHÔNG phát bằng chứng năng lực. `OPENED != UNDERSTOOD`.
/// - KHÔNG tóm tắt, KHÔNG viết lại, KHÔNG sinh lại hình bằng AI, KHÔNG đặt chú
///   thích. Chữ là chữ của sách; hình là ẢNH CẮT từ đúng trang của đúng bài;
///   chú thích chỉ có khi sách in một dòng «Hình N…».
///
/// READ = đọc nguồn. VISUAL = SAM xếp lại để học. Hai vai khác nhau, đừng trộn.
library;


import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/pack/grade_pack.dart';
import '../../core/pack/lesson_figure_store.dart';
import '../lesson_workspace/learning_image_viewer.dart';
import 'lesson_index.dart';

class LessonPagesScreen extends StatefulWidget {
  const LessonPagesScreen(
      {super.key,
      required this.pages,
      required this.lessonLabel,
      this.bookTitle,
      this.grade,
      this.figures});

  final LessonPages pages;

  /// «Bài 17 · Tách chất khỏi hỗn hợp» — do người gọi dựng, cùng vốn từ giá sách.
  final String lessonLabel;
  final String? bookTitle;

  /// Lớp của trẻ — quyết định mở pack hình nào. `null` ⇒ không nạp hình.
  final int? grade;

  /// Tiêm sẵn kho hình (test). `null` ⇒ màn tự nạp theo [grade]; rỗng ⇒ bài vẫn
  /// đọc được phần chữ, thiếu hình không được làm hỏng cả bài.
  final LessonFigureStore? figures;

  /// Dòng nguồn trẻ đọc được: sách + TRANG IN (thứ in ở chân trang sách giấy),
  /// không phải số trang PDF. Đưa số PDF ra là nói với trẻ một số trang không
  /// có trong quyển sách trên tay nó. Mục lục không nói trang in ⇒ nói ít đi.
  String get sourceLine {
    final book = bookTitle ?? pages.book;
    final n = pages.pageCount;
    if (pages.pageStart == null) return '$book · $n trang';
    final end = pages.pageStart! + n - 1;
    return n == 1
        ? '$book · trang ${pages.pageStart}'
        : '$book · trang ${pages.pageStart}–$end';
  }

  @override
  State<LessonPagesScreen> createState() => _LessonPagesScreenState();
}

class _LessonPagesScreenState extends State<LessonPagesScreen> {
  LessonFigureStore? _figures;

  @override
  void initState() {
    super.initState();
    _figures = widget.figures;
    if (_figures == null && widget.grade != null) _load();
  }

  /// Chữ hiện NGAY; hình tới khi pack mở xong. Chặn cả màn để chờ một tệp 30 MB
  /// là biến bài đọc thành màn chờ.
  ///
  /// Trước khi nạp, thử CÀI pack của lớp này từ nguồn trên máy — chỉ lớp đang
  /// mở, không phải cả 12. Cài hỏng / chưa có nguồn ⇒ đi tiếp bình thường và
  /// bài vẫn đọc được phần chữ.
  Future<void> _load() async {
    final dir = await getApplicationDocumentsDirectory();
    final d = Directory('${dir.path}/hoc-cung-sam');
    if (!d.existsSync()) d.createSync(recursive: true);
    final packs = Directory('${d.path}/packs');
    if (!packs.existsSync()) packs.createSync(recursive: true);
    try {
      await GradePackInstaller(
              source: DirectoryPackSource(gradePackStagingDir(dir.path)),
              dir: packs.path)
          .install(widget.grade!);
    } catch (_) {
      // Cài lỗi không được làm hỏng bài đọc.
    }
    final s = await LessonFigureStore.loadForGrade(widget.grade!, packs.path);
    if (mounted) setState(() => _figures = s);
  }

  LessonPages get pages => widget.pages;
  String get lessonLabel => widget.lessonLabel;
  String get sourceLine => widget.sourceLine;
  LessonFigureStore? get figures => _figures;

  @override
  Widget build(BuildContext context) {
    final items = pages.stream;
    return Scaffold(
      backgroundColor: WalColors.surface,
      appBar: AppBar(
        backgroundColor: WalColors.surface,
        foregroundColor: WalColors.ink,
        elevation: 0,
        title: Text(lessonLabel,
            style: const TextStyle(
                fontSize: WalType.body, fontWeight: FontWeight.w600)),
      ),
      body: SafeArea(
        child: ListView.builder(
          padding: const EdgeInsets.all(WalSpacing.lg),
          itemCount: items.length + 2,
          itemBuilder: (context, i) {
            if (i == 0) {
              return Padding(
                padding: const EdgeInsets.only(bottom: WalSpacing.md),
                child: Text('📖 $sourceLine',
                    style: const TextStyle(
                        fontSize: WalType.secondary, color: WalColors.inkSoft)),
              );
            }
            if (i == items.length + 1) {
              return const Padding(
                padding: EdgeInsets.only(top: WalSpacing.lg),
                child: Text(
                    'Đây là chữ và hình trong sách. SAM chưa soạn phần học cho bài này.',
                    style: TextStyle(
                        fontSize: WalType.secondary, color: WalColors.inkSoft)),
              );
            }
            return switch (items[i - 1]) {
              ReadText(:final text) => Padding(
                  padding: const EdgeInsets.only(bottom: WalSpacing.md),
                  child: SelectableText(text,
                      style: const TextStyle(
                          fontSize: WalType.body,
                          height: 1.6,
                          color: WalColors.ink)),
                ),
              ReadImage img => _figure(context, img),
            };
          },
        ),
      ),
    );
  }

  Widget _figure(BuildContext context, ReadImage img) {
    final bytes = figures?.jpeg(img.id);
    // Pack lớp này chưa có hình ⇒ KHÔNG chừa ô trống câm. Không có gì để xem
    // thì không hiện gì; phần chữ của bài vẫn đọc bình thường.
    if (bytes == null) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: WalSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Ảnh SGK giữ ĐÚNG tỉ lệ gốc — không ép thành ô vuông/thẻ icon.
          GestureDetector(
            onTap: () => showLearningImage(context,
                bytes: bytes,
                aspect: img.aspect,
                caption: img.caption,
                sourceLine: sourceLine),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
              child: AspectRatio(
                aspectRatio: img.aspect,
                child: Image.memory(bytes,
                    fit: BoxFit.contain,
                    errorBuilder: (_, _, _) => const SizedBox.shrink()),
              ),
            ),
          ),
          if (img.caption != null)
            Padding(
              padding: const EdgeInsets.only(top: WalSpacing.xs),
              child: Text(img.caption!,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      color: WalColors.inkSoft,
                      fontStyle: FontStyle.italic)),
            ),
        ],
      ),
    );
  }
}
