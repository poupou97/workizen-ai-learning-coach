/// ⭐⭐ Lệnh 59 §P2 — CHÂN DUNG PHẢI TỚI ĐƯỢC MẮT TRẺ, không chỉ tới test.
///
/// Test này sinh ra từ một phát hiện trên máy thật: chân dung Thạch Lam đã
/// xác minh xong lai lịch + quyền dùng, nằm đúng trong `PersonPortraits`, đóng
/// đúng vào APK — và KHÔNG hiện ở đâu cả. Người dùng duy nhất của kho là
/// [QuoteCard], mà thẻ ấy chỉ dựng khi `type == 'QUOTE'`; còn 21 `personId`
/// trong kho thì đều thuộc chuyện `PERSON`. Giao hai tập là RỖNG.
///
/// Nên bài học ở đây KHÔNG phải «thêm ảnh», mà là: TÀI SẢN ĐÚNG + CỔNG ĐÚNG
/// vẫn có thể ra SỐ KHÔNG nếu không ai đi hết đường bằng ngón tay.
///
/// Kho chuyện thật (`assets/pack/sam-stories.db`) KHÔNG được track, nên test
/// này tự dựng một DB nhỏ đúng lược đồ — chạy được cả trên CI.
library;

import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/stories/person_portrait.dart';
import 'package:learning_coach/core/stories/stories_store.dart';
import 'package:learning_coach/features/discovery/person_detail_screen.dart';
import 'package:sqlite3/sqlite3.dart';

/// Dựng DB tối thiểu đúng lược đồ mà [StoriesStore] đọc.
String _fixtureDb(String personId, String name) {
  final dir = Directory.systemTemp.createTempSync('sam-stories-fixture');
  addTearDown(() => dir.deleteSync(recursive: true));
  final path = '${dir.path}/stories.db';
  final db = sqlite3.open(path);
  db.execute('''
    CREATE TABLE person (personId TEXT PRIMARY KEY, canonicalName TEXT,
      birthYear INT, deathYear INT, subjects TEXT, refCount INT);
    CREATE TABLE story (id TEXT PRIMARY KEY, type TEXT, title TEXT, body TEXT,
      personId TEXT, personName TEXT, year INT, monthDay TEXT, subject TEXT,
      grade INT, status TEXT, sourceDocumentId TEXT, pagePdf INT);
  ''');
  db.execute("INSERT INTO person VALUES (?, ?, 1910, 1942, 'Ngữ văn', 1)", [
    personId,
    name,
  ]);
  db.execute(
    "INSERT INTO story VALUES ('s1','PERSON',?,'thân bài',?,?,1910,NULL,"
    "'Ngữ văn',6,'VERIFIED','06-sgk-ngu-van-6-tap-mot',74)",
    ['$name (1910–1942)', personId, name],
  );
  db.dispose();
  return path;
}

Future<void> _pump(WidgetTester t, String personId, String name) async {
  t.view.physicalSize = const Size(1080, 2400);
  t.view.devicePixelRatio = 3.0;
  addTearDown(t.view.resetPhysicalSize);
  addTearDown(t.view.resetDevicePixelRatio);
  final store = StoriesStore.open(_fixtureDb(personId, name));
  await t.pumpWidget(
    MaterialApp(
      home: PersonDetailScreen(personId: personId, stories: store),
    ),
  );
  await t.pumpAndSettle();
}

void main() {
  testWidgets(
    '⭐⭐ người CÓ chân dung đã xác minh ⇒ hiện ẢNH, không hiện chữ cái',
    (t) async {
      await _pump(t, 'p:thạch-lam', 'Thạch Lam');
      expect(
        find.byKey(PersonDetailScreen.portraitKey),
        findsOneWidget,
        reason:
            'ảnh đã xác minh mà màn hình về nhân vật vẫn vẽ chữ cái đầu ⇒ tài '
            'sản không tới được trẻ',
      );
      expect(find.byKey(PersonDetailScreen.initialAvatarKey), findsNothing);
    },
  );

  testWidgets('⭐ §P2.6 — ảnh mang LAI LỊCH RIÊNG ngay cạnh nó', (t) async {
    await _pump(t, 'p:thạch-lam', 'Thạch Lam');
    final line = t.widget<Text>(find.byKey(PersonDetailScreen.provenanceKey));
    final s = line.data!;
    // Nói ĐÚNG loại ảnh, nguồn, và quyền — ba thứ, không gộp, không làm sang.
    expect(s, contains('Ảnh tư liệu'));
    expect(s, contains('Gallica'));
    expect(s, contains('Phạm vi công cộng'));
  });

  testWidgets('⭐ người CHƯA có chân dung ⇒ chữ cái đầu, màn vẫn tử tế', (
    t,
  ) async {
    // 20/21 nhân vật đang ở nhánh này. Nó là trạng thái BÌNH THƯỜNG (§P2.7),
    // nên phải render đủ, không phải một ô trống hay một icon lỗi.
    await _pump(t, 'p:tô-hoài', 'Tô Hoài');
    expect(find.byKey(PersonDetailScreen.initialAvatarKey), findsOneWidget);
    expect(find.byKey(PersonDetailScreen.portraitKey), findsNothing);
    expect(find.byKey(PersonDetailScreen.provenanceKey), findsNothing);
    expect(find.text('Tô Hoài'), findsOneWidget);
    expect(find.textContaining('TRONG SÁCH CỦA CON'), findsOneWidget);
  });

  test('⭐⭐ cảnh báo cấu trúc: kho chân dung phải khớp personId của chuyện', () {
    // Đây chính là chỗ đã hỏng: khoá trong `verified` không khớp `personId`
    // nào mà UI thật sự tra thì ảnh im lặng biến mất. Không có DB thật ở CI
    // để đối chiếu, nên ít nhất giữ DẠNG khoá.
    for (final id in PersonPortraits.verified.keys) {
      expect(
        id.startsWith('p:'),
        isTrue,
        reason: '«$id» sai dạng personId của kho chuyện (phải là `p:...`)',
      );
    }
  });
}
