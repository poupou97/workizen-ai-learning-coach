# ROLE DEFINITION SPEC v1 — what each block role MEANS, what it teaches, what it is trusted to do

Round 5 · Lane A3 · Founder order §7 · 2026-09-06 · **status: SPEC + RE-ANNOTATION. No classifier was
trained, tuned or edited.** `tool/corpus/tc2_sdm.py` was read, never written. Verbatim SGK stays internal
(D4): every example below quotes at most a fragment, always with its book · page · block id so it can be
looked up in the gitignored corpus.

**Why this document exists.** Round 4 measured inter-annotator agreement on five audit classes with two
blind annotators. False trust **κ 1.000**, attachment **1.000**, teaching-critical **1.000**, display
**0.842** — and role **0.423 – 0.713**. Three of the four role disagreements were about *what a role
means*, not about what is printed on the page. A better classifier cannot fix that; a written definition
can. §8 re-annotates the disagreement sample against this spec and reports what moved.

---

## 1. The vocabulary, and the three vocabularies it has to reconcile

| layer | where it lives | roles |
|---|---|---|
| **spec (this document)** | here | the Founder's 20: HEADING · BODY · QUESTION · OPTION · ANSWER · CAPTION · SIDEBAR · TABLE · FORMULA · FIGURE · FIGURE_TEXT · FOOTNOTE · ATTRIBUTION · OBJECTIVE · ACTIVITY · RULE · SPEECH_BUBBLE · RUNNING_HEAD · PAGENUM · UNKNOWN |
| **gold** | `tool/corpus/tc_gold/*.json` (54 pages) + `tc_gold_bai17/` (4 pages) | 21 fine roles, `tc_sdm.GOLD_ROLE_MAP` |
| **pipeline** | `tc2_sdm.assign_role` → `tc2_sdm.COARSE` | 25 fine roles |

**Mapping — and the four holes it exposes.**

| spec role | pipeline fine role(s) | gold fine role(s) | gold blocks (54 pages, 759 total) |
|---|---|---|---|
| HEADING | `heading` · `stage_label` | `heading` | 167 |
| BODY | `body` | `body` | 158 |
| QUESTION | `question` (SGV: `teacher_prompt`) | `question` | 122 |
| OPTION | `option` · `answer_slot` | `option` · `answer_slot` | 7 |
| ANSWER | `answer` · `model_answer` | `answer` | 16 |
| CAPTION | `caption` | `caption` | 35 |
| SIDEBAR | `sidebar` | `sidebar` | 50 |
| TABLE | `table` | `table` | 20 |
| FORMULA | `formula` | `formula` | 19 |
| FIGURE | `figure` | (bbox only, no text) | — |
| FIGURE_TEXT | `figure_text` | `figure_label` · `diagram` | 31 |
| FOOTNOTE | `footnote` | `footnote` | 14 |
| ATTRIBUTION | `attribution` (SGV: `teacher_text`) | `attribution` | 8 |
| OBJECTIVE | `objective` | `objective` | 23 |
| ACTIVITY | `activity` · `instruction` | `activity` · `instruction` | 17 |
| **RULE** | **— never emitted** | `rule` | 3 |
| **SPEECH_BUBBLE** | **— never emitted** | `speech_bubble` | 11 |
| RUNNING_HEAD | `running_head` | `running_head` | 4 |
| PAGENUM | `page_number` | `page_number` | 54 |
| UNKNOWN | `empty` | — | — |

**Hole 1 — `rule` is in the pipeline's `COARSE` map but no branch of `assign_role` ever returns it.**
All 3 gold RULE blocks arrive as `body` (`09-sgk-toan-9-tap-mot` p29 b10 TRUSTED · `12-sgk-toan-12-tap-hai`
p20 b15 WITHHELD `math_guard` · `07-sgk-toan-7-tap-hai` p41 b07 CONFLICT). A theorem is served as prose.

**Hole 2 — SPEECH_BUBBLE has no pipeline role at all,** and it is the most expensive hole in the set:
5 of the 11 gold speech bubbles land in `figure_text`, which is **withheld unconditionally**. On
`03-sgk-toan-3-tap-mot` p32 the bubble that carries the lesson's actual word problem (b05) and the bubble
that carries its reasoning hint (b10) are both withheld as figure text. The teaching content of the page
is in the bubbles; the pipeline classifies them as decoration.

**Hole 3 — the spec's 20 has no slot for INSTRUCTION,** although `tc2_score.py` treats INSTRUCTION as one
of "the Founder's six" scored roles and the pipeline emits it. This spec folds INSTRUCTION into ACTIVITY
(§ACTIVITY) and flags the merge as **Q-ROLE-3**: it changes what the scoreboard's INSTRUCTION row means.

**Hole 4 — the spec's 20 has no slot for the SGV roles** `teacher_text`, `teacher_prompt`, `model_answer`,
nor for `stage_label`. This spec treats them as *document-type variants* of existing roles (§SGV rule),
not as separate roles.

---

## 2. How to read a role entry

Each role below carries the eight fields the Founder ordered:

**semantic definition** · **inclusion criteria** · **exclusion criteria** · **positive examples**
(book · page · block id) · **confusing counterexamples** (the measured confusions — these are what the
annotators split on) · **relationship rules** · **teaching consequence** (what SAM is allowed to do with a
block of this role) · **default trust consequence** (what `tc2_sdm.py` actually does today, and where that
looks wrong for the definition — flagged ⚠, never silently fixed).

The confusion counts come from the tc2-p2 run on the 54 gold pages
(`poc-out/round4/pipeline/tc2-p2/sdm-gold`, scored by `tc2_score.py`); the confusion direction is written
**gold → pipeline**.

---

## 3. The trust machinery every "default trust consequence" refers to

From `tc2_sdm.py`, read on `integration/round5-2026-09-06`:

- `COLOUR_HEAVY_EXEMPT = (heading, stage_label, page_number, running_head, caption, figure, empty)` — these
  roles ignore the colour-heavy guard entirely.
- `VERSE_EXEMPT = (heading, stage_label, page_number, running_head, figure_text, figure, empty, table)` —
  these ignore `line_structure`.
- `math_guard` / `unit_guard` / `chem_guard` are **skipped for** `formula`, `table`, `figure`, `empty`
  (`chem_guard` additionally for `page_number`, `running_head`).
- `figure_dependent` fires only for `question`, `activity`, `instruction`, `teacher_prompt`.
- `answer_leak` fires for `answer`, `model_answer`, or any text carrying an inline answer marker.
- `teacher_text` guard fires for `teacher_text`, `teacher_prompt`.
- `furniture` fires for `page_number`, `running_head`; `figure_text` fires for `figure_text`.
- `trust_status`: `figure` and `empty` are **always** WITHHELD.
- `NON_LEARNING = {page_number, running_head, figure, figure_text, empty}` — never counted as learning text.
- A `heading` becomes the `heading_path` of every block that follows it in the lesson.

**The load-bearing fact: guards are a pure function of the role.** Getting the role wrong does not merely
mislabel a block — it changes which guards can protect it. Four of the roles below carry a ⚠ because the
consequence the code attaches does not match the definition this spec writes.

---

## 4. The 20 roles

### HEADING
- **Semantic definition.** A printed line whose job is to *name* a span of the page — a lesson banner, a
  chapter/theme banner, a numbered or lettered section title, a stage label (KHỞI ĐỘNG · LUYỆN TẬP ·
  VẬN DỤNG · GHI NHỚ). It asserts nothing a child could be tested on; it locates.
- **Inclusion.** `Bài N` / `CHỦ ĐỀ N` / `CHƯƠNG N` banners; a short line set in display type above the text
  it names; a roman or arabic section numeral followed by a title-case phrase; a stage label.
- **Exclusion.** A line that ends in `?` (→ QUESTION). A line that opens with a bracket (→ ATTRIBUTION or
  BODY). A short uppercase line that is a *table column header* (→ TABLE). A short uppercase line inside a
  figure (→ FIGURE_TEXT). A sidebar's own label (`Em có biết?`, `Ghi nhớ`) is a HEADING **only** when the
  sidebar body is a separate block; when label and body are one block the block is SIDEBAR.
- **Positive examples.** `04-sgk-toan-4-tap-hai` p81 b01 «PHÉP TRỪ PHÂN SỐ» · `06-sgk-khoa-hoc-tu-nhien-6`
  p63 «3. Chiết» · `10-sgk-vat-li-10` p30 b01 «CHƯƠNG II – ĐỘNG HỌC» (this one is a RUNNING_HEAD, see there).
