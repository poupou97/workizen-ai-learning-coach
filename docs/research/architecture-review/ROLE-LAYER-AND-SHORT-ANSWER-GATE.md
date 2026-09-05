# Role Layer and the Short-Answer gate — is each of the six roles trustworthy enough for safe semantics? (MEASURED)

**Founder order (update item 1):** establish and MEASURE trustworthy semantics for at least QUESTION, ANSWER, ACTIVITY, INSTRUCTION, OBJECTIVE, SIDEBAR; Short-Answer stays DEFERRED; answer per role, with numbers. Target to measure (TC-19 #3): QUESTION precision ≥ 0.95 on gold.

Source: `poc-out/trusted-corpus/tc-v2/tc2-p1/metrics/gold-scores.md` (`tool/corpus/tc2_score.py`, matching = `tc_score.match`, roles over matched blocks as in TC-07). Sets: **dev** = 38 TC-v1 gold pages (the lexicon/guards were calibrated on them); **held-out** = 16 TC-v2 pages written before any tc-v2 gate was scored on them (8 lesson-boundary pages, 5 SGV, 3 diagram/picture); **science** = the 23 gold pages from the six slice books or their SGV counterparts. The labeller is deterministic (lexicon + geometry + colour + XY-cut hint); **no learned or VLM proposer was added**.

## 1. The six roles

| role | dev (38 p) P / R (n gold) | held-out (16 p) P / R (n) | science (23 p) P / R (n) | verdict for safe semantics |
|---|---|---|---|---|
| **QUESTION** | 0.893 / 0.750 (100) | 0.833 / 0.938 (16) | 0.889 / 0.870 (46) | **NOT trustworthy enough to ASK** — precision 0.83–0.89 vs the 0.95 target. Among **TRUSTED** question blocks only (the ones a surface would consume): 0.917 (dev, n=72) · 0.917 (held-out, n=12) · **0.970 (science, n=33)**. The science number touches the bar on a small n; the all-pages number does not |
| **ANSWER** | — / 0.000 (5) | 0.800 / 0.400 (10) | 0.800 / 0.400 (10) | **trustworthy as a BLOCKER, not as content**: every block the labeller calls answer/model_answer is withheld (`answer_leak`), and on the 75-page SGV sample **0 answer-key blocks reach a TSL with text**; recall 0.4 means 6 of 10 gold answers were labelled body/teacher_text — still withheld on SGV pages by `teacher_text`, but on an SGK page a missed "M:" model answer would be served as body |
| **ACTIVITY** | 0.000 / 0.000 (5) | 0.000 / 0.000 (6) | 0.000 / 0.000 (10) | **NOT trustworthy** — the labeller never gets it right. Gold activities (KNTT hand-icon items, "Chuẩn bị/Tiến hành" boxes) come out as question (then withheld as figure-dependent), instruction or body. The activity/question boundary is an icon and a box colour, not a word |
| **INSTRUCTION** | 0.000 / — (0) | 1.000 / 0.500 (6) | 0.500 / 0.500 (6) | **partly**: "Chuẩn bị / Tiến hành / Bước N" markers are precise on SGK pages; on SGV pages the same markers label teacher preparation (the dev false positives are 7 SGV/Toán blocks). Recall 0.5: unmarked numbered steps are missed |
| **OBJECTIVE** | 0.700 / 0.700 (10) | 0.706 / 0.923 (13) | 0.696 / 0.941 (17) | **trustworthy as a BLOCKER** (recall 0.92–0.94: objectives are kept out of questions and passages), **not as content** (precision 0.70: EM CÓ THỂ capability lines and some body lines with "được" are labelled objective) |
| **SIDEBAR** | 0.444 / 0.348 (23) | 0.958 / 0.852 (27) | 0.964 / 0.818 (33) | **trustworthy on the Science family** (0.96 precision on the colour-box conventions of KNTT Khoa học/KHTN); **not** across subjects (0.44 on dev: Toán/Ngữ văn boxes have other colours and labels) |

Other roles for reference (science set): HEADING 0.98 / 0.83 · CAPTION 0.75 / 0.78 · OPTION 1.00 / 1.00 (n=1; 1.00/1.00 on dev n=4) · TABLE 1.00 / 1.00 · FOOTNOTE 1.00 / 1.00 · FIGURE_TEXT 0.43 / 0.82 · TEACHER_PROMPT 1.00 / 0.67 (SGV quoted questions are never emitted as learner QUESTIONs: 0 such events on the 8 SGV gold pages).

## 2. What the false questions are (every one, science + dev)

From `gold-scores.json` → `roles6.false_questions`: 12 blocks on 54 pages.

| gold role | pipeline said QUESTION | trusted? | why |
|---|---|---|---|
| activity ×4 (Khoa học 5 p42/p43, KHTN 9 p38, Vật lí 10 p89) | "3. Quan sát hình 4 và cho biết…", "Quan sát Hình 7.6 và cho biết:" | **withheld** (figure_dependent) | the elementary hand-icon activity is a directive sentence; only the icon distinguishes it |
| instruction ×1 (KHTN 8 p96) | "– Đóng công tắc K. Quan sát hiện tượng… Hiện tượng đó chứng tỏ điều gì?" | trusted | a procedure step ending in "?" — needs the activity-box context |
| heading ×2 (Toán 7 p41, Toán 9 p29) | "Khi nào thì axⁿ chia hết cho bxᵐ?", "Nhận xét. Trong Ví dụ 2…" | trusted | question-form headings / worked-example lead-ins (Toán conventions) |
| body ×3 (Toán 9, Vật lí 10, Ngữ văn 8) | "Bài tập ví dụ: Một ca nô…", "– Ông nghĩ sao?" (dialogue) | trusted | worked example; dialogue line inside a reading |
| caption ×1 (KHTN 9 p46) | "Nhận xét đặc điểm ảnh của vật … theo mẫu Bảng 8.1" | withheld | a table instruction under a figure |
| sidebar ×1 (Vật lí 10 p30) | "1. Tự xác định được tốc độ…" | trusted | EM CÓ THỂ item without the box label in range |

Reading: 5 of the 12 are already **withheld** by a guard (figure-dependent / caption), so a text surface never sees them; the 7 trusted ones are Toán/Vật lí/Ngữ văn conventions (worked examples, question-form headings, dialogue) and one KHTN step. Fixing them needs typography (bold "Nhận xét", italic lead-ins) or the activity-box context — signals the OCR lines do not carry.

## 3. Verdict on the Short-Answer gate

- **QUESTION precision on gold = 0.83–0.89 < 0.95 → the gate is NOT passed; the Short-Answer Surface stays DEFERRED** (Founder item 3 confirmed by measurement).
- The only number that touches the bar is trusted-question precision on the science pages (0.970, n = 33). That is one wrong question in 33 on the pages the slice is about, on a sample too small to certify 0.95 (a 95 % lower bound at 32/33 is ≈ 0.85). It says the Science family is *closer* than the corpus; it does not clear the gate.
- **What "safe QUESTION / ANSWER / ACTIVITY semantics" would still need** (quantified):
  1. an ACTIVITY signal the OCR lines do not have — the KNTT icon (hand / "?" / target) or the box colour under the enumerator; the colour signal exists per block (`colour.share`) but the icon does not. Without it, every elementary "Quan sát hình N và cho biết…" is ambiguous between activity and question: 10 gold activities, 0 correct.
  2. a QUESTION-vs-worked-example distinction for Toán/Vật lí (5 of the 7 trusted false questions) — bold/italic typography, unavailable from Apple Vision lines; Docling's `section_header` label catches some.
  3. ANSWER recall from 0.4 → ≥ 0.9 before any SGK "M:" model answer can be considered safe; today the SGV answer-leak guard holds (0 leaks on 75 pages) but SGK-embedded answers are not measured beyond the 5 dev blocks.
  4. a gold set of ≥ 300 question blocks on the Science family to certify 0.95 with a usable confidence interval (today: 46 science gold questions, 116 in total).

## 4. What the Role Layer IS good for today (so the deferral is not a stop)

- As a **blocker layer** it works: objectives (recall 0.92–0.94), sidebars on the Science family (0.82–0.85), answer keys and teacher text on SGV pages (0 leaks), figure-dependent prompts (withheld), page furniture (PAGENUM 0.94–0.96). These are the roles that keep a passage clean and keep non-questions out of prompts — the WAL-204/206 failure classes.
- As a **reading layer** it is enough for the Hybrid Smart Book in `no_images` mode (C): headings 0.98 precision, body blocks with TLSR 0.64 / FTR 0.10 on science gold.
- As an **asking layer** it is not enough, and no amount of lexicon will get ACTIVITY from 0.00 to 0.95 — that needs a signal the source layer must carry (icon/box detection from the page image, deterministic), which is a bounded next step, not a re-architecture.
