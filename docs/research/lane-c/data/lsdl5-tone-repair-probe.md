# Tone-repair probe on LS&ĐL 5 Bài 8 (Lane C, round 5)

Question: using only the pipeline's own TRUSTED text, does a context-scoped tone-majority signal generate the repair the PRINT shows — and how often does it generate a wrong one? Ground truth is the human verbatim ledger. Nothing is applied to any artefact; every hit is a REPAIRED CANDIDATE.

| rule | scope | min support | evidence keys | slips in the lesson | candidates | correct | false corrections | missed | precision | recall | false-correction rate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| strict-unattested | lesson | 2 | 583 | 15 | 1 | 1 | 0 | 14 | 1.000 | 0.067 | 0.000 |
| strict-unattested | book | 2 | 9691 | 15 | 1 | 1 | 0 | 14 | 1.000 | 0.067 | 0.000 |
| dominant-majority | lesson | 2 | 583 | 15 | 6 | 6 | 0 | 9 | 1.000 | 0.400 | 0.000 |
| dominant-majority | book | 2 | 9691 | 15 | 9 | 8 | 1 | 7 | 0.889 | 0.533 | 0.111 |

## rule = strict-unattested · scope = lesson · block by block

| block | pipeline status | print verdict | slips the print shows | candidates the signal generated | correct | false corrections | missed |
|---|---|---|---|---|---|---|---|
| p038:tc2-p1:003 | WITHHELD | slip | ĐẦU→ĐẤU; KĨ→KÌ | KĨ→KÌ (support 2) | KĨ→KÌ | — | ĐẦU |
| p038:tc2-p1:006 | TRUSTED | slip | tẩm→tầm | — | — | — | tẩm |
| p038:tc2-p1:018 | WITHHELD | slip | đầu→đấu | — | — | — | đầu |
| p039:tc2-p1:001 | TRUSTED | slip | đầu→đấu | — | — | — | đầu |
| p039:tc2-p1:008 | TRUSTED | slip | Lích→Lịch | — | — | — | Lích |
| p039:tc2-p1:009 | WITHHELD | slip | TRỮ→TRỪ; HÂN→HÁN | — | — | — | TRỮ; HÂN |
| p040:tc2-p1:002 | TRUSTED | slip | BĨ→BÍ | — | — | — | BĨ |
| p040:tc2-p1:003 | WITHHELD | slip | triểu→triều | — | — | — | triểu |
| p040:tc2-p1:008 | TRUSTED | slip | PHẢ→PHÁ; HÃN→HÁN | — | — | — | PHẢ; HÃN |
| p041:tc2-p1:002 | TRUSTED | slip | Đăng→Đằng; hóa→hoá | — | — | — | Đăng; hóa |
| p041:tc2-p1:021 | WITHHELD | slip | hiếu→hiểu | — | — | — | hiếu |

## rule = strict-unattested · scope = book · block by block

| block | pipeline status | print verdict | slips the print shows | candidates the signal generated | correct | false corrections | missed |
|---|---|---|---|---|---|---|---|
| p038:tc2-p1:003 | WITHHELD | slip | ĐẦU→ĐẤU; KĨ→KÌ | — | — | — | ĐẦU; KĨ |
| p038:tc2-p1:006 | TRUSTED | slip | tẩm→tầm | — | — | — | tẩm |
| p038:tc2-p1:018 | WITHHELD | slip | đầu→đấu | — | — | — | đầu |
| p039:tc2-p1:001 | TRUSTED | slip | đầu→đấu | — | — | — | đầu |
| p039:tc2-p1:008 | TRUSTED | slip | Lích→Lịch | — | — | — | Lích |
| p039:tc2-p1:009 | WITHHELD | slip | TRỮ→TRỪ; HÂN→HÁN | — | — | — | TRỮ; HÂN |
| p040:tc2-p1:002 | TRUSTED | slip | BĨ→BÍ | — | — | — | BĨ |
| p040:tc2-p1:003 | WITHHELD | slip | triểu→triều | — | — | — | triểu |
| p040:tc2-p1:008 | TRUSTED | slip | PHẢ→PHÁ; HÃN→HÁN | — | — | — | PHẢ; HÃN |
| p041:tc2-p1:002 | TRUSTED | slip | Đăng→Đằng; hóa→hoá | — | — | — | Đăng; hóa |
| p041:tc2-p1:021 | WITHHELD | slip | hiếu→hiểu | hiếu→hiểu (support 14) | hiếu→hiểu | — | — |

