/// LANE C (round 4, Golden Slice #2) — NGUỒN / DẪN NGUỒN của câu chuyện lịch sử
/// (`story-attribution-v1`, PROPOSED), suy TẤT ĐỊNH từ các block ĐÃ TIN của
/// tài liệu — không có block kind mới, không sửa `lesson_document.dart`.
///
/// Sách LS&ĐL viết mỗi «Câu chuyện Lịch sử» là: tiêu đề (heading) → các đoạn
/// (paragraph) → một dòng `(Theo tác-giả, tên-sách, NXB nhà-xuất-bản, năm)`.
/// Pipeline hôm nay gán dòng ấy vai `body` (không có vai
/// `attribution`); luật này nhận ra nó bằng DẠNG CHỮ và gắn nó với câu chuyện
/// đứng trước — mọi id block giữ nguyên để truy về trang/bbox.
///
/// Fail-closed: đoạn nào của câu chuyện bị giữ lại (withheld) thì câu chuyện
/// được đánh dấu KHÔNG TRỌN VẸN (`complete == false`), không điền hộ; tác
/// giả và tên sách KHÔNG tách (chữ nghiêng đã mất trong text) — chỉ NXB và
/// năm được đọc, phần còn lại là nguyên văn.
library;

import 'lesson_document.dart';

class StoryAttribution {
  const StoryAttribution({
    required this.attributionBlockId,
    required this.text,
    required this.form,
    required this.storyBlockIds,
    required this.withheldPartIds,
    this.titleBlockId,
    this.title,
    this.publisher,
    this.year,
  });

  static const derivation = 'story-attribution-v1';

  /// Block mang dòng nguồn — nguyên văn ở [text].
  final String attributionBlockId;
  final String text;

  /// `theo` = «(Theo …)» · `quote` = `(tác-giả, tác-phẩm, NXB …, năm)`.
  final String form;

  /// Tiêu đề câu chuyện (heading gần nhất phía trên) — `null` ⇒ không tìm
  /// thấy heading trước khi gặp phần tử khác ⇒ câu chuyện không trọn vẹn.
  final String? titleBlockId;
  final String? title;

  /// Các đoạn của câu chuyện theo thứ tự đọc (có thể qua trang).
  final List<String> storyBlockIds;

  /// Vùng bị giữ lại nằm trong câu chuyện — SAM nói thật là thiếu.
  final List<String> withheldPartIds;

  /// «NXB Giáo dục Việt Nam» / năm — đọc bằng mẫu, không đoán.
  final String? publisher;
  final int? year;

  bool get complete => titleBlockId != null && withheldPartIds.isEmpty;

  /// Câu kết (đoạn cuối trước dòng nguồn) — chỗ sách nêu Ý NGHĨA, dùng cho
  /// bước «nhân – quả» của kịch bản SAM.
  String? get conclusionBlockId =>
      storyBlockIds.isEmpty ? null : storyBlockIds.last;

  /// Dòng trẻ đọc: «Kể theo: NXB Giáo dục Việt Nam, 2017».
  String get childLine {
    final p = publisher, y = year;
    if (p != null && y != null) return 'Kể theo: $p, $y';
    if (p != null) return 'Kể theo: $p';
    return 'Kể theo nguồn ghi cuối câu chuyện';
  }
}

final _theo = RegExp(r'^\(\s*Theo\s+[\s\S]+\)\s*$');
final _quote = RegExp(r'^\([\s\S]+?,\s*NXB\s[^)]+?,\s*\d{4}\s*\)\s*$');
final _publisher = RegExp(r'NXB\s+[^,)]+');
final _yearEnd = RegExp(r'(\d{4})\s*\)\s*$');

/// `story-attribution-v1` trên các block của [doc], theo thứ tự đọc.
List<StoryAttribution> deriveStoryAttributions(LessonDocument doc) {
  final out = <StoryAttribution>[];
  final blocks = doc.blocks;
  for (var i = 0; i < blocks.length; i++) {
    final b = blocks[i];
    final text = switch (b) {
      ParagraphBlock(:final text) => text,
      CaptionBlock(:final text) => text,
      _ => null,
    };
    if (text == null) continue;
    final t = text.trim();
    final form = _theo.hasMatch(t)
        ? 'theo'
        : _quote.hasMatch(t)
        ? 'quote'
        : null;
    if (form == null) continue;
    final story = <String>[];
    final withheld = <String>[];
    HeadingBlock? title;
    for (var j = i - 1; j >= 0; j--) {
      final p = blocks[j];
      if (p is HeadingBlock) {
        title = p;
        break;
      }
      if (p is ActivityBlock ||
          p is QuestionBlock ||
          p is CaptionBlock ||
          p is SourceRefBlock ||
          p is TableBlock) {
        break;
      }
      if (p is ParagraphBlock) story.insert(0, p.id);
      if (p is WithheldBlock) withheld.insert(0, p.id);
      // ImageBlock: bỏ qua (ảnh không cắt câu chuyện)
    }
    final pub = _publisher.firstMatch(t)?.group(0)?.trim();
    final yr = _yearEnd.firstMatch(t)?.group(1);
    out.add(
      StoryAttribution(
        attributionBlockId: b.id,
        text: t,
        form: form,
        titleBlockId: title?.id,
        title: title?.text,
        storyBlockIds: story,
        withheldPartIds: withheld,
        publisher: pub,
        year: yr == null ? null : int.tryParse(yr),
      ),
    );
  }
  return out;
}
