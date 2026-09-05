/// TRACK B — TRACE của phiên: «con đã mở bài/View nào» — TRONG BỘ NHỚ,
/// không kho, không sự kiện học.
///
/// ⭐ TRACE ≠ EVIDENCE (WAL-175/178): «Đã xem» chỉ nói trẻ đã MỞ, không nói
/// trẻ đã hiểu. Không ghi ra đĩa, mất khi tắt app — cố ý: một lát cắt
/// prototype không có quyền để lại dấu vết trong hồ sơ học của trẻ.
library;

import 'package:flutter/foundation.dart';

import '../../core/lesson_model/next_action.dart';

class WorkspaceTrace extends ChangeNotifier {
  WorkspaceTrace();

  /// Một trace cho cả phiên app (không persist).
  static final session = WorkspaceTrace();

  final Map<String, Set<WorkspaceView>> _views = {};
  final Set<String> _opened = {};

  bool opened(String slotKey) => _opened.contains(slotKey);
  Set<WorkspaceView> viewsFor(String slotKey) =>
      Set.unmodifiable(_views[slotKey] ?? const <WorkspaceView>{});

  void markOpened(String slotKey) {
    if (_opened.add(slotKey)) notifyListeners();
  }

  void markView(String slotKey, WorkspaceView view) {
    _opened.add(slotKey);
    final s = _views.putIfAbsent(slotKey, () => {});
    if (s.add(view)) notifyListeners();
  }

  /// Nhãn trẻ đọc — chỉ nói về việc MỞ, không nói về việc HỌC.
  String childLabel(String slotKey) =>
      opened(slotKey) ? 'Đã xem (phiên này)' : 'Chưa xem';

  @visibleForTesting
  void reset() {
    _views.clear();
    _opened.clear();
    notifyListeners();
  }
}
