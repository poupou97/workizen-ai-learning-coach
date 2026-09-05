#!/bin/zsh
# Assemble 06-CONCEPT-TO-CODE-MATRIX.md from the B/C rows and the UI rows.
D=/Users/alexnguyen/projects/workizen-ai-learning-coach/poc-out/audit/pre-autonomy
{
  echo "# 06 — Concept-to-code traceability matrix · 2026-09-05"
  echo
  echo "Columns: Founder Concept → Design/Doc → Code component/screen → Data dependency → Runtime dependency → Test → Device evidence → Status. Flags: concept-no-code · code-not-concept · UI-with-fake-backend · backend-without-UI · docs-say-wired-but-not · matches. Sources: \`data/concept-to-code-rows.md\` (architecture audit) and \`data/ui-concept-rows.md\` (device audit). Line numbers from \`main\` @ e5155f4."
  echo
  echo "## A. Learning architecture & runtime segments"
  echo
  sed -n '/^| Founder Concept/,$p' "$D/data/concept-to-code-rows.md"
  echo
  echo "## B. Screens vs the approved concept (device-verified where a screenshot path is given)"
  echo
  if [ -f "$D/data/ui-concept-rows.md" ]; then sed -n '/^| Founder Concept/,$p' "$D/data/ui-concept-rows.md"; else echo "_UI rows pending (device audit not finished)._"; fi
  echo
  echo "## C. Findings this matrix exposes"
  echo
  echo "- **concept-no-code:** LearningView, TrustedLearningSource, SemanticBinding, MethodCase, PlannedAct (dead type), Trusted Structured Lesson in the app, the Lesson Workspace with three Views."
  echo "- **docs-say-wired-but-not:** evidence validator as the \"only door\" (9/10 emitters bypass), lineage on Reader/Compose/Source/Tutor events, \`resolveSurface\` as the only mapping (0 callers), pedagogy runtime \"built and guarded\" (0 runtime callers), \"Founder-approved convergence\" (no artefact)."
  echo "- **backend-without-UI:** CurriculumEdge (1 edge, 0 consumers), QuizSelectScreen (unrouted), shadow LLM guard chain, SDM/TSL pipeline (offline only), sam-units.db (no Dart consumer)."
  echo "- **UI-with-fake-backend / hard-coded:** Home review chip and assessment hard-code lesson 6 / case denominator-non-divisible; \`decide()\` with a hard-coded case; grade ≠ 5 static message; see \`05\` mock inventory for screens."
  echo "- **code-not-concept:** Discovery/Stories path, perception boundary, entitlement/safety policy — real, tested, not in the Founder concept list (keep, document)."
} > "$D/06-CONCEPT-TO-CODE-MATRIX.md"
wc -w "$D/06-CONCEPT-TO-CODE-MATRIX.md"
