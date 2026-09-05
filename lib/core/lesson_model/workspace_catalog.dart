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
  static const defaultSlots = [
    FixtureSlot(book: '06-sgk-khoa-hoc-tu-nhien-6', lessonNo: 17),
  ];

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