## rule = dominant-majority · scope = lesson · block by block

| block | pipeline status | print verdict | slips the print shows | candidates the signal generated | correct | false corrections | missed |
|---|---|---|---|---|---|---|---|
| p038:tc2-p1:003 | WITHHELD | slip | ĐẦU→ĐẤU; KĨ→KÌ | KĨ→KÌ (support 2) | KĨ→KÌ | — | ĐẦU |
| p038:tc2-p1:006 | TRUSTED | slip | tẩm→tầm | — | — | — | tẩm |
| p038:tc2-p1:018 | WITHHELD | slip | đầu→đấu | đầu→đấu (support 4) | đầu→đấu | — | — |
| p039:tc2-p1:001 | TRUSTED | slip | đầu→đấu | đầu→đấu (support 4) | đầu→đấu | — | — |
| p039:tc2-p1:008 | TRUSTED | slip | Lích→Lịch | — | — | — | Lích |
| p039:tc2-p1:009 | WITHHELD | slip | TRỮ→TRỪ; HÂN→HÁN | — | — | — | TRỮ; HÂN |
| p040:tc2-p1:002 | TRUSTED | slip | BĨ→BÍ | BĨ→BÍ (support 3) | BĨ→BÍ | — | — |
| p040:tc2-p1:003 | WITHHELD | slip | triểu→triều | — | — | — | triểu |
| p040:tc2-p1:008 | TRUSTED | slip | PHẢ→PHÁ; HÃN→HÁN | HÃN→HÁN (support 2) | HÃN→HÁN | — | PHẢ |
| p041:tc2-p1:002 | TRUSTED | slip | Đăng→Đằng; hóa→hoá | Đăng→Đằng (support 2) | Đăng→Đằng | — | hóa |
| p041:tc2-p1:021 | WITHHELD | slip | hiếu→hiểu | — | — | — | hiếu |

## rule = dominant-majority · scope = book · block by block

| block | pipeline status | print verdict | slips the print shows | candidates the signal generated | correct | false corrections | missed |
|---|---|---|---|---|---|---|---|
| p038:tc2-p1:003 | WITHHELD | slip | ĐẦU→ĐẤU; KĨ→KÌ | KĨ→KÌ (support 17) | KĨ→KÌ | — | ĐẦU |
| p038:tc2-p1:006 | TRUSTED | slip | tẩm→tầm | tẩm→tầm (support 19) | tẩm→tầm | — | — |
| p038:tc2-p1:018 | WITHHELD | slip | đầu→đấu | đầu→đấu (support 7) | đầu→đấu | — | — |
| p039:tc2-p1:001 | TRUSTED | slip | đầu→đấu | đầu→đấu (support 7) | đầu→đấu | — | — |
| p039:tc2-p1:008 | TRUSTED | slip | Lích→Lịch | — | — | — | Lích |
| p039:tc2-p1:009 | WITHHELD | slip | TRỮ→TRỪ; HÂN→HÁN | — | — | — | TRỮ; HÂN |
| p040:tc2-p1:002 | TRUSTED | slip | BĨ→BÍ | BĨ→BÍ (support 3) | BĨ→BÍ | — | — |
| p040:tc2-p1:003 | WITHHELD | slip | triểu→triều | — | — | — | triểu |
| p040:tc2-p1:008 | TRUSTED | slip | PHẢ→PHÁ; HÃN→HÁN | HÃN→HÁN (support 2) | HÃN→HÁN | — | PHẢ |
| p041:tc2-p1:002 | TRUSTED | slip | Đăng→Đằng; hóa→hoá | Đăng→Đặng (support 3); Đăng→Đằng (support 7) | Đăng→Đằng | Đăng→Đặng | hóa |
| p041:tc2-p1:021 | WITHHELD | slip | hiếu→hiểu | hiếu→hiểu (support 14) | hiếu→hiểu | — | — |