- **Confusing counterexamples (measured).**
  - **HEADING → FIGURE_TEXT, 27 blocks — the largest single confusion in the corpus.** A heading printed on
    a coloured banner is swallowed by the layout parser's picture box: `02-sgk-tieng-viet-2-tap-hai` p14 b11
    «VIẾT», `02-sgk-toan-2-tap-hai` p48 b02 «SO SÁNH CÁC SỐ TRÒN TRĂM, TRÒN CHỤC». All are withheld.
  - **HEADING → BODY, 11.** `05-sgk-toan-5-tap-mot` p92 b06 «Hình tam giác» — a section title that reads
    like a noun phrase.
  - **SIDEBAR → HEADING, 6.** `09-sgk-ngu-van-9-tap-mot` p67 b08 «Theo dõi / Sự xuất hiện của nhân vật Kim
    Trọng.» — a margin prompt whose first line looks like a label.
  - **ANSWER → HEADING, 3 — and all three are served TRUSTED.** `04-sgv-toan-4` p54 b07–b09
    «Bài 1: Bài tập này giúp HS củng cố…» is SGV commentary that carries the answer; the `Bài N:` opening
    makes it a heading, and the heading role has no `answer_leak` guard.
- **Relationship rules.** A HEADING opens a span; every following block until the next HEADING of equal or
  higher level inherits it as `heading_path`. A HEADING never has a parent inside the page. A HEADING is
  never the child of a FIGURE.
- **Teaching consequence.** SAM may use a HEADING to *name* what the child is looking at and to build the
  lesson outline. SAM must never ask a question whose expected answer is a heading, and must never quote a
  heading as a statement of fact.
- **Default trust consequence.** `heading` is `COLOUR_HEAVY_EXEMPT`; it becomes the `heading_path` of every
  later block; it is a learning role. ⚠ **A wrong HEADING is more expensive than any other wrong role**,
  because it is exempt from the colour guard *and* it propagates: the round-4 correctness review already
  found an uppercase `(THEO …)` source line becoming a heading and therefore the `heading_path` of a whole
  lesson. The `ANSWER → HEADING` cases above are the same failure with a worse payload — SGV answer text
  entering the child's path with every answer guard bypassed.

### BODY
- **Semantic definition.** The lesson's own running prose: what the book *says*, addressed to the reader,
  outside any box, bubble, table, figure or margin.
- **Inclusion.** Continuous sentences in the main column; verse lines of a poem printed in the main column
  (the spec has no VERSE role — see relationship rules); a worked example's *narrative* framing.
- **Exclusion.** Text inside a tinted or ruled box (→ SIDEBAR). Text inside a figure (→ FIGURE_TEXT). A
  bracketed source line (→ ATTRIBUTION). A glossary line under a rule (→ FOOTNOTE). A statement the book
  marks as a rule or theorem (→ RULE). A solved example's *solution* (→ ANSWER).
- **Positive examples.** `05-sgk-tieng-viet-5-tap-mot` p124 «Trông trời, trông đất, trông mây» (a verse
  line) · `09-sgk-tin-hoc-9` p20 b04.
- **Confusing counterexamples (measured).**
  - **QUESTION → BODY, 17 — the second-largest confusion.** `02-sgk-tieng-viet-2-tap-mot` p103 b10–b11
    «1. Nói tiếp để hoàn thành câu:…», «2. Đặt một câu nói về trò chơi em thích.» — enumerated tasks that
    do not end in `?` and carry no directive verb the lexicon knows. **Both are TRUSTED**, i.e. served to a
    child as prose when they are tasks.
  - **BODY → SIDEBAR, 9** and **SIDEBAR → BODY, 8** — the box boundary is invisible to the text.
    `10-sgk-vat-li-10` p30 b12 «Tốc độ trung bình» (body → sidebar, TRUSTED); `06-sgk-tin-hoc-6` p21 b15
    (sidebar → body, TRUSTED).
  - **FOOTNOTE → BODY, 3, all TRUSTED.** `02-sgk-tieng-viet-2-tap-hai` p14 b02 «– Cá ròng ròng (cá lòng
    ròng): loài cá lóc nhỏ…» — a glossary gloss served as if it were the passage.
  - **ACTIVITY → BODY, 5, all TRUSTED.** `05-sgk-khoa-hoc-5` p42 b03–b05 «4. Chia sẻ với bạn về:» and its
    dash items.
- **Relationship rules.** BODY has no children. Verse is BODY with a **line-structure flag**: the printed
  line breaks carry meaning, so the block must not be reflowed into a paragraph (this is what the round-4
  `line_structure` guard exists for). An ATTRIBUTION that follows a BODY passage belongs to it.
- **Teaching consequence.** SAM may quote BODY verbatim as source text and may build explanations on it.
  It is the default source for `SourceQuoteIndex`.
- **Default trust consequence.** `body` is the *fallback* role — `assign_role` returns it with confidence
  **0.60** when nothing else matched. It carries no exemption and every content guard applies. ⚠ The
  fallback is the problem, not the guards: 84 of the 354 blocks the pipeline serves on the gold set are
  `body` at confidence 0.60, i.e. "we could not tell". A gate keyed on role confidence removes exactly
  these (§TRUST-GATE-SENSITIVITY, the 0.6 → 0.7 step).

### QUESTION
- **Semantic definition.** A printed unit that asks the child to produce something — an answer, a choice, a
  sentence, a calculation. Its defining property is that the book expects a response.
- **Inclusion.** Any line ending in `?`. An enumerated item opening with a directive verb (`Nêu`, `Tính`,
  `Viết`, `So sánh`, `Cho biết`, `Đặt câu`…). A stem ending in `:` **when options follow**. A lead-in
  `… em hãy:` and the dash sub-items under it.
- **Exclusion.** A rhetorical `…?` inside running prose (→ BODY). A question-form section title (→ HEADING).
  A worked example's lead-in (→ ANSWER). In an SGV, a quoted prompt addressed to the teacher
  (→ QUESTION with `docType = SGV`, emitted as `teacher_prompt`).
- **Positive examples.** `05-sgk-tieng-viet-5-tap-hai` p11, audit row `n20260906-0072` «4. Đặt 1 – 2 câu ghép nói về
  nhân vật Nai Ngọc…» · `06-sgk-tin-hoc-6` p21 b08 «1. Em hiểu Internet là gì?» · `07-sgk-khoa-hoc-tu-nhien-7` p32 b07
  (stem + A–D options).
- **Confusing counterexamples (measured).**
  - **QUESTION → BODY, 17** (above) — under-detection, and the expensive direction: a task served as prose.
  - **BODY → QUESTION, 4.** `09-sgk-toan-9-tap-mot` p29 b01 «Nhận xét. Trong Ví dụ 2» and
    `10-sgk-vat-li-10` p30 b03 «Bài tập ví dụ: Một ca nô chạy…» — both TRUSTED. These are the
    `nonquestion_as_question` critical-teaching class: **6 of the 26 wrong blocks the pipeline serves on the
    gold set are exactly this**, and 6 of the 12 teaching-critical served blocks sit on the `question` role.
  - **ACTIVITY ↔ QUESTION, 3 each.** `05-sgk-khoa-hoc-5` p42 b01 «3. Quan sát hình 4 và cho biết…» is an
    activity in gold and a question in the pipeline; `09-sgk-toan-9-tap-mot` p29 b07 «HĐ3 Chuyển các biểu
    thức…» is the reverse. The boundary is genuinely fuzzy — see ACTIVITY.
  - The role-signal experiment measured QUESTION precision **0.938 at n = 16** held-out and **0.727 on the
    Bài 17 showcase lesson**: 3 of 11 blocks the pipeline asked as questions there were not questions.
- **Relationship rules.** A QUESTION may own OPTION children (A–D), ANSWER_SLOT children (`?`, blanks) and,
  in an SGV, an ANSWER. A QUESTION that names a figure (`Quan sát hình 4…`) depends on that FIGURE and
  cannot be answered from text alone.
- **Teaching consequence.** The only role SAM may present as a prompt. TC-19 #3 requires **precision ≥ 0.95
  before any auto-labelled question is graded**; that bar is not met, so Short Answer stays deferred and no
  auto-labelled question is graded today.
- **Default trust consequence.** `question` triggers `figure_dependent` when the text refers to a figure —
  the only role (with `activity`/`instruction`/`teacher_prompt`) that does. It is not colour-exempt. This
  is correct for the definition: a question whose figure the child cannot see is unanswerable.

