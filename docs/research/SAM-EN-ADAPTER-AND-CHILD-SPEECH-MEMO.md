# WAL-117 — EN SEMANTIC ADAPTER + CHILD-SPEECH RESEARCH MEMO (2026-09-02)

## 1. EN marker set + distribution (SỐ ĐO THẬT)

Classifier: `tool/design/classify_en.py` v2 — hai tầng rule minh bạch:
(1) SECTION HEADER của bộ Global Success (Getting Started / A Closer Look /
Communication / Skills / Looking Back / Project / Pronunciation);
(2) marker-contains theo ưu tiên (Listen and repeat/tick/number · Let's
sing/chant/talk/play · Point and say · Ask and answer · Match/Circle/Tick/
Label · Choose the correct/Fill in · Read · Write/Complete…).

**LIMITATION ĐO ĐƯỢC (ghi thật):** trang EN dàn nhiều cột, OCR trộn dòng ⇒
v1 (marker ở vị-trí-lệnh như extractor VN) cho OTHER 97.7% — đó là artefact
trộn cột, KHÔNG phải thiếu marker. v2 contains-match có thể dính marker của
hoạt động bên cạnh cùng trang. Con số dưới đây đọc với caveat đó; KHÔNG claim
gì ngoài sample đo được (6.758 unit SGK EN, cả 12 lớp).

| Loại | n | % |
|---|---|---|
| OTHER (content: hội thoại/bài đọc/từ vựng liệt kê) | 4.523 | 66.9% |
| PRONUNCIATION (sing/chant/say sounds/repeat) | 510 | 7.5% |
| LISTENING | 424 | 6.3% |
| INTERACTION (Let's play/pairs/project/game) | 326 | 4.8% |
| READING | 272 | 4.0% |
| SPEAKING (talk/point-and-say/ask-answer/role-play) | 256 | 3.8% |
| WRITING | 222 | 3.3% |
| VOCABULARY (match/circle/tick/label) | 116 | 1.7% |
| GRAMMAR (choose/fill in/correct form) | 109 | 1.6% |

Theo lớp: tiểu học nghiêng LISTENING+INTERACTION (nghe-chơi); THCS/THPT
PRONUNCIATION+SPEAKING/WRITING tăng dần (lớp 12: PRON 103 · READING 50).

## 2. Mapping surface đề xuất (evidence-based)

- LISTENING → Audio player + TTS on-device (Hub, $0) — cần AUDIO ASSET theo
  track sách (① sách in số track — «(28)», «(60)» thấy trong unit thật) —
  KHÔNG có audio bản quyền trong corpus ⇒ Founder/Legal gate cho nguồn audio.
- READING → Reader hiện có (EN passage — cage đổi lexicon, READ-gate giữ).
- WRITING → Compose hiện có (checklist tự-soát EN).
- VOCABULARY/GRAMMAR → QuizSelect (match/choose là selectIdentify).
- SPEAKING/PRONUNCIATION → cần STT/pronunciation (P2-C WAL-123) — xem §3.
- INTERACTION → hoạt động lớp/cặp — ngoài scope 1-learner; giữ như hướng dẫn.

## 3. Child-speech research memo (nguồn dẫn được)

- **ASR non-native EN (có VN trong corpus L2-ARCTIC):** Whisper/AssemblyAI
  đạt MER ~0.054-0.056 trên READ speech người lớn non-native — gần mức người;
  spontaneous kém hơn (RevAI 0.063). ⇒ đọc-theo-đoạn (read-aloud) là use-case
  khả thi nhất về độ chính xác. [arXiv:2503.06924]
- **Trẻ em + mispronunciation detection:** nghiên cứu MDD trên trẻ và người
  lớn học EN cho thấy pipeline ASR-based khả dụng nhưng lỗi phone-level trên
  trẻ em có đặc thù riêng (giọng, độ tuổi) — cần model/threshold theo trẻ,
  không dùng ngưỡng người lớn. [arXiv:2104.05980]
- **VN↔EN phoneme:** có nghiên cứu Whisper cross-lingual phoneme recognition
  giữa tiếng Việt và tiếng Anh — nền cho hướng phát hiện lỗi phát âm do giao
  thoa VN (localize âm EN theo luật VN). [arXiv:2508.19270]
- **Offline/on-device:** Vosk (Apache-2.0, model ~50MB/ngôn ngữ, Android/iOS,
  không gửi audio đi đâu) — ứng viên STT offline; KeenASR — SDK thương mại
  chuyên giọng TRẺ EM, on-device, COPPA-by-design (đo đọc từng từ, insertion/
  deletion/substitution). ⇒ có đường on-device thật, không cần cloud.
- **Privacy verdict (khớp policy đã code):** audio giọng trẻ KHÔNG rời máy —
  education_safety_policy: stt = AGE_GATED, provider ≠ authority; mọi
  pronunciation feedback phải on-device hoặc không làm. Cloud STT cho giọng
  trẻ = Founder Gate (không đề xuất).

## 4. Điều còn KHÔNG biết (không bịa)

- WER thật của Vosk/Whisper-tiny trên giọng TRẺ VN nói EN: chưa có số công bố
  trực tiếp — phải đo POC (P2-C) trước khi hứa tính năng chấm phát âm.
- Audio bản quyền của bộ sách: chưa có trong corpus — LISTENING surface chưa
  build được từ data hiện tại.

Sources: arxiv.org/abs/2503.06924 · arxiv.org/pdf/2104.05980 ·
arxiv.org/html/2508.19270v1 · alphacephei.com/vosk · keenresearch.com.
