/// WAL-95 — kho dữ liệu học sinh, LOCAL-FIRST (ADR-006).
///
/// ⭐ Quyết định lưu trữ (có lý do, đo được):
/// - **Knowledge Pack = SQLite** (đọc nhiều, lớn, index — WAL-83 đã đo).
/// - **Dữ liệu học sinh = JSONL append-only** (kho này): bằng chứng vốn đã là
///   append-only + replay được (ADR-004); một dòng một sự kiện là dạng lưu tự
///   nhiên của chính mô hình đó, không cần engine DB. Cỡ: ~250 B/sự kiện ⇒
///   một năm học ~1.000 sự kiện ≈ 250 KB/trẻ.
/// Hai kho tách nhau còn vì QUYỀN RIÊNG TƯ: pack có thể chia sẻ/tải lại; dữ
/// liệu trẻ thì không bao giờ (Task Order §8).
///
/// Tầng này thuần Dart, KHÔNG dep native ⇒ test chạy được ở mọi nơi; đổi engine
/// sau không đụng schema (schema là thứ đắt nhất để đổi muộn).
library;

import 'dart:convert';

import '../student/learning_evidence.dart';
import '../student/mastery.dart';
import 'learner_profile.dart';
import 'learning_session.dart';
import 'timetable.dart';

/// Cổng lưu trữ. Ứng dụng nói chuyện với interface này, không với tệp.
abstract class LearnerStore {
  Future<void> saveProfile(LearnerProfile p);
  Future<List<LearnerProfile>> profiles({String? guardianId});
  Future<LearnerProfile?> profile(String learnerId);

  /// Append-only: một phiên ghi MỘT LẦN (§6 — không nhân bản cho view).
  Future<void> appendSession(LearningSession s);

  /// Truy vấn = PHÉP CHIẾU trên cùng một kho.
  Future<List<LearningSession>> sessions({
    required String learnerId,
    DateTime? onDay, // view NGÀY
    String? subjectId, // view MÔN
    String? skillCaseId, // view TRI THỨC
  });

  /// Toàn bộ sự kiện của MỘT ca — nguyên liệu replay (ADR-004).
  Future<EvidenceLog> evidenceFor(
      {required String learnerId, required String skillCaseId});

  /// Thời khoá biểu — TUỲ CHỌN (F13): rỗng là trạng thái hợp lệ, app chạy
  /// bình thường khi không có.
  Future<void> saveTimetable(String learnerId, List<TimetableEntry> entries);
  Future<List<TimetableEntry>> timetable(String learnerId);
}

/// Bản triển khai trên bộ nhớ + chuỗi JSONL — đủ cho app một máy, và là
/// đúng thứ ghi ra tệp khi tới lượt platform (một dòng một bản ghi).
class JsonlLearnerStore implements LearnerStore {
  JsonlLearnerStore();

  final List<String> _lines = [];

  /// Nạp từ nội dung JSONL đã lưu (khởi động app).
  factory JsonlLearnerStore.fromJsonl(String content) {
    final s = JsonlLearnerStore();
    for (final line in const LineSplitter().convert(content)) {
      if (line.trim().isNotEmpty) s._lines.add(line);
    }
    return s;
  }

  /// Nội dung để ghi ra đĩa. Append-only: chỉ thêm dòng, không sửa dòng cũ.
  String toJsonl() => _lines.join('\n');

  Iterable<Map<String, Object?>> _records(String type) sync* {
    for (final l in _lines) {
      final Object? j;
      try {
        j = jsonDecode(l);
      } catch (_) {
        continue; // dòng hỏng ⇒ bỏ QUA, không làm sập kho (append-only bền)
      }
      if (j is Map && j['type'] == type) yield j.cast<String, Object?>();
    }
  }

