#!/usr/bin/env python3
"""WAL-107 — so sánh scheduler: CURRENT vs FSRS-STYLE vs LEITNER (research-only).

KHÔNG đổi một dòng nào trong lib/core/student/review_schedule.dart.
CURRENT được chép lại đúng công thức reviewStateOf (base 7d, growth ×2,
maxGrowthSteps 4, overdueGrace 1.0) — nguồn: review_schedule.dart.
FSRS-STYLE: dạng rút gọn công khai (stability tăng theo ôn-thành-công,
retrievability = exp(-t/S)); KHÔNG copy code repo nào (license chưa rà file).
LEITNER: 3 hộp 1/3/7 ngày.

MÔ HÌNH HỌC SINH (ground truth mô phỏng — giả định, ghi thật):
trí nhớ mũ R(t) = exp(-t/S_true); S_true tăng ×2.2 mỗi lần ôn ĐÚNG lúc còn
nhớ (spacing effect), giảm về nửa nếu đã quên hẳn khi ôn (phải học lại).
Trẻ trả lời đúng lúc ôn với xác suất R(t). Seed cố định — tái lập được.

METRIC (mỗi scheduler, 200 học sinh × 6 kỹ năng × 120 ngày):
- reviews: tổng lần gọi ôn (chi phí thời gian của trẻ)
- lapses:  lần ôn mà trẻ ĐÃ QUÊN (R<0.5 → gọi TRỄ)
- early:   lần ôn khi R>0.95 (gọi SỚM — phí buổi học)
- retention_end: R trung bình ngày 120 (giữ được bao nhiêu)
- params:  số hằng số cần hiệu chuẩn (độ phức tạp bảo trì)
"""
import math, random

DAYS = 120
LEARNERS = 200
SKILLS = 6

def simulate(scheduler_factory, seed=42):
    rng = random.Random(seed)
    tot_reviews = tot_lapses = tot_early = 0
    retention = []
    for _ in range(LEARNERS):
        for _ in range(SKILLS):
            S_true = 3.0 + rng.random() * 4  # độ bền ban đầu 3-7 ngày
            last_seen = 0.0
            sch = scheduler_factory()
            due = sch.first_due()
            for day in range(1, DAYS + 1):
                if day >= due:
                    t = day - last_seen
                    R = math.exp(-t / S_true)
                    tot_reviews += 1
                    if R < 0.5:
                        tot_lapses += 1
                        S_true = max(2.0, S_true * 0.5)  # quên → học lại
                        correct = rng.random() < 0.6      # học lại ngay, dễ đúng
                    else:
                        if R > 0.95:
                            tot_early += 1
                        correct = rng.random() < R
                        if correct:
                            S_true = min(60.0, S_true * 2.2)  # spacing effect, trần 60d (hiện thực)
                    last_seen = day
                    due = day + sch.next_interval(correct)
            retention.append(math.exp(-(DAYS - last_seen) / S_true))
    n = LEARNERS * SKILLS
    return dict(reviews=tot_reviews / n, lapses=tot_lapses / n,
                early=tot_early / n, retention_end=sum(retention) / len(retention))

class Current:
    """Chép đúng reviewStateOf: interval = 7d × 2^min(successes,4)."""
    PARAMS = 4  # baseInterval, growthFactor, maxGrowthSteps, overdueGrace
    def __init__(self): self.successes = 0
    def first_due(self): return 7
    def next_interval(self, correct):
        if correct: self.successes = min(self.successes + 1, 4)
        else: self.successes = 0
        return 7 * (2 ** self.successes)

class FsrsStyle:
    """Rút gọn FSRS: S' = S × (1 + a·e^{-b·D}) khi đúng; S giảm khi sai.
    Gọi ôn khi retrievability dự đoán chạm 0.9 (t = S·ln(1/0.9))."""
    PARAMS = 5  # a, b, D0, fail_factor, target_R
    A, B, TARGET = 1.8, 0.3, 0.9
    def __init__(self): self.S = 4.0; self.D = 5.0
    def first_due(self): return max(1, round(self.S * math.log(1 / self.TARGET) * 10))
    def next_interval(self, correct):
        if correct:
            self.S *= 1 + self.A * math.exp(-self.B * self.D)
            self.D = max(1.0, self.D - 0.3)
        else:
            self.S = max(2.0, self.S * 0.4); self.D = min(10.0, self.D + 1)
        return max(1, round(self.S * math.log(1 / self.TARGET) * 10))

class CurrentBase3(Current):
    """CÙNG HÌNH DẠNG SM-2 của CURRENT, chỉ đổi MỘT hằng số có tên:
    baseInterval 7d → 3d. Tách «hình dạng sai» khỏi «tham số sai»."""
    def first_due(self): return 3
    def next_interval(self, correct):
        if correct: self.successes = min(self.successes + 1, 4)
        else: self.successes = 0
        return 3 * (2 ** self.successes)

class Leitner:
    PARAMS = 1  # bảng hộp
    BOX = [1, 3, 7]
    def __init__(self): self.i = 0
    def first_due(self): return 1
    def next_interval(self, correct):
        self.i = min(self.i + 1, 2) if correct else 0
        return self.BOX[self.i]

if __name__ == '__main__':
    print(f"{'scheduler':<12}{'reviews/skill':>14}{'lapses':>8}{'early':>8}"
          f"{'retention@120':>15}{'#params':>9}")
    for name, f in [('CURRENT', Current), ('CURRENT-3d', CurrentBase3),
                    ('FSRS-STYLE', FsrsStyle), ('LEITNER', Leitner)]:
        m = simulate(f)
        print(f"{name:<12}{m['reviews']:>14.1f}{m['lapses']:>8.2f}"
              f"{m['early']:>8.2f}{m['retention_end']:>15.3f}{f.PARAMS:>9}")
