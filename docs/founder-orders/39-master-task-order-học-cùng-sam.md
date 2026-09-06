# MASTER TASK ORDER — HỌC CÙNG SAM
## ROUND 6 — VERIFIED ACCURACY → REAL PRODUCT
### + PERMANENT ROUND GOVERNANCE / REPORTING / ARCHIVE RULE

PRIORITY: P0
MODE: AUTONOMOUS / DELIVERY-FOCUSED
MERGE: NO — FOUNDER APPROVAL REQUIRED
FINAL STATE: READY FOR FOUNDER REVIEW

==================================================
PART I — ROUND 6 EXECUTION
==================================================

ROUND 6 NORTH STAR:

MAKE VERIFIED ACCURACY REACH THE LEARNER.

Round 1–5 chủ yếu giúp chúng ta đo đúng hơn,
phát hiện sai tốt hơn và xây repair capability.

Round 6 phải bắt đầu đưa kết quả đó tới sản phẩm thật.

Use maximum 4 coordinated workstreams:

A. TRUTH ACCOUNTING
B. RECOGNITION
C. REPAIR → PRODUCT INTEGRATION
D. GOLDEN DELIVERY

Do not create 9 independent lanes again.

--------------------------------------------------
A. TRUTH ACCOUNTING — P0.1
--------------------------------------------------

Fix R13 first.

Current defect:

role=empty can cause source content to disappear from both:

blocks
and
withheld.

This is SILENT LOSS.

New invariant:

EVERY relevant source region
must have an explicit auditable disposition:

SERVED
WITHHELD
EXCLUDED_WITH_REASON

or an evidence-supported equivalent.

ZERO SILENT LOSS.

Implement deterministic conservation/accounting:

INPUT SOURCE REGIONS

=

SERVED
+
WITHHELD
+
EXCLUDED WITH REASON
+
explicitly defined non-learning regions.

Any unexplained difference = HARD FAILURE.

Reproduce:

overall served:
0.632 previously reported
→ 0.589 actual

holdout:
0.523

Toán 4 Bài 61:
0.211 previously reported
→ 0.078 actual.

Determine WHAT disappeared and WHY.

Do not simply convert every lost region to WITHHELD.

Repair root causes where safely possible.

Recalculate affected Round 5 metrics after R13 fix.

Preserve historical numbers and explicitly mark corrections.

--------------------------------------------------
A2. CANONICAL LESSON IDENTITY
--------------------------------------------------

Audit:

all-lessons.csv

3,679 rows
3,240 distinct current keys
154 duplicated keys
439 rows participating in duplicates.

Founder has NOT approved:

3,679 = unique canonical lessons

or:

3,240 = unique canonical lessons.

Classify duplicates:

true duplicate
source variant
edition variant
SGK/SGV relationship
multi-volume
key collision
canonicalization error
distinct lessons sharing key
other.

If evidence supports it, distinguish:

SourceLessonRecord
vs
CanonicalLessonIdentity.

Report:

SOURCE ROWS
DISTINCT CURRENT KEYS
TRUE DUPLICATES
KEY COLLISIONS
SOURCE VARIANTS
CANONICAL LESSON COUNT.

Until resolved:

3,679 = HISTORICAL BASELINE ONLY.

Never silently rewrite previous metrics.

--------------------------------------------------
B. RECOGNITION — P0.2
--------------------------------------------------

Round 5 established:

NEXT BOTTLENECK = RECOGNITION.

Examples:

II → I1
3×10⁸ → 3×10°

274 / 336 fraction failures cannot be repaired because
OCR never produced required digits.

Attack recognition BEFORE adding downstream reasoning rules.

Build a real failure census:

DIGIT LOSS
OPERATOR LOSS
FRACTION STRUCTURE
SUPERSCRIPT
SUBSCRIPT
ROMAN NUMERAL
DIACRITIC
SYMBOL CONFUSION
SEGMENTATION
MATH REGION
FORMULA
TABLE/STRUCTURE
OTHER.

