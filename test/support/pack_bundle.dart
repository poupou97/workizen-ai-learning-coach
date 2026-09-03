/// Bundle giả cho mọi test đụng `assets/pack/`.
///
/// WAL-163 rồi WAL-133 slice 2 đều vấp CÙNG một lỗi: widget test dựng màn có
/// `Image.asset('assets/pack/…')` thì ở máy dev nó tải được (file crop có
/// sẵn), còn ở CI và mọi máy khác thì không — vì `assets/pack/` gitignore theo
/// WAL-43. Test hoá ra đang đo TỦ ĐỒ của một người.
///
/// Dùng [packHost] để test chạy y hệt nhau ở mọi máy. Muốn kiểm nhánh
/// THIẾU ảnh thì dùng [missingPackHost] — thiếu là một trạng thái sản phẩm
/// phải kiểm CÓ CHỦ Ý, không phải thứ tuỳ môi trường.
library;

import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show CachingAssetBundle, rootBundle;

final _onePx = base64Decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhf'
    'DwAChwGA60e6kgAAAABJRU5ErkJggg==');

class _PackStub extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async => key.startsWith('assets/pack/')
      ? ByteData.view(Uint8List.fromList(_onePx).buffer)
      : rootBundle.load(key);
}

class _PackMissing extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async {
    if (key.startsWith('assets/pack/')) {
      throw FlutterError('Unable to load asset: "$key".');
    }
    return rootBundle.load(key);
  }
}

/// Máy CÓ pack: ảnh tải được.
Widget packHost(Widget child) =>
    DefaultAssetBundle(bundle: _PackStub(), child: MaterialApp(home: child));

/// Máy KHÔNG có pack: ảnh nguồn thiếu — kiểm nhánh hỏng-tử-tế.
Widget missingPackHost(Widget child) =>
    DefaultAssetBundle(bundle: _PackMissing(), child: MaterialApp(home: child));
