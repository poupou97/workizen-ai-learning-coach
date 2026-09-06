# Lane E1 ← Lane E2 · reconciliation (PR #85 ↔ PR #86)

E2 filed four divergences between its `VisualSpec` and E1's. This records how E1 resolved the ones
that reached the E1 side, and what stays a Founder decision. E2's own filing is
`VISUAL-SPEC-E1-E2-RECONCILIATION.md` on `e2/round5-visualspec-renderer`.

---

## 1. Lesson identity in the spec — **E1 CHANGED. E2 is right. No Founder decision needed.**

E2 made the per-lesson anti-pattern **untypable**: `VisualSpec` carries no `book` / `lessonNo` /
`slotKey`, `VisualRenderContext` carries no `LessonDocument`, and two source-scanning tests fail the
build if either stops being true.

E1's spec carried `{book, lesson, title, subject, grade}`. That would have made
`if (lessonId == BAI17)` typable again and dissolved the guarantee.

**Resolution: identity leaves the renderer-facing spec entirely.** `VisualSpec.to_json()` now
carries schema · family · layout · title · compiler · elements · counts · trust, and nothing else.
Identity lives on the claim/grounding side, in a separate `lineage_json()` artefact for the trust
layer, which a renderer never receives. Two tests hold it: **no identity key at any depth**, and
**no book or subject appearing as a value anywhere**.

This is not a concession. `04-BAI17-REPLACEMENT.md` reached the same conclusion from the other
direction before E2's message arrived — a renderer that can name a lesson is a renderer that can
grow 3,679 special cases, and the reason to decompose `khtn6_bai17.dart` is exactly that. Two lanes
arrived at one constraint independently, which is better evidence than either lane's argument.

> ⭐ **Writing the guard test found a leak neither lane had seen.** Element ids embedded the book
> and lesson number — `step:06-sgk-khoa-hoc-tu-nhien-6|17|0|0#n1`. A renderer could have parsed the
> id and branched on the lesson, through a door E2's field-level guards do not watch and E1 had not
> thought about. Node ids are now unique *within* a lesson and say nothing about *which* lesson.
> **E2 should consider the same check on its side**: a field-name guard does not catch identity
> smuggled inside a string value.

## 2. Serialisation strengthening a grounding — **E1 ADOPTED.**

E2's regression test caught a save/load round trip upgrading a grounding from
`inheritedFromEntity` to `cellStated`. Nothing announces that: the file is written, read back, and
the claim is quietly stronger than the page supports.

**Resolution:** strength is now explicitly ordered on four axes — `trust`, `support`, `status`,
`locatorKind` — and `assert_not_strengthened()` is asserted across every round trip.
`SemanticClaim.from_json` is deliberately **not lenient**: an unknown status or support raises
rather than defaulting, because a forgiving reader is exactly how a weak claim becomes a strong one
by being written to disk.

This is the same family as the "no constructor from a presentation form" rule adopted from Lane A2.
Both are doors through which a claim gains strength without gaining evidence. Together they give
three: a rendering may not become structure, a file round trip may not add support, and a lenient
parser may not supply a default.

## 3. "A grammar validated on one lesson does not generalise" — **CONFIRMED, THIRD TIME**

Three lanes now measure the same thing from three directions, and the numbers line up:

| lane | measurement |
|---|---|
| **E2** | its sequence rule fires on **6 of 54** gold pages, 3 of them teacher books, learner-facing precision **0.500**; Toán, Tiếng Việt and Tin học produce **nothing** — no upstream structure exists |
| **Lane C** | LS&ĐL 5 prints **112 date mentions in eight forms**; the round-4 rule accepts **one** form and extracts **3 events across 28 lessons** |
| **E1** | TIMELINE is EXTRACTABLE on **3 of 224** TSL lessons (1.3 %) — *the same 3* |

E1's census reached Lane C's number independently, from the corpus rather than from the rule. That
is the census doing the job the coordinator described: **counting the real forms per subject before
anyone proposes a rule.** `06-CENSUS.md` §3.2 already states the general version — four families
show EXTRACTABLE = 0 *because no extractor exists*, and the census emits `familiesWithNoExtractor`
beside the table so the zero cannot be read as a fact about the books.

The corollary E1 accepts: **`e1-prose-dated-events-v1`'s 7/7 on LS&ĐL 5 Bài 8 is a result about one
form on one lesson on one build.** It is reported as such in `05-KNOWN-DEFECTS.md` row D, and the
scoreboard's row 22 (holdout precision) stays blank rather than borrowing credit from it.

**What E1 owes next, revised by this:** a per-subject **form census** — how many distinct surface
forms each family's cue actually takes — before any new extraction rule is written. Lane C's 8
forms for dates is the model. That now ranks above the COMPARISON extractor on E1's queue.

## 4. The trust chip — **E1's contract earned its place**

E2 reports the contract caught a real defect in its build: no trust chip was being rendered at all.
It is now unconditional and reads the weakest trust across all sections. `03-VISUALSPEC-CONTRACT.md`
§3.4 stands as written — `trust.chipRequired` is `true` for every spec that can exist today, and a
renderer must not have a code path that omits it.

---

## Still open, and a Founder decision rather than a lane one

**Does the trust layer receive the lineage artefact, and through what path?** E1 now emits two
artefacts per (lesson × family): the spec, which a renderer sees, and the lineage, which it must
not. Nothing yet decides who reads the second one, or whether the trust sheet reaches it through
the app or through a build step. E1 has deliberately not designed that, because it touches
`lib/**`, which E1 does not own.
