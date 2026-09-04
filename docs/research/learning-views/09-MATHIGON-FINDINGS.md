# 09 — Mathigon textbooks — Findings (P0)

Source: https://github.com/mathigon/textbooks — shallow clone read in scratch (README,
`content/circles/{content.md, functions.ts, hints.yaml}`, `content/shared/hints.yaml`,
directory listing); GitHub page fetch for metrics. All FROM-REFERENCE.

## The twelve fields

1. **Reusable product principle.** "Part textbook and part virtual personal tutor" for ages 12–18;
   "Our content is divided into small steps. You have to complete the activities to reveal what's
   next" (`shared/hints.yaml` `tutorial1`). Reading and doing are the same page; progress is saved
   per step.
2. **Content model.** One folder per course (33 courses incl. circles, polygons, probability,
   graph-theory …): `content.md` — "a custom extension of Markdown" holding source and metadata;
   `functions.ts` — "all the TypeScript code for all the interactive elements in this course";
   `styles.scss`; optional `hints.yaml` — "messages that can be sent by Mathigon's virtual tutor".
   `content/shared`: biographies, glossary (`glossary.yaml`), shared web components.
3. **Lesson model.** `content.md` → `# Course` → `## Section` with metadata block (`> section:`,
   `> id:`, `> color:`, `> level:`, `> next:`, `> trailer:`) → steps separated by `---` each with
   `> id:` and optional `> goals: a b c` (the step completes when all goals are scored). Layout
   via `::: column(width=320)` blocks; captions `{.caption}`; reveals `{.reveal(when="compass")}`.
4. **Renderer model.** `@mathigon/studio` ("base NodeJS server, TypeScript components and markdown
   parser"); web components used in `circles/content.md` (MEASURED count in that file): `x-solid`
   24, `x-img` 24, `x-equation` 24, `x-geopad` 15, `x-video` 8, `x-gesture` 7, `x-slider` 5,
   `x-play-btn` 4, `x-equation-system` 3, `x-select` 2, plus course-specific components
   (`x-pi-scroll`, `x-ellipse`, `x-conic-section`).
5. **Interaction model.** Inline blanks `[[correct|wrong|wrong]]` (48 in `circles/content.md`);
   `[Continue](btn:next)`; glossary links `[__circle__](gloss:circle)`; target highlights
   `[radius](target:r)`; per-step TS functions receive `$step` and call `$step.score('goal')`,
   `$step.onScore(...)`, animations, drag handles.
6. **Tutor model.** Virtual tutor "Archie" (`welcome: "… I'm Archie, your personal tutor"`).
   Messages are **keyed, authored strings** in `hints.yaml` (per course and shared), triggered
   deterministically from step code: `$step.addHint('use-cylinder-volume')` on an incorrect blank;
   `$step.delayedHint(() => $step.addHint('inequality-impossible'), 20000)` (polygons). Shared
   `correct:` / `incorrect:` lists are random praise/retry phrases ("Well done", "Try again!").
7. **Assessment / evidence model.** Step-level: a blank fires `correct`/`incorrect`; goals scored;
   progress persisted server-side. No mastery model visible in the content repo.
8. **Strengths.** The clearest working example of **Mode 1 + Mode 3 coexistence**: the textbook
   *is* the interaction surface; progression is goal-gated (a general form of SAM's READ/PREDICT
   gates); hints are deterministic and keyed (= `RealizationPolicy.template`); typed components
   are reusable across courses; content is semantic Markdown with layout hints only.
9. **Weaknesses (for SAM).** Every course is hand-written, with bespoke TypeScript per course —
   non-transferable to a 531-book extracted corpus; the content is the source of truth (no
   external provenance concept); praise is random and content-free (would fail SAM's "can the praise
   be wrong?" test); maths-only components; content licence is proprietary.
10. **License.** No `LICENSE` file in the repository; README footer "© Mathigon 2016–2022, All
    rights reserved"; contributors must sign an Individual CLA. Treat **content and course code as
    not reusable**; `@mathigon/studio` is a separate package (not audited here).
11. **Maturity.** Production platform; GitHub page shows 392 stars / 160 forks at fetch time; CI
    tests and code-quality workflows; localisation docs.
12. **Applicability to SAM.**
    - **Step + goals** is the right generalisation of SAM's gates for Mode 1: a Smart Book section
      can carry an optional *goal* (answer the in-text question; confirm read) before the next block
      reveals — but on SAM only where a trusted `question` block exists.
    - **Keyed hints** validate SAM's `RealizationPolicy.template` for the low-risk acts; Mathigon
      shows they are enough for an award-winning product without an LLM.
    - **Inline blanks** are a candidate Activity Pattern surface (FILL_BLANK: 150 lessons in the
      registry) — but only with an SGV key; otherwise `correct: null`.
    - **Glossary links** ↔ SAM's glossary-parse provenance: a term in Mode 1 can open its trusted
      definition (the cheapest Mode 2 "flashcard" data, `05` §2).

## What NOT to copy

- Authoring per lesson (content, TS, styles).
- Random praise/retry phrase banks.
- Anything from the content under its all-rights-reserved terms.
- Treating the rendered course as the source of truth (SAM's truth is the SGK page).

## Founder question B — "textbook + interaction coexistence (Mode 1 + Mode 3)"

Mathigon answers it affirmatively and shows the mechanism: **interaction is embedded at step
granularity inside the reading flow, and the tutor speaks only on step events.** For SAM this
means Mode 1 and Mode 3 are not two screens but two *densities* of the same lesson document —
Mode 1 with gates and «Hỏi SAM» only; Mode 3 with the Pedagogy Runtime driving which block/
question is active. That matches Convergence §7 ("SAM's presence inversely proportional to the
child's capability at that moment").
