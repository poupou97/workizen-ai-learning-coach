# H — Next action (what the evidence supports; nothing here is started)

The Founder ordered no new workstream from this round. This page ranks the bounded next steps the slice's evidence justifies, each with the number that would decide it, so the Founder can pick one — or none.

| # | next action | why the slice justifies it | the number it must move | bound |
|---|---|---|---|---|
| H1 | **Adopt the source layer as PROPOSED decisions** (SDM-as-source, block trust, image-first/book-first for math & visual, trusted subset) — knowledge-base PR filed (DECISIONS-REQUESTED.md #1–4) | every stage ran end to end on 1,049 pages, deterministic, 0.854 trusted with reason codes on the rest; nothing downstream can be built on Markdown/units without losing the reason codes | Founder ratification (no measurement) | a PR review |
| H2 | **Icon / box detector for ACTIVITY vs QUESTION** — deterministic, from the page image (KNTT hand / "?" / target icons; box colour under the enumerator), verified against the lexicon | ACTIVITY precision 0.00, QUESTION 0.83–0.89; the missing signal is not lexical (ROLE-LAYER §3) | QUESTION precision ≥ 0.95 and ACTIVITY ≥ 0.8 on ≥ 300 science gold question blocks | 1 week; gold first (≥ 20 pages) |
| H3 | **Science gold to ≥ 300 question blocks** (today 46 science / 116 total) before any semantics decision | 0.970 at n=33 cannot certify 0.95 (lower bound ≈ 0.85) | confidence interval on QUESTION precision | 2–3 days of page reading |
| H4 | **Dart reader for the TSL** (`no_images` mode only) behind a research flag — no View, no routing | F.1: nothing per-block reaches Dart; every View option needs this first | parses 238 TSLs; renders one lesson's `no_images` sequence in the existing Reader with provenance | small; touches `lib/core` only after Founder OK |
| H5 | **False-trust audit on shipped lessons** (statistical, ≥ 3,000 validated blocks) instead of a bigger hard gold | FTR 0.10–0.12 on hard pages is stable across dev/held-out; the < 1 % bar cannot be certified from 54 pages (TC-17 #2) | measured FTR on served blocks with a CI | ongoing, product-side |
| H6 | **SGV pairing on section context + table cells** (not enumerators alone) | 2/26 pairable by enumerator; keys sit in "Đáp án" sections and tables (I.5) | PAIRABLE share on the 75-page sample | 3–5 days |
| H7 | **Denominator refresh** — re-derive canonical + ranged counts corpus-wide with `tc2_attach.py` (cheap: OCR lines only, no Docling) | six books moved 194 → 238 ranged, KHTN 7/8 canonical ≥ 39/47 | new 3,679' and 3,381' with method | 1 day; **needs Founder OK on I.1 first** |

**Explicitly not next:** full-corpus reprocess (not authorised; ≈ 14 h with 2 workers if it ever is — I.7), 27-pattern expansion, Short-Answer Surface (gate not passed), Learning Views implementation, page-image delivery (J.1 open).

**If only one thing is chosen:** H1 + H3 — record the source decisions and grow the science question gold. Every other row depends on one of them.
