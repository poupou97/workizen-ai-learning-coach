# Round 5 — the Founder's §16 SUCCESS CRITERIA, committed for the record

**Why this file exists.** The round-5 retrospective archive could not find §16 anywhere in
the repository and had to mark its ten criteria **RECONSTRUCTED**. The criteria had only
ever existed in the conversation that issued them. That is the same hazard the workspace
`CLAUDE.md` warns about — doctrine that binds work but lives nowhere a later reader can
check. `ROUND6-PLAN.md` already fixes this going forward by fixing gates at the start of
the round; this file closes it retrospectively for round 5.

Recorded verbatim in substance from the round-5 master task order, §16.

> **Round 5 thành công nếu chứng minh được:**
>
> 1. ít nhất một major failure class được REPAIR, không chỉ WITHHOLD;
> 2. restored blocks có independent validation;
> 3. wrong served tiếp tục giảm;
> 4. correct served/coverage bắt đầu phục hồi;
> 5. role taxonomy rõ hơn và agreement tăng;
> 6. third signal chứng minh có hoặc không có giá trị bằng measurement;
> 7. Bài 17 vẫn usable và thật hơn;
> 8. History tiếp tục falsify architecture;
> 9. UI/UX tiếp tục tiến bộ trên máy thật;
> 10. không có trust claim nào được tạo chỉ để đẹp metric.

## Settled tally: 8 PASS · 1 PARTIAL · 1 FAIL

| # | Criterion | Verdict |
|---|---|---|
| 1 | ≥1 failure class REPAIRed, not just withheld | **PASS** (narrowly — attachment 8/8 in the pipeline; math and History repairs stayed in harnesses) |
| 2 | Restored blocks independently validated | **PASS** — six deterministic validators, blind judging, holdout |
| 3 | Wrong served keeps falling | **PASS** — false trust 0.619→0.318; 2 fabricated expressions→0; 41 INFERRED stopped shipping |
| 4 | Correct served / coverage begins to recover | **FAIL** — corrected for R13 the served share *fell*; over-withhold worsened 0.400→0.633; the only coverage that recovered came from loosening a guard and was wrong (0/1) |
| 5 | Role taxonomy clearer **and agreement up** | **PARTIAL** — spec + threshold curve landed, but re-annotation was in-sample, the settling blind measurement was not run, and pipeline role error moved the wrong way 0.116→0.151 |
| 6 | Third signal proven valuable or not, by measurement | **PASS** (strongest-executed criterion of the round) |
| 7 | Bài 17 still usable and more real | **PASS** |
| 8 | History keeps falsifying the architecture | **PASS** (strong — Lane C falsified its own round-4 rule) |
| 9 | UI/UX keeps improving on a real device | **PASS** |
| 10 | No trust claim created merely to flatter a metric | **PASS** — and the criterion the round honoured most consistently |

**Note on over-withholding.** It moved the wrong way, 0.400 → **0.633**, and that is a
genuine regression. It is **not** a separate §16 criterion — it sits inside criterion 4,
which is already graded FAIL. It must not be counted twice.

## Coordinator correction

In the round-5 evaluation delivered to the Founder I summarised the tally as
«**7 đạt · 1 nửa · 2 không đạt**». That summary line was **wrong**: the per-criterion
table immediately above it in the same message graded eight PASS, one PARTIAL and one
FAIL. The archive agent, grading independently and without §16 in hand, reached
**8 · 1 · 1** and was right.

The corrected tally does not change any judgement about the round — criterion 4 remains
the clear failure, criterion 5 the partial, and the substantive assessment («succeeded as
a research round, failed as a delivery round») stands unaltered. Recorded here because a
Founder-facing scorecard should be correct, and because round 5's own doctrine is that
history is corrected in the open rather than quietly restated.