FORMS BEFORE RULES.

Evaluate bounded candidates such as:

- corpus/template-assisted recognition;
- targeted high-resolution re-crop;
- alternative OCR observation;
- multi-engine disagreement;
- specialized Math/STEM recognition;
- geometry-aware recognition;
- Docling formula enrichment where technically/licensing safe.

Measure on SAM's actual textbook failures.

Especially evaluate the 274/336 fraction failures.

Report separately:

DIGIT RECALL
SYMBOL RECALL
STRUCTURAL EXACT MATCH
EXPRESSION EXACT MATCH
FALSE RECOGNITION RATE
RECOVERABLE FRACTION RATE.

Do not combine into one score.

--------------------------------------------------
C. REPAIR → PRODUCT — P0.3
--------------------------------------------------

Round 5 proved:

REPAIR EXISTS
REPAIR IS VALIDATED

but:

REPAIR DOES NOT REACH PRODUCT.

Fix this.

CONNECT != TRUST.

Build:

OriginalObservation
        ↓
RepairCandidate
        ↓
Deterministic Validator
        ↓
ValidatedRepair
        ↓
Trust / Disposition
        ↓
Trusted Structured Content
        ↓
LessonDocument
        ↓
Learning View.

ValidatedRepair must retain equivalent information to:

original observation
candidate
source grounding
failure class
repair method
validator + version
validation result
repair version
provenance
disposition.

Do not create another disconnected provenance universe.

Do not mutate historical learner evidence.

Preserve corpus/repair/source version where replay requires it.

Round 5 evidence:

guard relaxation:
1/19 restored
0/1 correct
precision 0.

deterministic repair:
10/10
holdout 8/8.

Therefore preferred path:

WITHHELD
→ FAILURE CLASS
→ REPAIR CANDIDATE
→ VALIDATION
→ RESTORE.

Do not weaken guards merely to improve coverage.

--------------------------------------------------
LLM RULE
--------------------------------------------------

Round 5 evidence:

anomaly recall = 0.717
false-correction rate = 1.000
13/13 corrections on correct lines were wrong.

Therefore:

LLM MAY:
detect anomaly
route
propose candidate
perform semantic review.

LLM MUST NOT:
auto-correct canonical truth
be trust authority
silently rewrite corpus.

LLM OUTPUT != TRUTH.

--------------------------------------------------
D. GOLDEN DELIVERY — P0.4
--------------------------------------------------

Select approximately 3–5 representative real lessons.

Do NOT select only easy lessons to manufacture:

eligible > 0.

Prefer:

Science
History
Math

plus another useful domain if evidence supports it.

At least one must exercise a real Round 5/6
recognition or repair failure.

For every Golden lesson prove:

SOURCE
→ RECOGNITION
→ ACCOUNTED STRUCTURE
→ VALIDATED REPAIR where needed
→ TRUST/DISPOSITION
→ TSL
→ LESSON DOCUMENT
→ LEARNING VIEW
→ REAL DEVICE.

No fixture substitution in final delivery claim.

--------------------------------------------------
ROUND 6 ACCEPTANCE GATES
--------------------------------------------------

GATE A — ACCOUNTING
Zero unexplained silent loss on Golden + holdout.

GATE B — RECOGNITION
At least one previously unrecoverable OCR failure class
materially improves at recognition level.

GATE C — REPAIR
ValidatedRepair crosses the production-shaped pipeline.

GATE D — TEACHING
At least one real lesson becomes honestly eligible for teaching.

Target >0.

DO NOT lower trust/safety gates to achieve >0.

A truthful zero is acceptable if evidence demands it.

GATE E — DEVICE
At least one Golden lesson on real device visibly consumes
validated/repaired real data.

Must trace:

UI
→ LessonDocument
→ TSL
→ ValidatedRepair
→ Source.

