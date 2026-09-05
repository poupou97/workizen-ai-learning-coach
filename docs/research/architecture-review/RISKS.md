# Risks after the Science Slice (ranked by harm to a child × likelihood; evidence per row)

| # | risk | evidence from this slice | status / mitigation |
|---|---|---|---|
| 1 | **Silent agreement on a shared error** stays the top risk: order, CER and splice residue that both stacks share | FTR 0.112 dev / 0.121 held-out / 0.100 science; guards removed none of it (A.6 #1) | open — statistical audit on served blocks (H5); a structurally different verifier for the residue classes |
| 2 | **A withheld-set that looks meaningful hides that trust did not improve** — the guards make the *withheld* blocks explainable, which can read as "safer" | same numbers as #1; coverage fell 0.766 → 0.699 on dev | disclosed in 01 and A.2; never present the reason codes as an FTR improvement |
| 3 | **Question semantics** — 1 in 6–9 auto-labelled questions is not a question; ACTIVITY undetectable from words | ROLE-LAYER §1–2 | Short-Answer deferred; H2/H3 before any prompt is served |
| 4 | **Role Layer over-fit to the Science family's conventions** (KNTT colour boxes, "Em có biết/EM ĐÃ HỌC" labels) | SIDEBAR 0.96 on science vs 0.44 on dev (Toán/Ngữ văn) | scope the trusted subset to the family the lexicon was measured on; re-measure per family before extending |
| 5 | **Page-feature guards cost real content** on colour-heavy elementary pages | Khoa học 4 p6: both real questions withheld; 111 blocks on the slice | measured price; alternative is per-block colour reasoning (not built) |
| 6 | **Gold is small and single-annotator**; the held-out convention had to be corrected once | 54 pages; first-pass held-out FTR 0.261 was an annotation artefact (I.2) | `gold_revision` recorded; second human read of ≥ 10 pages still outstanding (TC-19 #9) |
| 7 | **TOC repair may propagate an OCR-misread header** into a lesson number | 0–2 rejected headers per Science book; the sequence rule + TOC cross-check caught the cover-page "6" only after a fix | rejected headers are logged per book; adopt (#5) only after H7 + spot checks |
| 8 | **SGV leakage** if any pipeline serves SGV pages without the lexicon | 711 blocks on 75 pages would have passed the agreement gate | `answer_leak`/`teacher_text` are mandatory; SGV never merged into SGK documents (B.1) |
| 9 | **Legal**: derivative text in TSLs; page crops in the review bundle | J.1–J.3 | bundle carries crops for the Founder only; nothing under `poc-out/` is committed |
| 10 | **Process**: the slice's success could be read as a green light for a full reprocess | ≈ 14 h with 2 workers is cheap (I.7) | explicitly not authorised; the trust numbers, not the cost, are the gate (TC-12) |
| 11 | **Determinism across OS builds**: Apple Vision output is tied to the macOS build (26.5 / 25F71 recorded) | 7/7 pages identical within the same build | manifest records the build; re-verify on any OS update |
| 12 | **Docling/ocrmac are bake-off venv tools, not project dependencies**; the slice depends on a gitignored venv | MANIFEST.md reproduce section | acceptable for research; productisation needs the licence decision (TC-17 #10) |
