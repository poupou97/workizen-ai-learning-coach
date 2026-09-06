# 08 · DEVICE EVIDENCE

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

# **ROUND 7 HAS NO DEVICE EVIDENCE. NOT CAPTURED.**

**No device walk was performed. No APK was built or installed. No input was injected. No frame was
captured. No app data was touched.**

`screenshots/` therefore contains **no images** — only
`NO-DEVICE-FRAMES-THIS-ROUND.md`, which says so. **That is the honest state, not an omission**, and
it is why every device-facing claim in this archive carries **[HU] HARDWARE UNVERIFIED**.

---

## 1. THE TWO READ-ONLY CHECKS — different events, both recorded

They are **not** the same observation, and collapsing them would misrepresent the decision.

### Check 1 — WS-R, while executing R-1

Read-only `adb` against `192.168.1.3:5555`, Nokia 6.1 (`Plate2_00WW`, Android 10),
`ai.workizen.learningcoach` present alongside `com.workizen.tongtai`:

```
mCurrentFocus = com.ss.android.ugc.trill/…SplashActivity     ← a third-party media app
mWakefulness  = Awake
mHoldingDisplaySuspendBlocker = true
foreground unchanged across an 8 s re-poll
```

> **The phone was in active personal use.** WS-R disconnected.

**And a second reason it could not proceed even had permission existed:** the idle check that proves
nobody is using the phone is a **per-pixel screenshot comparison**, and screenshotting a third-party
media app **captures personal content the device protocol forbids retaining.** *The check that would
have licensed a walk is itself the thing the protocol forbids in that state.*

### Check 2 — the coordinator, later

`adb devices` · foreground · power/lock state · package list. **No input injected, no APK built or
installed, no frame captured, no app data touched.** Disconnected immediately.

> **The device *appeared* free at the moment of this check.**
>
> **The Founder's instruction that the device not be touched stood regardless.**

**Both observations are recorded, not only the one that justifies the outcome.** *A device looking
free is not permission, and it did not become permission.* **That distinction is the whole point of
writing it down.**

---

## 2. WHAT THIS MEANS FOR THE ROUND'S CLAIMS

| Claim | At the artefact | On hardware |
|---|---|---|
| **R-1** — 17 lesson gaps carry page crops | **PROVEN** — 17/17 withheld regions carry a crop, 22 placed, 5 figure images, all eight lineage checks pass incl. **L5b 17/17** *(recomputed by the archive builder from the bytes)* | **NOT PROVEN.** Nobody has seen a child's screen show «Xem ảnh chụp trang sách», or tapped it and seen the printed page. |
| **R-2** — the «Về mục lục» contradiction | **PROVEN** — 128 cases swept, mutations kill the tests | **NOT PROVEN** |
| **R-3** — the lowercased proper noun | **PROVEN** — and the archive builder confirmed the data always carried the capital **B** | **NOT PROVEN** |

> **Widget tests and lineage gates are not real-device evidence.** Round 6's **GATE E step 09** —
> the one FAIL of that round's walk — is **exactly** what remains outstanding. **Round 7 fixed the
> data and did not retire the check.**

---

## 3. THE WALK THAT IS OWED — five steps, as WS-R specified them

1. re-check the foreground read-only, then the **per-pixel idle check**;
2. **rebuild the packs before building the APK** — *stale packs shipped 41 fabricated expressions in
   round 5*;
3. `adb install -r` — **never uninstall**; **the Founder's «Na» profile must survive**;
4. open LS&ĐL 5 Bài 8, tap a withheld card's **«Xem ảnh chụp trang sách»**, capture to
   `~/Desktop/wal-evidence/round7-ws-r/`;
5. confirm the header reads «Bài 8 · Đấu tranh giành độc lập thời kì **B**ắc thuộc» (R-3) and that
   the «Đã mở» row reads `Đã mở: ● Đọc · Bài này chưa có Trực quan, Học với SAM` with **no «Về mục
   lục» suggestion above it** (R-2).

**And one more, added by this archive:** before building, confirm the line **`L5b … 17/17 have a
crop`** — because rsyncing `assets/fixtures/` from the main checkout silently restores the
**crop-less** artefact, whose lineage fields all read as current. *(§8.1 of
`04-FAILURES-AND-FALSIFICATIONS.md`.)*

---

## 4. WHAT IS ARCHIVED INSTEAD OF FRAMES

| What | Where | Status |
|---|---|---|
| The regenerated Golden #1 fixture, `sha256 1862f27b…`, 57 blocks | `evidence/round7-artefacts/fixtures-real/` | **[TV]** |
| **22 SGK page crops** (17 withheld-region + 5 figure) | `evidence/round7-artefacts/fixtures-real/crops/` | **[LB]** — verbatim SGK page images, **D4, internal only** |
| Every crop's size and SHA-256, recomputed | `evidence/round7-artefact-verification.txt` | **[TV]** |

**The crops are deliberately NOT placed in `screenshots/`**, so that **no later reader mistakes a
page crop for a photograph of a screen.** They are images of a *book*, not of the *product*.

**Round 6's 7 device frames stay in `HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip`.** They show the
**round-6** build, in which the same 17 cards carried **no** page image. **They must not be
presented as round-7 evidence**, which is why this archive references them rather than copying them.

---

## 5. WHY THIS SECTION IS LONGER THAN THE EVIDENCE IT DESCRIBES

Because the absence is the finding.

Rounds 5 and 6 each closed with a real-device walk — 36 frames and 7 frames — and each time the
device found defects **no test had**: a card covering a mindmap's hub, a «why» naming the wrong
medium, SAM telling a child to leave a lesson, a proper noun lowercased. **Round 7 fixed two of
those from round 6's walk and could not check its own work the same way.**

> **Three fixes are finished, tested, mutation-checked — and unproven where it counts.** That is a
> real gap in this round, and it is recorded as a gap rather than dressed as a completion.
