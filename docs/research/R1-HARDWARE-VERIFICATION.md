# R-1 — HARDWARE VERIFICATION
## Nokia 6.1 device walk · 2026-09-06 · Founder-authorised

> **VERDICT: R-1 is VERIFIED on real hardware.**
> The 17 withheld lesson gaps render their page crops on a real device, from a build of `main`.
>
> **This does NOT mean any content became trusted.** `trusted = 0` and `eligible for teaching = 0`
> are unchanged. Phase F confirmed **nothing new reaches a child**. A green walk proves the Bài 8
> fixture *renders correctly*; it proves nothing about trust.

---

## 1 · What was built and installed

The build on the phone was **11:26**, which predated the entire autonomous run — it carried none of
Phase B's role fix and none of Phase E's Golden-chain verdict. **Walking that build would have
verified nothing about today's work**, so it was replaced.

| | |
|---|---|
| Repo commit | **`c86d377`** (`main`) |
| Package | `ai.workizen.learningcoach` 1.0.0 |
| **Installed** | **2026-09-06 19:36:53**, `adb install -r` — the Founder's profile and app data **preserved**, never uninstalled |
| Device | Nokia 6.1 · `Plate2_00WW` · **Android 10** |
| adb | **`192.168.1.3:5555`** |
| Packs | `toanExercises` = **0** |
| Fixture | 17 withheld blocks, **17 carrying a crop** · `validatedRepairs 9` · **`trusted 0`** |

**Recorded because it cost time:** the device's adb address **changed from `192.168.1.68` to
`192.168.1.3`**. The old address now times out. Project memory still names the old one.

---

## 2 · What the walk proves — read directly from the frames

**R-1 · the page crops render.** Frame `08-R1-page-crop.png` shows a withheld card with the SGK page
image displayed beneath it, under the toggle «Vì sao SAM để trống? **Ẩn ảnh trang**». Before this
work a withheld card told a child something was missing and then showed **nothing**.

**The real fixture loaded, not the synthetic fallback.** The header reads «Bài 8 · Đấu tranh giành
độc lập thời kì Bắc thuộc · SGK LS&ĐL 5 · **trang 36–39**».

**The research chip is present** — «🧪 Bản thử nghiệm · nguồn SGK có cấu trúc, chưa ki…» — so the
slice is not presented as finished product.

**Withheld cards speak child language and leak no machine ids:** «Phần này SAM chưa đọc được — con
xem SGK trang 36 nhé.» with «Lý do: SAM chưa chắc đọc đúng».

**The D4 caption is on the screen itself**, under the crop: «Ảnh chụp trang sách — chỉ để con đối
chiếu, **không phát hành**.» The licensing boundary is not only in a document; it is in front of the
child.

**Title fidelity holds.** «thời kì **B**ắc thuộc» — capital B. The PRESERVE SOURCE VERBATIM decision
(order 42) renders correctly.

### The regression check — and it passed

**No timeline appeared.** Frame `21-truc-quan.png` shows Trực quan with no timeline and an explicit
reason: «SAM chưa có sơ đồ cho bài này. SAM chỉ vẽ sơ đồ khi sách viết rõ từng bước hoặc từng cách;
bài này chưa có phần như vậy nên SAM không tự vẽ.»

A timeline appearing would have meant a withheld `VALIDATED_REPAIR` had become servable. It did not.

### Two things visible on the device that are worth more than the walk

**`OPENED != UNDERSTOOD`, rendered to a child in their own words:** «Bài này SAM chỉ có một cách học
— Đọc — và con đã mở rồi. **Mở bài không phải là hiểu bài** — SAM chưa chấm phần nào ở đây.» And
«Đã mở: ● Đọc · Bài này chưa có Trực quan, Học với SAM» — honest about what the lesson does *not*
have.

**The Next Action contradiction is fixed on hardware.** The CTA reads **«Xem tiếp bài này»**. The
round-6 defect — SAM telling a child to leave the lesson they had just opened («Về mục lục») — does
not appear. Phase B's fix is confirmed on a real screen, not only in a test.

---

## 3 · Evidence and its limits, stated

**77 frames** with a manifest at `~/Desktop/wal-evidence/round7-r1-device-walk-2026-09-06/`,
each hashed. **Frames are NOT committed** — they contain verbatim SGK page crops, INTERNAL /
RESEARCH ONLY under D4.

**How this walk was completed, because it affects how much weight it carries.** The walking agent was
**terminated mid-run by an API error** (`oauth_org_not_allowed`) after capturing the frames but
before writing its manifest or report. The coordinator finished it: opened
`08-R1-page-crop.png` and `21-truc-quan.png` directly, re-read the device state and the build tree,
and reconstructed provenance from the artefacts rather than from the agent's account.

**Consequences, stated rather than smoothed:**

- **Only 2 of the 27 substantive frames were read by the coordinator.** The remaining 25 are hashed
  and present but **not individually adjudicated**. The two read are the two that carry the verdict.
- **There is no per-step PASS/FAIL log** — the agent's `steps.json` was never written. Round 6's
  rule that *a step without a frame is not a PASS* is honoured in the opposite direction here: these
  frames exist but their steps do not, so **only the claims read directly from a frame are asserted**.
- Personal-content review covered the frames the coordinator opened. The status bar shows only
  notification **icons**, no content. **No frame was excluded**; the other 25 were not individually
  reviewed.

**So: R-1 is VERIFIED. The rest of the walk is EVIDENCE CAPTURED, NOT ADJUDICATED.** A fuller walk
with a per-step log would strengthen it; it is not needed for R-1's verdict, which rests on a frame
that shows the crop rendering.

---

## 4 · What this changes, and what it does not

**Changes:** R-1 moves **HARDWARE UNVERIFIED → VERIFIED**. Three round-6/7 fixes are confirmed on
real hardware: the crops, the title casing, and the Next Action wording.

**Does not change:** `trusted = 0` · `eligible for teaching = 0` · **no threshold activated** ·
SGK crops remain **LICENSING-DISTRIBUTION BLOCKED under D4** · and the answer to *what can a child
use now that they could not before* remains, per Phase F, **NOTHING**.

**TECHNICALLY VALIDATED ≠ HARDWARE VERIFIED ≠ DISTRIBUTION RIGHT.** R-1 has now cleared the second
of those three. It has not cleared the third, and the first was never in question.
