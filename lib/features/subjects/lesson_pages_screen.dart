/// TRANG SÁCH CỦA BÀI — màn đọc tối giản, nói đúng nó là gì.
///
/// Vì sao có màn riêng thay vì dùng `ReaderScreen`: Reader đòi PHẢI có câu hỏi
/// (`_hasPassage && _hasQuestion`), còn trang sách của một bài thì không có câu
/// hỏi nào cả. Nhét nó vào Reader nghĩa là phải bịa ra một câu hỏi và một chỗ
/// trả lời — tức là bịa cho trẻ một bài tập mà sách không ra.
///
/// Ba điều màn này KHÔNG làm, vì làm là nói dối:
/// - KHÔNG chấm, KHÔNG hỏi, KHÔNG %. Không có chìa khoá đáp án nào ở đây.
/// - KHÔNG phát bằng chứng năng lực. `OPENED != UNDERSTOOD` — mở một bài ra
///   đọc là một dấu vết, không phải chứng cứ trẻ đã hiểu.
/// - KHÔNG tóm tắt, KHÔNG viết lại. Chữ hiện ra là chữ trong sách; máy chỉ bỏ
///   số trang và tiêu đề chạy đầu/cuối trang rồi ghép lại.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import 'lesson_index.dart';

class LessonPagesScreen extends StatelessWidget {
  const LessonPagesScreen(
      {super.key, required this.pages, required this.lessonLabel, this.bookTitle});

  final LessonPages pages;

  /// «Bài 17 · Tách chất khỏi hỗn hợp» — do người gọi dựng, cùng vốn từ giá sách.
  final String lessonLabel;
  final String? bookTitle;

  /// Dòng nguồn trẻ đọc được: sách + TRANG IN (thứ in ở chân trang sách giấy),
  /// không phải số trang PDF. Khi mục lục không nói trang in thì nói ít đi chứ
  /// không đưa số PDF ra làm như đó là trang sách.
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
  Widget build(BuildContext context) {
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
        child: ListView(
          padding: const EdgeInsets.all(WalSpacing.lg),
          children: [
            Text('📖 $sourceLine',
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
            const SizedBox(height: WalSpacing.md),
            SelectableText(pages.text,
                style: const TextStyle(
                    fontSize: WalType.body, height: 1.6, color: WalColors.ink)),
            const SizedBox(height: WalSpacing.lg),
            const Text(
                'Đây là chữ trong sách. SAM chưa soạn phần học cho bài này.',
                style: TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
          ],
        ),
      ),
    );
  }
}
