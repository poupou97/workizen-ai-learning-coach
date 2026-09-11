/// TRACK B — nạp fixture bài học: THẬT (gitignore, sinh từ TSL) nếu có,
/// không thì MẪU (commit, giả lập). Không có cả hai ⇒ slot đó không có
/// workspace — giá sách giữ hành vi cũ, không màn rỗng.
library;

import 'dart:convert';

import 'package:flutter/services.dart' show AssetBundle, rootBundle;

import 'lesson_document.dart';

/// Một «chỗ» có thể có workspace: cuốn + số bài. Danh sách này là hằng —
/// thêm bài = thêm một dòng + một fixture; không quét thư mục ở runtime.
class FixtureSlot {
  const FixtureSlot({required this.book, required this.lessonNo});
  final String book;
  final int lessonNo;

  static const realDir = 'assets/fixtures/real/';
  static const syntheticDir = 'assets/fixtures/synthetic/';

  String get realPath => '$realDir${_stem()}.json';
  String get syntheticPath => '$syntheticDir${_stem()}.synthetic.json';
  String _stem() => 'lesson-$book-b$lessonNo';
  String get key => '$book#$lessonNo';
}

class WorkspaceCatalog {
  WorkspaceCatalog({this.bundle, this.slots = defaultSlots});

  /// Xây thẳng từ tài liệu — cho test và cho tầng trên đã có sẵn doc.
  WorkspaceCatalog.withDocs(Iterable<LessonDocument> docs)
    : bundle = null,
      slots = const [] {
    for (final d in docs) {
      _docs[d.slotKey] = d;
    }
    _loaded = true;
  }

