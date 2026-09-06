# TASK ORDER — HỌC CÙNG SAM
## LESSON WORKSPACE UX — CONTEXTUAL SAM RECOMMENDATION
### Reduce duplication · Progressive disclosure · Preserve AI-first experience

PRIORITY: P1 UX / ROUND 5 PARALLEL
MODE: RESEARCH + BOUNDED POC + REAL DEVICE
MERGE: NO
FINAL STATE: READY FOR FOUNDER REVIEW

==================================================
0. FOUNDER FEEDBACK
==================================================

Founder reviewed current Lesson Workspace on device.

Current UI feels:

- repetitive;
- vertically expensive;
- too many representations of the same three Learning Views;
- SAM recommendation occupies too much permanent space;
- CTA sometimes duplicates navigation already visible elsewhere.

Example current hierarchy effectively becomes:

Learning Views
[Đọc] [Trực quan] [Học với SAM]

then:

“Con muốn học bài này theo cách nào?”

then cards:
1. Đọc như sách
2. Trực quan hoá
3. Học cùng SAM

then inside a view again:

[Đọc] [Trực quan] [Học với SAM]

then:

SAM đề xuất
“Con đã đọc — giờ xem sơ đồ...”

then another:
[✨ Trực quan]

This creates duplicated navigation and recommendation UI.

Founder hypothesis:

SAM recommendation should NOT necessarily be
a permanently expanded card.

Research progressive disclosure such as:

COLLAPSED
💡

PEEK
💡 SAM gợi ý: Xem Trực quan →

EXPANDED
┌─────────────────────────────┐
│ 💡 SAM gợi ý            ×  │
│ Vì con vừa đọc xong...      │
│                             │
│      [✨ Xem trực quan →]   │
└─────────────────────────────┘

This is a HYPOTHESIS, not an implementation order.

Research alternatives before choosing.

==================================================
1. UX PRINCIPLE TO TEST
==================================================

Hypothesis:

SAM Recommendation
!=
permanent page section.

Instead:

SAM Recommendation
=
contextual adaptive assistance layer
driven by learner state / Next Action.

The Workspace should primarily contain:

LESSON
+
CURRENT LEARNING VIEW
+
LEARNING CONTENT.

SAM should intervene when useful,
not permanently consume a large portion of the viewport.

==================================================
2. AUDIT CURRENT INFORMATION ARCHITECTURE
==================================================

Audit the current Lesson Workspace end-to-end.

Inventory every occurrence of:

- Đọc;
- Trực quan;
- Học với SAM;
- SAM đề xuất;
- Next Action;
- recommendation reason;
- mode picker;
- CTA changing Learning View;
- mascot;
- progress/opened state.

For each occurrence classify:

NAVIGATION
CONTENT
RECOMMENDATION
EXPLANATION
STATUS
PROGRESS
DUPLICATE.

Produce a duplication map.

Answer:

Why does each occurrence exist?

What unique information does it add?

Could it be removed without losing capability?

==================================================
3. RESEARCH
==================================================

Research current UX patterns relevant to:

- contextual AI recommendations;
- progressive disclosure;
- contextual hints;
- coach marks;
- expandable recommendation chips;
- AI assistant affordances;
- adaptive Next Action;
- contextual FAB/chip;
- inline suggestion;
- bottom sheet;
- tooltip/popover;
- collapsible assistant;
- learning-app recommendations.

Look beyond education apps.

Study good patterns from contemporary:
- AI products;
- learning products;
- productivity products;
- mobile assistants.

Do NOT copy visual design.

Extract interaction principles.

Document references/screenshots/links where legally appropriate.

==================================================
4. DESIGN QUESTION
==================================================

Test at least 3 substantially different patterns.

Do not create three cosmetic variations of the same card.

Candidate A — ICON

[💡]

Tap:
→ recommendation popover/bottom sheet.

Candidate B — PEEK CHIP

[💡 SAM gợi ý: Xem Trực quan →]

Tap:
→ explanation expands.

Candidate C — INLINE CONTEXTUAL

[Đọc] [✨ Trực quan 💡] [🦉 SAM]

Recommendation attaches directly to the suggested destination.

Optional candidate if research supports it:

CONTEXTUAL FLOATING SAM
or
BOTTOM-SHEET RECOMMENDATION.

Do not assume these are final solutions.

==================================================
5. THREE STATES
==================================================

Research whether recommendation should have:

COLLAPSED
PEEK
EXPANDED.

Example:

COLLAPSED
💡

PEEK
💡 SAM gợi ý: Xem Trực quan →

EXPANDED
💡 SAM gợi ý
Con vừa đọc xong bài.
Xem sơ đồ sẽ giúp con thấy các bước rõ hơn.

[✨ Xem trực quan →]

Test state transitions:

first recommendation
→ peek?

user taps
→ expanded

user dismisses
→ collapsed

new meaningful recommendation
→ peek again?

Do not implement fake adaptive intelligence.

Use current honest learner state only.

==================================================
6. REMOVE DUPLICATED VIEW SELECTION
==================================================

Research whether we still need BOTH:

A.

[Đọc] [Trực quan] [Học với SAM]

AND

B.

1 Đọc như sách
2 Trực quan hoá
3 Học cùng SAM.

Founder suspects this is redundant.

POC a simplified hierarchy such as:

Bài 17

[📖 Đọc] [✨ Trực quan] [🦉 Học với SAM]

💡 SAM gợi ý: Trực quan →

────────────────────

CURRENT VIEW CONTENT

But do not blindly adopt this.

Compare against current picker.

==================================================
7. SAM MASCOT USAGE
==================================================

Audit mascot repetition.

Hypothesis:

Mascot should appear when SAM is actually:

- speaking;
- tutoring;
- reacting;
- explaining;
- celebrating;
- actively recommending something important.

