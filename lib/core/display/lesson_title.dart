/// ROUND 7 · QUYẾT ĐỊNH CỦA FOUNDER — **GIỮ NGUYÊN VĂN NGUỒN.** Một luật duy nhất.
///
/// ## Quyết định
///
/// **108 tiêu đề IN HOA nhiều từ trong pack đang phát hành được hiển thị
/// NGUYÊN VĂN như nguồn.** Không chuẩn hoá hoa/thường khi phép biến đổi có thể
/// **làm mất hoặc làm hỏng một danh từ riêng**.
///
/// Đây là **CHỐT AN TOÀN VỀ ĐỘ TRUNG THỰC, KHÔNG PHẢI UX cuối cùng.** Việc
/// chuẩn hoá có thể được nghiên cứu sau, nhưng **chỉ được BẬT khi đã CHỨNG MINH
/// giữ được danh từ riêng TRÊN MỘT QUẦN THỂ THẬT — không phải trên fixture tự
/// dựng.** Điều kiện ấy hôm nay **CHƯA đạt**, và mức chưa đạt là đo được:
/// `sentenceCaseAllCaps` làm mất chữ hoa trên **107 / 107** tiêu đề IN HOA
/// nhiều từ (duy nhất) của pack — xem `test/core/display/title_fidelity_test.dart`.
///
/// ## Vì sao, bằng chính dữ liệu đang phát hành
///
/// Ba nạn nhân, lấy nguyên văn từ `assets/pack/lesson-index-*.json`:
///
///     «ASEAN AND VIET NAM»                       → «Asean and viet nam»
///     «BÁC HÔ VỚI THIÊU NHI»                     → «Bác hô với thiêu nhi»
///     «CHIẾN TRANH VÀ HOA BÌNH TRONG THẾ KỈ XX»  → «… trong thế kỉ xx»
///
/// Một chữ viết tắt, một tên riêng, một số La Mã. **Không phép biến đổi theo
/// HÌNH DẠNG CHUỖI nào phân biệt được chúng với chữ thường**, vì tiếng Việt
/// không mã hoá «danh từ riêng» vào hình dạng của từ. Cách duy nhất chữa được
/// là **dữ liệu**: lấy tên từ mục lục in (`lesson-title-v1`) hoặc một từ điển
/// danh từ riêng có nguồn — cả hai đều nằm trước tầng hiển thị, không nằm ở đây.
///
/// ## Bài học của vòng này, viết thành luật
///
/// Luật cũ (`LessonDocument.titleCase`) chỉ từng được kiểm bằng chuỗi IN HOA —
/// **tức chỉ bằng đúng tiền đề của chính nó**. Một hàm hạ-chữ-thường luôn xanh
/// khi đầu vào vốn không có chữ thường nào để phá. **Thứ gì thay thế nó cũng
/// không được phép chỉ kiểm được bằng đầu vào chọn cho vừa nó**: bộ test đi kèm
/// nạp **quần thể tiêu đề thật** và có một test riêng canh rằng quần thể ấy thực
/// sự CHỨA những ca có thể làm luật đỏ.
///
/// Lịch sử (WS-R, vòng 7): lỗi máy thật trên Nokia 6.1 — LS&ĐL 5 Bài 8 mang
/// tiêu đề đúng chính tả «Đấu tranh giành độc lập thời kì **B**ắc thuộc» còn
/// màn hình hiện «thời kì **b**ắc thuộc». Quyết định này đóng lớp lỗi ấy ở mọi
/// hình dạng đầu vào, không chỉ ở chuỗi đã có chữ thường.
library;

/// Ranh giới «đầu chuỗi hoặc sau dấu kết câu».
final RegExp _sentenceStart = RegExp(r'(^\s*|[.!?]\s*)(\S)', unicode: true);

/// `true` khi chuỗi KHÔNG mang một chữ cái thường nào. Chuỗi rỗng / chỉ có số
/// và dấu cũng thoả. Đây là PHÉP PHÂN LOẠI để đo, không còn là điều kiện rẽ
/// nhánh của `displayTitle`.
bool isAllUpperCase(String s) => s == s.toUpperCase();

