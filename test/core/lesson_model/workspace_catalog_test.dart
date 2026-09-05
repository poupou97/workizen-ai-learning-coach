/// TRACK B — WorkspaceCatalog: thật nếu có, không thì mẫu, không có ⇒ không
/// workspace (không màn rỗng).
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';
import 'package:learning_coach/core/lesson_model/workspace_catalog.dart';

import '../../features/lesson_workspace/support.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('chỉ có fixture MẪU (CI) ⇒ nạp mẫu, trust fixtureSynthetic', () async {
    final c = WorkspaceCatalog(bundle: syntheticOnlyBundle());
    await c.load();
    expect(c.isLoaded, isTrue);
    final d = c.docFor('06-sgk-khoa-hoc-tu-nhien-6', 17);
    expect(d, isNotNull);
    expect(d!.trust, ContentTrust.fixtureSynthetic);
    expect(d.assetBase, FixtureSlot.syntheticDir);
    expect(c.hasWorkspaceFor('06-sgk-khoa-hoc-tu-nhien-6'), isTrue);
    expect(c.hasWorkspaceFor('06-sgk-toan-6-tap-mot'), isFalse);
  });

  test('không có fixture nào ⇒ không workspace, không ném', () async {
    final c = WorkspaceCatalog(bundle: noFixtureBundle());
    await c.load();
    expect(c.booksWithWorkspace, isEmpty);
    expect(c.docFor('06-sgk-khoa-hoc-tu-nhien-6', 17), isNull);
  });

  test('load() gọi nhiều lần chỉ nạp một lần', () async {
    final c = WorkspaceCatalog(bundle: syntheticOnlyBundle());
    final f1 = c.load(), f2 = c.load();
    expect(identical(f1, f2), isTrue);
    await f1;
  });

  test('withDocs: xây thẳng cho test', () {
    final c = WorkspaceCatalog.withDocs([loadSyntheticDoc()]);
    expect(c.isLoaded, isTrue);
    expect(c.docsForBook('06-sgk-khoa-hoc-tu-nhien-6').length, 1);
  });
}
