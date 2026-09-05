/// ROUND 3 B5 — hai lỗi «nhìn thấy trước khi vào app»:
/// - khung TRẮNG lúc khởi động (audit O1) ⇒ màn khởi động có nhãn hiệu;
/// - hộp thoại hệ thống gọi app là «learning_coach» (audit §1) ⇒ nhãn Android
///   là tên sản phẩm. Test đọc thẳng manifest — đổi lại là đỏ.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/app/boot_screen.dart';

void main() {
  testWidgets('BootScreen: nhãn hiệu + dòng «đang mở», không %/spinner', (
    t,
  ) async {
    await t.pumpWidget(
      const MaterialApp(home: BootScreen(note: 'Đang mở hồ sơ của con…')),
    );
    expect(find.byKey(BootScreen.key_), findsOneWidget);
    expect(find.text('Học cùng SAM'), findsOneWidget);
    expect(find.text('Đang mở hồ sơ của con…'), findsOneWidget);
    expect(find.byType(CircularProgressIndicator), findsNothing);
    for (final w in t.widgetList<Text>(find.byType(Text))) {
      expect(w.data ?? '', isNot(contains('%')));
    }
  });

  test('main.dart không còn khung trắng lúc chờ; dùng BootScreen', () {
    final src = File('lib/main.dart').readAsStringSync();
    expect(src, isNot(contains('Scaffold(body: SizedBox.shrink())')));
    expect(src, contains('BootScreen('));
  });

  test('AndroidManifest: nhãn app là tên sản phẩm, không phải tên gói', () {
    final xml = File(
      'android/app/src/main/AndroidManifest.xml',
    ).readAsStringSync();
    expect(xml, contains('android:label="Học cùng SAM"'));
    expect(xml, isNot(contains('android:label="learning_coach"')));
  });
}
