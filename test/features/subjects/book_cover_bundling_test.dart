/// WAL-167 n89 — BÌA CÓ TRÊN ĐĨA ≠ BÌA CÓ TRONG BẢN BUILD.
///
/// Máy thật (Nokia) dựng ra giá sách toàn ô chữ: 22 tấm bìa nằm đủ trong
/// `assets/pack/covers/` nhưng `pubspec.yaml` chỉ khai báo `assets/pack/`, mà
/// **khai báo thư mục của Flutter không đệ quy** ⇒ không tấm nào vào bundle.
///
/// Test này CHỦ Ý không đọc file bìa: bìa là SOURCE_ASSET, gitignore theo
/// WAL-43, nên CI không bao giờ có. Hợp đồng kiểm được ở mọi máy là
/// **«thư mục chứa bìa phải được khai báo»** — thứ nằm trong mã nguồn.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/features/subjects/lesson_index.dart';

void main() {
  test('⭐ pubspec KHAI BÁO thư mục bìa (thiếu ⇒ máy thật ra giá sách trắng)',
      () {
    final lines = File('pubspec.yaml')
        .readAsLinesSync()
        .map((l) => l.trim())
        .where((l) => l.startsWith('- '))
        .map((l) => l.substring(2).trim())
        .toSet();
    expect(lines, contains('assets/pack/${BookRef.coverDir}'),
        reason: '⭐ đột biến xoá dòng khai báo ⇒ đỏ. Khai báo `assets/pack/` '
            'KHÔNG kéo theo thư mục con — đây đúng là lỗi đã xảy ra trên Nokia.');
  });

  test('⭐ THƯ MỤC bìa phải có trong git, không chỉ có trên máy tôi', () {
    // Nội dung bìa gitignore (WAL-43) và git KHÔNG theo dõi thư mục rỗng ⇒
    // trên bản checkout sạch thư mục đã khai báo trong pubspec biến mất và
    // `flutter analyze` đỏ: asset_directory_does_not_exist. Máy tôi xanh vì
    // có sẵn 22 tấm bìa — đúng họ lỗi «test kiểm tủ đồ của một người».
    expect(File('assets/pack/${BookRef.coverDir}.gitkeep').existsSync(), isTrue,
        reason: '⭐ đột biến xoá file mốc ⇒ đỏ (CI đã đỏ đúng chỗ này).');
  });

  test('⭐ bìa NGOÀI thư mục đã khai báo ⇒ sách không lên giá (fail closed)',
      () {
    final idx = LessonIndex.fromJsonString('''
{"grade":5,"subjects":{},"toanExercises":{},"books":[
 {"sourceDocumentId":"a","subject":"Toán","title":"Toán 5",
  "cover":"covers/a.webp","lessonCount":3},
 {"sourceDocumentId":"b","subject":"Toán","title":"Toán 5 lạc chỗ",
  "cover":"bia/b.webp","lessonCount":3}]}
''')!;
    expect(idx.books.map((b) => b.sourceDocumentId), ['a'],
        reason: '⭐ đột biến bỏ kiểm tiền tố ⇒ đỏ. Cuốn "b" sẽ lên giá với một '
            'ô trống vĩnh viễn vì `bia/` không nằm trong pubspec.');
  });
}