  /// Bài 17 KHTN 6 — bài trưng bày do Founder chốt (2026-09-05).
  /// Bài 8 LS&ĐL 5 — Golden Slice #2 (Lane C, round 4): LÁT CẮT NGHIÊN CỨU
  /// (sách lớp 5) — Founder duyệt ứng viên §7; cổng gate ghi ở
  /// docs/research/lane-c/05-GOLDEN-SLICE-2-GATE.md. Chip thử nghiệm bắt buộc.
  /// ⭐⭐ Bài 16 KHTN 6 — BÀI THỨ HAI, và nó là BẰNG CHỨNG chứ không phải
  /// thêm nội dung.
  ///
  /// Câu hỏi cần trả lời: Bài 17 chạy được là nhờ NĂNG LỰC CHUNG hay nhờ dữ
  /// liệu riêng của nó? Bài 16 sinh ra bằng ĐÚNG cầu TSL→LessonDocument sẵn
  /// có, KHÔNG sửa một dòng mã nào — 77 block, 68 tin cậy, 2 sơ đồ quy trình.
  /// Nên Đọc và Trực quan đúng là năng lực chung.
  ///
  /// ⚠ «Học với SAM» TỪNG bị chặn ở đây: `tutor_script_for` trong cầu ấy mở
  /// đầu bằng `if book != '06-sgk-khoa-hoc-tu-nhien-6' || lesson != 17 → None`,
  /// với block id đóng cứng — không phải thiếu dữ liệu mà là một nhánh mã chỉ
  /// nhận đúng một bài. WAL-228 đã bỏ nhánh ấy: kịch bản nay là DỮ LIỆU
  /// (`tool/corpus/tutor_scripts/<book>-b<NN>.json`), thêm bài không cần sửa mã.
  ///
  /// Nhưng CƠ CHẾ MỞ KHÔNG PHẢI LÀ NỘI DUNG ĐÃ CÓ. Hôm nay vẫn đúng MỘT tệp
  /// kịch bản (Bài 17), nên Bài 16/9/10 vẫn chỉ có Đọc + Trực quan — giờ là vì
  /// chưa ai soạn kịch bản cho chúng, không phải vì mã từ chối. Soạn kịch bản
  /// là việc của NGƯỜI: `acceptable`/`hints`/`scaffold` mà máy tự sinh là máy
  /// bịa cách dạy. Màn hình vẫn nói thẳng thay vì hiện một tab rỗng.
  /// ⚠ CHỌN THEO THỨ TRẺ MỞ ĐƯỢC, KHÔNG THEO SỐ BÀI CÓ TSL.
  ///
  /// Tôi từng suy «9 bài lớp 6 có TSL ⇒ 9 bài có Đọc + Trực quan». SAI: số ấy
  /// đếm thí nghiệm trong PACK, còn tab Trực quan của màn học lấy từ mảng
  /// `semantic` của FIXTURE — hai đường ống khác nhau. Sinh thử cả 7 bài còn
  /// lại thì chỉ Bài 9 và 10 có sơ đồ; 11, 12, 46, 48, 50 ra `semantic` RỖNG.
  ///
  /// Nên ở đây chỉ có bài đã ĐO là mở được cả hai cách học. Năm bài kia thêm
  /// vào cũng chỉ tăng con số, còn trẻ bấm Trực quan thì gặp chỗ trống.
  static const defaultSlots = [
    FixtureSlot(book: '06-sgk-khoa-hoc-tu-nhien-6', lessonNo: 17),
    FixtureSlot(book: '06-sgk-khoa-hoc-tu-nhien-6', lessonNo: 16),
    FixtureSlot(book: '06-sgk-khoa-hoc-tu-nhien-6', lessonNo: 10),
    FixtureSlot(book: '06-sgk-khoa-hoc-tu-nhien-6', lessonNo: 9),
    FixtureSlot(book: '05-sgk-lich-su-va-dia-li-5', lessonNo: 8),
    // ⭐ LEARNABLE_V1 — lát cắt đầu tiên, Founder duyệt 2026-09-10, rút bằng
    // seed ĐÓNG BĂNG 20260910, một bài mỗi lớp 4–9. Không chọn tay.
    //
    // ⚠ ĐÃ RÚT LẠI CẢ SÁU LỚP sau khi cổng ③ được sửa. Cổng cũ («có ít nhất
    // một SemanticData có kiểu») nhận cả sơ đồ RỖNG RUỘT — KHTN 6 Bài 8 có
    // đúng một bước và bước ấy BỊ GIỮ LẠI, nên trẻ bấm ✨ Trực quan chỉ thấy
    // một ô xám. Cổng mới đòi ≥1 phần tử ĐỌC ĐƯỢC; quần thể 44 → 37; mẫu tất
    // định rút lại từ đầu cho ra ĐÚNG năm bài cũ, chỉ lớp 6 đổi Bài 8 → Bài 9.
    //
    // Lớp 6 Bài 9 vốn đã có mặt trong danh sách trên (golden slice cũ), nên
    // không thêm dòng trùng.
    FixtureSlot(book: '04-sgk-khoa-hoc-4', lessonNo: 4),
    FixtureSlot(book: '05-sgk-khoa-hoc-5', lessonNo: 4),
    FixtureSlot(book: '07-sgk-khoa-hoc-tu-nhien-7', lessonNo: 4),
    FixtureSlot(book: '08-sgk-khoa-hoc-tu-nhien-8', lessonNo: 19),
    FixtureSlot(book: '09-sgk-khoa-hoc-tu-nhien-9', lessonNo: 14),
    // ⭐ SAM SCALE POC 1 → 10 (Founder duyệt 2026-09-11). Chọn TẤT ĐỊNH từ 46
    // bài có VIỆC của trẻ chứng minh được: luân phiên theo môn rồi theo lớp.
    // Đây là DỮ LIỆU riêng từng bài — KHÔNG có logic riêng từng bài ở đâu cả;
    // mọi bài đi qua cùng một bộ dựng và cùng một runtime.
    //
    // ⚠ CHẤM ĐIỂM BỊ KHOÁ Ở CẢ MƯỜI BÀI. Trong 589 bài ghép CONFIDENT chỉ
    // 6 việc / 3 bài có đáp án gắn theo danh sách đánh số, và soi tay thì quá
    // nửa số ấy VẪN là đáp án của câu khác. Không đủ để nói với trẻ em sai.
    // Vòng dạy là KHÔNG CHẤM: chỉ `explain` + `next`, KHÔNG có `ask` — không
    // có bước hỏi thì không có chỗ nào để lỡ tay phán đúng/sai.
    FixtureSlot(book: '11-sgk-sinh-hoc-11', lessonNo: 2),  // POC 1→10
    FixtureSlot(book: '11-sgk-hoa-hoc-11', lessonNo: 13),  // POC 1→10
    FixtureSlot(book: '09-sgk-cong-nghe-9-trai-nghiem-nghe-nghiep-mo-dun-trong-cay-an-qua', lessonNo: 1),  // POC 1→10
    FixtureSlot(book: '10-sgk-dia-li-10', lessonNo: 5),  // POC 1→10
    FixtureSlot(book: '12-sgk-chuyen-de-hoc-tap-cong-nghe-12-lam-nghiep-thuy-san', lessonNo: 5),  // POC 1→10
    FixtureSlot(book: '10-sgk-lich-su-10', lessonNo: 9),  // POC 1→10
    FixtureSlot(book: '07-sgk-tin-hoc-7', lessonNo: 13),  // POC 1→10
    FixtureSlot(book: '11-sgk-sinh-hoc-11', lessonNo: 6),  // POC 1→10
  ];

