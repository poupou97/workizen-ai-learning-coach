# 06 · PRODUCT REALITY — what actually changed for a human being

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

Round 5's answer to this question was *"presentation only, and only on the test device."*
**Round 6's answer is different, and it is not a clean win.**

---

## 1. THE CHILD — the loss first, because the loss is the headline

### 1.1 A real History lesson replaced a fake one

**LS&ĐL 5 Bài 8 — «Đấu tranh giành độc lập thời kì Bắc thuộc», SGK pages 36–39.**

| | before round 6 (the `[MẪU]` build) | **after round 6, on a real Nokia 6.1** |
|---|---|---|
| served text | **23 blocks, every paragraph beginning `[MẪU]`** — invented prose | **34 blocks of real SGK text** |
| gaps | few, fabricated | **17, each stating its reason** |
| **timeline** | **7 events** (fabricated) | **0 events** |
| **SAM script** | **7 steps** (fabricated) | **none** |
| page crops on the gaps | 5 sample images | **0** — gap **G1**, the device walk's one FAIL |

*(**PROVEN** — the archive builder parsed the shipped fixture: 52 blocks · 17 withheld · 34 served
content blocks + 1 `sourceRef` · `semantic: 0` · `tutorSteps: 0`.)*

### 1.2 **THE CHILD LOSES THE TIMELINE**

Before this round, opening Trực quan on Bài 8 showed a seven-event timeline. **Now there are no
events at all.**

The block carrying all seven, `p039:000`, was **detected, repaired and validated** in round 6 — and
is **still withheld**, because no production trust threshold exists:

```
type withheld · trust withheld · reasons ["agree_tones"] · textLen 272 · NO `text` field
repair.disposition VALIDATED_REPAIR · verdict validated · changed false · servable false
```

*(PROVEN — read directly from the file that was on the phone.)*

**Round 5 withheld this block on a single token** — «Bạch **Đằng**» (primary) versus «Đăng»
(verifier) — **and the print says the primary stack was right.** Round 6 proved that, wrote the
proof onto the artefact, and **still did not serve it.**

> `VALIDATED REPAIR ≠ TRUSTED` · `RESTORED ≠ TRUSTED` · `CONNECT ≠ TRUST` · **`VISIBLE ≠ SERVED`**

**This is a real trade, not a pure win.** The child exchanged a fabricated timeline and a fabricated
tutor script for real book text and honest gaps. Per doctrine (`FIXTURE ≠ TRUSTED CORPUS`,
`MOCK ≠ EVIDENCE`) that is the right direction — **but saying this round only added things for the
child would be false.**

### 1.3 **THE CHILD LOSES EVERY TOÁN EXERCISE**

Round 5's fail-closed fix — geometry-rebuilt expressions that lost their `status`/`provenance` are
not emitted at all — **reached an APK on this machine for the first time in round 6**.

**Result: the app ships `toanExercises: 0`.** *(PROVEN — recomputed by the archive builder across
all 12 archived pack files; every other activity family is unchanged.)*

**A truthful zero, exactly where the Founder said not to pretend a Toán path exists before it does.**

