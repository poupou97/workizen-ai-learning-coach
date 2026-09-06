# NO DEVICE FRAMES WERE CAPTURED IN ROUND 7 — **NOT CAPTURED**

> **INTERNAL / RESEARCH ONLY — DO NOT PUBLISH.**

**This directory is deliberately empty of images.** Rounds 5 and 6 filled it with 36 and 7 frames
from a real Nokia 6.1. **Round 7 has none, and that is the honest state, not an omission.**

---

## Why

**No device walk was performed. No APK was built or installed. No input was injected. No frame was
captured. No app data was touched.**

Two read-only checks were made, by two different people, and they are **not the same event**:

| # | Who | What was observed |
|---|---|---|
| 1 | **WS-R**, while executing R-1 | `adb` read-only against `192.168.1.3:5555`. `mCurrentFocus = com.ss.android.ugc.trill/…SplashActivity` — a **third-party media app in the foreground**; `mWakefulness = Awake`; display suspend blocker held; foreground **unchanged across an 8-second re-poll**. **The phone was in active personal use.** WS-R disconnected. |
| 2 | **The coordinator**, later | `adb devices`, foreground, power/lock state, package list. **The device *appeared* free at that moment.** No input injected, no APK built or installed, no frame captured, no app data touched; disconnected immediately. |

**The Founder had instructed that the device not be touched, and that instruction stood regardless
of what the second check saw.** The archive records both observations rather than only the one that
justifies the outcome: *the device looking free is not permission, and it did not become permission.*

**A further reason WS-R could not clear it even had permission existed:** the idle check that
proves nobody is using the phone is a **per-pixel screenshot comparison**, and screenshotting a
third-party media app **captures personal content the device protocol forbids retaining.** The
check that would have licensed a walk is itself the thing the protocol forbids in that state.

## What this means for the round's claims

**R-1 — the 17 lesson gaps now carrying page crops — is `HARDWARE UNVERIFIED`.**

It is **PROVEN at the artefact**: 17 of 17 withheld regions carry a crop, all eight lineage checks
pass including **L5b 17/17**, and the archive builder re-verified it from the bytes
(`evidence/round7-artefact-verification.txt`).

It is **NOT PROVEN on hardware**: nobody has seen a child's screen show «Xem ảnh chụp trang sách»
on a withheld card, or tapped it and seen the printed page.

**Widget tests and lineage gates are not real-device evidence.** Round 6's own GATE E step 09 is
the check still outstanding, and round 7 did not retire it.

The same applies to **R-2** (the «Về mục lục» contradiction) and **R-3** (the lowercased proper
noun): both are fixed in code, both have tests that go red under mutation, and **neither has been
seen on a device.**

## The walk that is still owed, as WS-R specified it

1. re-check the foreground read-only, then the per-pixel idle check;
2. **rebuild the packs before building the APK** — stale packs shipped 41 fabricated expressions in
   round 5;
3. `adb install -r` — **never uninstall**; the Founder's «Na» profile must survive;
4. open LS&ĐL 5 Bài 8, tap a withheld card's «Xem ảnh chụp trang sách», capture to
   `~/Desktop/wal-evidence/round7-ws-r/`;
5. confirm the header reads «Bài 8 · Đấu tranh giành độc lập thời kì **B**ắc thuộc» (R-3) and that
   the «Đã mở» row reads `Đã mở: ● Đọc · Bài này chưa có Trực quan, Học với SAM` with **no «Về mục
   lục» suggestion above it** (R-2).

## What is in this archive instead of frames

- `evidence/round7-artefacts/` — the regenerated fixture and its **22 SGK page crops**. These are
  **LICENSING-DISTRIBUTION BLOCKED**: verbatim SGK page images, INTERNAL / RESEARCH ONLY under
  Founder rule **D4**. They are not screenshots and are deliberately **not** placed in this
  directory, so that no later reader mistakes a page crop for a photograph of a screen.
- `evidence/round7-artefact-verification.txt` — every crop's size and hash, recomputed.
- Round 6's 7 device frames remain in `HOC-CUNG-SAM-ROUND-06-2026-09-06-v2.zip`. **They show the
  round-6 build**, in which the same 17 cards carried **no** page image. **They must not be
  presented as round-7 evidence**, which is why they are referenced here rather than copied.
