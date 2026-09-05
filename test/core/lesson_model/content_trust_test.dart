/// TRACK B — ranh giới máy đọc được: kiểu dữ liệu giữ luật, không phải comment.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/lesson_model/content_trust.dart';

void main() {
  test(
    '⭐ chỉ trustedCorpus là sự thật sản phẩm; mọi giá trị khác bắt buộc chip',
    () {
      for (final t in ContentTrust.values) {
        expect(t.requiresFixtureChip, t != ContentTrust.trustedCorpus);
        expect(
          fixtureChipLabel(t) == null,
          t == ContentTrust.trustedCorpus,
          reason: 'đột biến bỏ nhãn của ${t.name} ⇒ đỏ',
        );
      }
      expect(
        fixtureChipLabel(ContentTrust.fixtureSynthetic),
        contains('giả lập'),
      );
      expect(
        fixtureChipLabel(ContentTrust.fixtureFromTrustedCorpus),
        contains('nội bộ'),
      );
    },
  );

  test('parse fail-closed: chuỗi lạ ⇒ null, không mặc định thành tin được', () {
    expect(ContentTrust.parse('trusted'), isNull);
    expect(ContentTrust.parse(null), isNull);
    expect(ContentTrust.parse('trustedCorpus'), ContentTrust.trustedCorpus);
    expect(EvidencePolicy.parse('record'), isNull);
    expect(EvidencePolicy.parse('none'), EvidencePolicy.none);
    expect(SamMode.parse('live'), isNull);
  });

  test(
    '⭐⭐ EvidencePolicy và SamMode chỉ có MỘT giá trị — không có cửa bật',
    () {
      expect(EvidencePolicy.values, [EvidencePolicy.none]);
      expect(SamMode.values, [SamMode.prototypeScripted]);
      expect(SamMode.prototypeScripted.childLabel, 'SAM (kịch bản thử nghiệm)');
    },
  );

  test('sáu bất đẳng thức của Founder có mặt, nguyên văn', () {
    expect(BoundaryClaim.values.map((c) => c.statement), [
      'MOCK ≠ EVIDENCE',
      'FIXTURE ≠ TRUSTED CORPUS',
      'UI COMPLETION ≠ MASTERY',
      'TAP ≠ COMPETENCE',
      'PROTOTYPE SAM ≠ PROVEN PEDAGOGY',
      'SCREEN EXISTS ≠ CAPABILITY PROVEN',
    ]);
  });
}