### OPTION
- **Semantic definition.** One of the printed alternatives a multiple-choice QUESTION offers, or the blank
  the child fills. Meaningless on its own.
- **Inclusion.** A line opening `A.` `B.` `C.` `D.` (or `A)` …) directly under a stem. A bare `?` or a run
  of dots/underscores standing where an answer goes (`answer_slot`). A word-bank cell offered as a choice.
- **Exclusion.** `A.` as a section enumerator in a heading. `a)` `b)` as *sub-item* enumerators of an
  exercise (those items are QUESTION or FORMULA, not OPTION).
- **Positive examples.** `07-sgk-khoa-hoc-tu-nhien-7` p32 b07 «A. Kim loại và phi kim / B. …» TRUSTED ·
  `09-sgk-tin-hoc-9` p20 b08 · `02-sgk-toan-2-tap-hai` p48 b19 «? ? ?» (an `answer_slot`).
- **Confusing counterexamples (measured).** OPTION scores precision 1.00 / recall 1.00 on the gold set —
  but on only 4 matched blocks. **2 of the 6 gold OPTION blocks are not matched at all**:
  `02-sgk-tieng-viet-2-tap-hai` p14 b08 «dầm dề | rả rích | sướt mướt | dai dẳng» and
  `04-sgk-tieng-viet-4-tap-mot` p28 b09 — word banks printed as a row of cells, which the extractor
  flattens into one string. A perfect score on a role the pipeline mostly cannot see is not a good score.
  And `02-sgk-toan-2-tap-hai` p48 b19 «? ? ?» is classified **`empty`** and withheld (see UNKNOWN ⚠).
- **Relationship rules.** **An OPTION always belongs to a QUESTION.** An OPTION with no QUESTION parent is
  a defect, not a block. This relation is the one exemption to the extent rule in §7 — a served region
  containing a stem *and* its options is one unit, not a role error.
- **Teaching consequence.** SAM may present OPTIONs only together with their QUESTION, and must present
  **all** of them or none — a subset changes the item. SAM must never reveal which one is correct unless an
  SGV ANSWER says so.
- **Default trust consequence.** `option` and `answer_slot` map to coarse OPTION; no exemption, all guards
  apply. Correct for the definition. ⚠ but see UNKNOWN: an `answer_slot` made of punctuation only is
  reclassified `empty` and withheld, so the child never sees that a blank exists.

### ANSWER
- **Semantic definition.** Text that states the expected response to a question — a model answer, a worked
  solution, an answer key, or a teacher-book commentary that gives the answer away.
- **Inclusion.** `Đáp án` · `Lời giải` · `Gợi ý trả lời` · `Trả lời` · `Hướng dẫn giải` · `M:` markers; the
  solution half of a worked example (`Mẫu`, `Ví dụ N` with its computation, the `Thử lại` check lines);
  any block inside an SGV `Đáp án` section.
- **Exclusion.** The *statement* of the worked example (its data and its question) — that is QUESTION or
  FORMULA. A `Nhận xét`/`Kết luận` that generalises rather than answering (→ RULE or BODY).
- **Positive examples.** `02-sgk-tieng-viet-2-tap-mot` p103 b12 «M: Rồng rắn lên mây là một trò chơi vui
  nhộn.» · `02-sgk-tieng-viet-2-tap-hai` p14 b10 «M: ào ào» · `04-sgv-khoa-hoc-4` p28 b04.
- **Confusing counterexamples (measured).**
  - **ANSWER → BODY, 6** and **ANSWER → HEADING, 3.** The heading cases (`04-sgv-toan-4` p54 b07–b09) are
    the dangerous ones: **served TRUSTED, with `answer_leak` bypassed**, because the guard keys on the role
    and the role became `heading`.
  - ANSWER recall on the gold set is **0.267** (4 of 15 matched gold answers found), precision 0.800. The
    role that must never leak is the role the pipeline finds least often.
  - **The worked-example boundary is where the two round-4 annotators split twice** (§8, rows
    `s20260905-0162` and `s20260905-0391`): a `Mẫu`/`Ví dụ` box served as an `exercise`. One annotator read
    "it is inside an exercise", the other "it is a solution". This spec rules: **a printed solution is
    ANSWER, whatever it is printed inside.**
