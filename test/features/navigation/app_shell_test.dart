/// ⭐ Lệnh 52 — IA cấp 1: năm tab, thứ tự Founder ĐÃ CHỐT (§13).
///
/// Thứ tự tab là một quyết định sản phẩm, không phải chi tiết bố cục. Nên nó
/// được khoá bằng test: đổi thứ tự hay đẩy SAM khỏi giữa ⇒ đỏ ngay.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/navigation/app_shell.dart';

Widget _page(String label) => Scaffold(body: Center(child: Text(label)));

Future<void> _pump(WidgetTester t, {int initial = 0}) async {
  await t.pumpWidget(
    MaterialApp(
      home: AppShell(
        initialIndex: initial,
        home: _page('NỘI DUNG TRANG CHỦ'),
        bookshelf: _page('NỘI DUNG GIÁ SÁCH'),
        sam: _page('NỘI DUNG SAM'),
        achievements: _page('NỘI DUNG THÀNH TÍCH'),
        more: _page('NỘI DUNG THÊM'),
      ),
    ),
  );
  await t.pumpAndSettle();
}

NavigationBar _bar(WidgetTester t) =>
    t.widget<NavigationBar>(find.byType(NavigationBar));

void main() {
  group('§13 — thứ tự tab đã chốt', () {
    test('SAM ở CHÍNH GIỮA, và thứ tự đúng như Founder chốt', () {
      expect(AppShell.tabLabels, [
        'Trang chủ',
        'Giá sách',
        'SAM',
        'Thành tích',
        'Thêm',
      ]);
      expect(AppShell.samTab, 2, reason: 'SAM phải nằm chính giữa');
      expect(AppShell.tabLabels.length, 5);
      // Giữa của 5 phần tử là chỉ số 2 — viết ra để đổi số tab cũng phải
      // nghĩ lại chỗ đứng của SAM.
      expect(AppShell.samTab, AppShell.tabLabels.length ~/ 2);
    });

    testWidgets('cả năm nhãn hiện trên thanh, đúng thứ tự trái→phải', (
      t,
    ) async {
      await _pump(t);
      for (final label in AppShell.tabLabels) {
        expect(find.text(label), findsOneWidget, reason: 'thiếu nhãn «$label»');
      }
      final xs = [
        for (final label in AppShell.tabLabels)
          t.getCenter(find.text(label)).dx,
      ];
      final sorted = [...xs]..sort();
      expect(xs, sorted, reason: 'thứ tự tab trên màn không đúng');
    });
  });

  group('§11 A/B — mở app và chuyển tab', () {
    testWidgets('A. mở app ⇒ tab Trang chủ được chọn', (t) async {
      await _pump(t);
      expect(_bar(t).selectedIndex, AppShell.homeTab);
      expect(find.text('NỘI DUNG TRANG CHỦ'), findsOneWidget);
    });

    testWidgets('B. chạm lần lượt cả năm tab ⇒ không crash, đúng nội dung', (
      t,
    ) async {
      await _pump(t);
      const expected = [
        'NỘI DUNG TRANG CHỦ',
        'NỘI DUNG GIÁ SÁCH',
        'NỘI DUNG SAM',
        'NỘI DUNG THÀNH TÍCH',
        'NỘI DUNG THÊM',
      ];
      for (var i = 0; i < 5; i++) {
        await t.tap(find.byKey(AppShell.tabKey(i)));
        await t.pumpAndSettle();
        expect(_bar(t).selectedIndex, i);
        expect(find.text(expected[i]), findsOneWidget);
      }
      // Quay lại Trang chủ vẫn được.
      await t.tap(find.byKey(AppShell.tabKey(AppShell.homeTab)));
      await t.pumpAndSettle();
      expect(_bar(t).selectedIndex, AppShell.homeTab);
    });
  });

  group('§2 — thanh nav bền, state từng tab được giữ', () {
    testWidgets('thanh nav còn nguyên ở CẢ năm tab', (t) async {
      await _pump(t);
      for (var i = 0; i < 5; i++) {
        await t.tap(find.byKey(AppShell.tabKey(i)));
        await t.pumpAndSettle();
        expect(
          find.byType(NavigationBar),
          findsOneWidget,
          reason: 'thanh nav biến mất ở tab $i',
        );
      }
    });

    testWidgets('⭐ đổi tab KHÔNG dựng lại màn — state của tab còn nguyên', (
      t,
    ) async {
      var homeBuilds = 0;
      await t.pumpWidget(
        MaterialApp(
          home: AppShell(
            home: Builder(
              builder: (_) {
                homeBuilds++;
                return _page('NỘI DUNG TRANG CHỦ');
              },
            ),
            bookshelf: _page('NỘI DUNG GIÁ SÁCH'),
            sam: _page('NỘI DUNG SAM'),
            achievements: _page('NỘI DUNG THÀNH TÍCH'),
            more: _page('NỘI DUNG THÊM'),
          ),
        ),
      );
      await t.pumpAndSettle();
      final afterFirst = homeBuilds;

      await t.tap(find.byKey(AppShell.tabKey(AppShell.moreTab)));
      await t.pumpAndSettle();
      await t.tap(find.byKey(AppShell.tabKey(AppShell.homeTab)));
      await t.pumpAndSettle();

      expect(
        homeBuilds,
        afterFirst,
        reason: 'Trang chủ bị dựng lại khi quay về ⇒ mất state (§2)',
      );
    });
  });

  group('§8 — route đẩy lên phủ thanh nav, back thì thanh trở lại', () {
    testWidgets('mở màn toàn màn hình ⇒ ẩn nav; back ⇒ nav trở lại', (t) async {
      await t.pumpWidget(
        MaterialApp(
          home: AppShell(
            home: Builder(
              builder: (ctx) => Scaffold(
                body: Center(
                  child: TextButton(
                    onPressed: () => Navigator.of(ctx).push(
                      MaterialPageRoute(
                        builder: (_) => _page('MÀN TOÀN MÀN HÌNH'),
                      ),
                    ),
                    child: const Text('MỞ'),
                  ),
                ),
              ),
            ),
            bookshelf: _page('b'),
            sam: _page('s'),
            achievements: _page('t'),
            more: _page('m'),
          ),
        ),
      );
      await t.pumpAndSettle();
      expect(find.byType(NavigationBar), findsOneWidget);

      await t.tap(find.text('MỞ'));
      await t.pumpAndSettle();
      expect(find.text('MÀN TOÀN MÀN HÌNH'), findsOneWidget);
      expect(
        find.byType(NavigationBar),
        findsNothing,
        reason: 'flow toàn màn hình phải phủ thanh nav (§8)',
      );

      // Nút BACK của Android (§11 C), không phải mũi tên trên AppBar — màn
      // đẩy lên trong app này không phải màn nào cũng có AppBar.
      await t.binding.handlePopRoute();
      await t.pumpAndSettle();
      expect(
        find.byType(NavigationBar),
        findsOneWidget,
        reason: 'back xong thanh nav phải trở lại (§8)',
      );
    });
  });

  group('§10 — vùng chạm và nhãn tiếng Việt', () {
    testWidgets('nhãn tiếng Việt có dấu KHÔNG bị cắt, luôn hiện', (t) async {
      await _pump(t);
      expect(
        _bar(t).labelBehavior,
        NavigationDestinationLabelBehavior.alwaysShow,
      );
      for (final label in AppShell.tabLabels) {
        final w = t.widget<Text>(find.text(label));
        expect(
          w.overflow,
          isNot(TextOverflow.ellipsis),
          reason: '«$label» bị cắt',
        );
      }
    });

    testWidgets('máy hẹp 320dp vẫn vẽ đủ năm tab, không tràn', (t) async {
      t.view.physicalSize = const Size(320 * 3, 640 * 3);
      t.view.devicePixelRatio = 3.0;
      addTearDown(t.view.resetPhysicalSize);
      addTearDown(t.view.resetDevicePixelRatio);
      // `pumpAndSettle` trong `_pump` đã NÉM nếu có overflow — không cần
      // (và không được) thêm một expect luôn đúng để trông như có kiểm.
      await _pump(t);
      for (final label in AppShell.tabLabels) {
        expect(find.text(label), findsOneWidget);
      }
    });
  });
}