--------------------------------------------------
WORKSPACE UX DECISION
--------------------------------------------------

Founder selects OPTION B.

Default compact presentation:

💡 SAM gợi ý: <Next Action> →

Reason/details expand on demand.

Do not reopen A/B/C research unless implementation reveals
a concrete blocker.

SAM Recommendation must remain a presentation of Next Action,
not a second recommendation engine.

OPENED != UNDERSTOOD
READ != MASTERY
TAP != COMPETENCE.

--------------------------------------------------
VISUAL GRAMMAR
--------------------------------------------------

Generalized Semantic Graph / Visual Grammar remains strategically P0.

During Round 6:

continue:
- forms census;
- semantic-pattern census;
- provenance architecture;
- bounded POC.

Do NOT aggressively expand renderer families yet.

Round 5 establishes:

FORMS BEFORE RULES.

Apply:

FORM CENSUS
→ CLUSTER
→ REPRESENTATIVE EXAMPLES
→ RULE
→ HOLDOUT
→ MEASURE
→ GENERALIZE.

Do not infer visual/semantic coverage from a few examples.

--------------------------------------------------
COMPOSITION CHECK
--------------------------------------------------

Individual PR green != integrated product green.

Before Round closure create disposable integration composition.

Run:

flutter analyze
all Dart tests
all Python tests
relevant corpus audits
Golden end-to-end checks.

Report:

INDIVIDUAL CI
and
COMPOSITION CI.

==================================================
PART II — MERGE DEBT
==================================================

Audit:

main
Round 4 integration #73
Round 5 integration #79
Round 6 dependencies.

Classify components:

SAFE FOUNDATION
ROUND6 REQUIRED
NEEDS R13 FIX
OBSOLETED
CAN WAIT.

Return:

A — MERGE #73
B — MERGE #79
C — SELECTIVE MERGE
D — HOLD

with exact dependency/order/risk.

Give one recommendation.

DO NOT MERGE.

==================================================
PART III — PERMANENT ROUND REPORTING RULE
==================================================

This applies to ROUND 6 AND EVERY FUTURE ROUND.

Every round must close the loop across three horizons:

A. ROUND JUST COMPLETED
B. NEXT ROUND
C. REMAINING PRODUCT ROADMAP.

The Founder must always be able to answer:

What did we plan?
What did we actually do?
What succeeded?
What failed?
What was falsified?
What got worse?
What reached the child?
What remains research only?
What exactly happens next?
What major gates remain before product readiness?

--------------------------------------------------
PLAN VS ACTUAL
--------------------------------------------------

For every major planned item report:

PLANNED
ACTUAL
STATUS
EVIDENCE
GAP REASON.

Allowed status:

DONE
PARTIAL
FAILED
FALSIFIED
BLOCKED
DEFERRED
NOT STARTED.

Never turn PARTIAL into DONE.

--------------------------------------------------
ACCEPTANCE GATES
--------------------------------------------------

Repeat the ORIGINAL round acceptance gates.

For each:

PASS
PARTIAL
FAIL
NOT MEASURABLE.

Do not redefine gates after seeing results.

Final tally:

X PASS
Y PARTIAL
Z FAIL.

--------------------------------------------------
PRODUCT REALITY
--------------------------------------------------

Every round must explicitly answer:

WHAT CAN A CHILD ACTUALLY USE NOW
THAT THEY COULD NOT USE BEFORE THIS ROUND?

If answer is NOTHING:

write NOTHING.

Also report separately:

WHAT CAN PARENT USE?
WHAT CAN SAM USE?
WHAT IS INTERNAL/RESEARCH ONLY?

Tests/tools/prototypes do not count as learner delivery.

--------------------------------------------------
REALITY SCOREBOARD
--------------------------------------------------

Report separately:

SOURCE REALITY
SOURCE TRUST
RECOGNITION REALITY
REPAIR REALITY
PEDAGOGY REALITY
EVIDENCE REALITY
PRODUCT DELIVERY REALITY.

