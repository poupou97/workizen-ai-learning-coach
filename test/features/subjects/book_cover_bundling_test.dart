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
