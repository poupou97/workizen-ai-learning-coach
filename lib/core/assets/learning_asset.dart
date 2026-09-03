/// WAL-133 — MÔ HÌNH TÀI SẢN HÌNH ẢNH: ba loại, KHÔNG loại nào không khai.
///
/// Cùng một bài học của [Provenance]: thứ dễ sai âm thầm phải để **trình biên
/// dịch giữ hộ**, không phải để review nhớ. Ở đây chỗ sai âm thầm là một hình
/// SAM tự vẽ nằm cạnh bài học và trông y như hình chụp từ sách — trẻ (và phụ
/// huynh) không có cách nào phân biệt, và ta thì đã nói dối mà không định nói
/// dối.
///
/// `sealed` ⇒ mọi `switch` trên tài sản là VÉT CẠN: thêm loại thứ tư là mọi
/// chỗ tiêu thụ đỏ ngay, không có nhánh nào lặng lẽ rơi vào «mặc định».
library;

/// Tài sản hình ảnh dùng trong bài học.
sealed class LearningAsset {
  const LearningAsset({required this.path});

  /// Đường dẫn TRONG BUNDLE (vd `assets/pack/map-....png`) — không phải đường
  /// dẫn ổ đĩa: đường dẫn ổ đĩa rò rỉ bố cục máy người dùng và đổi máy là hỏng.
  final String path;
}

/// ⭐ Trích/crop TỪ SGK. Provenance đầy đủ là ĐIỀU KIỆN TỒN TẠI — không có
/// constructor nào tạo được `SourceAsset` mà thiếu nguồn, trang, khung cắt hay
/// phiên bản trích.
///
/// WAL-43: mọi `SourceAsset` là `localResearchOnly` — nằm dưới `assets/pack/`
/// (đã gitignore), không commit, không phân phối. Ràng buộc đó được ASSERT ở
/// constructor chứ không nằm trong tài liệu.
final class SourceAsset extends LearningAsset {
  SourceAsset({
    required super.path,
    required this.sourceDocumentId,
    required this.pagePdf,
    required this.bboxFrac,
    required this.extractionVersion,
    this.printedCaption,
    this.samGloss,
    this.pagePrinted,
  })  : assert(sourceDocumentId != '', 'crop không nguồn thì không dùng được'),
        assert(bboxFrac.length == 4, 'khung cắt phải đủ 4 số'),
        assert(extractionVersion != '', 'không truy được cách cắt ⇒ không tin'),
        assert(path.startsWith('assets/pack/'),
            'WAL-43: crop từ SGK chỉ được nằm trong vùng KHÔNG commit');

  final String sourceDocumentId;

  /// Trang trong tệp PDF (đếm từ 1) — dùng để cắt lại/kiểm chứng.
  final int pagePdf;

  /// Trang IN trên sách — thứ nói cho trẻ và phụ huynh. `null` khi chưa dò
  /// được, và khi đó UI KHÔNG được bịa ra một số trang.
  final int? pagePrinted;

  /// Khung cắt theo tỉ lệ [l, t, r, b] ∈ [0,1] — độc lập DPI, cắt lại được.
  final List<double> bboxFrac;
  final String extractionVersion;

  /// Caption IN trong sách, NGUYÊN VĂN — `null` khi sách không in caption nào.
  ///
  /// WAL-133 slice 2 phát hiện: hình phân số SGK Toán 5 tr.22 KHÔNG có caption
  /// in. Bản đầu bắt buộc trường này, nên muốn dùng thì phải tự viết một câu
  /// rồi đặt vào ô «nguyên văn sách» — đúng kiểu nói dối mà cả mô hình sinh ra
  /// để chặn. Thà để `null` và UI im, còn hơn có chữ mà chữ ấy không phải của
  /// sách.
  final String? printedCaption;

  /// Lời của SAM về hình này (curated, systemDerived). UI BẮT BUỘC dán nhãn
  /// riêng — không bao giờ trộn vào chỗ của caption sách. Cùng luật với
  /// `SuSource.samGloss`.
  final String? samGloss;
}

/// Hình SAM tự dựng. `what` là điều BẮT BUỘC nói ra — UI không có cách nào
/// hiển thị loại này mà giấu nhãn (xem `LearningAssetImage`).
final class SamGeneratedAsset extends LearningAsset {
  const SamGeneratedAsset({required super.path, required this.what})
      : assert(what != '', 'hình SAM vẽ phải nói được nó vẽ cái gì');

  /// Vd «sơ đồ quy đồng mẫu số» — để trẻ biết mình đang nhìn cái gì, do ai vẽ.
  final String what;
}

/// Trang trí thuần: linh vật, nền, biểu tượng. KHÔNG mang một tuyên bố nội
/// dung nào, nên thiếu nó cũng không làm bài học sai — và cũng vì thế KHÔNG
/// được dùng để minh hoạ tri thức.
final class UiDecorativeAsset extends LearningAsset {
  const UiDecorativeAsset({required super.path});
}

/// Nhãn BẮT BUỘC hiển thị cùng tài sản. `null` = không cần nhãn.
///
/// Vét cạn trên `sealed` — thêm loại mới mà quên nghĩ về nhãn là không biên
/// dịch được.
String? mandatoryLabelOf(LearningAsset a) => switch (a) {
      SourceAsset() => null, // nguồn được nói bằng dòng trích dẫn riêng
      SamGeneratedAsset() => 'Minh hoạ của SAM',
      UiDecorativeAsset() => null,
    };

/// Dòng nguồn cho trẻ đọc. Chỉ `SourceAsset` mới có — hai loại kia KHÔNG được
/// mượn dòng nguồn của sách (đó chính là kiểu nói dối mà mô hình này chặn).
String? sourceLineOf(LearningAsset a) => switch (a) {
      SourceAsset(:final sourceDocumentId, :final pagePrinted) =>
        pagePrinted == null
            ? sourceDocumentId
            : '$sourceDocumentId · trang $pagePrinted',
      SamGeneratedAsset() => null,
      UiDecorativeAsset() => null,
    };

/// Thiếu tệp thì nói gì. Khác nhau theo loại vì HẬU QUẢ khác nhau: thiếu ảnh
/// nguồn là thiếu một phần bài học (phải nói); thiếu hình trang trí thì không
/// ai mất gì (im lặng, đừng làm trẻ lo).
String? missingNoticeOf(LearningAsset a) => switch (a) {
      SourceAsset() => 'Máy này chưa có ảnh của bài — phần chữ vẫn đọc được.',
      SamGeneratedAsset() => null,
      UiDecorativeAsset() => null,
    };