  @override
  Future<void> saveProfile(LearnerProfile p) async {
    // Ghi đè logic = bản ghi MỚI cùng learnerId; bản cuối thắng. Lịch sử đổi
    // lớp vì thế còn nguyên — đúng tinh thần append-only.
    _lines.add(jsonEncode({'type': 'profile', ...p.toJson()}));
  }

  @override
  Future<List<LearnerProfile>> profiles({String? guardianId}) async {
    final latest = <String, LearnerProfile>{};
    for (final r in _records('profile')) {
      final p = LearnerProfile.fromJson(r);
      if (p != null) latest[p.learnerId] = p; // bản sau đè bản trước
    }
    final all = latest.values.toList()
      ..sort((a, b) => a.learnerId.compareTo(b.learnerId));
    if (guardianId == null) return all;
    return [for (final p in all) if (p.guardianId == guardianId) p];
  }

  @override
  Future<LearnerProfile?> profile(String learnerId) async {
    final all = await profiles();
    for (final p in all) {
      if (p.learnerId == learnerId) return p;
    }
    return null;
  }

  @override
  Future<void> appendSession(LearningSession s) async {
    _lines.add(jsonEncode({'type': 'session', ...s.toJson()}));
  }

  @override
  Future<List<LearningSession>> sessions({
    required String learnerId,
    DateTime? onDay,
    String? subjectId,
    String? skillCaseId,
  }) async {
    final out = <LearningSession>[];
    for (final r in _records('session')) {
      final s = LearningSession.fromJson(r);
      if (s == null || s.learnerId != learnerId) continue;
      if (subjectId != null && s.subjectId != subjectId) continue;
      if (onDay != null &&
          !(s.startedAt.year == onDay.year &&
              s.startedAt.month == onDay.month &&
              s.startedAt.day == onDay.day)) {
        continue;
      }
      if (skillCaseId != null &&
          !s.skillCaseIds.contains(skillCaseId) &&
          !s.events.any((e) => e.skillCaseId == skillCaseId)) {
        continue;
      }
      out.add(s);
    }
    out.sort((a, b) => a.startedAt.compareTo(b.startedAt));
    return out;
  }

  @override
  Future<void> saveTimetable(
      String learnerId, List<TimetableEntry> entries) async {
    // Ghi cả tuần thành MỘT bản ghi: bản sau đè bản trước (append-only vẫn
    // giữ lịch sử đổi TKB, hữu ích khi trường đổi lịch giữa kỳ).
    _lines.add(jsonEncode({
      'type': 'timetable',
      'learnerId': learnerId,
      'entries': [for (final e in entries) e.toJson()],
    }));
  }

  @override
  Future<List<TimetableEntry>> timetable(String learnerId) async {
    List<TimetableEntry>? latest;
    for (final r in _records('timetable')) {
      if (r['learnerId'] != learnerId) continue;
      latest = [
        for (final e in (r['entries'] as List? ?? const []))
          ?TimetableEntry.fromJson((e as Map).cast<String, Object?>())
      ];
    }
    return latest ?? const [];
  }

  @override
  Future<EvidenceLog> evidenceFor(
      {required String learnerId, required String skillCaseId}) async {
    final ss = await sessions(learnerId: learnerId, skillCaseId: skillCaseId);
    var log = EvidenceLog.empty(skillCaseId);
    final events = [
      for (final s in ss)
        for (final e in s.events)
          if (e.skillCaseId == skillCaseId) e
    ]..sort((a, b) => a.at.compareTo(b.at));
    for (final e in events) {
      log = log.append(e);
    }
    return log;
  }
}

/// Tiện ích đọc: mức hỗ trợ CAO NHẤT đã dùng trong một phiên — cần cho phát
/// ngôn trung thực («lần này có gợi ý…») sau khi nạp lại từ đĩa.
SupportLevel maxSupportIn(LearningSession s) {
  var m = SupportLevel.none;
  for (final e in s.events) {
    final sup = e.support;
    if (sup != null && sup.index > m.index) m = sup;
  }
  return m;
}
