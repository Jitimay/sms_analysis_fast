import 'package:flutter/material.dart';

class Detection {
  final Rect box;
  final double confidence;
  final String className;

  Detection({
    required this.box,
    required this.confidence,
    required this.className,
  });
}