/// Số «từ có chữ cái» — dùng để tách VIẾT TẮT («GDTC 5») khỏi TIÊU ĐỀ in hoa.
int letterWordCount(String s) => s
    .split(RegExp(r'\s+'))
    .where((w) => w.runes.any((r) {
          final c = String.fromCharCode(r);
          return c.toUpperCase() != c.toLowerCase();
        }))
    .length;

/// Mọi chữ HOA của chuỗi, theo thứ tự. Bất biến mà bất kỳ phép chuẩn hoá nào
/// cũng phải giữ: **không được làm ngắn danh sách này** ở chỗ không phải đầu câu.
List<String> capitalsOf(String s) => [
      for (final c in s.split(''))
        if (c != c.toLowerCase() && c == c.toUpperCase()) c,
    ];

/// ⭐⭐ **TIÊU ĐỀ BÀI ĐỂ HIỂN THỊ — NGUYÊN VĂN NGUỒN.**
///
/// Quyết định của Founder (vòng 7): không biến đổi. Từng ký tự sách in ra là
/// từng ký tự trẻ đọc. Đây là hàm DUY NHẤT được phép dựng tiêu đề hiển thị;
/// một test soi mã canh rằng không tệp nào trong `lib/` gọi thẳng phép chuẩn hoá.
///
/// Hàm này là phép đồng nhất **có chủ ý**. Nó tồn tại (thay vì bị xoá cùng chỗ
/// gọi) vì nó là **CHỖ ĐẶT CỔNG**: khi nào điều kiện bật được chứng minh, chỉ
/// một hàm này đổi, và mọi màn hình đổi theo. Xoá nó đi là mời một luật thứ hai
/// mọc lại ở bảy chỗ khác nhau — đúng cái vòng 6 đã có.
String displayTitle(String title) => title;

/// «Bài 8 · Đấu tranh giành độc lập thời kì Bắc thuộc».
String displayLessonLabel(int lessonNo, String title) =>
    'Bài $lessonNo · ${displayTitle(title)}';

/// ⛔ **KHÔNG PHẢI ĐƯỜNG HIỂN THỊ. CHƯA ĐƯỢC BẬT.**
///
/// Phép chuẩn hoá ứng viên của vòng 3–7: hạ chuỗi IN HOA nhiều từ xuống chữ
/// thường rồi viết hoa lại đầu chuỗi và sau «.!?». Giữ lại **làm đối tượng
/// nghiên cứu và làm bằng chứng**, không phải để dùng: nó là thứ mà nghĩa vụ
/// chứng minh dưới đây đo, và hôm nay nó **trượt trên 107/107** tiêu đề thật.
///
/// **ĐIỀU KIỆN BẬT (của Founder, không phải của một lane):** chứng minh giữ
/// được danh từ riêng **trên một quần thể thật**. `titlesLosingCapitals` là
/// phép đo; `test/core/display/title_fidelity_test.dart` là chỗ chạy nó. Cho
/// tới lúc ấy, gọi hàm này từ `lib/` là một lỗi, và có test soi mã bắt.
String sentenceCaseAllCaps(String title) {
  if (!isAllUpperCase(title)) return title;
  if (letterWordCount(title) < 2) return title;
  return title.toLowerCase().replaceAllMapped(
        _sentenceStart,
        (m) => '${m[1]}${m[2]!.toUpperCase()}',
      );
}

/// ⭐ **NGHĨA VỤ CHỨNG MINH, viết thành hàm chạy được.**
///
/// Trả về những tiêu đề mà `transform` làm **ngắn đi** danh sách chữ hoa — tức
/// làm mất ít nhất một chữ hoa mà nguồn có. Một phép chuẩn hoá chỉ được đề xuất
/// bật khi hàm này trả về **rỗng trên quần thể thật**, chứ không phải trên một
/// fixture chọn sẵn.
///
/// Cố ý KHÔNG bỏ qua chữ hoa đầu câu: nếu một phép biến đổi muốn được phép hạ
/// chữ đầu câu thì nó phải nói ra điều đó và tự chứng minh, chứ không được thừa
/// hưởng một ngoại lệ đã cài sẵn trong thước đo.
List<String> titlesLosingCapitals(
  String Function(String) transform,
  Iterable<String> titles,
) =>
    [
      for (final t in titles)
        if (capitalsOf(transform(t)).length < capitalsOf(t).length) t,
    ];