- **Relationship rules.** An ANSWER belongs to a QUESTION (or to a worked example's statement). **An ANSWER
  may only exist in an SGV or in an explicitly printed answer section of an SGK** — an ANSWER discovered in
  SGK body flow is either a model answer the book prints on purpose (`M:`) or a misclassification.
- **Teaching consequence.** SAM must **never** show an ANSWER to a child before the child has answered, and
  never as source text. An ANSWER is usable only as a *validator* — and only where the SGK/SGV states the
  fact, which for Bài 17 it does not (round 4 registered zero validators, honestly).
- **Default trust consequence.** `answer` / `model_answer` raise `answer_leak` → WITHHELD. Correct for the
  definition. ⚠ but the guard is role-keyed, so every ANSWER the classifier misses (11 of 15 on gold) is
  unguarded, and the three that became `heading` are additionally colour-exempt.

### CAPTION
- **Semantic definition.** The printed label of a figure, table or diagram: it names or explains the
  picture, and it is meaningless when separated from it.
- **Inclusion.** `Hình N` · `Bảng N` · `Sơ đồ N` · `Biểu đồ N` · `Lược đồ N` · `Tranh N` · `Ảnh N`, alone or
  followed by a naming phrase; the continuation sentence of such a label when it is printed as part of it.
- **Exclusion.** A sentence *in the prose* that mentions a figure (`Hình 20.1 mô tả cấu tạo…` is BODY —
  it is a sentence of the lesson that happens to reference a figure). A label printed *inside* the picture
  area (→ FIGURE_TEXT). A source line under a figure (→ ATTRIBUTION).
- **Positive examples.** `05-sgk-khoa-hoc-5` p17 «Hình 5» · `06-sgk-khoa-hoc-tu-nhien-6` p061 block 012
  «Hình 17.1».
- **Confusing counterexamples (measured).**
  - **CAPTION → FIGURE_TEXT, 5.** `04-sgk-khoa-hoc-4` p30 b08 «Hình 1», `07-sgk-khoa-hoc-tu-nhien-7` p97
    b13 «Hình 20.1 Cấu tạo của nam châm điện» — the caption sits inside the grown picture box and is
    withheld. Round 4 fixed the *reverse* case (a caption's continuation staying withheld while the label
    was trusted); this direction remains.
  - **BODY → CAPTION, 3, all TRUSTED — and this is a trust gain the definition does not justify.**
    `04-sgk-khoa-hoc-4` p78 b01 «Bước 5. Nướng bánh ở nhiệt độ khoảng từ 170 °C đến 2…» is a *procedure
    step* served as a caption; `07-sgk-khoa-hoc-tu-nhien-7` p97 b09 «Hình 20.1 mô tả cấu tạo của một nam
    châm điện:» is a *sentence of the lesson* served as a caption.
  - **ATTRIBUTION → CAPTION, 1, TRUSTED.** `07-sgk-khoa-hoc-tu-nhien-7` p26 b05 «(Nguồn:
    https://iupac.org/…)».
- **Relationship rules.** **A CAPTION belongs to exactly one FIGURE or TABLE**, decided by geometry
  (`caption_for_picture`), never by reading-order distance — round 4 changed this precisely because a wrong
  caption is worse than no caption. A FIGURE may have zero or one CAPTION. A CAPTION is never a child of a
  QUESTION.
- **Teaching consequence.** SAM may use a CAPTION to say what a picture shows, and may cite it as the
  picture's name. SAM must never present a CAPTION as a fact of the lesson, and must never quote a caption
  as if it were body prose.
- **Default trust consequence.** ⚠ **`caption` is `COLOUR_HEAVY_EXEMPT`.** The exemption is right for a
  real caption (captions are printed on tinted panels) and wrong for the three BODY blocks above, which
  acquire a colour exemption by being mislabelled. This is the clearest case in the corpus of *the code's
  trust consequence not matching the definition*: the exemption should follow "is printed on a figure
  panel", a geometric fact, not "was labelled caption", a classifier output.

### SIDEBAR
- **Semantic definition.** A bounded aside printed beside or within the main flow — `Em có biết?`,
  `Ghi nhớ`, `Lưu ý`, `Chú ý`, `Mở rộng`, `Kết nối`, `Em đã học`, `Em có thể` — carrying content that is
  *about* the lesson rather than *in* its argument.
- **Inclusion.** Any block whose own label is a sidebar label; any block geometrically inside a labelled
  tinted box; a narrow right-hand block on colour.
- **Exclusion.** A tinted box that states a rule the child must learn (→ RULE). A tinted box listing what
  the child will be able to do (→ OBJECTIVE). A speech bubble (→ SPEECH_BUBBLE). The main column's prose,
  even when the page as a whole is heavily coloured.
- **Positive examples.** `08-sgk-lich-su-va-dia-li-8` p71 b09 «Em có biết? / Hô-xê Ri-dan…» ·
  `07-sgk-khoa-hoc-tu-nhien-7` p96 b01–b02.
- **Confusing counterexamples (measured).** SIDEBAR precision 0.738 / recall 0.620 — the loosest of the
  named roles. **SIDEBAR → BODY 8** (the box vanishes), **BODY → SIDEBAR 9** (a box appears),
  **SIDEBAR → HEADING 6**, **SIDEBAR → OBJECTIVE 4** — `04-sgk-khoa-hoc-4` p9 b12 «Giải thích được việc làm
  khơi thông miệng hố ga góp…» is a sidebar whose sentence matches the objective lexicon (`verb + được`),
  and it is **TRUSTED as an objective**. The role-signal experiment left SIDEBAR unchanged (0.958/0.852
  held-out with and without the icon signal): colour alone does not carry the box boundary. A real
  **box detector** is the missing primitive, named in that experiment §5.
- **Relationship rules.** A SIDEBAR owns its own label; it is never the child of a QUESTION or a FIGURE.
  A SIDEBAR must never be spliced into a BODY passage — that is the `box_boundary` failure class.
- **Teaching consequence.** SAM may offer a SIDEBAR as an aside ("the book also says…"), and may use
  `Ghi nhớ` as a summary. SAM must not treat a SIDEBAR as part of the passage a comprehension question is
  about, and must not read it in the middle of a reading.
- **Default trust consequence.** `sidebar` is **not** colour-exempt, so a genuine sidebar on a tinted panel
  is withheld by `page_feature:color_heavy` unless its own measured colour share is below 0.25 (round 4
  moved the measurement from the page to the block for exactly this reason). It is subject to
  `page_feature:diagram`. This is defensible but it means **the role most often printed on colour is the
  role least protected from the colour guard**.

### TABLE
- **Semantic definition.** A printed grid whose meaning is carried by the alignment of its cells: the
  relation between a row and a column is data, not layout.
- **Inclusion.** Anything the layout parser emits as a table object; a ruled grid; a two-column
  term/definition matching block; a timetable.
- **Exclusion.** Two columns of running prose (that is layout, → BODY). A word bank printed as cells
  (→ OPTION). A figure containing a small labelled grid (→ FIGURE_TEXT).
- **Positive examples.** `01-sgk-tu-nhien-va-xa-hoi-1` p6 b01 (a 3-column TOC table) ·
  `04-sgk-khoa-hoc-4` p10 b12 «Sự chuyển thể của nước | Hiện tượng».
- **Confusing counterexamples (measured).** TABLE precision 1.000, recall **0.550** — the pipeline never
  claims a table it does not have, and misses nearly half. **TABLE → FIGURE_TEXT, 8:**
  `03-sgk-toan-3-tap-mot` p32 b08–b09 «Bảng nhân 7» / «Bảng chia 7» — the multiplication tables of a
  grade-3 lesson, withheld as figure text. `05-sgk-lich-su-va-dia-li-5` p41 b07 «Sự kiện» is a column
  header read as figure text. The audit's `table_flattened` class (22 rows on the shipped sample) is the
  serving-side face of the same problem: a flattened table becomes false statements
  («Danh từ Từ chỉ hoạt động…»).
- **Relationship rules.** A TABLE may own a CAPTION. Its cells are not blocks; a served TABLE must carry
  its cell structure or be withheld — a table flattened to a string is not a table.
- **Teaching consequence.** SAM may read a value *at a named row and column*. SAM must never read a
  flattened table row-wise as prose; that is how «Góc nhọn bé hơn Góc tù lớn hơn» was produced.
- **Default trust consequence.** `table` skips `math_guard`/`unit_guard`/`chem_guard` and is
  `VERSE_EXEMPT`. Defensible: a table legitimately contains bare numbers and units, and its line breaks are
  structural. ⚠ The exemption is only safe **while the cell structure survives**. The pipeline stores
  `cells`, but a downstream consumer that reads `text` gets the flattened string with the math guards
  already waived. The exemption should be conditioned on cells being present.

### FORMULA
- **Semantic definition.** A standalone mathematical or chemical expression printed as an object of the
  lesson — an equation, a comparison, an identity, a formula statement.
- **Inclusion.** A line consisting of numbers, operators, relations, fractions, exponents and at most a
  minimal enumerator; a displayed equation; a chemical equation.
- **Exclusion.** A sentence containing a number (→ BODY / QUESTION). An expression printed inside a figure
  (→ FIGURE_TEXT). A table cell (→ TABLE).
- **Positive examples.** `02-sgk-toan-2-tap-hai` p48 b06 «200 < 300 / 300 > 200» ·
  `05-sgk-toan-5-tap-mot` p21 b08 «1/5 + 1/2 = ? (l)» · `12-sgk-toan-12-tap-hai` p20 b15.
- **Confusing counterexamples (measured).** **FORMULA precision — / recall 0.000. The pipeline emits the
  role zero times on 54 gold pages.** Where do the 19 gold formulas go?
  - **FORMULA → EMPTY, 8.** `02-sgk-toan-2-tap-hai` p48 b06, b08–b12: «200 < 300», «120 > 110», «250 < 350»,
    «610 > 590». `assign_role`'s second test is
    `if not t or not LETTERS.search(t) and not DIGITS.match(t): return 'empty'`, and `DIGITS` is
    `^\d{1,3}$` — so **any line with no letters that is not a bare 1–3 digit number is classified `empty`
    and withheld with `empty_block`.** Every printed arithmetic comparison in a grade-2 lesson is
    "an empty block".
  - **FORMULA → FIGURE_TEXT, 4.** `03-sgk-toan-3-tap-mot` p32 b06 «7 × 2 = ? / 7 + 7 = 14 …» —
    the derivation of the times table, withheld as figure text.
- **Relationship rules.** A FORMULA may be the body of a RULE, an item of a QUESTION, or the solution of an
  ANSWER; its role does not change with its parent. **This is Q-ROLE-2** (§9): a bare printed expression
  that *is* an exercise item — is it FORMULA or QUESTION? The gold vocabulary says FORMULA; the pack
  vocabulary says `exercise`; the two round-4 annotators used the pack reading.
- **Teaching consequence.** SAM may state a FORMULA and may ask the child to apply it. SAM must never
  paraphrase one, and must never serve one whose structure was flattened — `b) 10 +` for
  `b) 3/10 + 5/21` is the canonical failure.
- **Default trust consequence.** ⚠ **`formula` skips `math_guard`, `unit_guard` and `chem_guard`** — the
  three guards that exist to catch destroyed mathematics. That is correct only if the formula arrives as
  *structure*. It arrives as a flattened string. So the spec's own correct answer for
  `n20260906-0040` («b) 3/10 + 5/21» served as `body`) would, if the classifier acted on it, have
  **removed the guard that should have caught the damage**. The definition and the code's consequence point
  in opposite directions here. Recommendation (for whoever owns the classifier, not for this lane): make
  the math-guard exemption conditional on a structured representation, not on the role name.

### FIGURE
- **Semantic definition.** The printed image itself: a photograph, drawing, map, or diagram area. It has a
  bounding box and no text of its own.
- **Inclusion.** Every picture object the layout parser reports.
- **Exclusion.** Text printed inside the picture (→ FIGURE_TEXT). The picture's label (→ CAPTION).
- **Positive examples.** Recorded as `figures[]` on every SDM page; the gold set annotates figure regions
  by bbox rather than text, so no gold FIGURE row appears in the role table.
- **Confusing counterexamples.** The systematic error is not mislabelling a figure but **the picture box
  growing over its neighbours** — the mechanism behind HEADING → FIGURE_TEXT (27), TABLE → FIGURE_TEXT (8),
  CAPTION → FIGURE_TEXT (5), SPEECH_BUBBLE → FIGURE_TEXT (5) and FORMULA → FIGURE_TEXT (4). **A single
  geometry error is the largest role failure in the corpus, and it presents as five different confusions.**
- **Relationship rules.** A FIGURE may own one CAPTION and any number of FIGURE_TEXT children. A QUESTION
  that names a figure depends on it.
- **Teaching consequence.** SAM may point at a FIGURE (it keeps its bbox, so a withheld region can still be
  shown as an image — this is what makes withholding survivable). SAM may not describe a figure it has not
  been given a description of.
- **Default trust consequence.** `figure` is **always** WITHHELD (`trust_status` hard rule) and is
  NON_LEARNING. Correct: an image is not text.

### FIGURE_TEXT
- **Semantic definition.** Text printed *inside* a figure whose meaning depends on its position in the
  picture — an axis label, a part name, an arrow legend, a value on a diagram.
- **Inclusion.** Short labels geometrically inside a picture bbox; legends; measurement annotations.
- **Exclusion.** **Anything inside a picture bbox that is a self-contained sentence, a question, a heading,
  a table or a speech bubble.** The bbox is evidence, not proof: a picture box that has grown over a
  neighbour does not turn that neighbour into figure text.
- **Positive examples.** Genuine cases exist (the gold `figure_label` / `diagram` roles, 31 blocks) but the
  pipeline's own FIGURE_TEXT precision is **0.288** on 73 predictions — 52 of the 73 blocks it calls figure
  text are something else.
- **Confusing counterexamples (measured).** FIGURE_TEXT has **117 unmatched pipeline blocks** on the gold
  set — the largest unmatched count of any role — plus the 27 + 8 + 5 + 5 + 4 confusions listed under
  FIGURE. Concretely: `03-sgk-toan-3-tap-mot` p32 b05 «Mỗi đội chơi kéo co có 7 bạn. Hỏi 2 đội chơi kéo co
  có bao n…» is the lesson's word problem, withheld as figure text.
- **Relationship rules.** FIGURE_TEXT is always the child of a FIGURE. It is never quotable on its own.
- **Teaching consequence.** SAM must not read FIGURE_TEXT as prose. It may use it only together with the
  image it annotates. The round-3 audit's `figure_text` display class (66 rows) is what happens when this
  rule is broken by the serving layer.
- **Default trust consequence.** `figure_text` raises the `figure_text` guard → **always WITHHELD**, and is
  NON_LEARNING. ⚠ The consequence is right for the definition and catastrophic for the *misclassifications*:
  because the role is unconditionally withheld, **every over-assignment of FIGURE_TEXT is a silent, total
  loss of teaching content** — the guard fires on 37 blocks of the gold set and is the SOLE reason 24 of them are withheld —
  16 of those 24 are clean text (`guard-cost.md`), and among them are a grade-3 word problem and two multiplication tables.

### FOOTNOTE
- **Semantic definition.** A gloss printed below a rule at the foot of the page (or under a passage),
  explaining a word or naming a source, marked by a dash, an asterisk or a numeral.
- **Inclusion.** `– term: explanation` lines under a reading; starred notes; small-type notes at the page
  foot.
- **Exclusion.** A bracketed source line (→ ATTRIBUTION). A `Từ ngữ` glossary box printed *as a box*
  (→ SIDEBAR).
- **Positive examples.** `02-sgk-tieng-viet-2-tap-hai` p14 b02 «– Cá ròng ròng (cá lòng ròng): loài cá lóc
  nhỏ…» · `04-sgk-tieng-viet-4-tap-mot` p28 b07 «– Cu-ba: một nước ở châu Mỹ…».
- **Confusing counterexamples (measured).** FOOTNOTE precision 1.000 / recall 0.727. **FOOTNOTE → BODY, 3,
  all TRUSTED** — a gloss served as part of the passage. The reverse never happens.
- **Relationship rules.** A FOOTNOTE belongs to the page, or to the BODY passage above it; it is never part
  of the passage's own text.
- **Teaching consequence.** SAM may use a FOOTNOTE to explain a word the child asks about. SAM must never
  include a FOOTNOTE in a passage it asks comprehension questions about — the gloss is not the story.
- **Default trust consequence.** `footnote` is a FLEX_ROLE (the order-agreement guard is waived for it,
  because footnotes legitimately move in reading order) and a learning role. Defensible.

### ATTRIBUTION
- **Semantic definition.** The line that says where a text came from — its author, its source work, its
  publisher.
- **Inclusion.** `(Theo …)` · `(Nguồn: …)` · `(Dẫn theo …)` · `(Trích …)` · `(Kể theo …)` · `(Phỏng theo …)`
  · `(Sưu tầm)` · a bracketed line naming a publisher (`NXB …`).
- **Exclusion.** A caption that happens to be bracketed. A line ending in `?`. In an SGV the same line is
  `teacher_text` (the pipeline changes only the role name; the withholding is unchanged).
- **Positive examples.** `04-sgk-tieng-viet-4-tap-mot` p28 b05 «(Theo Truyện kể hằng đêm dành cho các cô bé
  cá tính)» · `05-sgk-lich-su-va-dia-li-5` p41 b03 «(Theo Đăng Khoa, Hoài Thu, …)».
- **Confusing counterexamples (measured).** 8 gold attributions; **3 served as BODY** —
  `02-sgk-tieng-viet-2-tap-mot` p103 b03 «(Vũ Thanh tổng hợp)», `08-sgk-ngu-van-8-tap-mot` p38 b14
  «(Thái Bá Lợi, Minh sư, NXB Hội Nhà văn, …)», `11-sgk-ngu-van-11-tap-mot` p39 b03 «(Nam Cao, Chí Phèo)» —
  and **1 served as CAPTION** (`07-sgk-khoa-hoc-tu-nhien-7` p26 b05). All four are TRUSTED. The marker
  lexicon covers `Theo/Nguồn/Trích/…` and `NXB`; a bare `(Author, Work)` matches nothing.
  **`n20260906-0071` «(Theo Văn Thành Lê)» served as `sidebar` is one of the six round-4 role
  disagreements** — annotator #1 accepted it because the line sits in a tinted box, annotator #2 rejected it
  because the vocabulary has an ATTRIBUTION role. §8 rules for #2.
- **Relationship rules.** An ATTRIBUTION belongs to the BODY passage (or FIGURE) immediately above it.
  Detaching it is the `attribution_detached` critical-teaching class. It is never a SIDEBAR merely because
  it is printed in a box.
- **Teaching consequence.** SAM must show the ATTRIBUTION whenever it quotes the passage it belongs to —
  this is a provenance obligation, not decoration. SAM must never treat an ATTRIBUTION as content.
- **Default trust consequence.** `attribution` maps to coarse BODY, carries no exemption, and — since the
  round-4 correctness fix — is tested **before** the uppercase-heading rules, so an UPPERCASE `(THEO …)` can
  no longer become a `heading` and a `heading_path`. This is the one role whose trust consequence round 4
  demonstrably improved.

### OBJECTIVE
- **Semantic definition.** A statement of what the child will be able to do after the lesson — the book
  talking about the lesson, not teaching it.
- **Inclusion.** Blocks inside a `MỤC TIÊU` / «Sau bài học này, em sẽ…» box; sentences of the form
  `verb … được` that state a capability.
- **Exclusion.** A sidebar that happens to use `được`. A question. A `Em đã học` recap of content
  (→ SIDEBAR).
- **Positive examples.** `12-sgk-toan-12-tap-hai` p20 b06 «Sử dụng tích phân để tính diện tích của một số
  hình…» · the two Bài 17 objectives.
- **Confusing counterexamples (measured).** OBJECTIVE precision 0.704 / recall 0.826. **SIDEBAR →
  OBJECTIVE, 4, all TRUSTED** — `04-sgk-khoa-hoc-4` p9 b12 and p78 b15, `07-sgk-khoa-hoc-tu-nhien-7` p20 b14
  «Ở Hy Lạp cổ đại, người ta tin rằng mọi thứ đều được…»: the `verb + được` pattern fires on ordinary prose.
  **OBJECTIVE → BODY, 3**, two of them in SGVs where the block becomes `teacher_text`.
- **Relationship rules.** OBJECTIVEs belong to the lesson, not to any block. They are the lesson's contract.
- **Teaching consequence.** SAM may use OBJECTIVEs to plan and to tell the child what the lesson is for.
  **SAM must never ask an OBJECTIVE as a question** — this is the WAL-204 failure class, and it is why the
  Role Layer's "blocker" job (objectives, sidebars, answer keys, figure-dependent prompts) matters more than
  its labelling job.
- **Default trust consequence.** `objective` maps to coarse BODY and is subject to `page_feature:diagram`.
  No exemption. ⚠ The mis-assignment direction is the dangerous one: four sidebars serving as objectives
  means four blocks entering the "lesson contract" that are not the lesson's contract.

### ACTIVITY
- **Semantic definition.** An instruction to *do* something physical, procedural or collaborative —
  an experiment, a game, a group task, a project, a step of a procedure. It expects an action, not an answer.
- **Inclusion.** `Hoạt động N` · `Thực hành` · `Thí nghiệm` · `Trò chơi` · `Dự án` · `Thảo luận nhóm`;
  procedure markers `Chuẩn bị`, `Tiến hành`, `Bước N`, `Dụng cụ`, `Hoá chất` and the numbered steps that
  follow them (the pipeline calls these `instruction`; **this spec folds INSTRUCTION into ACTIVITY —
  Q-ROLE-3**).
- **Exclusion.** A question about an activity's result (→ QUESTION). A stage label naming the activity
  section (→ HEADING).
- **Positive examples.** `05-sgk-khoa-hoc-5` p42 b03 «4. Chia sẻ với bạn về:» ·
  `09-sgk-khoa-hoc-tu-nhien-9` p38 b01 «Quan sát Hình 7.6 và cho biết:» (gold ACTIVITY).
- **Confusing counterexamples (measured).** **ACTIVITY precision 0.000 / recall 0.000 on the gold set** —
  the pipeline predicts the role 6 times and is right 0 times, against 11 gold blocks. **ACTIVITY → BODY 5**
  (all TRUSTED), **ACTIVITY → QUESTION 3** (all withheld by `figure_dependent`), **QUESTION → ACTIVITY 3**
  (two TRUSTED). The role-signal experiment lifted ACTIVITY from 0.000 to **0.222–0.333** using an orange
  hand-icon signal and concluded it is *detectable, not usable*; it also found the signal marks the **box**,
  not the line, so activity *contents* are missed even when the box title is found.
- **Relationship rules.** An ACTIVITY may own steps (themselves ACTIVITY), a materials list, and QUESTIONs
  asked about its outcome. Its steps are ordered and the order is meaning — the round-3 audit's `sequence`
  class (11 rows) is what happens when two steps interleave.
- **Teaching consequence.** SAM may guide a child through an ACTIVITY step by step, and must preserve step
  order. SAM must not present an ACTIVITY as a question to be answered in words, and must not skip a
  materials line — the round-3 audit found 8 experiment steps cut at the first printed line, losing
  reagents and the observation.
- **Default trust consequence.** `activity` and `instruction` raise `figure_dependent` when the text names a
  figure, and are subject to `page_feature:diagram`. Correct for the definition. ⚠ But with precision 0.000
  the guard is firing on the wrong blocks: the three gold ACTIVITYs the pipeline calls QUESTION are withheld
  as figure-dependent (right outcome, wrong reason), while the five it calls BODY are served with no
  activity guard at all.

### RULE
- **Semantic definition.** A statement the book marks as something to be *held true and reused* — a
  definition, a theorem, a law, a `Ghi nhớ` rule, a boxed formula statement.
- **Inclusion.** Text in a `Ghi nhớ` / `Kết luận` / definition box; a numbered theorem; a stated law of
  physics; «Diện tích S của hình phẳng giới hạn bởi đồ thị …».
- **Exclusion.** An example of the rule (→ ANSWER or BODY). A question about the rule (→ QUESTION). A
  sidebar of general interest (→ SIDEBAR).
- **Positive examples.** `09-sgk-toan-9-tap-mot` p29 b10 «Đối với phương trình chứa ẩn ở mẫu, ta thường đặt
  điều kiện…» · `12-sgk-toan-12-tap-hai` p20 b15 · `07-sgk-toan-7-tap-hai` p41 b07 «Cho hai đơn thức».
- **Confusing counterexamples (measured).** **The pipeline never emits RULE.** All 3 gold RULEs become
  `body`: one TRUSTED, one WITHHELD by `math_guard`, one CONFLICT. The gold has only 3 RULE blocks on 58
  pages, so the *frequency* is unknown — 3 is far too few to measure a rate from, and that itself is a
  finding: **the corpus cannot yet say how often a rule is served as prose.**
- **Relationship rules.** A RULE may contain a FORMULA. A RULE is the thing an ACTIVITY or QUESTION asks the
  child to apply. A RULE printed in a box is still a RULE, not a SIDEBAR.
- **Teaching consequence.** A RULE is the highest-value block a lesson has: it is what SAM should quote when
  a child asks "why", and what a spaced-repetition item should be built from. Serving a rule as body prose
  costs the lesson its spine. SAM must never paraphrase a RULE.
- **Default trust consequence.** None — the role is unreachable. Rules inherit `body`'s consequences:
  no exemption, all guards. ⚠ **A role in the `COARSE` map that no branch can produce is a definition the
  system cannot act on.** Either `assign_role` gains a branch (not this lane's work) or the role should be
  removed from the vocabulary so the gap is visible.

### SPEECH_BUBBLE
- **Semantic definition.** Text in a cartoon balloon attached to a character — the book's device for
  putting a hint, a question or a piece of reasoning in a peer's voice.
- **Inclusion.** Text inside a balloon or callout shape attached to a drawn figure; the first-person
  register (`Tớ đã đổ…`, `Nhớ lại quy tắc … nhé!`) is a strong cue.
- **Exclusion.** A caption. An axis label. A sidebar in a rectangle.
- **Positive examples.** `05-sgk-toan-5-tap-mot` p21 b05–b07 «Tớ đã đổ 1/5 l nước vào bình.» / «Tớ đã đổ 1/2
  l nước vào bình.» / «Cả hai bạn đã đổ bao nhiêu phần lít nước vào bình?» ·
  `03-sgk-toan-3-tap-mot` p32 b05, b10 · `07-sgk-toan-7-tap-hai` p41 b02 «Nhớ lại quy tắc chia hai luỹ thừa
  cùng cơ số nhé!».
- **Confusing counterexamples (measured).** **The pipeline never emits SPEECH_BUBBLE.** Of the 11 gold
  bubbles: **5 → `figure_text` (withheld unconditionally)**, 4 → `body`, 1 → `sidebar`, 1 unmatched. The Toán 5
  p21 sequence is the sharpest example in the whole corpus: three bubbles together state the problem's two
  data and its question, and all three are withheld as figure text — **the lesson's entire word problem is
  classified as decoration.**
- **Relationship rules.** A SPEECH_BUBBLE is attached to a FIGURE (its speaker) but its *text* is lesson
  content, not figure annotation. That is exactly the distinction FIGURE_TEXT's exclusion criterion draws,
  and exactly the one the pipeline cannot draw today. Bubbles in a sequence are ordered.
- **Teaching consequence.** SAM may voice a SPEECH_BUBBLE as a peer's turn — it is the book's own scaffolding
  and maps directly onto SAM's tutoring register. Losing bubbles loses the lesson's dialogue.
- **Default trust consequence.** None — unreachable. In practice bubbles inherit `figure_text`'s
  consequence: **withheld, NON_LEARNING**. ⚠ This is the single most costly definition hole measured:
  a missing role turning teaching content into decoration, silently, with no guard reporting a problem.

### RUNNING_HEAD
- **Semantic definition.** The repeated page furniture that names the chapter or book at the top or bottom
  of every page.
- **Inclusion.** A short line in the header or footer band repeating the chapter name; `CHƯƠNG II – ĐỘNG HỌC`
  at the top of every page of a chapter.
- **Exclusion.** A chapter banner printed once, on the chapter's opening page (→ HEADING).
- **Positive examples.** `10-sgk-vat-li-10` p30 b01 «CHƯƠNG II – ĐỘNG HỌC» · `11-sgk-vat-li-11` p105 b01
  «CHƯƠNG IV – DÒNG ĐIỆN MẠCH ĐIỆN».
- **Confusing counterexamples (measured).** 4 gold RUNNING_HEADs, 3 correct. The fourth,
  `06-sgv-khoa-hoc-tu-nhien-6` p5 b02 «Trang», is a **TOC column header** classified `heading` with an
  order CONFLICT — the same word is furniture on one page and a table header on another, and only position
  distinguishes them.
- **Relationship rules.** RUNNING_HEAD belongs to the page, never to a lesson. Its repetition across pages
  is its definition; a single occurrence cannot be a running head.
- **Teaching consequence.** Never shown, never quoted, never counted as lesson text. It may be used to
  *verify* which chapter a page belongs to.
- **Default trust consequence.** `furniture` guard → WITHHELD; NON_LEARNING; `COLOUR_HEAVY_EXEMPT` and
  `VERSE_EXEMPT` (harmless, since it is withheld anyway). Correct.

### PAGENUM
- **Semantic definition.** The printed page number.
- **Inclusion.** Digits alone in the header or footer band.
- **Exclusion.** A large standalone numeral that is a lesson number on an elementary banner (→ HEADING —
  the pipeline's `big_digit` context exists for this). A number inside a table or a formula.
- **Positive examples.** 54 gold PAGENUMs; `01-sgk-tu-nhien-va-xa-hoi-1` p6 b02 «5».
- **Confusing counterexamples (measured).** PAGENUM precision 1.000 / recall 0.944 — the most reliable role
  in the system. **PAGENUM → EMPTY, 2** is the only failure. The expensive direction is not
  misclassification but **contamination**: the round-3 audit found page numbers appended to **120 served
  rows**, sometimes fused into a value («D. 20 112»), and «2. Câu thơ nào…? **162** II. Đọc hiểu…» is one of
  the six role disagreements. The page number is identified correctly and then serialised into the content
  anyway — a serving defect, not a role defect, and the spec must not let the role class absorb the blame.
- **Relationship rules.** PAGENUM belongs to the page. It is never part of any block's text.
- **Teaching consequence.** Never shown. Used for provenance («trang 62») — and round 4 found a *fabricated*
  «trang 62» citation on the device, so a page number must be carried from the source, never composed.
- **Default trust consequence.** `furniture` → WITHHELD; NON_LEARNING; `COLOUR_HEAVY_EXEMPT`. Correct.

### UNKNOWN
- **Semantic definition.** The system could not determine a role. **Not** "the block is empty" and **not**
  "the block is worthless" — an honest refusal to label.
- **Inclusion.** A block whose text is absent or purely decorative punctuation; a fragment the classifier
  has no rule for.
- **Exclusion.** Everything the other 19 definitions cover.
- **Positive examples.** By construction there is no gold UNKNOWN — the gold annotator always had a role.
- **Confusing counterexamples (measured).** The pipeline's `empty` role is doing UNKNOWN's job **and one
  other job it should not**: 8 gold FORMULAs and 1 gold ANSWER_SLOT are classified `empty`
  (`02-sgk-toan-2-tap-hai` p48). `empty` fires when a line has no letters and is not a 1–3 digit number, so
  «200 < 300» and «? ? ?» are "empty". `empty_block` is the sole withholding reason on 14 blocks of the gold set, and **10 of those 14
  are clean text** (`guard-cost.md`).
- **Relationship rules.** UNKNOWN has none. It is a leaf.
- **Teaching consequence.** Never served, never quoted, never counted against coverage as a *loss* — an
  honest UNKNOWN is a correct outcome. But an UNKNOWN that is really a FORMULA is a silent deletion.
- **Default trust consequence.** `empty` is **always** WITHHELD (`trust_status` hard rule), NON_LEARNING,
  and `COLOUR_HEAVY_EXEMPT`. ⚠ The hard withhold is right for a genuine UNKNOWN and wrong for the
  8 formulas: **the most conservative role in the system is being assigned by the least conservative test.**

---

## 5. What the trust consequences look like side by side

| spec role | pipeline role | colour-exempt | math/unit/chem waived | own guard | learning | default outcome |
|---|---|---|---|---|---|---|
| HEADING | `heading`, `stage_label` | **yes** | no | — | yes | served; becomes `heading_path` |
| BODY | `body` | no | no | — | yes | served at confidence 0.60 |
| QUESTION | `question` | no | no | `figure_dependent` | yes | served unless figure-dependent |
| OPTION | `option`, `answer_slot` | no | no | — | yes | served |
| ANSWER | `answer`, `model_answer` | no | no | **`answer_leak`** | yes | **withheld** |
| CAPTION | `caption` | **yes** ⚠ | no | — | yes | served |
| SIDEBAR | `sidebar` | no | no | `page_feature:diagram` | yes | served unless on colour |
| TABLE | `table` | no | **yes** ⚠ | — | yes | served |
| FORMULA | `formula` | no | **yes** ⚠ | — | yes | served — but never assigned |
| FIGURE | `figure` | yes | yes | — | **no** | **always withheld** |
| FIGURE_TEXT | `figure_text` | no | no | **`figure_text`** | **no** | **always withheld** ⚠ |
| FOOTNOTE | `footnote` | no | no | — | yes | served (order guard waived) |
| ATTRIBUTION | `attribution` | no | no | — | yes | served |
| OBJECTIVE | `objective` | no | no | `page_feature:diagram` | yes | served |
| ACTIVITY | `activity`, `instruction` | no | no | `figure_dependent` | yes | served unless figure-dependent |
| RULE | — | — | — | — | — | **unreachable** ⚠ |
| SPEECH_BUBBLE | — | — | — | — | — | **unreachable** ⚠ |
| RUNNING_HEAD | `running_head` | yes | chem only | **`furniture`** | **no** | **withheld** |
| PAGENUM | `page_number` | yes | chem only | **`furniture`** | **no** | **withheld** |
| UNKNOWN | `empty` | yes | yes | **`empty_block`** | **no** | **always withheld** ⚠ |

**The five ⚠ in one sentence each.**
1. **CAPTION is colour-exempt by role name**, so three BODY blocks mislabelled caption gained an exemption
   they should not have; the exemption belongs to a geometric fact, not to a label.
2. **FORMULA and TABLE waive the math/unit/chem guards**, which is only safe while the expression or the
   cells survive as structure — and today they arrive as a flattened string.
3. **FIGURE_TEXT is withheld unconditionally**, so every over-assignment is a total, silent loss; 16 of the
   37 blocks it withholds on the gold set are clean text.
4. **UNKNOWN (`empty`) is assigned by a letters-and-digits test** that catches every printed arithmetic
   comparison, and then withholds it as an empty block.
5. **RULE and SPEECH_BUBBLE cannot be produced at all**, so two definitions in the vocabulary have no
   effect on any decision the system makes.

None of these was changed. This lane writes the spec; it does not touch the classifier (Founder order §7:
*do not train or tune a role classifier before the taxonomy is clear*).

---

## 6. Relationship rules, collected

1. **OPTION ⊂ QUESTION.** An option without a question is a defect. A served region containing a stem and
   its options is **one** unit (this exemption exists because of a control row — §8, `s20260905-0124`).
2. **ANSWER_SLOT ⊂ QUESTION.**
3. **CAPTION ⊂ FIGURE | TABLE**, at most one per figure, decided by geometry, never by reading distance.
4. **FIGURE_TEXT ⊂ FIGURE**, and never quotable alone.
5. **SPEECH_BUBBLE → FIGURE** (attached to a speaker) but its text is lesson content, not figure annotation.
   This is the distinction the pipeline cannot draw.
6. **ATTRIBUTION → the BODY passage or FIGURE above it.** Detaching it is a critical teaching error.
7. **FOOTNOTE → the page or the passage above**, never *inside* the passage.
8. **ANSWER → a QUESTION**, and **an ANSWER may only exist in an SGV or in an explicitly printed answer
   section of an SGK.**
9. **HEADING → a span.** Every block until the next heading of equal or higher level inherits it.
10. **ACTIVITY → ordered steps.** Step order is meaning.
11. **RULE ⊃ FORMULA** is allowed; a RULE in a box is still a RULE, not a SIDEBAR.
12. **Verse is BODY with a line-structure flag**, never reflowed. There is no VERSE role.
13. **SGV rule.** `docType = SGV` does not create roles; it re-points them: a QUESTION becomes a teacher
    prompt, an ATTRIBUTION becomes teacher text, ordinary prose becomes teacher text — all withheld from a
    child by the `teacher_text` guard, with the role name changing but the withholding unchanged.

---

## 7. How to judge role fidelity (the procedure the re-annotation applies)

- **R1.** Judge the region the served block claims — its bbox and the printed lines inside it — not the page.
- **R2.** One block, one printed role. If the region carries one printed unit, the served role must equal
  that unit's spec role.
- **R2c — the extent rule.** If the region carries printed units of **different** spec roles, the served
  role is WRONG, **except** where the roles stand in a declared parent–child relation of §6 (OPTION ⊂
  QUESTION, ANSWER_SLOT ⊂ QUESTION, CAPTION ⊂ FIGURE). ⚠ **This rule is open — Q-ROLE-1.**
- **R3.** A printed worked example's solution (`Mẫu`, `M:`, `Ví dụ N` + its computation, `Thử lại` lines) is
  **ANSWER**, whatever it is printed inside.
- **R4.** A parenthesised source line is **ATTRIBUTION**, whatever box it is printed in.
- **R5.** Role is judged from the **printed** region, never from the served (possibly destroyed) string.
  Truncation, tone slips and flattening are display or teaching-critical errors, not role errors.
- **R6.** A bare printed mathematical expression is **FORMULA**. ⚠ **Open — Q-ROLE-2.**
- **R7.** Page furniture and non-lesson pages (covers, ISBN blocks, back-cover book lists) are never lesson
  content; serving them under any content role is a role error.

---

## 8. Re-annotation against this spec — what moved, and what did not

**Sample.** All **6** role disagreements between the two blind round-4 annotators (4 from the round-3
484-row sample, seed 20260906; 2 from the legacy batch-1 rows, seed 20260908) plus a **control** of **7**
rows both called WRONG and **13** rows both called OK, drawn deterministically (every 5th of the 61 OK/OK
rows in sample-id order). **n = 26.** Data:
`poc-out/round5/lane-a3/role-reannotation-2026-09-06.json`; script
`tool/corpus/thresholds/role_reannotation.py`.

**Method — and its honest name.** The spec is a function from an *observation of the printed page* to a
role verdict. Both annotators recorded their observation in free text. Each row's observation was replayed
through §7. **On all 26 rows the two annotators' observations describe the same printed content** — the
claim that these were definition disagreements rather than perception disagreements is checked row by row
and holds everywhere. So the measurable question is not "do they see the same thing" but "does the written
procedure decide what they saw".

| | agreement | **κ** | #1 WRONG | #2 WRONG |
|---|---|---|---|---|
| **before** (as judged in round 4, on these 26 rows) | 0.769 | **0.524** | 0.308 | 0.462 |
| **after** (spec applied; the 3 rows it cannot decide left as disagreements) | 0.962 | **0.923** | 0.500 | 0.538 |
| **after, on the 23 rows the spec decides** | 1.000 | **1.000** | — | — |

κ on the whole round-3 second-annotation sample was 0.713 and on the batch-1 rows 0.423; **0.524 here is
lower than both because this sample deliberately over-samples the disagreements** (6 of 26 rather than 4 of
74). The three numbers are on three different samples and must not be compared as a trend.

**κ = 1.000 on decided rows is not a discovery.** A deterministic procedure applied to identical
observations agrees with itself; that is arithmetic, not evidence. And the spec was written **after** these
rows were read, so this is an **in-sample** result. The honest measure of the spec is its **decidability
rate: 23 of 26 = 0.885 decided, 3 convention-dependent, 0 undecidable.**

**What the spec resolved (5 of the 6 disagreements).**
- `s20260905-0162` and `s20260905-0391` — a `Mẫu` / `Ví dụ 2` worked example served as an `exercise`.
  **R3 settles both for annotator #2.** These were the same disagreement twice, in two different books.
- `n20260906-0071` — «(Theo Văn Thành Lê)» served as `sidebar`. **R4 settles it for #2.**
- `n20260906-0040` — «b) 10 +» for printed «b) 3/10 + 5/21», served as `body`. **R5 settles it for #1**:
  #2 had judged the role acceptable *because the served string was a bare fragment*, which R5 forbids. The
  verdict is the same under both answers to Q-ROLE-2 — the printed unit is FORMULA or QUESTION, and `body`
  is neither.
- `s20260905-0380` — chapter banner + lesson banner + icon label + an exercise stem + table headers served
  as one `section_text`. **Decided under both readings of Q-ROLE-1**, because even the label-only reading
  keys on the leading printed unit, which is a HEADING.

**What the spec did not resolve — it moved (1 of the 6, plus 2 controls).**
- `s20260905-0329` — question 2 + a page number + the whole next section's passage and glossary, served as
  one `exercise`. Extent-inclusive → WRONG (#2); label-only → OK (#1). **This is not an annotator
  disagreement any more; it is Q-ROLE-1, and it needs a Founder ruling.**
- `s20260905-0481` (control, both OK) — a writing prompt served together with the reading-record form.
  Same open question: a TABLE is not a declared child of a QUESTION.
- `s20260905-0178` (control, both OK) — three bare printed sums served as one `exercise`. **Q-ROLE-2:** the
  gold vocabulary calls a bare printed comparison a FORMULA (19 such blocks, e.g. `02-sgk-toan-2-tap-hai`
  p48 «200 < 300»); the pack vocabulary calls the same shape an `exercise`. The two vocabularies disagree
  and both annotators used the pack's.

**What the control sample did to the spec — the part worth reading.**
- `s20260905-0124` (both OK): an MCQ stem served together with its four options. **The extent rule as first
  written made this WRONG — an agreed-OK control broken by the rule.** The parent–child exemption in R2c
  (OPTION ⊂ QUESTION) exists because of this row and only because of it. Without a control sample the spec
  would have shipped a rule that fires on every multiple-choice item in the corpus.
- `s20260905-0372` (both OK): a lesson title banner plus a stage icon label served under a body role. **The
  spec says WRONG where both annotators said OK.** It is the one row where the spec overrules both. So
  **applying this spec would raise the measured role-error rate, not lower it** — the spec is stricter than
  the round-4 annotators were, and any before/after role rate must be recomputed under it rather than
  compared across it.
- All **7** WRONG/WRONG controls stay WRONG, and **11 of 13** OK/OK controls stay OK. The spec does not
  flatter the pipeline and does not collapse the control.

**What this does not establish.** The spec was written after reading these rows: the result is in-sample and
the κ movement is a property of determinism. **The measurement that would settle it is not done here:** a
*fresh* disagreement sample, drawn with a new seed, judged blind by two annotators who are given this
document and nothing else. Until that runs, the defensible claim is "the definitions decide 88.5 % of a
known-hard sample and name the rest", not "inter-annotator agreement on role has improved".

---

## 9. Open definition questions for the Founder

| id | question | what it touches | measured cost of leaving it open |
|---|---|---|---|
| **Q-ROLE-1** | Does role fidelity judge the **label** the block asserts, or the **extent** of what it covers? When a served region spans a question *and* a foreign passage, is that a role error or only a display/order error? | R2c; every merged-region row | 1 of 6 measured role disagreements and 1 of 13 OK controls flip with the answer. It also decides whether the round-3 `role` rate of 0.093 is right or a large under-count. |
| **Q-ROLE-2** | Is a bare printed mathematical expression that constitutes an exercise item a **FORMULA** or a **QUESTION**? | R6; FORMULA vs QUESTION; the gold vocabulary vs the pack vocabulary | 19 gold blocks; 1 of 13 OK controls; and it decides whether the `math_guard` exemption (which FORMULA carries and QUESTION does not) applies to every arithmetic exercise item in Toán. |
| **Q-ROLE-3** | Does **INSTRUCTION** fold into ACTIVITY (as this spec assumes) or stay a 20-first role? | the §7 list of 20 vs `tc2_score`'s six | changes what the scoreboard's INSTRUCTION row (precision 0.300 / recall 0.500) measures |
| **Q-ROLE-4** | Should **RULE** and **SPEECH_BUBBLE** be built, or removed from the vocabulary? | Holes 1 and 2 | 3 + 11 gold blocks today; the Toán 5 p21 and Toán 3 p32 bubbles carry the lesson's word problem, and are withheld as decoration |
| **Q-ROLE-5** | Should a **trust exemption ever follow a role name**, or only a verifiable fact? CAPTION's colour exemption, FORMULA's and TABLE's math exemption, and FIGURE_TEXT's unconditional withhold are all keyed on a classifier output. | §5, the five ⚠ | 3 BODY blocks gained a colour exemption by being mislabelled CAPTION; 16 clean blocks are unconditionally withheld as FIGURE_TEXT |

---

## 10. Denominators (D5)

Everything in §4–§5 is measured on the **gold set: 58 pages (54 + 4 Bài 17), 643 learning blocks** on the
54-page set, tc2-p2, `poc-out/round4/pipeline/tc2-p2/sdm-gold`. §8 is measured on **26 rows** drawn from two
audit samples of **58** and **16** second-annotated rows. Nothing here is divided by **3,679** canonical or
**3,381** ranged lessons, and nothing here is a rate over the **243** legacy lessons in scope. The role
rates quoted from round 3 (0.093 on 420 shipped blocks) and round 4 (0.125 / 0.216 on the legacy batches)
belong to their own populations and are not pooled with the gold set.