Never average them.

--------------------------------------------------
REGRESSION / HISTORICAL CORRECTION
--------------------------------------------------

Every round must report:

REGRESSIONS
NEW PROBLEMS
PREVIOUS METRICS DISCOVERED WRONG
DENOMINATOR CHANGES.

Historical metrics must remain reproducible.

Never silently rewrite history.

--------------------------------------------------
PROVEN / FALSIFIED / HYPOTHESIS
--------------------------------------------------

Every round has three explicit sections:

PROVEN
FALSIFIED
STILL HYPOTHESIS.

No claim laundering.

==================================================
PART IV — NEXT ROUND RULE
==================================================

Every round report MUST propose ROUND N+1.

For every proposed workstream include:

WHY NOW
PROBLEM
OBJECTIVE
MEASURABLE TARGET
DELIVERABLE
DEPENDENCIES
RISKS
STOP CONDITION
FOUNDER GATE.

Every next round must have:

ONE NORTH STAR

and preferably:

3–5 acceptance gates.

Do not create 20 equal priorities.

==================================================
PART V — REMAINING ROUNDS ROADMAP
==================================================

Every round must maintain a living forecast.

Do NOT invent a fixed number of rounds.

Future rounds are:

COMMITTED
PROPOSED
TBD.

Maintain:

ROUND
STATUS
THEME
NORTH STAR
ENTRY CONDITION
EXIT CONDITION
DEPENDENCIES
FOUNDER GATES.

Current planning hypothesis may look approximately like:

ROUND 6 — COMMITTED
Delivery + Recognition
Verified accuracy reaches learner.

ROUND 7 — PROPOSED
Scale Validated Pipeline
Expand only after Round 6 proves end-to-end path.

ROUND 8 — PROPOSED
Semantic / Visual Generalization
Scale reusable knowledge/visual architecture after source quality permits.

ROUND 9 — TBD
Pedagogy / Evidence breadth
Based on measured bottleneck.

ROUND 10 — TBD
Product hardening / release readiness
Only if preceding gates justify it.

THIS IS A FORECAST, NOT A PROMISE.

Evidence may:

ADD
REMOVE
MERGE
SPLIT
REORDER

future rounds.

==================================================
PART VI — MAJOR PRODUCT GATES
==================================================

Maintain a cross-round gate table.

Candidate gates include:

SOURCE ACCURACY
RECOGNITION
TRUSTED CORPUS
STRUCTURED LEARNING CONTENT
SEMANTIC GENERALIZATION
VISUAL LEARNING
PEDAGOGY
EVIDENCE
STUDENT STATE
NEXT ACTION
DEVICE UX
PRIVACY
LICENSING
PERFORMANCE
RELEASE QUALITY.

Each must be one of:

NOT STARTED
RESEARCH
POC
PARTIAL
PROVEN
PRODUCT-INTEGRATED
RELEASE-READY.

Do not estimate remaining work merely as:

"3 rounds left."

Report:

MAJOR GATES REMAINING.

==================================================
PART VII — PER-ROUND DESKTOP ZIP
==================================================

At the end of EVERY round create ONE immutable standalone ZIP
on Founder Desktop.

Naming:

HOC-CUNG-SAM-ROUND-XX-YYYY-MM-DD.zip

Example:

HOC-CUNG-SAM-ROUND-06-2026-09-06.zip

Never overwrite previous archive.

If regeneration is necessary:

...-v2.zip.

Mark archive:

INTERNAL / RESEARCH ONLY

where SGK/source material requires it.

Do not publish externally.

==================================================
ZIP REQUIRED STRUCTURE
==================================================

