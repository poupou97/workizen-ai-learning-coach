/// WAL-152 (§20) — STORY DETAIL: SOURCE FACT nguyên gốc + trace nguồn.
/// KHÔNG long-article LLM; phần «SAM giải thích» chỉ mở khi có realization
/// gate (WAL-131) — hiện là ghi chú trung thực, không sinh chữ.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/stories_store.dart';
import 'person_detail_screen.dart';
import '../subjects/subject_display.dart';

const storyTypeLabel = {
  'PERSON': 'Danh nhân',
  'QUOTE': 'Câu nói',
  'EVENT': 'Sự kiện',
  'INVENTION_DISCOVERY': 'Phát minh & Khám phá',
  'SOURCE_EXCERPT': 'Trích văn bản',
};

class StoryDetailScreen extends StatelessWidget {
  const StoryDetailScreen(
      {super.key, required this.item, required this.stories});

  final StoryItem item;
  final StoriesStore stories;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: ListView(
            padding: const EdgeInsets.all(WalSpacing.lg),
            children: [
              Text(storyTypeLabel[item.type] ?? item.type,
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.05,
                      color: WalColors.inkSoft)),
              const SizedBox(height: WalSpacing.sm),
              Text(item.title,
                  style: const TextStyle(
                      fontSize: WalType.display,
                      fontWeight: FontWeight.w700,
                      color: WalColors.ink,
                      height: 1.25)),
              if (item.year != null || item.subject.isNotEmpty) ...[
                const SizedBox(height: WalSpacing.xs),
                Text(
                    [
                      if (item.year != null) 'Năm ${item.year}',
                      '${item.subject} · Lớp ${item.grade}',
                    ].join(' · '),
                    style: const TextStyle(
                        fontSize: WalType.secondary,
                        color: WalColors.inkSoft)),
              ],
              const SizedBox(height: WalSpacing.md),
              Container(
                padding: const EdgeInsets.all(WalSpacing.lg),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(WalSpacing.radiusCard),
                ),
                child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // ⭐ §21/§39 — SOURCE FACT ≠ SAM EXPLANATION: nhãn rõ.
                      const Text('TRÍCH NGUYÊN VĂN TỪ NGUỒN',
                          style: TextStyle(
                              fontSize: WalType.secondary,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1.05,
                              color: WalColors.primaryText)),
                      const SizedBox(height: WalSpacing.sm),
                      Text(item.body,
                          style: const TextStyle(
                              fontSize: WalType.body,
                              color: WalColors.ink,
                              height: 1.5)),
                    ]),
              ),
              const SizedBox(height: WalSpacing.sm),
              Text(storySourceLine(sourceDocumentId: item.sourceDocumentId, pagePdf: item.pagePdf),
                  style: const TextStyle(
                      fontSize: WalType.secondary,
                      fontWeight: FontWeight.w600,
                      color: WalColors.primaryText)),
              if (item.personId != null) ...[
                const SizedBox(height: WalSpacing.md),
                OutlinedButton(
                  onPressed: () => Navigator.of(context).push(
                      MaterialPageRoute(
                          builder: (_) => PersonDetailScreen(
                              personId: item.personId!, stories: stories))),
                  child: Text('Về ${item.personName ?? "nhân vật"} ▸',
                      style: const TextStyle(
                          fontSize: WalType.body,
                          color: WalColors.primaryText)),
                ),
              ],
              const SizedBox(height: WalSpacing.md),
              const Text(
                'SAM sẽ kể thêm về mục này khi phần trò chuyện được mở — '
                'hiện tại con đang đọc đúng những gì sách viết.',
                style: TextStyle(
                    fontSize: WalType.secondary,
                    color: WalColors.inkSoft,
                    height: 1.4),
              ),
              const SizedBox(height: WalSpacing.md),
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('◂ Quay lại',
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.primaryText)),
              ),
            ],
          ),
        ),
      );
}
