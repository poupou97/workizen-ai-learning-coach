#!/usr/bin/env python3
"""⭐ POC F-OCR — đo chuỗi: OCR → dựng phân số (hình học) → biểu thức → ca → applicability.

Founder (2026-09-01): đo caseUnknown frequency; fail closed khi bằng chứng thị giác
không đủ; KHÔNG bù OCR xấu bằng cách bịa cấu trúc toán học.

Thiết kế falsification không cần nhãn tay:
  - Trang BÀI HỌC đã biết nội dung (Toán 4 Bài 57 tr.62 = ca CHIA HẾT;
    Toán 5 Bài 6 tr.20-21 = ca KHÔNG CHIA HẾT) ⇒ phân bố ca đo được phải khớp sách.
  - Trang MỤC LỤC (p003-p007) = ĐỐI CHỨNG ÂM: tìm ra "phân số" ở mục lục nghĩa là
    thuật toán đang bịa cấu trúc — đúng thứ bị cấm.
Mọi ngưỡng hình học là hằng số CÓ TÊN, bảo thủ: thà bỏ sót còn hơn dựng bừa.
"""
import json, math, sys
from pathlib import Path
from collections import Counter

# ── Ngưỡng hình học (toạ độ chuẩn hoá 0..1) — bảo thủ, fail closed ──
X_ALIGN_FRAC   = 0.6    # lệch tâm ngang tối đa: 60% bề rộng token lớn hơn
Y_GAP_MAX      = 0.030  # tử số cách mẫu số tối đa 3% chiều cao trang
Y_GAP_MIN      = 0.0    # mẫu số phải nằm DƯỚI tử số
OP_Y_TOLERANCE = 0.03   # dấu +/− phải nằm trong dải dọc của hai phân số
OP_X_GAP_MAX   = 0.12   # dấu cách phân số tối đa 12% bề rộng trang
MAX_DEN        = 999    # mẫu số 4+ chữ số ở tiểu học = gần chắc lỗi OCR ⇒ unknown

def is_int_token(t): 
    s = t["text"].strip()
    return s.isdigit() and len(s) <= 3

def xc(t): return t["x"] + t["w"]/2
def yc(t): return t["y"] + t["h"]/2

def reconstruct_fractions(tokens):
    """Ghép (tử, mẫu) theo chiều dọc. Nhập nhằng ⇒ BỎ (fail closed), đếm riêng."""
    nums = [t for t in tokens if is_int_token(t)]
    fractions, ambiguous = [], 0
    for a in nums:
        cands = []
        for b in nums:
            if a is b: continue
            gap = b["y"] - (a["y"] + a["h"])
            if not (Y_GAP_MIN <= gap <= Y_GAP_MAX): continue
            if abs(xc(a)-xc(b)) > X_ALIGN_FRAC * max(a["w"], b["w"], 0.01): continue
            cands.append(b)
        if len(cands) == 1:
            b = cands[0]
            fractions.append({"num": int(a["text"]), "den": int(b["text"]),
                              "x": (xc(a)+xc(b))/2, "ytop": a["y"],
                              "ybot": b["y"]+b["h"]})
        elif len(cands) > 1:
            ambiguous += 1   # nhiều mẫu số khả dĩ ⇒ không đoán
    return fractions, ambiguous

def find_expressions(tokens, fractions):
    """Biểu thức nhị phân: phân số  op  phân số, op ∈ {+, −}."""
    ops = [t for t in tokens if t["text"].strip() in {"+", "-", "−"}]
    exprs = []
    for op in ops:
        left  = [f for f in fractions if f["x"] < xc(op)]
        right = [f for f in fractions if f["x"] > xc(op)]
        if not left or not right: continue
        l = max(left,  key=lambda f: f["x"])
        r = min(right, key=lambda f: f["x"])
        if xc(op)-l["x"] > OP_X_GAP_MAX or r["x"]-xc(op) > OP_X_GAP_MAX: continue
        oy = yc(op)
        if not (min(l["ytop"], r["ytop"]) - OP_Y_TOLERANCE <= oy
                <= max(l["ybot"], r["ybot"]) + OP_Y_TOLERANCE): continue
        exprs.append((l, op["text"].strip(), r))
    return exprs

