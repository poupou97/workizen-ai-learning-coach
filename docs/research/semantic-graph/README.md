# Semantic graph — Lane E1 (round 5)

**Status: RESEARCH. Nothing here is approved architecture, and nothing is production truth.**
`LEARNER_READY = 0` by construction: `THRESHOLDS.json` does not exist, so
`ContentTrust.trustedCorpus` is unreachable.

The Founder's framing this lane tests:

> *«Không thiết kế 3.679 visualization — thiết kế một ngôn ngữ để 3.679 bài có thể được compile
> thành visualization.»*

`Trusted Structured Lesson → Semantic Extraction → SemanticGraphCandidate → Grounding + Validation
→ Validated Semantic Graph → Visual Pattern Selector → VisualSpec → Controlled Renderer`

Hard boundary held throughout: **`SOURCE TRUTH ≠ SEMANTIC INTERPRETATION ≠ VISUAL REPRESENTATION`**,
and **`TRACE ≠ EVIDENCE`**. **No LLM is called anywhere in this lane** — not for census, not for
classification, not for generation.

## Documents

| # | Document | Answers |
|---|---|---|
| 00 | `00-EARLY-FOUNDER-CHECKPOINT.md` | §27 — `SOURCE → SEMANTIC → VISUAL SPEC` end to end, with a verbatim lineage row |
| 01 | `01-AUDIT-CLASSIFICATION.md` | REUSE BEFORE ADDING: the audit table; §10 KEEP/EVOLVE/ADAPT/DEPRECATE; the bridge gaps; §25 |
| 02 | `02-SEMANTIC-FOUNDATION.md` | §5 `SemanticClaim` · §6 the provenance bridge · §7 `SourceGrounding` · the enum delta |
| 03 | `03-VISUALSPEC-CONTRACT.md` | **Lane E2's input** — the spec, the five renderer rules, the family-frequency table, §15 |
| 04 | `04-BAI17-REPLACEMENT.md` | §24 — what replaces `khtn6_bai17.dart` at K-12 scale |
| 05 | `05-KNOWN-DEFECTS.md` | eight defects fixed with regression tests, eight still open |
| 06 | `06-CENSUS.md` | P0.3 — the census, tiers, denominators, how few primitives suffice, which extensions are proven |
| 07 | `07-EXCEPTIONS-AND-STRUCTURE-GAPS.md` | §15 exception clusters ranked by lessons-unlocked · §17 structure gaps |
| 08 | `08-SCOREBOARD.md` | §19 — 25 metrics with denominators, and the recommendation |
| 09 | `09-E2-RECONCILIATION.md` | the four E1↔E2 divergences and how each was resolved |

## Code

| Path | What |
|---|---|
| `tool/semantic/graph.py` | `SemanticClaim` · `SourceGrounding` · `SemanticNode/Relation/Graph` · `provenance_of` · `lineage_of` |
| `tool/semantic/extract.py` | six subject-agnostic rules, TSL → graph candidate |
| `tool/semantic/visualspec.py` | `VisualSpec` + six compilers + `compiler_audit()` |
| `tool/semantic/ontology.py` | the discovered primitives, relations, families and cues |
| `tool/semantic/discover_markers.py`, `probe_cues.py` | the DISCOVER step — every cue cites its measured lesson count |
| `tool/semantic/census.py`, `gaps.py` | P0.3, §15, §17 |
| `tool/semantic/run_poc.py` | the §27 checkpoint run |
| `tool/semantic/verify.py` | grounding integrity over all 238 TSL lessons + a seeded holdout sample |
| `tool/tests/test_semantic_foundation.py` | 58 tests |

Outputs are corpus-derived and stay in the gitignored `poc-out/round5/semantic/` (Founder D4 — no
verbatim SGK text or page crops in the repo).

```
python3 tool/semantic/run_poc.py          # the checkpoint: 2 subjects, 1 extractor
python3 tool/semantic/census.py           # the census
python3 tool/semantic/gaps.py             # structure gaps + exception clusters
python3 tool/semantic/verify.py integrity # does every grounding point where it says?
python3 -m unittest discover -s tool/tests -p "test_*.py"
```
