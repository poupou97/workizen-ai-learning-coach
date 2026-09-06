/// LANE C (round 4, Golden Slice #2) — `TimelineValidator`: KIỂM TẤT ĐỊNH câu
/// trả lời của trẻ đối chiếu với các mốc SÁCH NÊU (`TimelineSemantic` suy từ
/// `prose-dated-events-v1`).
///
/// Đây là «validator» theo nghĩa hẹp của Founder: một hàm thuần, không LLM,
/// không SGV, không ghi bằng chứng. Nó CHỈ tồn tại khi sách nêu đủ mốc và
/// mọi mốc đọc được thành năm (`TimelineValidator.forSemantic` trả về `null`
/// kèm lí do nếu không) — không có mốc thì không có validator, không bịa.
///
/// Ba phép kiểm:
/// - [checkPair]   «tên — năm» trẻ điền có khớp một mốc sách nêu không
///                 (so tên không phân biệt hoa/thường, cho phép thiếu dấu
///                 gạch ngang; năm phải nằm trong khoảng sách nêu).
/// - [checkOrder]  dãy tên trẻ xếp có đúng thứ tự thời gian theo sách không
///                 (đếm cặp ngược, chỉ ra cặp đầu tiên sai).
/// - [checkBefore] «A trước B?» — so hai mốc.
/// Kết quả là KIỂU (`TimelineCheck`) mang id block nguồn của từng mốc — UI
/// nói «sách viết …» chứ không nói «con sai».
///
/// KHÔNG tạo `ValidatedEvidence` (registry của Lane A-runtime là nơi duy nhất
/// làm việc đó); tệp này không import kho nào.
library;

import 'semantic_data.dart';
import 'timeline_date.dart';
import 'timeline_verbatim.dart';

/// Kết quả một phép kiểm — luôn kèm mốc sách để UI trích.
class TimelineCheck {
  const TimelineCheck({
    required this.ok,
    required this.reason,
    this.matched = const [],
    this.expectedOrder = const [],
    this.firstInversion,
  });

  final bool ok;

  /// Lời TẤT ĐỊNH, đọc được, nhắc chỗ trong sách — không phải lời khen/chê.
  final String reason;

  /// Các mốc sách đã khớp (theo thứ tự trẻ đưa).
  final List<DatedEvent> matched;

  /// Thứ tự đúng theo sách (khi kiểm thứ tự).
  final List<DatedEvent> expectedOrder;

  /// Cặp đầu tiên bị đảo (chỉ số trong dãy của trẻ), nếu có.
  final (int, int)? firstInversion;

  Iterable<String> get sourceBlockIds =>
      matched.map((m) => m.event.sourceBlockId).toSet();
}

class TimelineValidator {
  const TimelineValidator._(this.semantic, this.dated);

  static const id = 'timeline-order-v1';

  final TimelineSemantic semantic;

  /// Mọi mốc đều đọc được ngày (điều kiện tồn tại).
  final List<DatedEvent> dated;

  /// `null` ⇒ không có validator cho sơ đồ này; [unavailableReason] nói vì sao.
  ///
  /// Round 5 — CỔNG NGUYÊN VĂN: mốc nào có block chưa đối chiếu bản in thì
  /// không được dùng để kiểm. Validator không được đứng trên chữ có thể sai.
  static TimelineValidator? forSemantic(
    TimelineSemantic? s, {
    VerbatimIndex verbatim = VerbatimIndex.off,
  }) {
    if (unavailableReason(s, verbatim: verbatim) != null) return null;
    return TimelineValidator._(s!, dateEvents(s));
  }

  /// Các mốc còn dùng được sau cổng nguyên văn (cổng tắt ⇒ tất cả).
  static List<TimelineEvent> servableEvents(
    TimelineSemantic s, {
    VerbatimIndex verbatim = VerbatimIndex.off,
  }) => [
    for (final e in s.events)
      if (verbatim.servable(e.sourceBlockId)) e,
  ];

  static String? unavailableReason(
    TimelineSemantic? s, {
    VerbatimIndex verbatim = VerbatimIndex.off,
  }) {
    if (s == null) return 'Bài này không có dòng thời gian suy từ sách.';
    final held = s.events.length - servableEvents(s, verbatim: verbatim).length;
    if (held > 0) {
      return 'Có $held mốc chưa đối chiếu được với bản in — SAM không kiểm thứ tự.';
    }
    if (s.events.length < 2) {
      return 'Sách chỉ nêu ${s.events.length} mốc — chưa đủ để kiểm thứ tự.';
    }
    final undated = s.events.where((e) => TimelineDate.parse(e.when) == null);
    if (undated.isNotEmpty) {
      return 'Có mốc SAM chưa đọc được năm («${undated.first.when}») — không kiểm.';
    }
    return null;
  }

