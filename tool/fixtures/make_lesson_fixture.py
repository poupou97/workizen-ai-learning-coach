#!/usr/bin/env python3
"""TRACK B (WAL-210) — sinh FIXTURE bài học cho Lesson Workspace từ MỘT
Trusted Structured Lesson (TSL, `tc2-p1`) + trang PDF SGK.

Round 3 (A1): script này chỉ còn là VỎ MỎNG của cầu chính thức
`tool/corpus/tsl_to_lesson_document.py` — MỘT đường TSL → LessonDocument,
không phải hai. Mọi luật ánh xạ (trust, withheld không chữ, licence, vai trò
lạ ⇒ giữ lại, quan hệ, provenance) và crop nội bộ (Founder D4) nằm ở đó;
hợp đồng: docs/research/TSL-TO-LESSON-DOCUMENT-CONTRACT.md.

    python3 tool/fixtures/make_lesson_fixture.py \
        [--tsl poc-out/trusted-corpus/tc-v2/tc2-p1/lessons/06-sgk-khoa-hoc-tu-nhien-6/bai-17.tsl.json] \
        [--out assets/fixtures/real] [--dpi 150] [--no-crops] \
        [--audit-status notAudited|sampledNoGate] [--audit-ref <đường dẫn tài liệu audit>]

Đầu ra (GITIGNORE — chữ SGK nguyên văn + crop trang KHÔNG lên git, WAL-43):
    assets/fixtures/real/lesson-<book>-b<N>.json
    assets/fixtures/real/crops/<book>-p<NNN>-<figure|withheld>-<id>.png
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'corpus'))
import tsl_to_lesson_document as bridge  # noqa: E402

# Giữ tên cũ cho ai import script này: cùng một hàm, cùng một đường.
build = bridge.build
GENERATOR = bridge.GENERATOR
DISTRIBUTION = bridge.DISTRIBUTION

if __name__ == '__main__':
    sys.exit(bridge.main())
