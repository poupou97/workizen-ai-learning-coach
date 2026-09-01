/// «Học cùng SAM» — entry. Slice 1: mở thẳng màn HÔM NAY trên fixture domain
/// thật (WAL-51). Điều hướng đầy đủ đến khi các slice sau ghép vào.
library;

import 'package:flutter/material.dart';

import 'features/mission/mission_center_screen.dart';
import 'features/mission/mission_data.dart';

void main() => runApp(const HocCungSamApp());

class HocCungSamApp extends StatelessWidget {
  const HocCungSamApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Học cùng SAM',
        debugShowCheckedModeBanner: false,
        home: MissionCenterScreen(data: buildDemoMission()),
      );
}