  /// Mốc sách xếp theo thời gian (ổn định: cùng năm ⇒ theo thứ tự sách).
  List<DatedEvent> get chronological {
    final out = [...dated];
    out.sort((a, b) {
      final c = a.date!.astronomicalStart.compareTo(b.date!.astronomicalStart);
      return c != 0 ? c : dated.indexOf(a).compareTo(dated.indexOf(b));
    });
    return out;
  }

  /// Sách nêu các mốc theo đúng thứ tự thời gian không (tự kiểm chính dữ liệu).
  bool get bookOrderIsChronological {
    for (var i = 1; i < dated.length; i++) {
      if (dated[i].date!.astronomicalStart < dated[i - 1].date!.astronomicalStart) {
        return false;
      }
    }
    return true;
  }

  static String _norm(String s) => s
      .toLowerCase()
      .replaceAll(RegExp(r'[-–—]'), ' ')
      .replaceAll(RegExp(r'[.,;:!?"«»()]'), ' ')
      .replaceAll(RegExp(r'\s+'), ' ')
      .trim();

  /// Mốc sách có tên khớp [name] (khớp cả tên, hoặc tên sách chứa tên trẻ gõ
  /// khi trẻ gõ ≥ 2 từ) — không có ⇒ `null`.
  DatedEvent? findByName(String name) {
    final n = _norm(name);
    if (n.isEmpty) return null;
    for (final d in dated) {
      if (_norm(d.event.title) == n) return d;
    }
    if (n.split(' ').length >= 2) {
      for (final d in dated) {
        if (_norm(d.event.title).contains(n) || n.contains(_norm(d.event.title))) {
          return d;
        }
      }
    }
    return null;
  }

  /// «tên — năm» trẻ điền vào ô «?» của trục thời gian.
  TimelineCheck checkPair(String name, String when) {
    final d = findByName(name);
    if (d == null) {
      return TimelineCheck(
        ok: false,
        reason: 'Sách không nêu mốc tên «$name» trong đoạn liệt kê — con xem lại tên trong sách nhé.',
      );
    }
    final given = TimelineDate.parse(when);
    if (given == null) {
      return TimelineCheck(
        ok: false,
        reason: 'SAM chưa đọc được năm «$when» — con ghi như sách, ví dụ «${d.date!.raw}».',
        matched: [d],
      );
    }
    final ok =
        given.astronomicalStart >= d.date!.astronomicalStart &&
        given.astronomicalEnd <= d.date!.astronomicalEnd;
    return TimelineCheck(
      ok: ok,
      reason: ok
          ? 'Khớp với sách: ${d.event.title} (${d.date!.raw}).'
          : 'Sách viết ${d.event.title} (${d.date!.raw}) — con so lại năm nhé.',
      matched: [d],
    );
  }

  /// Dãy tên trẻ xếp — đúng thứ tự thời gian theo sách?
  TimelineCheck checkOrder(List<String> names) {
    final found = <DatedEvent>[];
    for (final n in names) {
      final d = findByName(n);
      if (d == null) {
        return TimelineCheck(
          ok: false,
          reason: 'Sách không nêu mốc tên «$n» — con xem lại tên trong sách nhé.',
          matched: found,
          expectedOrder: chronological,
        );
      }
      found.add(d);
    }
    if (found.length < 2) {
      return TimelineCheck(
        ok: false,
        reason: 'Cần ít nhất hai mốc để xếp thứ tự.',
        matched: found,
        expectedOrder: chronological,
      );
    }
    for (var i = 0; i < found.length; i++) {
      for (var j = i + 1; j < found.length; j++) {
        if (found[j].date!.astronomicalStart < found[i].date!.astronomicalStart) {
          return TimelineCheck(
            ok: false,
            reason:
                'Theo sách, ${found[j].event.title} (${found[j].date!.raw}) diễn ra trước ${found[i].event.title} (${found[i].date!.raw}).',
            matched: found,
            expectedOrder: chronological,
            firstInversion: (i, j),
          );
        }
      }
    }
    return TimelineCheck(
      ok: true,
      reason: 'Thứ tự khớp với năm sách nêu.',
      matched: found,
      expectedOrder: chronological,
    );
  }

  /// «[a] diễn ra trước [b]?» — `null` khi thiếu tên.
  TimelineCheck checkBefore(String a, String b) {
    final da = findByName(a), db = findByName(b);
    if (da == null || db == null) {
      return TimelineCheck(
        ok: false,
        reason: 'Sách không nêu mốc tên «${da == null ? a : b}».',
        matched: [?da, ?db],
      );
    }
    final ok = da.date!.astronomicalStart <= db.date!.astronomicalStart;
    return TimelineCheck(
      ok: ok,
      reason: ok
          ? 'Đúng theo sách: ${da.event.title} (${da.date!.raw}) rồi mới tới ${db.event.title} (${db.date!.raw}).'
          : 'Theo sách, ${db.event.title} (${db.date!.raw}) diễn ra trước ${da.event.title} (${da.date!.raw}).',
      matched: [da, db],
    );
  }
}
