/// WAL-149 — cổng trạng thái: AUTO ≠ production; today đòi verified + ngày.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:learning_coach/core/stories/story_state.dart';

void main() {
  test('CHỈ verified lên production — autoVerified/candidate/review đều KHÔNG',
      () {
    expect(canShowInProduction(StoryStatus.verified), isTrue);
    for (final s in [
      StoryStatus.candidate,
      StoryStatus.autoVerified,
      StoryStatus.reviewRequired,
      StoryStatus.rejected,
    ]) {
      expect(canShowInProduction(s), isFalse, reason: '$s');
      expect(canRenderAsDirectQuote(s), isFalse,
          reason: '$s không được render như lời danh nhân');
    }
  });

  test('«Ngày này năm xưa»: verified + monthDay tin cậy — thiếu một là rớt',
      () {
    expect(
        todayCardEligible(
            status: StoryStatus.verified, hasReliableMonthDay: true),
        isTrue);
    expect(
        todayCardEligible(
            status: StoryStatus.verified, hasReliableMonthDay: false),
        isFalse,
        reason: 'không suy đoán ngày (§14)');
    expect(
        todayCardEligible(
            status: StoryStatus.autoVerified, hasReliableMonthDay: true),
        isFalse,
        reason: 'máy-verify chưa phải verified');
  });

  test('parse trạng thái lạ ⇒ candidate (mức thấp nhất), không đoán lên', () {
    expect(storyStatusFrom('AUTO_VERIFIED'), StoryStatus.autoVerified);
    expect(storyStatusFrom('gì-đó-lạ'), StoryStatus.candidate);
  });
}
