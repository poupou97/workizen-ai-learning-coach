/// WAL-152 (§18) — «KHO KHÁM PHÁ CỦA SAM»: browse + search trên 38 item
/// VERIFIED. IA theo LƯỢNG CONTENT THẬT — section rỗng không render.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/stories_store.dart';
import 'person_detail_screen.dart';
import 'story_detail_screen.dart';

class DiscoveryLibraryScreen extends StatefulWidget {
  const DiscoveryLibraryScreen({super.key, required this.stories});

  final StoriesStore stories;

  @override
  State<DiscoveryLibraryScreen> createState() => _DiscoveryLibraryScreenState();
}

class _DiscoveryLibraryScreenState extends State<DiscoveryLibraryScreen> {
  final _search = TextEditingController();
  List<StoryItem>? _results;

  StoriesStore get s => widget.stories;

  void _doSearch(String q) {
    setState(() => _results = q.trim().isEmpty ? null : s.search(q));
  }

  @override
  Widget build(BuildContext context) {
    final sections = <(String, List<StoryItem>)>[
      ('Danh nhân', s.byType('PERSON')),
      ('Câu nói', s.byType('QUOTE')),
      ('Sự kiện lịch sử', s.byType('EVENT')),
      ('Phát minh & Khám phá', s.byType('INVENTION_DISCOVERY')),
    ];
    return Scaffold(
      backgroundColor: WalColors.surface,
      body: SafeArea(
        child: s.isEmpty
            ? const Center(
                child: Padding(
                  padding: EdgeInsets.all(WalSpacing.lg),
                  child: Text(
                    'Kho khám phá chưa được nạp trên máy này.\n'
                    'SAM sẽ mang các câu chuyện từ sách tới sớm nhé!',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                        fontSize: WalType.body,
                        color: WalColors.inkSoft,
                        height: 1.5),
                  ),
                ),
              )
            : ListView(
                padding: const EdgeInsets.all(WalSpacing.lg),
                children: [
                  const Text('Kho khám phá của SAM',
                      style: TextStyle(
                          fontSize: WalType.display,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink)),
                  const SizedBox(height: WalSpacing.xs),
                  const Text(
                      'Người thật · chuyện thật · từ chính sách giáo khoa — '
                      'mỗi mục đều ghi rõ nguồn.',
                      style: TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft,
                          height: 1.4)),
                  const SizedBox(height: WalSpacing.md),
                  TextField(
                    controller: _search,
                    onSubmitted: _doSearch,
                    onChanged: (v) {
                      if (v.isEmpty) _doSearch('');
                    },
                    decoration: InputDecoration(
                      hintText: 'Tìm người, sự kiện, câu nói…',
                      prefixIcon:
                          const Icon(Icons.search, color: WalColors.inkSoft),
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                          borderRadius:
                              BorderRadius.circular(WalSpacing.radiusButton),
                          borderSide: BorderSide.none),
                    ),
                  ),
                  const SizedBox(height: WalSpacing.md),
                  if (_results != null) ...[
                    Text(
                        _results!.isEmpty
                            ? 'Không tìm thấy trong kho — thử từ khác nhé.'
                            : 'Kết quả (${_results!.length}):',
                        style: const TextStyle(
                            fontSize: WalType.secondary,
                            fontWeight: FontWeight.w700,
                            color: WalColors.inkSoft)),
                    const SizedBox(height: WalSpacing.sm),
                    for (final i in _results!) _tile(i),
                  ] else
                    for (final (label, items) in sections)
                      if (items.isNotEmpty) ...[
                        Padding(
                          padding: const EdgeInsets.only(
                              top: WalSpacing.sm, bottom: WalSpacing.sm),
                          child: Text(
                              '$label (${items.length})',
                              style: const TextStyle(
                                  fontSize: WalType.title,
                                  fontWeight: FontWeight.w700,
                                  color: WalColors.ink)),
                        ),
                        for (final i in items.take(6)) _tile(i),
                        if (items.length > 6)
                          Padding(
                            padding:
                                const EdgeInsets.only(bottom: WalSpacing.sm),
                            child: Text('… và ${items.length - 6} mục nữa '
                                '(tìm để xem hết)',
                                style: const TextStyle(
                                    fontSize: WalType.secondary,
                                    color: WalColors.inkSoft)),
                          ),
                      ],
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

  Widget _tile(StoryItem i) => Padding(
        padding: const EdgeInsets.only(bottom: WalSpacing.sm),
        child: Material(
          color: Colors.white,
          borderRadius: BorderRadius.circular(WalSpacing.radiusChip),
          child: ListTile(
            title: Text(i.title,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                    fontSize: WalType.body,
                    fontWeight: FontWeight.w600,
                    color: WalColors.ink)),
            subtitle: Text('${storyTypeLabel[i.type]} · ${i.subject}',
                style: const TextStyle(
                    fontSize: WalType.secondary, color: WalColors.inkSoft)),
            trailing:
                const Icon(Icons.chevron_right, color: WalColors.primaryText),
            onTap: () {
              if (i.type == 'PERSON' && i.personId != null) {
                Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) => PersonDetailScreen(
                        personId: i.personId!, stories: s)));
              } else {
                Navigator.of(context).push(MaterialPageRoute(
                    builder: (_) =>
                        StoryDetailScreen(item: i, stories: s)));
              }
            },
          ),
        ),
      );
}
