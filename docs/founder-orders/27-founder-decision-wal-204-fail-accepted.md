# FOUNDER DECISION — WAL-204 FAIL ACCEPTED
## P0 NEXT: Layout-Aware K–12 Extraction

WAL-204 FAIL is accepted as useful falsification evidence.

Do NOT implement the remaining 27 Activity Patterns now.

Preserve WAL-203/WAL-205 backlog.

The new P0 blocker is upstream:

SOURCE PDF
→ LAYOUT / READING ORDER
→ LESSON ATTACHMENT
→ ACTIVITY DETECTION
→ PATTERN ROUTING
→ SURFACE
→ SAM.

Current failure occurs at:

LAYOUT / READING ORDER.

==================================================
1. BUILD A GENERAL CAPABILITY
==================================================

Do NOT write a KHTN-specific two-column hack.

Research and implement a bounded:

K–12 LAYOUT-AWARE / COLUMN-AWARE EXTRACTION CAPABILITY.

It must identify, where possible:

- reading order;
- columns;
- headings;
- body text;
- questions;
- captions;
- sidebars;
- tables;
- figures/figure references;
- activity blocks;
- page boundaries;
- lesson boundaries.

Preserve provenance:

book
page
region/block
reading order
lesson
confidence.

Fail closed when layout cannot be trusted.

==================================================
2. AUDIT CORPUS IMPACT
==================================================

Before optimizing one book, measure across K–12:

- how many books/pages are multi-column;
- affected grades;
- affected subjects;
- affected lessons;
- common layout families;
- percentage potentially recoverable.

Determine whether a small number of layout patterns
covers a large portion of the corpus.

Do not manually inspect every page.
Use automated census + representative gold validation.

==================================================
3. REUSE EXISTING TOOLS FIRST
==================================================

Audit existing extraction stack and previously researched
document/layout tooling before inventing a new parser.

Compare bounded candidates where appropriate.

Choose based on real corpus evidence:

layout fidelity
reading order
table/figure handling
speed
determinism
license
offline feasibility
integration cost.

Do not introduce a large new dependency without evidence.

==================================================
4. GOLD SET
==================================================

Build a cross-subject layout gold set.

Must include at least:

KHTN / Khoa học
Ngữ văn / Tiếng Việt
Toán
Lịch sử / Địa lý
Tin học

and examples of:

single column
two column
sidebar
figure + caption
question block
table
complex/broken layout.

Gold truth must establish expected reading order
and block roles.

==================================================
5. RE-RUN WAL-204
==================================================

After extraction passes the gold set,
re-run the EXACT WAL-204 experiment:

Khoa học / KHTN Grade 4–9

Layout-aware extraction
→ TOC-range attachment
→ Activity Pattern
→ Pattern Router
→ Surface
→ SAM
→ Evidence
→ device.

Original success bar remains:

>= 50 NEW unique lessons device-valid

AND

0 regression of the existing Experiment baseline.

Do not lower the bar to manufacture PASS.

==================================================
6. CONTENT QUALITY GATE
==================================================

A lesson does NOT count device-valid merely because
the Reader opens.

Validate:

- passage is coherent;
- reading order is correct;
- question is actually a learner question;
- heading is not treated as question;
- source provenance is correct;
- no cross-lesson contamination;
- no future-content leakage;
- Surface behavior is appropriate.

==================================================
7. MEASURE THE CASCADE
==================================================

Report:

BEFORE proven lessons

→ lessons recovered by layout extraction

→ lessons correctly attached

→ lessons with recognized Activity Pattern

→ lessons successfully routed

→ lessons content-valid

→ lessons device-valid

→ AFTER proven lessons.

This funnel is mandatory.

Founder needs to know where lessons are lost.

==================================================
8. DO NOT START PATTERN EXPANSION YET
==================================================

Pattern expansion remains blocked until this experiment passes.

If PASS:

recalculate the full K–12 Activity Pattern registry
using improved extraction.

The old pattern counts may be incomplete or distorted
because extraction itself was faulty.

Then reprioritize patterns by:

NEW UNIQUE LESSONS UNLOCKED
× LEARNING VALUE
× CONFIDENCE
÷ COST.

Do not blindly trust the previous 27-pattern counts
after changing extraction.

==================================================
9. IMPORTANT PRODUCT PRINCIPLE
==================================================

Do not optimize for:

PDF text extraction accuracy alone.

Optimize for:

TRUSTWORTHY LEARNING UNIT RECOVERY.

The real target is:

SOURCE TRUTH
→ TRUSTED STRUCTURE
→ LEARNING ACTIVITY
→ LEARNING EXPERIENCE.

==================================================
10. AUTONOMOUS EXECUTION
==================================================

Proceed autonomously through:

corpus layout census
tool comparison
gold set
bounded implementation
tests
WAL-204 rerun
device validation
Jira/Confluence
PR/CI/merge.

If WAL-204 passes, STOP and report before mass pattern expansion.

If it fails again, identify the next measured bottleneck.

Do not compensate with manual lesson annotation
or uncontrolled LLM generation.

Proceed.
