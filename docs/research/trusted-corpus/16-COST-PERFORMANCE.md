# 16 — Cost / Performance (one Apple M1, 16 GB, 8 cores; MEASURED unless marked ESTIMATED)

## Per-page cost of each stack

| stack | s/page (median) | measured on | notes |
|---|---|---|---|
| Apple Vision OCR (existing) | already paid for all 62,729 pages | — | `poc-out/graph/ocr-body`, 665 MB |
| current XY-cut | 0.02 | 188 pages | pure Python |
| **Docling 2.126 + ocrmac** | **3.33** (p10 2.7, p90 4.3, max 13.1) | 146 pilot pages, CPU, **while Marker + VLM were also running** | first page of a process +25 s model load; single-page PDFs; no batching |
| MinerU 3.4.5 pipeline (CPU) | 18.5 | 38 gold pages | + one-time 2 GB model download; Vietnamese OCR unusable |
| Marker 2.0 / Surya 2 (llama.cpp, CPU/Metal) | 129 | 24–28 gold pages | 650M VLM per page; GPU class hardware changes this by ~50–100× (ESTIMATED from published figures, not measured) |
| Qwen2.5-VL-3B 4-bit (mlx) | 83 | 22–27 gold pages | 120-dpi input, 3,000 max tokens |
| layout census (both signals) | 0.003 (6 workers) | 62,729 pages | 179 s total |

## Whole-corpus extrapolation (62,729 pages)

| pipeline | wall time on this Mac | feasible? |
|---|---|---|
| census (done) | 3 min | done |
| XY-cut for all pages | ~20 min | yes |
| Docling + ocrmac, sequential | 62,729 × 3.33 s ≈ **58 h** (≈ 2.4 days); with 2 parallel processes on 8 cores ≈ 30–35 h (ESTIMATED; RAM ≈ 2 GB/process) | yes, over a weekend |
| Docling ▸ XY-cut cascade | Docling + 20 min | yes |
| MinerU (layout only, text from Apple Vision) | 62,729 × 18.5 s ≈ 13.4 days | marginal; not useful without Vietnamese OCR |
| Marker / Surya 2 | 62,729 × 129 s ≈ **94 days** | no on this Mac; ESTIMATED 1–3 days on one CUDA GPU |
| VLM verifier (3B) | 62,729 × 83 s ≈ 60 days | no; and it does not add trust (10) |
| human review of the withheld share | ESTIMATED 15–20 % of blocks ≈ 40–60 k blocks ≈ 60–90 person-days at 1 min/block | only for shipped lessons, not the corpus |

## Storage

| artefact | per page | corpus |
|---|---|---|
| Docling JSON (raw) | 17.6 KB median | ≈ 1.1 GB |
| XY-cut JSON | 5.8 KB | ≈ 0.36 GB |
| SDM with two stacks + trust reasons | ≈ 30–40 KB (ESTIMATED) | ≈ 2–2.5 GB |
| page renders 200 dpi (review only, withheld pages) | ≈ 330 KB | ≈ 4 GB if 20 % of pages |
| this study's outputs | — | census 32 MB, renders 86 MB, single-page PDFs 50 MB, raw bake-off 7 MB |

## Determinism / offline / integration

- Docling (CPU) and the XY-cut are deterministic and fully offline once models are cached (`DOCLING_ARTIFACTS_PATH`); Apple Vision is deterministic per macOS build but **macOS-only** — a Linux batch farm would need a different OCR (the census shows why that is not a small change: every trust number here is tied to this OCR's error profile).
- Integration complexity (ESTIMATED): SDM writer + Docling adapter 1–2 days (exists as research code); role layer 1–2 weeks to reach a measurable 0.95 question precision; guards + review queue 1 week; header-based lesson attachment + TOC repair 3–5 days.

## What was NOT spent

No cloud inference, no paid API, no GPU. Total compute for the study: ≈ 6 h of Mac time (census 3 min, bake-off ≈ 3.5 h dominated by Marker/VLM, pilot ≈ 10 min, scoring minutes). Installed tooling: 4 venvs (4.1 GB) + llama.cpp via Homebrew — all gitignored, none a project dependency.
