/// ⭐ Lệnh 51 §8–§10 — SINH THỜI KHOÁ BIỂU GỢI Ý, có ràng buộc và tái lập được.
///
/// ⭐⭐ ĐÂY KHÔNG PHẢI CHƯƠNG TRÌNH CỦA BỘ GD&ĐT. Kết quả là **gợi ý** để gia
/// đình sửa (§11), không phải phân phối chương trình. Không hàm nào ở đây được
/// nói ngược lại, và tầng UI phải gắn nhãn «Thời khoá biểu gợi ý».
///
/// ⭐⭐⭐ TẦN SUẤT MÔN — VÌ SAO MẶC ĐỊNH LÀ ĐỀU (đo rồi mới chọn):
/// §10 yêu cầu tìm dữ liệu tần suất THẬT trước khi dùng heuristic. Trong repo
/// hôm nay KHÔNG có trường số-tiết/tuần nào. Tín hiệu duy nhất mang hình dạng
/// tần suất là `lessonCount` của mỗi cuốn — và đo thử thì nó TỰ BÁC BỎ mình:
///
///   Lớp 6: KHTN 55 bài · Toán 43 · GDTC 24 · **Ngữ văn 6**
///
/// Ngữ văn 6 có hai tập mà chỉ 6 bài bắt được: con số ấy đo ĐỘ PHỦ OCR/gắn
/// bài, không đo tuần học của trẻ. Lấy nó làm trọng số sẽ biến một lỗ hổng
/// pipeline thành lời khẳng định rằng con học GDTC nhiều hơn Ngữ văn — sai
/// với thực tế, và sai theo kiểu trẻ không kiểm chứng được.
///
/// Nên mặc định là **đều**: mỗi môn ít nhất một tiết, phần dư chia vòng tròn.
/// Trọng số chỉ tồn tại khi người dùng KHAI RA ([subjectWeights]) — nghĩa là
/// nó luôn có nguồn là con người, không bao giờ là suy đoán của máy.
///
/// ⭐ Bất biến giữ nguyên từ WAL-96 (`timetable.dart`): MÔN TRONG TKB ≠ BÀI
/// HỌC CỤ THỂ. Hàm này sinh MÔN theo tiết, không bao giờ sinh bài, không sinh
/// tiến độ, không sinh bằng chứng (§14: TIMETABLE ENTRY != LEARNING SESSION).
library;

import 'dart:math';

import 'timetable.dart';

/// Nhãn bắt buộc cho mọi TKB do máy sinh — UI phải hiện, không được bỏ.
const String suggestedTimetableLabel = 'Thời khoá biểu gợi ý';

/// Sinh thời khoá biểu có ràng buộc từ danh sách môn CÓ THẬT của lớp.
///
/// [subjects] phải là môn đã chuẩn hoá BOOK→SUBJECT (SGK/SBT/Tập 1/Tập 2 của
/// cùng một môn là MỘT phần tử — xem `gradeSubjects`). Truyền vào danh sách
/// chưa chuẩn hoá sẽ sinh ra «Toán» hai lần như hai môn khác nhau.
///
/// Cùng [seed] + cùng đầu vào ⇒ cùng kết quả, mọi lúc, mọi máy (§9).
///
/// Ràng buộc (test giữ):
/// - Đúng `daysPerWeek * slotsPerDay` tiết.
/// - Mỗi môn xuất hiện ít nhất một lần, nếu số tiết đủ chỗ.
/// - Không lặp một môn hai lần trong CÙNG một ngày, trừ khi số tiết ép phải.
/// - Không sinh môn nào ngoài [subjects].
List<TimetableEntry> generateTimetable({
  required String learnerId,
  required List<String> subjects,
  required int seed,
  int daysPerWeek = 5,
  int slotsPerDay = 4,
  Map<String, int> subjectWeights = const {},
}) {
  if (subjects.isEmpty || daysPerWeek < 1 || slotsPerDay < 1) return const [];
  if (daysPerWeek > 7) daysPerWeek = 7;

  final rng = Random(seed);
  final total = daysPerWeek * slotsPerDay;

  // 1) Nhu cầu: mỗi môn `weight` suất (mặc định 1), rồi chia vòng tròn phần
  //    dư theo ĐÚNG thứ tự đầu vào — vòng tròn tất định, không random.
  final demand = <String>[];
  for (final s in subjects) {
    final w = (subjectWeights[s] ?? 1).clamp(1, slotsPerDay);
    for (var i = 0; i < w; i++) {
      demand.add(s);
    }
  }
  if (demand.length > total) {
    // Nhiều môn hơn số tiết: giữ mỗi môn nhiều nhất một suất, cắt phần thừa.
    // Cắt ở CUỐI danh sách môn — không random, để người dùng thấy được vì sao.
    final seen = <String>{};
    demand
      ..clear()
      ..addAll([
        for (final s in subjects)
          if (seen.add(s)) s,
      ]);
    if (demand.length > total) demand.removeRange(total, demand.length);
  }
  for (var i = 0; demand.length < total; i++) {
    demand.add(subjects[i % subjects.length]);
  }

  // 2) Xáo tất định.
  demand.shuffle(rng);

  // 3) CHIA BÀI VÒNG TRÒN: tiết thứ i về ngày (i % daysPerWeek).
  //    Quét ngày 1→N rồi «đặt vào ngày đầu tiên chưa có môn này» làm đầy ngày
  //    đầu trước, nên tới ngày cuối không còn ngày nào để tránh ⇒ ép trùng.
  //    Chia vòng tròn cho mọi ngày cùng độ đầy, rồi mới sửa va chạm.
  final perDay = <int, List<String>>{
    for (var d = 1; d <= daysPerWeek; d++) d: <String>[],
  };
  for (var i = 0; i < demand.length; i++) {
    perDay[(i % daysPerWeek) + 1]!.add(demand[i]);
  }

  // 4) SỬA VA CHẠM bằng hoán vị: một môn trùng ngày đổi chỗ với một tiết ngày
  //    khác, khi cú đổi ấy KHÔNG đẻ ra va chạm mới. Quét tất định (không
  //    random) ⇒ cùng seed vẫn cho cùng kết quả. Có trần lượt: số tiết đủ ép
  //    phải trùng (một môn, bốn tiết) thì dừng, không lặp vô hạn.
  for (var pass = 0; pass < total; pass++) {
    var fixed = false;
    for (var d = 1; d <= daysPerWeek && !fixed; d++) {
      final day = perDay[d]!;
      for (var i = 0; i < day.length && !fixed; i++) {
        // Lần đầu xuất hiện trong ngày ⇒ không phải va chạm.
        if (day.indexOf(day[i]) == i) continue;
        for (var o = 1; o <= daysPerWeek && !fixed; o++) {
          if (o == d) continue;
          final other = perDay[o]!;
          for (var j = 0; j < other.length; j++) {
            final mine = day[i], theirs = other[j];
            if (mine == theirs) continue;
            if (other.contains(mine)) continue; // đổi sang vẫn trùng ⇒ vô ích
            if (day.contains(theirs)) continue; // đổi về lại đẻ va chạm mới
            day[i] = theirs;
            other[j] = mine;
            fixed = true;
            break;
          }
        }
      }
    }
    if (!fixed) break; // không còn cú đổi nào cải thiện được ⇒ dừng
  }

  return [
    for (var d = 1; d <= daysPerWeek; d++)
      for (var p = 0; p < perDay[d]!.length; p++)
        TimetableEntry(
          learnerId: learnerId,
          weekday: d,
          period: p + 1,
          subjectId: perDay[d]![p],
        ),
  ];
}
