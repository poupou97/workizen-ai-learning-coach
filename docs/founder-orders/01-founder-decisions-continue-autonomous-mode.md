FOUNDER DECISIONS — CONTINUE AUTONOMOUS MODE

Bootstrap report accepted.

GitHub is now the canonical repository:
poupou97/workizen-ai-learning-coach

Canonical branch:
main

Continue FULL AUTONOMOUS MODE.

Do not wait for Jira/Confluence bootstrap.
When WAL containers become available, backfill governance automatically.

==================================================
DECISION 1 — CONCEPT MASTERY AGGREGATION
==================================================

Do NOT choose `mean` as Concept mastery truth.

Do NOT promote `min` to scientific/product truth either.

Founder rejects the framing:

ConceptMastery = min OR mean

as insufficient.

F1 demonstrated that mastery and evidence coverage are separate
dimensions.

Replace the research question with:

"How should the system summarize evidence across SkillCases
without claiming knowledge it has not observed?"

Candidate Concept-level representation:

ConceptSummary {
  estimatedMastery
  coverage
  confidence
  weakestObservedCases
  unobservedCases
  evidenceCount
  lastEvidenceAt
}

Names/schema may change based on evidence.

Critical invariant:

HIGH MASTERY ESTIMATE
!=
SUFFICIENT COVERAGE
!=
HIGH CONFIDENCE.

A Concept MUST NOT become confidently MASTERED merely because
observed SkillCases are strong while required SkillCases remain
unobserved.

Parent-facing claims require stronger evidence than an internal
ranking heuristic.

Research/POC aggregation policies autonomously.

Use evidence from BKT / KT / cognitive diagnosis / mastery-learning
research where useful.

Keep raw SkillCase evidence so aggregation policy remains replaceable.

Add golden/adversarial tests for at least:

- 2 strong cases + 1 unobserved
- all cases observed and strong
- one weak observed case
- contradictory evidence
- stale evidence
- sparse evidence
- strong post-hint success only
- strong pre-hint independent success
- concept with only one known SkillCase
- newly discovered SkillCase after Concept was previously considered mastered.

Parent Coach must fail conservatively:

If evidence does not justify "mastered",
do not say "mastered."

==================================================
DECISION 2 — F1
==================================================

F1 is P0.

Fix the semantic problem, not merely the test.

Separate:

MASTERY
COVERAGE
CONFIDENCE.

Do not encode UNKNOWN as FAILED.

Do not encode UNOBSERVED as MASTERED.

==================================================
DECISION 3 — F2
==================================================

F2 is P0 and must be fixed before building further Tutor behavior.

`3/5 + 1/5` must not enter a denominator-conversion SkillCase
merely because divisibility arithmetic returns true.

Problem applicability must model the mathematical case correctly.

Strengthen:

APPLICABLE_TO_PROBLEM

before TutorScope.

Add boundary/equivalence tests:

same denominator
one denominator divides another
coprime denominators
non-coprime/non-divisible denominators
unknown/malformed input.

Unknown remains fail closed.

==================================================
DECISION 4 — F3
==================================================

F3 is P0 architectural work.

LearningEvidence must distinguish at minimum:

independent attempt
hint requested
hint shown
guided attempt
post-hint success
self-correction
final correctness.

Do not let:

SYSTEM INTERVENTION
→ POST-HINT SUCCESS
→ FULL MASTERY CREDIT
→ SYSTEM CONFIDENCE

form a self-confirming loop.

Investigate evidence weighting rather than hard-code arbitrary
scientific constants without justification.

Preserve raw events.

Derived mastery must remain recomputable.

==================================================
DECISION 5 — F4
==================================================

F4 must be deterministic.

Parent/student claims must NEVER depend on Map insertion order.

Define explicit deterministic selection/ranking policy.

If evidence cannot justify selecting one weakest case:
say that evidence is insufficient or summarize multiple cases.

Parent-facing explanation must be traceable to evidence.

==================================================
NEXT — F6 MULTI-SKILL / Q-MATRIX
==================================================

Proceed.

This is high priority.

Do not assume one exercise = one Concept.

Model possibility:

Exercise
→ multiple Knowledge Components / SkillCases
→ different evidence contribution.

Use `3/4 + 2/5` as one example but test other structures.

Research Q-matrix / cognitive diagnosis patterns from EduStudio
and relevant OSS/literature.

Do not adopt a full cognitive-diagnosis model merely because
Q-matrix exists.

We need a representation that can evolve.

==================================================
NEXT — F5 FORGETTING
==================================================

Proceed after/in parallel with F6 where safe.

Mastery is not permanent.

Investigate:

recency
forgetting
review due
spaced repetition
BKT variants
SkillCoco/SM-2/FSRS-style ideas where relevant.

Keep distinction:

knowledge estimate
vs
review scheduling.

Do not collapse them prematurely.

==================================================
NEXT — CAMERA / OCR
==================================================

Proceed with bounded Camera Tutor OCR POC.

Goal is NOT UI.

Measure:

photo → OCR/problem representation → mathematical parsing
→ Concept/SkillCase candidate mapping → applicability.

Especially measure:

caseUnknown frequency.

Fail closed when visual/problem evidence is insufficient.

Do not compensate for bad OCR by hallucinating mathematical structure.

==================================================
JIRA / CONFLUENCE
==================================================

Jira and Confluence remain governance bootstrap blockers only.

They are NOT product-development blockers.

Expected Jira project:

Key: WAL
Name: Workizen AI Learning Coach

Expected Confluence home/space:

Workizen AI Learning Coach

When containers become available:

- create/backfill 10 Epics + 31 prepared issues
- preserve actual status
- do not mark architecture design as product implementation
- create concise Confluence hierarchy
- link GitHub/Jira/Confluence.

Until then maintain Jira-ready backlog in repository.

==================================================
PARENT UMBRELLA REPO
==================================================

Do NOT resolve parent-repo divergence now.

Do NOT push unrelated parent changes.

Record:

"Convert AI Learning Coach to umbrella submodule per ADR-059"

as governance work.

The child GitHub repository is canonical.

Do not risk shared repository history for this.

==================================================
EXECUTION PRIORITY
==================================================

P0:
F1 ConceptSummary / coverage / confidence
F2 applicability correctness
F3 LearningEvidence intervention contamination

P1:
F4 deterministic explanation
F6 multi-skill/Q-matrix
F5 forgetting/review

Then:
OCR/problem-understanding POC
retrieval
stronger domain thin slice
application integration.

Continue falsification throughout.

==================================================
REPORTING
==================================================

Do not report ticket count as progress.

Report newly established or falsified knowledge.

Use:

STATUS
EVIDENCE
FALSIFIED
DECISIONS
TESTS
ARCHITECTURE CHANGE
JIRA
CONFLUENCE
BLOCKERS
NEXT

Continue autonomously.

No routine Founder questions.