ROUND-XX/
│
├── 00-START-HERE.md
├── 01-ROUND-OBJECTIVE.md
├── 02-PLAN-VS-ACTUAL.md
├── 03-WORK-COMPLETED.md
├── 04-FAILURES-AND-FALSIFICATIONS.md
├── 05-METRICS-BEFORE-AFTER.md
├── 06-PRODUCT-REALITY.md
├── 07-TEST-CI-PR-EVIDENCE.md
├── 08-DEVICE-EVIDENCE.md
├── 09-ARCHITECTURE-DATA-CHANGES.md
├── 10-OPEN-RISKS-BLOCKERS.md
├── 11-FOUNDER-ACCEPTANCE-CARD.md
├── 12-NEXT-ROUND-PLAN.md
├── 13-REMAINING-ROADMAP.md
├── 14-JIRA-CONFLUENCE-STATUS.md
├── 15-FILE-MANIFEST.md
│
├── evidence/
├── metrics/
├── screenshots/
├── reports/
└── manifests/

==================================================
00-START-HERE
==================================================

Founder must understand the round in approximately 2–5 minutes.

Include:

ROUND
DATE
VERDICT

ONE-LINE RESULT

NORTH STAR:
PASS / PARTIAL / FAIL

TOP COMPLETED ITEMS

TOP FAILURES / DISCOVERIES

WHAT REACHED CHILD

WHAT DID NOT REACH CHILD

KEY METRICS

NEXT BOTTLENECK

NEXT ROUND NORTH STAR

MERGE RECOMMENDATION

FOUNDER DECISIONS REQUIRED.

==================================================
ARCHIVE EVIDENCE RULE
==================================================

Claims must be labelled where appropriate:

PROVEN
MEASURED
OBSERVED
INFERRED
HYPOTHESIS
UNKNOWN.

Include supporting references where available:

commit
PR
test
path
metric source
device manifest
corpus version
pipeline version.

Do not create a ZIP containing only links to external files.

Copy relevant evidence where legally appropriate.

Do NOT copy the 20GB corpus.

For large/external source data record:

path
hash/version
subset
reproduction instructions.

==================================================
DEVICE EVIDENCE
==================================================

If device work happened, archive:

DEVICE
OS
BUILD/COMMIT
LESSON
LEARNER STATE
FLOW TESTED
SCREENSHOT/MANIFEST where permitted.

Widget tests/emulators do not equal real-device evidence.

==================================================
ARCHIVE IMMUTABILITY
==================================================

Closed round ZIPs are historical records.

Do not modify them later.

If Round N+1 discovers Round N metric was wrong:

Round N remains unchanged.

Round N+1 records:

HISTORICAL CORRECTION TO ROUND N.

Only regenerate archive for corruption/missing archive content,
using v2/v3 filename.

==================================================
ZIP VERIFICATION
==================================================

After creation verify:

ZIP EXISTS
ZIP OPENS
REQUIRED FILES PRESENT
NO ZERO-BYTE REQUIRED REPORTS
MANIFEST MATCHES CONTENT
NO BROKEN REQUIRED REFERENCES.

Record:

FILE COUNT
ZIP SIZE
HASH/CHECKSUM.

==================================================
PART VIII — CROSS-ROUND DESKTOP INDEX
==================================================

Maintain:

HOC-CUNG-SAM-ROUNDS-INDEX.md

on Desktop.

One row per round:

ROUND
DATE
VERDICT
NORTH STAR
KEY RESULT
PRODUCT DELIVERY
ZIP NAME
MERGE STATUS
NEXT BOTTLENECK.

Update after every round.

Per-round ZIP remains canonical.

Do not create a giant master ZIP every round.

==================================================
PART IX — RETROSPECTIVE ROUND 5 ARCHIVE
==================================================

Before Round 6 advances too far:

create a retrospective Round 5 archive from existing evidence.

Filename:

HOC-CUNG-SAM-ROUND-05-2026-09-05.zip

or use the actual repository-evidenced close date.

DO NOT fabricate missing evidence.

Mark:

UNAVAILABLE
NOT CAPTURED

where appropriate.

