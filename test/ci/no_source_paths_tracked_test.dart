/// ⛔⭐⭐ D4 — KHÔNG ĐƯỜNG DẪN NGUỒN NÀO ĐƯỢC NẰM TRONG GIT, KỂ CẢ DƯỚI DẠNG
/// SYMLINK.
///
/// `.gitignore` chặn `nguon-chi-thuc/` và `poc-out/` **có dấu `/` cuối** — mà
/// dấu ấy nói với git: «chỉ khớp THƯ MỤC». Một **symlink** cùng tên thì không
/// bị chặn. Đó không phải giả thuyết: vòng 7 · V2 dựng lại pack trong một
/// worktree bằng cách symlink nguồn về, và symlink `nguon-chi-thuc →
/// /Users/…/workizen-ai-learning-coach/nguon-chi-thuc` **đã lọt vào commit
/// `266cdff`** qua một `git add -A`.
///
/// Bản thân symlink chỉ mang một chuỗi đường dẫn — KHÔNG có nội dung SGK, nên
/// đây không phải một vụ rò bản quyền. Nhưng nó là:
///
/// 1. một đường dẫn **máy-cụ-thể** đi vào lịch sử chung;
/// 2. một cách làm **rỗng chính hàng rào** mà `.gitignore` dựng lên — lần sau
///    có thể là `poc-out` (text trích xuất SGK) hoặc một thư mục thật.
///
/// Không test nào trong repo đo được điều này: mọi cổng đều đo MÃ, không đo
/// **cái gì đang nằm trong index**. Đây là cổng ấy.
library;

import 'dart:io';

import 'package:flutter_test/flutter_test.dart';

/// Tên (đúng ở gốc repo) không bao giờ được git theo dõi — dù là thư mục,
/// tệp, hay symlink.
const _forbidden = <String>[
  'nguon-chi-thuc', // 9,8GB PDF SGK — bản quyền, xem đầu .gitignore
  'poc-out', // sản phẩm phái sinh của SGK (text, ảnh trang, chunk)
];

void main() {
  test('⛔⭐⭐ D4: không đường dẫn nguồn SGK nào được git theo dõi, kể cả symlink',
      () {
    final ls = Process.runSync('git', ['ls-files', '-s', ..._forbidden]);
    expect(ls.exitCode, 0, reason: 'git ls-files lỗi: ${ls.stderr}');
    final out = (ls.stdout as String).trim();
    expect(
      out,
      isEmpty,
      reason: 'Đường dẫn nguồn SGK đang nằm TRONG git:\n$out\n'
          'Gỡ bằng `git rm --cached <đường dẫn>` và kiểm lại .gitignore — '
          'dạng có dấu «/» cuối KHÔNG chặn symlink.',
    );
  });

  test('⭐ .gitignore chặn CẢ dạng KHÔNG-thư-mục (symlink / tệp)', () {
    // `git check-ignore` trả lời cho một ĐƯỜNG DẪN, không cần tệp tồn tại —
    // nên phép đo này không đụng vào đĩa. Một dòng chỉ có dạng «tên/» sẽ
    // TRƯỢT ở đây, và đó đúng là khuyết tật cần bắt.
    //
    // ⚠ `--no-index` cố ý: không có nó, git bỏ qua .gitignore cho đường dẫn
    // ĐANG được theo dõi — tức cổng sẽ xanh giả đúng lúc nó cần đỏ nhất.
    for (final name in _forbidden) {
      final r = Process.runSync('git', ['check-ignore', '--no-index', '-q', name]);
      expect(
        r.exitCode,
        0,
        reason: 'đường dẫn «$name» KHÔNG bị .gitignore chặn ở dạng '
            'symlink/tệp — thêm một dòng «$name» (KHÔNG có dấu «/» cuối)',
      );
    }
  });
}