*(**41 removed — g4 26, g5 15; activities 248 → 207. PROVEN**, recomputed from the two pack sets
archived here. And the backup identifies itself as the **2026-09-05T04:37Z** build — **the very one
round 5's device walk used — so the APK a child was shown in round 5 carried all 41 of them.**)*

### 1.4 The one gain that is not a subtraction

**A less cramped lesson screen.**

| pinned chrome | Đọc | Trực quan | Học với SAM |
|---|---|---|---|
| before | 225 dp | 225 dp | **411 dp = 58.9 % of the viewport** |
| **after (Option B)** | **281 dp** | **281 dp** | **281 dp** |
| after «Để sau» | 225 dp | 225 dp | 225 dp |

First visual content **384 → 289 dp** peeking, **233 dp** collapsed; on the device, collapsing lifts
content by **~146 px**. **View labels 7 → 4, and now one word set instead of two** («Học **với**
SAM» / «Học **cùng** SAM» is gone).

**The number that matters is the equal one.** The 411-vs-225 gap existed only because of a card;
all three views now pay the same price, and a test pins it.

### 1.5 And the child sees the honest zeros, in their own words

On the real device, the «Vào bài học» screen answers three questions from the lesson's own data —
and two of the answers are zero:

```
📖 Đọc         Như trong sách · 18 đoạn · 3 câu hỏi trong sách · 17 chỗ SAM để trống
✨ Trực quan   Chưa có sơ đồ cho bài này — chỉ có bảng tóm tắt lời sách
🦉 Học với SAM Chưa có kịch bản cho bài này
```

*(OBSERVED — frame `round6-03-picker.png`.)* **The app says «I don't have this» rather than showing
something invented.** That is the round's product thesis in one screen.

---

## 2. THE PARENT — **NOTHING NEW**

Not "small improvements". **Nothing.** No parent surface was touched, walked or measured in round 6.
`EVIDENCE REALITY` remains **0 of 0** — zero validator-permitted interactions out of zero possible —
so there is nothing new a parent could honestly be shown.

**UNAVAILABLE:** no parent-surface measurement exists from this round.

---

## 3. SAM — **NOTHING NEW**

`PEDAGOGY REALITY` is flat at **7 / 17** tutor steps runtime-guided, unchanged from round 4.

**And on the real Bài 8 path SAM has no script at all** — the lesson honestly says «Chưa có kịch bản
cho bài này». The learning-view census puts SAM's teaching reach across the canonical corpus at
**exactly one lesson out of 238 (0.004)**.

What changed *around* SAM, not *in* SAM: the recommendation is now one presentation instead of four,
in three honest states; SAM's portrait is gone from places SAM is not speaking; the «Đã mở ● ○ ○»
row moved into EXPANDED because **it is a session trace, not learning evidence**
(`OPENED ≠ UNDERSTOOD`).

### And the device found SAM saying something wrong

**SAM tells the child to leave the lesson they just opened.** In all three views the suggestion was
**«SAM gợi ý: Về mục lục»**, and its reason read **«Con đã đi qua các cách học của bài này»** —
while the row directly beneath it read **`● Đọc ○ Trực quan ○ Học với SAM`**. The child had opened
**one**. The Next Action runtime is treating «the other two views have nothing to show» as «already
visited».

**Two lines contradicting each other on the same card** *(OBSERVED on the device)* — and it was
**moving «Đã mở» into the expanded state that exposed it**. The defect is in `lib/core/agenda/**`,
outside WS-D's lane; **returned to its owner rather than patched.**

---

## 4. INTERNAL / RESEARCH ONLY

Real, measured, and reaching **no user**: the recognition harness · the conservation ledger · the
repair projection · the lineage gate · the forms census · the archive tooling.

> **Tests, tools and prototypes are not learner delivery.**

---

## 5. WHAT REMAINS STRUCTURALLY BLOCKED

| Blocker | State after round 6 |
|---|---|
| **No production trust threshold** | `THRESHOLDS.json` still does not exist. `trusted` computes to **0 by construction**, `eligible for teaching` = **0**, Source Trust **0 / 97**. **Founder gate.** |
| **No *servable* structured content kind** | `no_carrier:formula` now names the gap honestly *(PROVEN)*, but a servable kind needs **app rendering *and* a trust decision**. Deliberately not built. |
| **The app has no rich text** | Unchanged and **accepted as is**. The page crop with provenance is the honest path — *and on Golden #1 the crops are missing (G1)*. |
| **118 blocks withheld for want of a type** | `footnote` 64 · `activity` 50 · `option` 4. **A model gap, not a data gap** — the cheapest win available, and it changes what a child reads, so it needs a wording decision first. |
| **The 4 `option` blocks are defect #8** | A **mutilated multiple-choice set** — the shape where withholding is *not* the safe move. |

---

## 6. THE HONEST BOUNDARY SENTENCE

> **Round 6 put real, verified book text in front of a child for the first time — and the same
> honesty that put it there took away a timeline, a tutor script and every Toán exercise. The
> product got smaller and truer on the same day.**

## 7. WHAT WOULD MAKE THE NEXT ROUND FEEL LIKE A GAIN TO A CHILD

Stated as a forecast, not a promise *(see `12-NEXT-ROUND-PLAN.md`)*:

1. **A Founder-set trust threshold** — the only thing that can turn the six validated-and-withheld
   regions on Bài 8 back into readable text, timeline included. **Nothing else can.**
2. **Restore the page crops (G1)** — 17 gaps currently offer a reason and a page number where an
   image of the printed page was available all along.
3. **The 118-block model gap** — three block types in `lib/core/lesson_model/**`.
