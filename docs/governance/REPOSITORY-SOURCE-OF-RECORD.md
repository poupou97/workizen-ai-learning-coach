# REPOSITORY IS THE SOURCE OF RECORD

**Standing rule, in force from 2026-09-06** (Founder task order 43). This supersedes any earlier
wording that treated a Desktop ZIP or per-round archive as the record.

---

## 1 · The rule

> **REPO = CANONICAL RECORD.**
> **DESKTOP / ZIP / scratchpad / temp folder = REVIEW SNAPSHOT ONLY.**

Any artefact carrying a decision, an architecture, research, or anything needing traceability
**must live in the repository and be committed.** At minimum: task orders · research plans ·
research reports · audit reports · round reports · Founder decisions · ADRs · RFCs · architecture
proposals and assessments · technical proposals · product and UX proposals that affect
implementation · acceptance criteria · measurement methodology · gate definitions · threshold
definitions · evaluation methodology · important experiment results · final recommendations and
verdicts · manifests, provenance and reproduction instructions needed to understand or recreate a
result.

**If a decision could affect future implementation, it may not exist only in a chat window or on
the Desktop.** It needs a canonical document in this repository.

## 2 · Review copies are expected to be deleted

The Founder deletes Desktop review copies after reading them. **That is correct behaviour, not
data loss.** No process may depend on a Desktop ZIP continuing to exist.

## 3 · Why this rule exists — two things that actually happened

**A whole round was graded against reconstructed criteria.** The round-5 retrospective archive
could not find §16 of the round-5 master order anywhere in the repository, because the order
existed only in the conversation that issued it. It had to mark the ten acceptance criteria
**RECONSTRUCTED** and reason about what they probably were.

*(Both facts are now historical: the orders were committed later the same day, and the
reconstruction proved **byte-equal** to the real §16. That does not weaken the rule — it sharpens
it. The reconstruction was right, and **no one could have known it was right**, which is the whole
reason an order must be canonical when it arrives rather than reconstructed afterwards.)*

**Forty-three Founder task orders existed nowhere durable until 2026-09-06.** Every report, plan,
audit and correction for rounds 3–7 was committed. **The orders they answer to were not.** The
authority had no home while the answers did. They are now at `docs/founder-orders/`, recovered
verbatim from the session transcript.

This is the same hazard the workspace `CLAUDE.md` warns about: *doctrine that binds work but lives
nowhere a later reader can check.*

## 4 · Evidence exception — do NOT blindly commit everything

The rule does not mean pushing every binary into Git. **Never commit merely to satisfy it:**
verbatim SGK pages · SGK crops restricted under **D4** · copyrighted or restricted material ·
large datasets · large generated binaries · sensitive or private device evidence · anything
unsuited to Git.

**Restricted evidence does not become distributable because the archive rule exists. D4 remains in
force. TECHNICALLY POSSIBLE != DISTRIBUTION RIGHT.**

For an evidence body that cannot or should not live in the repo, the repo must still hold enough
**metadata** to understand it:

- manifest · provenance · SHA/hash where meaningful
- source and status
- generation / reproduction instructions
- **licensing and distribution classification**
- its relation to the report or decision that uses it
- **the reason the evidence body is not in Git**

## 5 · Round / task close sequence

A round or task is **not closed because a ZIP was built.**

```
WORK COMPLETE
  → CANONICAL DOCS WRITTEN
  → DECISIONS RECORDED
  → ARCHITECTURE / RESEARCH CONCLUSIONS RECORDED
  → METHODOLOGY / GATES RECORDED
  → COMMIT TO REPO
  → VERIFY TRACEABILITY
  → OPTIONAL REVIEW ZIP
  → FOUNDER REVIEW
  → REVIEW COPY MAY BE DELETED
```

**The review ZIP is built AFTER canonicalisation, never before.** There must never be a state
where a Desktop ZIP is the only source of truth.

## 6 · Order-before-work

**A task order is committed to `docs/founder-orders/` when it is received, before the work it
orders begins.** An order living only in a chat window is an order that can be lost.

## 7 · Historical clarification — no history is rewritten

Previous Desktop ZIPs were **review snapshots**. Repository documentation is the canonical project
record under the Founder governance clarified on **2026-09-06**.

Earlier documents describing per-round ZIPs as the «archive of record» were written before this
clarification. **They are corrected in place as to semantics only** — no hash is deleted, no
history is rewritten, and the fact that four Desktop ZIPs were deleted after review is recorded
rather than hidden. See `docs/research/ARCHIVE-REGISTRY.md`.

## 8 · What this changes in practice

| Before | Now |
|---|---|
| «Build the round ZIP» was the close step | Canonicalise into the repo, **then** optionally build a review ZIP |
| A missing Desktop ZIP looked like record loss | A missing Desktop ZIP is **normal**; a real loss is information existing nowhere but a ZIP, Desktop, scratchpad or chat |
| Archives held identity | The repo holds the record; `ARCHIVE-REGISTRY.md` holds **identities** of review snapshots so a rebuild is not mistaken for tampering |
| Task orders lived in chat | Task orders are committed on receipt |