Round 5 archive must include at least:

- actual work;
- nine lanes / PR status;
- composition CI;
- R13;
- corrected served-share discovery;
- repair results;
- guard-relaxation failure;
- LLM 0.717 / false-correction 1.000 finding;
- forms-before-rules discovery;
- Workspace A/B/C;
- 3,679 vs 3,240 issue;
- recognition bottleneck;
- product reality;
- Round 6 plan;
- remaining roadmap.

Then continue Round 6.

==================================================
PART X — ROUND CLOSURE DEFINITION OF DONE
==================================================

A ROUND IS NOT CLOSED until:

1. planned work is completed/stopped;
2. composition CI checked;
3. metrics frozen;
4. Plan vs Actual written;
5. Product Reality written;
6. regressions/falsifications written;
7. Founder Acceptance Card written;
8. next-round plan written;
9. remaining roadmap updated;
10. per-round Desktop ZIP created;
11. ZIP verified;
12. cross-round index updated;
13. merge status explicitly reported.

If any is missing:

ROUND STATUS = REPORTING INCOMPLETE.

==================================================
PART XI — EARLY ROUND 6 CHECKPOINT
==================================================

Do not wait until Round 6 finishes.

Return an early Founder checkpoint after proving:

1. R13 conservation/accounting works;

2. at least one previously unrecoverable recognition case improves;

3. one ValidatedRepair crosses into production-shaped TSL
   without automatically becoming trusted.

Then continue autonomously.

==================================================
PART XII — ROUND 6 FINAL ACCEPTANCE CARD
==================================================

Final Round 6 report must include:

R13:
silent loss before → after.

LESSON IDENTITY:
3,679 rows
3,240 keys
canonical conclusion.

RECOGNITION:
failure class improved
before → after.

FRACTIONS:
274/336 unrecoverable before
→ after.

REPAIR:
lab-only before
→ production-shaped pipeline after.

WRONG SERVED:
before → after.

CORRECT SERVED:
before → after.

ELIGIBLE FOR TEACHING:
0 → X.

REAL DEVICE:
which lesson actually consumed repaired/validated data?

WORKSPACE B:
implemented/tested status.

VISUAL GRAMMAR:
bounded status.

MERGE DEBT:
#73 / #79 recommendation.

NEXT BOTTLENECK:
ONE primary bottleneck.

ROUND 7:
proposed North Star.

REMAINING MAJOR GATES.

VERDICT:

DELIVERY PROVEN
PARTIAL DELIVERY
MORE EVIDENCE
FAILED.

==================================================
GOVERNANCE
==================================================

Claude may autonomously:

audit
research bounded blockers
fix R13
build recognition POCs
build repair integration
build Golden Delivery
implement Workspace B
test
device-test under existing protocol
update Jira/Confluence
create branches/PRs
create disposable integration composition
create local Desktop reporting archives.

Founder approval remains required for:

MERGE
production trust threshold
mass corpus reprocessing
destructive migration
unrestricted LLM generation
licensing/public SGK distribution
paid infrastructure
public release
fundamental irreversible architecture replacement.

DO NOT MERGE.

==================================================
FINAL DIRECTIVE
==================================================

ROUND 6:

ZERO SILENT LOSS
→ IMPROVE RECOGNITION
→ CONNECT VALIDATED REPAIR
→ DELIVER GOLDEN LESSON
→ PROVE ON REAL DEVICE.

AND FROM THIS ROUND FORWARD:

EVERY ROUND MUST LEAVE BEHIND:

WHAT WE PLANNED
WHAT WE ACTUALLY DID
WHAT THE CHILD GOT
WHAT FAILED
WHAT WE LEARNED
WHAT NEXT ROUND DOES
WHAT MAJOR GATES REMAIN
AND ONE VERIFIED IMMUTABLE DESKTOP ZIP.

START ROUND 6 NOW.

READY FOR FOUNDER REVIEW.