def classify(d1, d2):
    """Bản sao 1:1 của analyzeFractionPair (Dart) — 4 ca vét cạn + unknown."""
    if d1 <= 0 or d2 <= 0 or d1 > MAX_DEN or d2 > MAX_DEN: return "caseUnknown"
    if d1 == d2: return "denominator-equal"
    if d1 % d2 == 0 or d2 % d1 == 0: return "denominator-divisible"
    return "denominator-non-divisible"

import re
INLINE_RE = re.compile(r"(\d{1,3})\s*/\s*(\d{1,3})\s*([+\-\u2212])\s*(\d{1,3})\s*/\s*(\d{1,3})")

def inline_expressions(tokens):
    """Kênh 2 — phân số VIẾT NGANG trong một dòng OCR ("3/5 + 1/5").
    Hình học không thấy được dạng này; regex tất định, không đoán."""
    out = []
    for t in tokens:
        for m in INLINE_RE.finditer(t["text"]):
            n1, d1, op, n2, d2 = m.groups()
            out.append({"expr": f"{n1}/{d1} {op} {n2}/{d2}",
                        "den": (int(d1), int(d2))})
    return out

def run(groups):
    report = {}
    for label, pages in groups.items():
        agg = Counter(); per_page = {}
        for path in pages:
            d = json.load(open(path))
            toks = d["lines"]
            fr, amb = reconstruct_fractions(toks)
            exprs = find_expressions(toks, fr)
            inline = inline_expressions(toks)
            cases = Counter(classify(l["den"], r["den"]) for l, _, r in exprs)
            cases.update(classify(*e["den"]) for e in inline)
            agg["fractions"] += len(fr); agg["ambiguous"] += amb
            agg["expressions_geom"] += len(exprs)
            agg["expressions_inline"] += len(inline); agg.update(cases)
            per_page[Path(path).stem] = {
                "fractions": len(fr), "ambiguous_dropped": amb,
                "expressions": [
                    {"expr": f"{l['num']}/{l['den']} {op} {r['num']}/{r['den']}",
                     "case": classify(l["den"], r["den"]), "channel": "geom"}
                    for l, op, r in exprs] + [
                    {"expr": e["expr"], "case": classify(*e["den"]),
                     "channel": "inline"}
                    for e in inline]}
        report[label] = {"aggregate": dict(agg), "pages": per_page}
    return report

if __name__ == "__main__":
    base = Path("poc-out/ocr")
    groups = {
        # ĐỐI CHỨNG ÂM — mục lục: phải ~0 biểu thức
        "NEG-CONTROL·toan5-toc":     sorted(str(p) for p in base.glob("toan5/p00[3-9].json")),
        "NEG-CONTROL·toan4mot-toc":  sorted(str(p) for p in base.glob("toan4-mot/p00[3-7].json")),
        # DƯƠNG ĐÃ BIẾT — Toán 4 Bài 57 (tr.62→): ca CHIA HẾT
        "KNOWN·toan4-bai57-quydong": sorted(str(p) for p in base.glob("toan4-hai/p06[2-6].json")),
        # DƯƠNG ĐÃ BIẾT — Toán 5 quanh Bài 6 (PDF=in+1 ⇒ tr.20 = p021): KHÔNG CHIA HẾT
        "KNOWN·toan5-bai6-nondiv":   sorted(str(p) for p in base.glob("toan5/p02[0-3].json")),
        # NỀN RỘNG — mọi trang phân số Toán 5 đã OCR (p024–046)
        "BROAD·toan5-fraction-unit": sorted(str(p) for p in base.glob("toan5/p0[2-4][0-9].json")),
    }
    print(json.dumps(run(groups), ensure_ascii=False, indent=1))
