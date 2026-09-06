# HỌC CÙNG SAM — Round 4 consolidated report · PROVE + EXPERIENCE + DISCOVER + LEGACY REPROCESS
**READY FOR FOUNDER REVIEW — nothing merged.** Base `main` @ 61dbfdb; integration branch `integration/round4-2026-09-05` (PR #73) = base + #74 A-runtime + #77 A-pipeline (incl. its correctness review fixes) + #75 Lane C + #76 Lane D + #78 Lane B. Gates on the integrated tree: `flutter analyze` clean · `flutter test` **960 passed / 2 skipped / 0 failed** · Python tool tests OK. Denominators per D5, never summed: **3,679** canonical (historical) · **3,381** ranged · **243** legacy lessons in scope · gold **54 pages / 643 blocks**.

---

## The five Founder questions

**1 · Where is Bài 17 more real?**
Pedagogy went from **5/17 to 7/17 tutor steps runtime-guided, measured on the device** — and it moved for the right reason twice over. Lane A-runtime built a *real capability*, `SourceQuoteIndex` (a hint may only quote text that is verbatim in a trusted block of the same lesson, recording `sourceBlockId`), and registered **zero validators — honestly**, because no Bài 17 question has an SGK-stated answer set; inventing one would have been a fake validator. Lane B then found that capability was **inert on the device** (the UI never passed `quoteIndex`), wired it, and fixed the two script defects it exposed — a fabricated «trang 62» citation and two dropped «các». Evidence is now strict by default (`readClass`: validated / participation / historicalUnvalidated), with **history preserved and never rewritten**, and a real half-stamp bug removed (a Book-tier context used to leak `sourceDocumentId` with no lesson).
*Not more real:* Source Trust is still **0/97** — nothing has crossed a production-trusted gate, because no gate exists yet.

**2 · Where does the child see a better product?**
Experience Fidelity **70–80 % → 80–85 %**. Reading room on the Nokia went from **57 % of the screen to 73 %**; chapter emphasis un-inverted; the trust explanation is in a child's words; the Home card no longer promises a chat SAM cannot do; the research slice sits in its own honest section instead of masquerading as grade-6 content. Four defects were found *on the device* and re-walked after fixing. Capped at 80–85 % for a stated reason, not a glossed one: **Trực quan is still text where the board is an illustrated mindmap.**

**3 · What did History prove or falsify?**
The gate on LS&ĐL 5 Bài 8 passed **with withholds**. Falsified: **A25** «the header page is trustworthy for its own objectives» (its title page had 0/15 text blocks trusted) and — twice, independently — **A26 «two OCR stacks agreeing means verbatim»**: a block with `text_sim = 100` still carried tone slips. Proven: header attachment, the printed offset, per-element trust, and that a **non-arithmetic validator can be keyed to the lesson's own prose** (7/7 dated events extracted deterministically with character spans). The cross-domain answer: the **document layer** generalises; the **semantic layer** generalises only as *«a deterministic rule projecting trusted blocks into a typed shape»*, not as Process/Timeline themselves; a **validator exists only where the SGK states the fact**; **tutor typing** generalises, hand-written scripts do not.

**4 · Can the legacy data actually be rescued? — PARTIAL. Safer and smaller. Not teachable.**
False trust on the audited legacy batch: **OLD 0.727 → tc2-p1 0.365 → tc2-p2 0.297**. Teaching-critical 0.722 → 0.176. Reading order 0.424 → 0.048. All 16 geometry-rebuilt Toán expressions are now **withheld instead of reconstructed**. Blocks served fell 131 → 79 % → **64 %**: tc2-p2 delivers **≈39 fewer wrong and ≈27 fewer right** than p1, and about **4× the correct content at ⅔ the wrong claims** vs OLD. Over-withholding was measured too, not hidden: **12 of 30 reviewed withheld regions (0.400) were clean text refused wrongly**. Three defects survive on both builds (an imprint page filed as «Bài 73» body; a tone-corrupted Toán 5 lesson title; `b) 10 +` for `b) 3/10 + 5/21`).

**5 · The biggest bottleneck after round 4 — two, and neither is effort.**
**(a) There is no gate to cross.** The pipeline can now measure, withhold and prove; but `THRESHOLDS.json` does not exist, so `trusted` computes to **0 by construction** and `eligible for teaching` needs a second, separate Founder act. Every lane is blocked at the same wall: *measured, not authorised.*
**(b) The fidelity floor cannot be closed by more agreement.** 4 of 11 Bài 17 tone slips survive because **both OCR stacks make the same error** («Tiền hành») or the base vowel changes («phẫu»/«phễu»). No agreement guard reaches these — it needs a **third signal**: a Vietnamese lexicon, a third stack, or a human. Until then the display-fidelity class has a floor.
Behind those: **role is the one class where the two blind annotators disagree** (κ 0.423–0.713, and three of four disagreements are about *what a role means* — a definition problem, not a model problem).

---

## The five product scores — reported separately, never averaged

| # | Score | Value | Basis |
|---|---|---|---|
| 1 | **Experience Fidelity** | **80–85 %** overall (Đọc 85–90 · picker 80–90 · Next Action 80–90 · trust sheet 80–90 · Học với SAM 80–88 · Chương 75–85 · Home 70–80 · Trực quan 70–80 · Sách 70–80 · Giá sách 65–75 · research slice 65–75) | frame-by-frame vs the two concept boards, denominator = boards minus what doctrine forbids |
| 2 | **Source Reality** | **97 visible elements**: 78 TSL · 10 fixtureFromTrustedCorpus · 5 prototype · 4 withheld | machine census on device |
| 3 | **Source Trust** | **0 / 97** through a production-trusted path | no threshold exists; audit status `sampledNoGate` |
| 4 | **Pedagogy Reality** | **7 / 17** tutor steps runtime-guided (Bài 17, on device) · **0 / 7** for the History research slice (no binding — and it says so in child words) | `PedagogyRuntime` + `SourceQuoteIndex` |
| 5 | **Evidence Reality** | **0** validator-permitted interactions, out of **0 possible** in the workspace across ~44 device interactions | no registered validator applies to Bài 17 |

## Legacy reprocess scoreboard

| in scope | pending | reprocessed | independently audited | trusted | partial | withheld | rejected | **eligible for teaching** |
|---|---|---|---|---|---|---|---|---|
| **243** | 237 | 6 | 6 | **0** | 6 | 0 | 0 | **0** |

243 = the 113 baseline-learnable ∪ sam-units lessons = 6.6 % of 3,679 canonical / 7.2 % of 3,381 ranged. `trusted` is computed against `THRESHOLDS.json`; **the file does not exist, so the tool returns 0 and prints why** — REPROCESSED ≠ TRUSTED is encoded in code, not merely asserted in prose.

**OLD vs NEW-p1 vs NEW-p2, per failure class** (wrong / judged served rows, Wilson 95 %):

| class | OLD (n=55) | tc2-p1 (n=74) | tc2-p2 (n=64) |
|---|---|---|---|
| display | 0.709 [0.579, 0.812] | **0.203** | 0.203 |
| teaching-critical | 0.722 [0.560, 0.842] | 0.208 | **0.176** |
| reading order | 0.424 [0.272, 0.592] | **0.000** [0, 0.129] | 0.048 |
| role | 0.164 | 0.216 ⚠ | **0.125** |
| attachment | 0.036 | 0.108 ⚠ | **0.034** |
| formula/number/unit | 0.400 [0.281, 0.532] | **0.095** | — |
| **false trust (derived)** | **0.727** [0.598, 0.827] | 0.365 [0.264, 0.479] | **0.297** [0.199, 0.418] |
| **blocks served** | 131 | 79 % | **64 %** |

tc2-p1 had made **role and attachment worse than the old product**; PR #77 pulled both back below OLD. Inter-annotator κ (two blind passes, different models): false trust **1.000**, attachment 1.000, teaching-critical 1.000, display 0.842, **role 0.423–0.713**.

## Pipeline: what changed and what it cost

Gold (54 pages / 643 blocks): false-trusted **42 → 26** · FTR **0.0957 → 0.0734** · CTE **79 → 68** · attachment **45 → 49/54** · **coverage 0.683 → 0.551**. That is the round's central trade: **85 more blocks withheld to deliver 16 fewer wrong ones.** No threshold was lowered and no guard loosened to achieve it.
A correctness review of the pipeline branch found **14 defects**, all reproduced with failing tests before being fixed — including one that **silently truncated an entire book** (a price line «Giá:» plus a «Website:» line in the last 12 % of a book was enough to mark a back cover, after which every later page lost its lesson), chapter labels invented out of ordinary words («PHẦN VĂN HỌC» → «Phần V» / «ĂN HỌC»), and years eaten from History titles («… ĐẾN NĂM 1945» → «… ĐẾN NĂM 1»). Ending a book is now **reversible**, and a printed banner re-opens it.
Also fixed as coordinator: `pack_provenance.py` hard-coded `capped-toc-v1` while the attachment rule had moved to v2 — **every pack built today stamped a rule it was not built with.** The tool now derives the name from its owner and consequently **fails verification on the packs currently on disk**, which is the provenance system working: those packs are stale.

## Device evidence
Nokia 6.1 / Android 10, learner «Na · Lớp 6». **Two iterations, 32 frames, manifest with git SHA + APK sha256 + pack versions + fixture hash + frame hashes, 0 downgraded claims** (`docs/design/track-b-evidence/round4/`). Protocol held throughout: two identical screencaps ≥20 s apart before each iteration, never woken or unlocked, no profile/setting/data touched, the Founder's other app never touched, two launcher frames deleted. Honestly recorded: one queued History step is `NOT WALKED` and one is a code claim, not a device claim.
**Integrated-build walk not performed** — the device was in use by the Founder at check time and the protocol forbids interrupting. This is honest rather than fatal: the integrated branch's `lib/`, `android/` and `assets/` are **byte-identical** to Lane B's branch (verified by `git diff`), so the 32 frames cover exactly this app; the integration adds only tooling, tests and docs.

## Open P0 / decisions requested
1. **Trust thresholds (G1)** — without `THRESHOLDS.json` nothing can ever be «trusted» or «eligible for teaching». This is now the single biggest blocker.
2. **Adopt `tc2-p2` for the golden fixture?** It raises fidelity but **removes the Bài 17 tutor script and one process diagram** (one of the six blocks the script quotes becomes withheld). Currently NOT adopted; the app still runs tc2-p1.
3. **Rebuild the shipped packs?** They carry stale attachment verdicts and now fail provenance verification. Rebuilding changes shipped content and moves the baseline Lane D measured against.
4. **Lane C's two PROPOSED rules** (`prose-dated-events-v1`, `story-attribution-v1`) — accept into the bridge or leave in research.
5. **Role definition** — κ 0.42–0.71 because annotators disagree on what a role *means*; needs a written definition, not a better model.
6. **Second annotator** on ≥10 % is done for two samples; the protocol's remaining share and the third fidelity signal (lexicon / third stack / human) need a decision.
7. Residuals recorded, not tuned away: one verse stanza still served joined; «Xem bảng bên dưới» correctly matched but «Đọc bảng chia 3» over-matched (fixed); audit sample 0177 (a lesson starting mid-page with no header); 3 legacy defects surviving both builds.

## PRs (all CI green, none merged)
| PR | Lane | Contents |
|---|---|---|
| **#73** | integration base | round-4 plan + ownership; now contains all five lanes |
| **#74** | A-runtime | strict validation default, `readClass`, `SourceQuoteIndex`, camera lineage, SemanticBinding, Next Action |
| **#77** | A-pipeline | failure classes 1–5, Lane C requests 2–6, gold errata, tc2-p2, **+ 14 review defects fixed** |
| **#75** | Lane C | Golden Slice #2 gate (PASS WITH WITHHOLDS) + History slice, 5 PROPOSED rules |
| **#76** | Lane D | legacy registry (243), batch 1, OLD/p1/p2 compare, blind second annotations, scoreboard |
| **#78** | Lane B | journey to 80–85 %, fabricated-stamp removal, quote wiring, 4 device defects, evidence manifests |
