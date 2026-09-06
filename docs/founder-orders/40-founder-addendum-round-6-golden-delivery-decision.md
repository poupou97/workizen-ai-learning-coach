# FOUNDER ADDENDUM — ROUND 6 GOLDEN DELIVERY DECISION

Based on the verified inventory, Founder selects:

GOLDEN #1 — LS&ĐL 5 Bài 8
Purpose:
PROVE REPAIR → TSL → LESSON DOCUMENT → APP → REAL DEVICE.

GOLDEN #2 — Toán 4 tập hai Bài 61
Purpose:
PROVE R13 ACCOUNTING + RECOGNITION RECOVERY.

REGRESSION GOLDEN — KHTN 6 Bài 17
Purpose:
PROVE ROUND 6 DOES NOT BREAK EXISTING REAL WORKSPACE.

==================================================
1. LS&ĐL 5 BÀI 8 — PRIMARY DELIVERY SLICE
==================================================

Do NOT use the old Round-4 LessonDocument as the final proof.

Use the current Round-6 pipeline.

Required chain:

real source
→ current observation/SDM
→ repair ledger
→ ValidatedRepair
→ projected/repaired TSL
→ LessonDocument generated from that TSL
→ assets/fixtures/real/
→ WorkspaceCatalog real-path load
→ real device.

The final learner-visible file must be generated from the
current Round-6 repaired/projected TSL.

Prove lineage with hashes.

The existing app slot for:
05-sgk-lich-su-va-dia-li-5#8
should be reused.

No new lesson-specific loading path.

==================================================
2. REPAIR GATE
==================================================

Round 6 currently has:

ValidatedRepair code
+
tsl_projection.py

but no projected TSL artefact.

This is NOT yet considered integrated.

Produce a real projected TSL for Golden #1.

Demonstrate at least one validated repair crossing:

RepairLedger
→ Projected TSL
→ LessonDocument.

Do NOT automatically promote repair to TRUSTED.

Disposition/trust rules remain fail-closed.

==================================================
3. GOLDEN #1 CONTENT CHECK
==================================================

Pay special attention to the known sharp case:

LS&ĐL 5 Bài 8
p039:000

where one tone disagreement previously caused the whole
dated-events block to be withheld and removed all 7 timeline events.

Round 6 must show what happens to this block now.

If repaired and validated:
show exact lineage.

If still withheld:
report honestly.

Do NOT restore timeline by special-casing lesson identity.

==================================================
4. TOÁN 4 BÀI 61 — ACCOUNTING / RECOGNITION
==================================================

Do not force learner-facing Math delivery if it requires a
large new formula architecture during Round 6.

Use Bài 61 to prove:

R13 conservation
recognition improvement
fraction/digit recovery
zero unexplained disappearance.

Target:

INPUT
=
SERVED
+ WITHHELD
+ EXCLUDED_WITH_REASON

with:

UNACCOUNTED = 0

for the evaluated slice.

Also measure the 274/336 unreachable fraction problem.

==================================================
5. DO NOT FAKE MATH DELIVERY
==================================================

Current evidence shows:

- bridge has no formula role mapping;
- LessonDocument has no formula type;
- app has no math renderer;
- pack path drops important provenance/status.

Therefore:

do NOT claim Math structure reaches child
until that path actually exists.

A withheld crop is not structured Math delivery.

==================================================
6. KHTN 6 BÀI 17
==================================================

Keep as regression/reference.

Verify:

current Round-6 changes do not break
the existing real fixture flow.

Do not use Bài 17 as primary proof of repair effectiveness,
because it currently exercises essentially no repair.

==================================================
7. FIXTURE VERSION SAFETY
==================================================

Every real fixture used for Founder/device evidence must record:

source TSL hash
pipeline version
SDM version
repair version
generator version.

A fixture reproducible from tc2-p1/sdm-v2 is not automatically
a current-pipeline fixture.

Do not silently mix generations.

==================================================
8. ROUND 6 DELIVERY CLAIM
==================================================

Round 6 may only claim:

VERIFIED ACCURACY REACHED THE LEARNER

if the device-loaded Golden #1 file can be traced to a
current Round-6 projected/repaired TSL.

Old generated documents or synthetic fallback do not count.

==================================================
9. EARLY CHECKPOINT
==================================================

Return early once all three are true:

A. R13 ledger has zero unexplained loss on one Golden slice.

B. A projected TSL containing ValidatedRepair exists on disk.

C. LS&ĐL 5 Bài 8 real fixture loads instead of synthetic fallback.

Then continue to real-device verification.

DO NOT MERGE.

READY FOR FOUNDER REVIEW.
