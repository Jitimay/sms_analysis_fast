import 'package:flutter/material.dart';
import 'package:live_fish_ai/models/detection.dart';

class BoxPainter extends CustomPainter {
  final List<Detection> detections;
  final Size previewSize;
  final Size screenSize;

  BoxPainter({
    required this.detections,
    required this.previewSize,
    required this.screenSize,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0
      ..color = Colors.red;

    for (final detection in detections) {
      // Scale box from preview size to screen size
      final scaleX = screenSize.width / previewSize.width;
      final scaleY = screenSize.height / previewSize.height;

      final scaledBox = Rect.fromLTRB(
        detection.box.left * scaleX,
        detection.box.top * scaleY,
        detection.box.right * scaleX,
        detection.box.bottom * scaleY,
      );

      canvas.drawRect(scaledBox, paint);

      final textPainter = TextPainter(
        text: TextSpan(
          text: '${detection.className} ${(detection.confidence * 100).toStringAsFixed(2)}%',
          style: const TextStyle(
            color: Colors.white,
            backgroundColor: Colors.red,
            fontSize: 14.0,
          ),
        ),
        textAlign: TextAlign.left,
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(scaledBox.left, scaledBox.top - textPainter.height));
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) {
    return true;
  }
}
