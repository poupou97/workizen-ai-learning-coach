#!/usr/bin/env bash
# Supervisor cho AI Workforce runtime — có PHANH.
#
# Vì sao cần: runtime chạy AUTONOMOUS PRODUCT BUILD MODE với chỉ thị
# «never poll idly / SELF-ASSIGNMENT when no Story is executable» — hết việc
# nó TỰ TẠO việc. Vòng lặp trần của nó vì thế không bao giờ tự dừng.
#
# Luật dừng (lệnh Founder 2026-09-01): 3 vòng LIÊN TIẾP không sinh KẾT QUẢ
# THẬT ⇒ dừng. «Kết quả thật» = có commit mới trên repo. Đếm ticket không
# dùng làm tiêu chí vì agent tự tạo ticket cho chính mình.
#
# Dùng:  tool/ops/wf_supervise.sh [SỐ_VÒNG_TỐI_ĐA]
set -uo pipefail
cd "$(dirname "$0")/../.."
export PATH="$HOME/.local/bin:$PATH"

MAX_IDLE=3                      # 3 vòng không tiến bộ ⇒ dừng
MAX_CYCLES="${1:-20}"           # trần tuyệt đối, an toàn token
LOG="poc-out/wf-supervisor.log"
mkdir -p poc-out

idle=0
say() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG"; }
say "SUPERVISOR bắt đầu · dừng sau $MAX_IDLE vòng không có commit mới · trần $MAX_CYCLES vòng"

for ((i = 1; i <= MAX_CYCLES; i++)); do
  before=$(git rev-parse HEAD)
  before_n=$(git rev-list --count HEAD)
  say "vòng $i/$MAX_CYCLES — dispatch…"

  ai-wf --once >>"$LOG" 2>&1
  rc=$?
  if [ $rc -eq 17 ]; then
    say "  (một tiến trình runtime khác đang giữ lock — chờ 60s)"
    sleep 60
    continue
  fi

  after=$(git rev-parse HEAD)
  after_n=$(git rev-list --count HEAD)
  if [ "$before" != "$after" ]; then
    idle=0
    say "  ✅ tiến bộ: +$((after_n - before_n)) commit → $(git log --oneline -1 | cut -c1-70)"
  else
    idle=$((idle + 1))
    say "  ⏸️  không commit mới (vòng rỗng $idle/$MAX_IDLE)"
    if [ $idle -ge $MAX_IDLE ]; then
      say "🛑 DỪNG: $MAX_IDLE vòng liên tiếp không sinh kết quả — tiết kiệm token."
      exit 0
    fi
  fi
  sleep 10
done
say "🛑 DỪNG: chạm trần $MAX_CYCLES vòng."
