FOUNDER DECISIONS — PRE-AUTONOMY CHECKPOINT

Verdict C is ACCEPTED:

NOT READY FOR BROAD AUTONOMOUS DEVELOPMENT.
RESOLVE P0 GATES FIRST.

D1 — EVIDENCE CONTRACT

APPROVED invariant:

Ungraded learner self-report / completion MUST NOT create
competence, mastery or independent-attempt claims.

A tap such as:
"Con đã trả lời xong"
may establish participation/completion only.

Competence/mastery requires ValidatedEvidence.

No parent-facing claim such as:
"Con đã tự làm được"
may be derived solely from an unvalidated tap.

Implement mechanical consequences only where semantics are clear.
Any ambiguous claim returns for Founder review.

D2 — ARCHITECTURE CONVERGENCE

Do NOT choose Deep OR Scale.

Target relationship:

Trusted Structured Lesson
→ LearningActivity
→ SemanticBinding
→ Concept / SkillCase
→ Method
→ Pedagogy Runtime

Scale/Activity path provides breadth.
Concept/SkillCase/Method provides pedagogical depth.

They are complementary dimensions.

Do not mass-implement convergence yet.
Produce only bounded contracts needed by the current round.

Mark any unsupported "Founder-approved convergence" claim TBD.

D3 — SOURCE TRUST

APPROVE a statistical false-trust audit protocol for the exact
content currently shipped.

Do not expand coverage before G1/G2/G3.

Do not lower a trust threshold merely to make the experiment pass.

Report separately:
- display-only source fidelity;
- teaching-critical fidelity;
- role fidelity;
- lesson attachment;
- false trust.

D4 — LICENCE

Until explicit legal/licensing approval exists:

verbatim SGK text
and
SGK page/image crops

are INTERNAL / RESEARCH ONLY.

Technical ability to render/crop content does not imply a right
to distribute it.

Do not make a public-release assumption.

D5 — DENOMINATORS

Keep 3,679 as the historical canonical baseline until the repaired
canonical census is independently reviewed.

Do not silently replace it.

Every metric must carry:
- denominator definition;
- census/version;
- applicable subset.

Source-ranged denominators remain separate.

D6 — GOVERNANCE

Where no Founder approval artefact exists:

"Founder-approved convergence"

must become:

TBD / PROPOSED CONVERGENCE

until explicitly approved.

==================================================
AUTONOMOUS B-LANE — AUTHORIZED
==================================================

Run only bounded, reversible, test-backed work:

1. Pack provenance manifest + default-build test.
2. Unique evidence event IDs + idempotent append.
3. Mechanical implementation of D1:
   self-report != competence evidence.
4. Lineage threading across Scale emitters.
5. Attachment cap/header + lesson identity checks.
6. Remove experimental router content from default build.
7. Fix the two honest UI defects:
   - duplicate/ambiguous "Đọc bài" labels;
   - Home claiming no content when routed content exists.
8. Remove 'unknown-case' grading fallback / fail closed.
9. knowledgeModelVersion from pack provenance.
10. Bounded Role-Layer research and false-trust audit tooling.

Every behavioral change needs tests.

DO NOT:

- expand lesson coverage;
- full-corpus reprocess;
- implement Short Answer;
- implement 27 patterns;
- mass-build Learning Views;
- wire an LLM;
- finalize LearningContext ↔ LearningView;
- make public textbook licensing assumptions.

==================================================
NEXT CHECKPOINT
==================================================

After B-lane completes, STOP.

Return one report answering:

DATA:
Can we trust what currently ships?

EVIDENCE:
Can a tap still become a competence claim?

INTEGRITY:
Can retry/reopen double-count mastery?

PROVENANCE:
Can every APK prove exactly which pack it contains?

LINEAGE:
Can every learner event identify its lesson/source?

ARCHITECTURE:
Is Deep ↔ Scale convergence now mechanically possible
without creating another architecture?

UI:
Have known misleading states been removed?

Then give a new autonomy verdict:

A READY
B READY WITH GUARDRAILS
C NOT READY
D REBASE

Do NOT begin Learning Views implementation after the checkpoint.

All PRs stop at READY FOR FOUNDER REVIEW.
Do not merge without explicit permission.
