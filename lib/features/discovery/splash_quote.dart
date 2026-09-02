/// WAL-152 (§15) — LOADING QUOTE: hiện TRONG lúc app load thật — không delay
/// nhân tạo; app load nhanh thì màn này chỉ thoáng qua, đó là ĐÚNG.
library;

import 'package:flutter/material.dart';

import '../../app/theme/wal_tokens.dart';
import '../../core/stories/stories_store.dart';

class SplashQuoteScreen extends StatelessWidget {
  const SplashQuoteScreen({super.key, required this.quote});

  final StoryItem quote;

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: WalColors.surface,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(WalSpacing.xl),
            child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(quote.title,
                      style: const TextStyle(
                          fontSize: WalType.title,
                          fontWeight: FontWeight.w700,
                          color: WalColors.ink,
                          height: 1.4)),
                  const SizedBox(height: WalSpacing.sm),
                  if (quote.personName != null)
                    Text('— ${quote.personName}',
                        style: const TextStyle(
                            fontSize: WalType.body,
                            color: WalColors.primaryText)),
                  const SizedBox(height: WalSpacing.xs),
                  Text(quote.sourceLine,
                      style: const TextStyle(
                          fontSize: WalType.secondary,
                          color: WalColors.inkSoft)),
                ]),
          ),
        ),
      );
}
