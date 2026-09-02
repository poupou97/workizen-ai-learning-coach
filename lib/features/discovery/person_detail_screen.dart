/// WAL-152 (§19) — PERSON DETAIL: chỉ những gì CÓ TRONG KHO GIÁO DỤC —
/// không Wikipedia clone, không bịa tiểu sử.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/stories_store.dart';
import 'story_detail_screen.dart';

class PersonDetailScreen extends StatelessWidget {
  const PersonDetailScreen(
      {super.key, required this.personId, required this.stories});

  final String personId;
  final StoriesStore stories;

  @override
  Widget build(BuildContext context) {
    final p = stories.person(personId);
    final items = stories.byPerson(personId);
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: p == null
            ? const Center(
                child: Text('Chưa có thông tin về nhân vật này trong kho.',
                    style: TextStyle(
                        fontSize: WalType.body, color: WalColors.inkSoft)))
            : ListView(
                padding: const EdgeInsets.all(WalSpacing.lg),
                children: [
                  CircleAvatar(
                    radius: 36,
                    backgroundColor: WalColors.surfaceLavender,
                    child: Text(p.name.characters.first,
                        style: const TextStyle(
                            fontSize: 30,
                            fontWeight: FontWeight.w700,
                            color: WalColors.primaryText)),
                  ),
                  const SizedBox(height: WalSpacing.sm),
                  Text(p.name,
                      style: const TextStyle(
                          fontSize: WalType.display,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  Text(
                      [
                        if (p.birthYear != null)
                          '${p.birthYear}–${p.deathYear ?? "?"}',
                        'Xuất hiện trong: ${p.subjects.join(", ")}',
                      ].join(' · '),
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft)),
                  const SizedBox(height: WalSpacing.md),
                  const Text('TRONG SÁCH CỦA CON',
                      style: TextStyle(
                          fontSize: WalType.secondary,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1.05,
                          color: WalColors.inkSoft)),
                  const SizedBox(height: WalSpacing.sm),
                  for (final i in items)
                    Padding(
                      padding: const EdgeInsets.only(bottom: WalSpacing.sm),
                      child: Material(
                        color: Colors.white,
                        borderRadius:
                            BorderRadius.circular(WalSpacing.radiusChip),
                        child: ListTile(
                          title: Text(i.title,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                  fontSize: WalType.body,
                                  fontWeight: FontWeight.w600,
                                  color: WalColors.ink)),
                          subtitle: Text(i.sourceLine,
                              style: const TextStyle(
                                  fontSize: WalType.secondary,
                                  color: WalColors.inkSoft)),
                          onTap: () => Navigator.of(context).push(
                              MaterialPageRoute(
                                  builder: (_) => StoryDetailScreen(
                                      item: i, stories: stories))),
                        ),
                      ),
                    ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('◂ Quay lại',
                        style: TextStyle(
                            fontSize: WalType.body,
                            color: WalColors.primaryText)),
                  ),
                ],
              ),
      ),
    );
  }
}
