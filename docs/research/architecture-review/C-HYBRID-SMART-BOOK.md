# C — Hybrid Smart Book (research projection; two modes, page images NOT assumed)

**Founder orders:** approve Hybrid Smart Book *for research* — trusted blocks render natively, withheld formulas/diagrams/maps/picture regions stay source crops with provenance (item 5); **and** (update item 2) do **not** assume page-image delivery: the projection must be fully functional with NO page image, withheld region → structured "WITHHELD: <reason> — see SGK page N" reference; report both modes' counts. Page-image licensing is an open LEGAL GATE (J.1).

## C.1 What was built (data only) — `tc2_tsl.py` → `hybridSmartBook`

Both projections are the **same ordered block sequence** of a lesson; they differ only in what a withheld region becomes:

| mode | trusted block | withheld region |
|---|---|---|
| `with_images` | `{kind: native, block: <id>}` | `{kind: source_crop, page, bbox, reason, licence_gate: "page-image delivery UNRESOLVED (OQ8)"}` — a crop the client *would* render **if** J.1 opens |
| `no_images` | `{kind: native, block: <id>}` | `{kind: withheld_ref, reason, page_printed, page_pdf, text: "WITHHELD: <reason> — see SGK page N"}` — fully functional without any image |

No image is stored, cut or delivered by the tooling; the only crops in existence are in the Founder's review bundle (research use).

## C.2 Counts (MEASURED, six books, 238 lessons)

| book | lessons | native blocks (both modes) | withheld regions = `source_crop` (with_images) = `withheld_ref` (no_images) | share of sequence that is withheld |
|---|---|---|---|---|
| Khoa học 4 | 31 | 1,166 | 240 | 17 % |
| Khoa học 5 | 30 | 1,077 | 191 | 15 % |
| KHTN 6 | 53 | 2,441 | 517 | 17 % |
| KHTN 7 | 33 | 1,869 | 323 | 15 % |
| KHTN 8 | 42 | 2,614 | 363 | 12 % |
| KHTN 9 | 49 | 2,804 | 398 | 12 % |
| **total** | **238** | **11,971** | **2,032** | **14.5 %** |

Withheld regions by reason (what a `withheld_ref` would say): agree_text 865 (43 %) · figure_dependent 638 (31 %) · agree_order 229 · page_feature:diagram 199 · page_feature:color_heavy 111 · box_boundary 95 · math_guard 42 · answer_leak 30 · low_ocr_conf 20 · role_conflict 7.

Reading: **in `no_images` mode a Science lesson renders ≈ 85 % of its learning blocks natively and shows ≈ 8 "see SGK page N" references per lesson** (median). The two biggest reference classes are the two the Founder named: text the verifier could not confirm (agreement) and prompts that need a figure. Nothing in the `no_images` sequence depends on an image — the reference carries the printed page number the child's own book has.

## C.3 What the two modes mean for the legal gate

- `no_images` is what can be built **now** under `ContentLicense.localResearchOnly` semantics for text (still a derivative work — J.2), with the book itself as the "image".
- `with_images` is a **research hypothesis** whose only unknown is J.1; the data needed to render it (page + bbox + reason) is already in every TSL, so opening the gate later is a client change, not a pipeline change.
- Neither mode contains a formula, a table cell grid or a diagram label as *text* (math_guard / figure_text / page_feature) — consistent with "image-first for math/visual" (decision record 3 in DECISIONS-REQUESTED.md), which under `no_images` degrades to "book-first".

## C.4 Where the Smart Book would be wrong today (MEASURED on gold)

FTR 0.100–0.121 on hard pages means ≈ 1 native block in 10 on such pages carries a text, order or splice error; on plain-prose pages ≈ 0 (TC-08). The `no_images` mode makes this *visible* only if the surface shows uncertainty (WAL-207 `15` §6 "uncertainty must look uncertain") — the TSL gives it `role.confidence`, `agreement.text_sim` and `ocr_conf` per block to do so.

## C.5 Not done

No rendering, no Flutter, no reflow, no bookmarks, no "Smart Book = lookup" decision (F.4).