  /// Lát cắt NGHIÊN CỨU: hiện trên Home cho mọi lớp (kèm nhãn «sách lớp N»)
  /// vì học sinh trên máy thử là lớp 6 mà sách là lớp 5 — quyết định hiển thị
  /// tạm cho vòng kiểm chứng, không phải luật sản phẩm (Lane C round 4).
  static const researchSlotKeys = {'05-sgk-lich-su-va-dia-li-5#8'};

  static bool isResearchSlot(LessonDocument d) =>
      researchSlotKeys.contains(d.slotKey);

  /// Một catalog cho cả app — nạp một lần, đọc nhiều nơi.
  static final shared = WorkspaceCatalog();

  /// `null` ⇒ `rootBundle` của app; test bơm bundle giả.
  final AssetBundle? bundle;
  final List<FixtureSlot> slots;
  final Map<String, LessonDocument> _docs = {};
  bool _loaded = false;
  Future<void>? _loading;

  bool get isLoaded => _loaded;

  Future<void> load() => _loading ??= _load();

  Future<void> _load() async {
    final b = bundle ?? rootBundle;
    for (final s in slots) {
      final doc =
          await _try(b, s.realPath, FixtureSlot.realDir) ??
          await _try(b, s.syntheticPath, FixtureSlot.syntheticDir);
      if (doc != null && doc.slotKey == s.key) _docs[s.key] = doc;
    }
    _loaded = true;
  }

  Future<LessonDocument?> _try(
    AssetBundle bundle,
    String path,
    String base,
  ) async {
    try {
      final raw = await bundle.loadString(path);
      final j = jsonDecode(raw);
      if (j is! Map) return null;
      return LessonDocument.fromJson(
        j.cast<String, Object?>(),
        assetBase: base,
      );
    } catch (_) {
      return null; // thiếu asset / JSON hỏng ⇒ không có workspace, nói thật
    }
  }

  LessonDocument? docFor(String book, int lessonNo) => _docs['$book#$lessonNo'];

  bool hasWorkspaceFor(String book) => _docs.values.any((d) => d.book == book);

  List<LessonDocument> docsForBook(String book) => [
    for (final d in _docs.values)
      if (d.book == book) d,
  ];

  Set<String> get booksWithWorkspace => {for (final d in _docs.values) d.book};
}