Avoid using 🦉 + mascot portrait + “SAM” repeatedly
as decoration.

Test whether recommendation can use:

💡 for suggestion

while:

🦉 / SAM mascot

is reserved for actual SAM interaction.

Goal:

make SAM presence MORE meaningful,
not simply less visible.

==================================================
8. AI-FIRST MUST NOT DISAPPEAR
==================================================

Important:

Reducing the SAM card must NOT turn the product
into a normal textbook reader with three tabs.

The learner should still understand:

“Ứng dụng biết mình đang ở đâu
và đề xuất mình nên làm gì tiếp theo.”

Therefore measure:

DISCOVERABILITY OF RECOMMENDATION

and:

UNDERSTANDING OF WHY SAM RECOMMENDED IT.

Do not optimize only for screen space.

==================================================
9. NEXT ACTION ARCHITECTURE
==================================================

Check relationship between:

SAM Recommendation
and
Next Action.

Avoid building two competing recommendation systems.

Preferred conceptual direction:

Student State
+
Learning Context
+
Pedagogy Runtime
        ↓
Next Action
        ↓
Recommendation Presentation.

UI presentation may be:

icon
chip
inline hint
expanded explanation.

But presentation should not create a second
source of recommendation truth.

Audit existing architecture before changing it.

==================================================
10. SCREEN-SPACE METRIC
==================================================

Measure before/after on Nokia 6.1.

At minimum:

- vertical pixels consumed before lesson content;
- % viewport occupied by navigation/recommendation chrome;
- first meaningful lesson content Y-position;
- number of repeated CTAs;
- number of visible SAM/mode labels;
- taps required to switch view;
- taps required to understand recommendation.

Example goal:

LESS CHROME
+
MORE LEARNING CONTENT
+
SAME OR BETTER AI DISCOVERABILITY.

Do not optimize against an arbitrary pixel target.

==================================================
11. BOUNDED POC
==================================================

Use current real representative slice:

KHTN 6
Bài 17 · Tách chất khỏi hỗn hợp.

Do not create another fake lesson solely for UI.

Build bounded prototypes for the strongest
2–3 approaches after research.

Keep current implementation available for A/B comparison.

==================================================
12. DEVICE TEST
==================================================

If device protocol permits, test on Nokia 6.1.

Capture comparable frames:

CURRENT

vs

OPTION A

vs

OPTION B

vs strongest OPTION C if justified.

Same lesson.
Same learner state.
Same viewport/state where possible.

Evaluate:

1. Which screen feels least repetitive?
2. Which exposes more actual learning content?
3. Can learner still discover SAM recommendation?
4. Is it clear why SAM recommends something?
5. Is switching Đọc / Trực quan / SAM easier?
6. Does SAM feel more intelligent or merely less visible?
7. Does expanded recommendation interrupt learning?
8. Does collapsed recommendation become too easy to miss?

==================================================
13. IMPORTANT UX RULE
==================================================

Do NOT solve duplication by simply hiding everything.

Use:

PROGRESSIVE DISCLOSURE.

Primary information:
always visible.

Secondary explanation:
available on demand.

Contextual AI recommendation:
visible enough to discover,
small enough not to dominate.

Detailed “why?”:
expand on demand.

==================================================
14. ACCESSIBILITY
==================================================

Do not rely on 💡 icon alone without accessible meaning.

Ensure:

semantic label
touch target
screen-reader description
state indication

for:

“Gợi ý của SAM”.

If icon-only wins visually,
accessibility still needs explicit semantics.

==================================================
15. NO FAKE PERSONALIZATION
==================================================

Do not show:

“Vì SAM biết con chưa hiểu...”

unless evidence actually supports it.

Current example:

“Con đã đọc — giờ xem sơ đồ...”

is allowed only if current state genuinely establishes
that the learner opened/read the relevant view according
to the existing state semantics.

OPENED != UNDERSTOOD.
TAP != LEARNED.
READ != MASTERY.

Preserve existing evidence doctrine.

==================================================
16. EXPECTED OUTPUT
==================================================

Deliver:

A. CURRENT UX DUPLICATION AUDIT

B. RESEARCH REFERENCES

C. 3 INTERACTION CONCEPTS

D. BEFORE / AFTER INFORMATION ARCHITECTURE

E. BOUNDED IMPLEMENTATION OF 2–3 STRONG OPTIONS

F. DEVICE COMPARISON

G. SCREEN-SPACE METRICS

H. DISCOVERABILITY / AI-FIRST ASSESSMENT

I. RECOMMENDATION:
- KEEP CURRENT
- ICON
- PEEK CHIP
- INLINE
- HYBRID
- OTHER

with evidence.

==================================================
17. FOUNDER ACCEPTANCE CARD
==================================================

Report exactly:

CURRENT PROBLEM
→ evidence of duplication

OPTION A
→ strengths / weaknesses

OPTION B
→ strengths / weaknesses

OPTION C
→ strengths / weaknesses

WINNER
→ why

SPACE SAVED
→ measured

AI DISCOVERABILITY
→ better / same / worse

DUPLICATION
→ what was removed

REAL DEVICE
→ tested / not tested + why

OPEN RISKS

RECOMMENDED NEXT STEP.

==================================================
18. GOVERNANCE
==================================================

Allowed autonomously:

- UX audit;
- web/repo research;
- prototypes;
- reversible Flutter implementation;
- tests;
- screenshots;
- device test under existing protocol;
- docs;
- Jira/Confluence;
- branch + PR.

Do NOT:

- merge;
- redesign the entire product;
- change pedagogy truth;
- invent learner state;
- change evidence semantics;
- create a second Next Action engine.

Stop at:

READY FOR FOUNDER REVIEW.
