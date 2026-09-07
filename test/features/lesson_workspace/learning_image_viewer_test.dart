/// ⭐ Lệnh 59 §P0 / §P7 — viewer ảnh học tập: phóng, kéo, đóng, và KHÔNG nới
/// quyền dùng ảnh.
library;

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/lesson_workspace/learning_image_viewer.dart';

Future<void> _open(WidgetTester t, {VoidCallback? onSource}) async {
  await t.pumpWidget(
    MaterialApp(
      home: Builder(
        builder: (c) => Scaffold(
          body: Center(
            child: TextButton(
              onPressed: () => showLearningImage(
                c,
                asset: 'assets/mascot/sam-hello.png',
                aspect: 1.5,
                caption: 'Hình 17.1 · Tách chất',
                sourceLine: 'SGK KHTN 6 · trang 61',
                onOpenSource: onSource,
              ),
              child: const Text('mở'),
            ),
          ),
        ),
      ),
    ),
  );
  await t.tap(find.text('mở'));
  await t.pumpAndSettle();
}

/// Hai cú chạm phải cách nhau ĐỦ LÂU để không bị coi là một, và ĐỦ NHANH để
/// còn là double-tap (kDoubleTapMinTime … kDoubleTapTimeout).
Future<void> doubleTap(WidgetTester t) async {
  final f = find.byKey(LearningImageViewer.imageKey);
  await t.tap(f);
  await t.pump(const Duration(milliseconds: 60));
  await t.tap(f);
  await t.pumpAndSettle();
}

InteractiveViewer _iv(WidgetTester t) =>
    t.widget<InteractiveViewer>(find.byType(InteractiveViewer));

void main() {
  testWidgets('chạm ảnh ⇒ mở viewer toàn màn hình', (t) async {
    await _open(t);
    expect(find.byKey(LearningImageViewer.viewerKey), findsOneWidget);
    expect(find.byKey(LearningImageViewer.imageKey), findsOneWidget);
  });

  testWidgets('⭐ phóng và kéo được — InteractiveViewer với maxScale > 1', (
    t,
  ) async {
    await _open(t);
    final iv = _iv(t);
    expect(iv.minScale, 1);
    expect(iv.maxScale, greaterThan(1));
    expect(iv.panEnabled, isTrue);
  });

  testWidgets('⭐ chạm hai lần ⇒ phóng; chạm hai lần nữa ⇒ về như cũ', (
    t,
  ) async {
    await _open(t);
    double scale() =>
        _iv(t).transformationController!.value.getMaxScaleOnAxis();
    expect(scale(), closeTo(1, 0.001));

    await doubleTap(t);
    expect(scale(), greaterThan(1.5), reason: 'chạm hai lần không phóng');

    await doubleTap(t);
    expect(scale(), closeTo(1, 0.01), reason: 'không trở về được');
  });

  testWidgets('giữ ĐÚNG tỉ lệ ảnh, không kéo méo', (t) async {
    await _open(t);
    final ar = t.widget<AspectRatio>(
      find.descendant(
        of: find.byKey(LearningImageViewer.viewerKey),
        matching: find.byType(AspectRatio),
      ),
    );
    expect(ar.aspectRatio, 1.5);
    final img = t.widget<Image>(find.byKey(LearningImageViewer.imageKey));
    expect(img.fit, BoxFit.contain);
  });

  testWidgets('đóng được, và màn phía dưới CÒN NGUYÊN (§P0.2)', (t) async {
    await _open(t);
    await t.tap(find.byKey(LearningImageViewer.closeKey));
    await t.pumpAndSettle();
    expect(find.byKey(LearningImageViewer.viewerKey), findsNothing);
    // Màn đọc chỉ bị PHỦ, không bị dựng lại ⇒ vị trí đọc còn.
    expect(find.text('mở'), findsOneWidget);
  });

  testWidgets('back của Android cũng đóng viewer', (t) async {
    await _open(t);
    await t.binding.handlePopRoute();
    await t.pumpAndSettle();
    expect(find.byKey(LearningImageViewer.viewerKey), findsNothing);
  });

  testWidgets('⭐⭐ §P0.5 — viewer KHÔNG có tải về / chia sẻ / sao chép', (
    t,
  ) async {
    await _open(t);
    for (final banned in ['Tải', 'Chia sẻ', 'Lưu ảnh', 'Sao chép']) {
      expect(find.textContaining(banned), findsNothing, reason: banned);
    }
    for (final icon in [Icons.download, Icons.share, Icons.save_alt]) {
      expect(find.byIcon(icon), findsNothing);
    }
  });

  testWidgets('nguồn đi THEO ảnh và mở được tờ nguồn đầy đủ', (t) async {
    var opened = false;
    await _open(t, onSource: () => opened = true);
    expect(find.textContaining('SGK KHTN 6 · trang 61'), findsOneWidget);
    await t.tap(find.byKey(LearningImageViewer.sourceKey));
    await t.pumpAndSettle();
    expect(opened, isTrue);
  });

  testWidgets('thiếu tệp ảnh ⇒ nói thật, không màn đen câm', (t) async {
    await t.pumpWidget(
      const MaterialApp(
        home: LearningImageViewer(asset: 'assets/khong-co-that.png'),
      ),
    );
    await t.pumpAndSettle();
    expect(find.textContaining('chưa có ảnh'), findsOneWidget);
  });

  testWidgets('⭐ che mép crop bằng CÙNG hệ số với màn Đọc', (t) async {
    await t.pumpWidget(
      const MaterialApp(
        home: LearningImageViewer(
          asset: 'assets/mascot/sam-hello.png',
          aspect: 1.5,
          bleedScale: 1.14,
        ),
      ),
    );
    await t.pumpAndSettle();
    final tr = t.widget<Transform>(
      find
          .ancestor(
            of: find.byKey(LearningImageViewer.imageKey),
            matching: find.byType(Transform),
          )
          .first,
    );
    expect(tr.transform.getMaxScaleOnAxis(), closeTo(1.14, 0.001));
  });

  // ⭐⭐ Test trên dựng THẲNG widget, nên nó không hề đi qua `showLearningImage`
  // — và đó đúng là chỗ `bleedScale` bị rơi. Test này đi ĐÚNG đường sản phẩm:
  // chạm ảnh trong bài ⇒ helper ⇒ viewer.
  testWidgets('⭐ đi qua showLearningImage — hệ số che mép KHÔNG được rơi', (
    t,
  ) async {
    await t.pumpWidget(
      MaterialApp(
        home: Builder(
          builder: (c) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () => showLearningImage(
                  c,
                  asset: 'assets/mascot/sam-hello.png',
                  aspect: 1.5,
                  bleedScale: 1.14,
                ),
                child: const Text('mở'),
              ),
            ),
          ),
        ),
      ),
    );
    await t.tap(find.text('mở'));
    await t.pumpAndSettle();
    final tr = t.widget<Transform>(
      find
          .ancestor(
            of: find.byKey(LearningImageViewer.imageKey),
            matching: find.byType(Transform),
          )
          .first,
    );
    expect(
      tr.transform.getMaxScaleOnAxis(),
      closeTo(1.14, 0.001),
      reason: 'helper nuốt mất bleedScale ⇒ toàn màn hình lại lòi mép chữ',
    );
  });
}
