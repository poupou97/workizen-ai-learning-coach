FOUNDER ADDENDUM — STRUCTURED STEM EXPRESSION AUDIT

Trước khi tiếp tục Round 5, hãy AUDIT implementation hiện tại xem Học cùng SAM
đã xử lý công thức Toán/Lý/Hóa theo hướng structured expression hay chưa.

Founder đang đề xuất kiến trúc:

SOURCE PDF / IMAGE
→ detect expression region
→ specialized OCR/parser
→ canonical structured representation
→ validation against source
→ mobile rendering.

Target representation:

1. TOÁN
   - LaTeX: representation để render
   - Math AST: representation cho machine/pedagogy
   - source page + bbox/crop: provenance/fallback

2. VẬT LÝ
   - Math AST
   - Symbol / Quantity / Unit semantics
   - LaTeX rendering
   - source provenance

3. HÓA HỌC
   - Chemical Formula / Reaction AST
   - coefficient / element / subscript / charge / reaction arrow
   - suitable LaTeX/structured rendering
   - source provenance

4. FALLBACK
   Nếu expression chưa validate được:
   WITHHOLD structured claim
   + giữ source region/crop cho internal verification/fallback.

Markdown/HTML/plain text KHÔNG được coi là canonical representation
cho mathematical/scientific expressions.

Ví dụ:

3/10 + 5/21

không chỉ nên tồn tại dưới dạng text.

Candidate canonical object nên có tối thiểu:

MathExpression
- sourceBlockId
- page
- bbox
- raw observations
- latex candidate
- structured AST
- validation status
- provenance
- trust/disposition

AST ví dụ phải hiểu đây là:

ADD(
  FRACTION(3,10),
  FRACTION(5,21)
)

chứ không chỉ là string "3/10 + 5/21".

QUAN TRỌNG:
Không được dùng LLM-generated LaTeX/AST như source truth.

OCR/LLM/parser output = candidate.

Chỉ trở thành validated structured expression sau independent
validation/source evidence.

==================================================
AUDIT FIRST — DO NOT DUPLICATE
==================================================

Trước khi implement, trả lời bằng repo evidence:

A. Hiện tại đã có MathBlock / FormulaBlock / Math AST / LaTeX /
   MathML / structured expression model nào chưa?

B. Mobile hiện render công thức bằng gì?
   Plain Text / RichText / Markdown / HTML / LaTeX / SVG / image?

C. OCR pipeline hiện công thức bị flatten thành text ở bước nào?

D. Có specialized math OCR/parser nào đang dùng hoặc đã research chưa?

E. Formula bbox/source crop/provenance hiện có được giữ end-to-end không?

F. Có structural validation cho:
   - fractions
   - operators
   - superscript/subscript
   - equations
   - units
   - symbols
   chưa?

G. Physics hiện có Quantity/Unit semantics chưa?

H. Chemistry hiện có structured chemical formula/reaction representation chưa?

I. Accessibility/export có lý do cần MathML không?

J. Lỗi Round 4 như:
   "3/10 + 5/21" → "10 +"
   sẽ được kiến trúc hiện tại xử lý thế nào?

Phân loại từng capability:

EXISTS AND USED
EXISTS BUT NOT WIRED
PARTIAL
RESEARCH ONLY
MISSING

==================================================
SAU AUDIT
==================================================

Nếu kiến trúc tương đương đã tồn tại:
KHÔNG xây hệ thống thứ hai.
Đề xuất cách harden/reuse.

Nếu thiếu:
đề xuất bounded POC tích hợp vào Round 5 Data Accuracy.

Ưu tiên:

SOURCE REGION
→ Math/Science parser
→ structured AST
→ deterministic structural validation
→ LaTeX/mobile renderer
→ source comparison
→ VALIDATED / WITHHELD.

Không mass-convert corpus.

POC trước trên các expression thật đang FAIL trong legacy audit,
đặc biệt Toán.

Đo:

- expression exact-match accuracy
- structural accuracy
- number/operator accuracy
- false repair rate
- restore precision
- correct-served restored
- wrong-served prevented

Mục tiêu cuối:

FORMULA WITHHELD
→ SPECIALIZED RECOGNITION
→ STRUCTURAL VALIDATION
→ SAFE RESTORE

thay vì:

FORMULA
→ PLAIN OCR TEXT
→ SAM TEACHES IT.

Hãy audit và báo Founder trước:
1. Cái gì đã có.
2. Cái gì đang dùng thật.
3. Gap ở đâu.
4. Có cần thay kiến trúc không.
5. POC nhỏ nhất nên làm gì.

Không merge.
Nếu bounded/reversible research hoặc test có thể làm độc lập,
được phép tiếp tục theo governance Round 5.
