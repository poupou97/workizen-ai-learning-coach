/// WAL-151 KS-D — StoriesStore: đọc sam-stories.db (SQLite+FTS5, CHỈ chứa
/// VERIFIED — cổng §28 nằm ở build; runtime vẫn kiểm phòng thủ).
///
/// Local-first: db từ asset copy ra documents rồi mở (pattern pack WAL-84).
/// Fail-closed: thiếu db ⇒ store rỗng — UI nói thật, không bịa nội dung.
library;

import 'package:sqlite3/sqlite3.dart';

import 'story_state.dart';

class StoryItem {
  const StoryItem({
    required this.id,
    required this.type,
    required this.title,
    required this.body,
    required this.subject,
    required this.grade,
    required this.status,
    required this.sourceDocumentId,
    required this.pagePdf,
    this.personId,
    this.personName,
    this.year,
    this.monthDay,
  });

  final String id;
  final String type;
  final String title;

  /// SOURCE FACT nguyên gốc từ sách (textEvidence) — không phải lời SAM.
  final String body;
  final String subject;
  final int grade;
  final StoryStatus status;
  final String sourceDocumentId;
  final int pagePdf;
  final String? personId;
  final String? personName;
  final int? year;
  final String? monthDay;

  /// «Nguồn: sách · trang N» — mọi item trace được về nguồn (§34).
  String get sourceLine =>
      'Nguồn: $sourceDocumentId · trang $pagePdf';
}

class StoriesStore {
  StoriesStore._(this._db);
  final Database? _db;

  /// Mở từ FILE đã nằm trên đĩa (caller lo copy asset). Lỗi ⇒ store rỗng.
  static StoriesStore open(String path) {
    try {
      final db = sqlite3.open(path);
      db.select('SELECT COUNT(*) FROM story'); // sanity
      return StoriesStore._(db);
    } catch (_) {
      return const StoriesStore._empty();
    }
  }

  const StoriesStore._empty() : _db = null;

  bool get isEmpty => _db == null;

  StoryItem _row(Row r) => StoryItem(
        id: r['id'] as String,
        type: r['type'] as String,
        title: r['title'] as String,
        body: r['body'] as String,
        subject: r['subject'] as String,
        grade: r['grade'] as int,
        status: storyStatusFrom(r['status'] as String),
        sourceDocumentId: r['sourceDocumentId'] as String,
        pagePdf: r['pagePdf'] as int,
        personId: r['personId'] as String?,
        personName: r['personName'] as String?,
        year: r['year'] as int?,
        monthDay: r['monthDay'] as String?,
      );

  /// Phòng thủ hai lớp: pack chỉ chứa VERIFIED, nhưng runtime vẫn lọc —
  /// một pack build sai không được phép lộ nội dung chưa duyệt.
  List<StoryItem> _guarded(Iterable<StoryItem> xs) =>
      [for (final x in xs) if (canShowInProduction(x.status)) x];

  List<StoryItem> search(String query, {int limit = 20}) {
    final db = _db;
    if (db == null || query.trim().isEmpty) return const [];
    final rows = db.select(
        'SELECT s.* FROM story_fts f JOIN story s ON s.rowid=f.rowid '
        'WHERE story_fts MATCH ? LIMIT ?',
        ['"${query.replaceAll('"', '')}"', limit]);
    return _guarded(rows.map(_row));
  }

  /// «Ngày này năm xưa» — CHỈ event VERIFIED có monthDay khớp hôm nay (§14).
  List<StoryItem> todayEvents(DateTime today) {
    final db = _db;
    if (db == null) return const [];
    final md = '${today.month.toString().padLeft(2, '0')}-'
        '${today.day.toString().padLeft(2, '0')}';
    final rows = db.select(
        "SELECT * FROM story WHERE type='EVENT' AND monthDay=?", [md]);
    return _guarded(rows.map(_row))
        .where((e) => todayCardEligible(
            status: e.status, hasReliableMonthDay: e.monthDay != null))
        .toList();
  }

  /// Quote cho loading — VERIFIED + đủ ngắn (§15).
  List<StoryItem> loadingQuotes({int maxChars = 160}) {
    final db = _db;
    if (db == null) return const [];
    final rows = db.select(
        "SELECT * FROM story WHERE type='QUOTE' AND length(title)<=?",
        [maxChars + 4]);
    return _guarded(rows.map(_row));
  }

  List<StoryItem> byType(String type, {int limit = 50}) {
    final db = _db;
    if (db == null) return const [];
    return _guarded(db
        .select('SELECT * FROM story WHERE type=? LIMIT ?', [type, limit])
        .map(_row));
  }

  List<StoryItem> byPerson(String personId) {
    final db = _db;
    if (db == null) return const [];
    return _guarded(db
        .select('SELECT * FROM story WHERE personId=?', [personId])
        .map(_row));
  }

  ({String name, int? birthYear, int? deathYear, List<String> subjects})?
      person(String personId) {
    final db = _db;
    if (db == null) return null;
    final rows =
        db.select('SELECT * FROM person WHERE personId=?', [personId]);
    if (rows.isEmpty) return null;
    final r = rows.first;
    return (
      name: r['canonicalName'] as String,
      birthYear: r['birthYear'] as int?,
      deathYear: r['deathYear'] as int?,
      subjects: (r['subjects'] as String).split(','),
    );
  }
}
