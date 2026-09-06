/// ⭐ Lệnh 52 — IA CẤP 1: năm tab, thứ tự Founder đã chốt.
///
///   Trang chủ · Giá sách · SAM · Thành tích · Thêm
///
/// SAM nằm CHÍNH GIỮA (chỉ số 2) — điểm vào AI Tutor. Vị trí này là quyết định
/// sản phẩm đã chốt (§13), nên nó được khoá bằng hằng + test, không phải bằng
/// thứ tự tình cờ của một danh sách.
///
/// ⭐⭐ VÌ SAO `IndexedStack` chứ không phải dựng lại màn mỗi lần đổi tab:
/// §2 đòi «giữ state của từng tab» và «không reload màn hình vô lý». IndexedStack
/// giữ nguyên cây widget của cả năm tab, nên cuộn tới đâu, lọc gì, gõ dở gì —
/// đổi tab đi rồi quay lại vẫn còn.
///
/// ⭐⭐⭐ THANH NAV BIẾN MẤT KHI NÀO (§8): mọi màn mở bằng `Navigator.push` của
/// app đều phủ toàn màn hình, nên thanh tab tự ẩn ở camera, quiz, Learning View
/// — và tự hiện lại khi back. Đây là **hệ quả của kiến trúc hiện tại** (app
/// đẩy route ở navigator gốc), không phải luật riêng của tab.
///
/// Đánh đổi đã biết, ghi ra để Founder chốt sau: màn CHI TIẾT không-immersive
/// cũng ẩn thanh tab. Muốn giữ thanh ở màn chi tiết thì phải cho mỗi tab một
/// `Navigator` riêng VÀ đổi các flow immersive sang đẩy ở navigator gốc — delta
/// rộng hơn nhiều và đụng vào mọi flow đang chạy. Lệnh 52 ưu tiên «minimal
/// delta → production-safe», nên bản này chọn đường ít phá nhất.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';

class AppShell extends StatefulWidget {
  const AppShell({
    super.key,
    required this.home,
    required this.bookshelf,
    required this.sam,
    required this.achievements,
    required this.more,
    this.initialIndex = homeTab,
  });

  final Widget home;
  final Widget bookshelf;
  final Widget sam;
  final Widget achievements;
  final Widget more;
  final int initialIndex;

  /// ⭐ Thứ tự Founder chốt (§13) — SAM ở GIỮA. Test khoá các hằng này.
  static const int homeTab = 0;
  static const int bookshelfTab = 1;
  static const int samTab = 2;
  static const int achievementsTab = 3;
  static const int moreTab = 4;

  static const List<String> tabLabels = [
    'Trang chủ',
    'Giá sách',
    'SAM',
    'Thành tích',
    'Thêm',
  ];

  static Key tabKey(int i) => Key('app-shell-tab-$i');

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  late int _index = widget.initialIndex;

  List<Widget> get _tabs => [
    widget.home,
    widget.bookshelf,
    widget.sam,
    widget.achievements,
    widget.more,
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: WalColors.surface,
      // IndexedStack giữ state cả năm tab (§2).
      body: IndexedStack(index: _index, children: _tabs),
      bottomNavigationBar: _bar(),
    );
  }

  /// Material 3 `NavigationBar`: đã lo sẵn safe area (gesture nav VÀ 3 nút),
  /// vùng chạm, trạng thái chọn, và quy ước điều hướng của nền tảng — §10 cấm
  /// tự chế lại Design System, nên ta dùng component chuẩn và chỉ thay icon.
  Widget _bar() => NavigationBarTheme(
    data: NavigationBarThemeData(
      backgroundColor: Colors.white,
      indicatorColor: WalColors.surfaceLavender,
      labelTextStyle: WidgetStateProperty.resolveWith(
        (states) => TextStyle(
          fontSize: 12,
          fontWeight: states.contains(WidgetState.selected)
              ? FontWeight.w700
              : FontWeight.w500,
          color: states.contains(WidgetState.selected)
              ? WalColors.primaryText
              : WalColors.inkSoft,
        ),
      ),
    ),
    child: NavigationBar(
      selectedIndex: _index,
      height: 68,
      // Nhãn luôn hiện: tiếng Việt có dấu, chỉ icon thì trẻ đoán sai.
      labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
      onDestinationSelected: (i) => setState(() => _index = i),
      destinations: [
        _dest(AppShell.homeTab, Icons.home_outlined, Icons.home),
        _dest(AppShell.bookshelfTab, Icons.menu_book_outlined, Icons.menu_book),
        _samDest(),
        _dest(
          AppShell.achievementsTab,
          Icons.emoji_events_outlined,
          Icons.emoji_events,
        ),
        _dest(AppShell.moreTab, Icons.menu, Icons.menu),
      ],
    ),
  );

  NavigationDestination _dest(int i, IconData icon, IconData selected) =>
      NavigationDestination(
        key: AppShell.tabKey(i),
        icon: Icon(icon, size: 26, color: WalColors.inkSoft),
        selectedIcon: Icon(selected, size: 26, color: WalColors.primary500),
        label: AppShell.tabLabels[i],
      );

  /// SAM: to hơn MỘT CHÚT và có mặt mascot — nổi bật vừa đủ, KHÔNG thành nút
  /// nổi khổng lồ, KHÔNG phá chiều cao thanh nav (§2).
  NavigationDestination _samDest() => NavigationDestination(
    key: AppShell.tabKey(AppShell.samTab),
    icon: _samIcon(selected: false),
    selectedIcon: _samIcon(selected: true),
    label: AppShell.tabLabels[AppShell.samTab],
  );

  Widget _samIcon({required bool selected}) => SizedBox(
    width: 34,
    height: 34,
    child: ClipOval(
      child: Image.asset(
        'assets/mascot/sam-hello@64.png',
        width: 34,
        height: 34,
        fit: BoxFit.cover,
        // Thiếu asset ⇒ icon thường, không phải ô vỡ.
        errorBuilder: (_, _, _) => Icon(
          selected ? Icons.school : Icons.school_outlined,
          size: 26,
          color: selected ? WalColors.primary500 : WalColors.inkSoft,
        ),
      ),
    ),
  );
}
