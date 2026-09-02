/// WAL-108 — bản THẬT của [EducationOcrAdapter] trên thiết bị: ML Kit
/// text recognition (REUSE từ Hub — cùng package/version, quyết định
/// REUSE+ADAPTER trong HUB-TO-SAM matrix; WAL-110).
///
/// Chỉ file này import plugin — adapter interface và extractor thuần Dart
/// nằm ở `education_ocr_adapter.dart` để test chạy mọi nơi.
library;

import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';

import '../../core/perception/perception_provenance.dart';
import 'education_ocr_adapter.dart';

class MlkitEducationOcrAdapter implements EducationOcrAdapter {
  @override
  String get pipelineVersion => 'mlkit-text-v0.15+extract-v1';

  @override
  Future<PerceptionHypothesis?> recognizeExpression(String imagePath) async {
    final recognizer = TextRecognizer(script: TextRecognitionScript.latin);
    try {
      final result =
          await recognizer.processImage(InputImage.fromFilePath(imagePath));
      final lines = [
        for (final block in result.blocks)
          for (final line in block.lines) line.text
      ];
      final expr = extractFractionExpression(lines);
      if (expr == null) return null; // fail closed — SAM sẽ nói «chưa chắc»
      final t = DateTime.now();
      return PerceptionHypothesis(
        // rawImageRef là TÊN TỆP, không phải đường dẫn — không rò bố cục máy.
        hypothesisId: 'mlkit-${t.microsecondsSinceEpoch}',
        rawImageRef: imagePath.split('/').last,
        expression: expr,
        pipelineVersion: pipelineVersion,
        at: t,
      );
    } finally {
      await recognizer.close();
    }
  }
}
