/// WAL-108 — kho JSONL RA ĐĨA: dữ liệu học sinh sống qua restart (S24
/// acceptance §3). Bọc [JsonlLearnerStore] (logic không đổi — một nguồn luật);
/// mỗi mutation ghi lại toàn kho (~250 KB/năm/trẻ — đo ở WAL-95, rẻ hơn mọi
/// engine); format từng dòng vẫn append-only nên lịch sử nguyên vẹn.
///
/// Ghi hỏng giữa chừng: dòng cuối vỡ JSON ⇒ [JsonlLearnerStore.fromJsonl]
/// bỏ qua dòng hỏng khi nạp — kho không sập (bất biến append-only bền).
library;

import 'dart:io';

import '../student/learning_evidence.dart';
import 'learner_profile.dart';
import 'learner_store.dart';
import 'learning_session.dart';
import 'timetable.dart';

class FileLearnerStore implements LearnerStore {
  FileLearnerStore._(this._file, this._mem);

  final File _file;
  final JsonlLearnerStore _mem;

  static Future<FileLearnerStore> open(File file) async {
    final content = await file.exists() ? await file.readAsString() : '';
    return FileLearnerStore._(file, JsonlLearnerStore.fromJsonl(content));
  }

  Future<void> _flush() async {
    await _file.parent.create(recursive: true);
    await _file.writeAsString(_mem.toJsonl(), flush: true);
  }

  @override
  Future<void> saveProfile(LearnerProfile p) async {
    await _mem.saveProfile(p);
    await _flush();
  }

  @override
  Future<void> appendSession(LearningSession s) async {
    await _mem.appendSession(s);
    await _flush();
  }

  @override
  Future<void> saveTimetable(
      String learnerId, List<TimetableEntry> entries) async {
    await _mem.saveTimetable(learnerId, entries);
    await _flush();
  }

  @override
  Future<List<LearnerProfile>> profiles({String? guardianId}) =>
      _mem.profiles(guardianId: guardianId);

  @override
  Future<LearnerProfile?> profile(String learnerId) => _mem.profile(learnerId);

  @override
  Future<List<LearningSession>> sessions({
    required String learnerId,
    DateTime? onDay,
    String? subjectId,
    String? skillCaseId,
  }) =>
      _mem.sessions(
          learnerId: learnerId,
          onDay: onDay,
          subjectId: subjectId,
          skillCaseId: skillCaseId);

  @override
  Future<List<TimetableEntry>> timetable(String learnerId) =>
      _mem.timetable(learnerId);

  @override
  Future<String> exportLearner(String learnerId) =>
      _mem.exportLearner(learnerId);

  /// Xoá rồi PHẢI ghi đè tệp ngay: nếu chỉ xoá trong bộ nhớ, dữ liệu vẫn nằm
  /// trên đĩa và lần mở sau nó sống lại — «đã xoá» hoá ra là nói dối.
  @override
  Future<int> deleteLearner(String learnerId) async {
    final n = await _mem.deleteLearner(learnerId);
    await _flush();
    return n;
  }

  @override
  Future<void> saveParentPin(String pin) async {
    await _mem.saveParentPin(pin);
    await _flush();
  }

  @override
  Future<String?> parentPin() => _mem.parentPin();

  @override
  Future<void> saveActiveLearner(String learnerId) async {
    await _mem.saveActiveLearner(learnerId);
    await _flush();
  }

  @override
  Future<String?> activeLearnerId() => _mem.activeLearnerId();

  @override
  Future<EvidenceLog> evidenceFor(
          {required String learnerId, required String skillCaseId}) =>
      _mem.evidenceFor(learnerId: learnerId, skillCaseId: skillCaseId);
}
