import 'dart:math';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:image/image.dart' as img;
import 'package:live_fish_ai/models/detection.dart';
import 'package:live_fish_ai/utils/image_converter.dart';
import 'package:tflite_flutter/tflite_flutter.dart';

class TfliteService {
  static const int modelInputSize = 320;
  static const double confidenceThreshold = 0.5;
  static const double nmsThreshold = 0.4;

  Interpreter? _interpreter;
  bool _isModelLoaded = false;

  bool get isModelLoaded => _isModelLoaded;

  Future<void> loadModel() async {
    try {
      final options = InterpreterOptions();
      _interpreter = await Interpreter.fromAsset('assets/ml/yolov8n.tflite', options: options);
      _interpreter!.allocateTensors();
      _isModelLoaded = true;
      print('Model loaded successfully!');
    } catch (e) {
      print('Failed to load model: $e');
      _isModelLoaded = false;
    }
  }

  Future<List<Detection>?> runInference(CameraImage cameraImage) async {
    if (!_isModelLoaded || _interpreter == null) return null;

    final rgbImage = convertCameraImage(cameraImage);
    if (rgbImage == null) return null;

    final resizedImage = img.copyResize(rgbImage, width: modelInputSize, height: modelInputSize);
    final inputBytes = Float32List(1 * modelInputSize * modelInputSize * 3);
    int pixelIndex = 0;
    for (int y = 0; y < modelInputSize; y++) {
      for (int x = 0; x < modelInputSize; x++) {
        final pixel = resizedImage.getPixel(x, y);
        inputBytes[pixelIndex++] = pixel.r / 255.0;
        inputBytes[pixelIndex++] = pixel.g / 255.0;
        inputBytes[pixelIndex++] = pixel.b / 255.0;
      }
    }
    
    final input = inputBytes.reshape([1, modelInputSize, modelInputSize, 3]);
    final output = List.filled(1 * 84 * 8400, 0.0).reshape([1, 84, 8400]);

    _interpreter!.run(input, output);

    return _postprocessOutput(output, cameraImage.height, cameraImage.width);
  }

  List<Detection> _postprocessOutput(List<dynamic> output, int originalHeight, int originalWidth) {
    final transposedOutput = List.generate(
        output[0][0].length, (i) => List.generate(output[0].length, (j) => output[0][j][i]));

    final List<Rect> boxes = [];
    final List<double> confidences = [];

    for (final row in transposedOutput) {
      final confidence = row[4]; // Assuming confidence is at index 4 for single class
      if (confidence > confidenceThreshold) {
        final cx = row[0];
        final cy = row[1];
        final w = row[2];
        final h = row[3];

        // Scale coordinates back to original image size
        final scaleX = originalWidth / modelInputSize;
        final scaleY = originalHeight / modelInputSize;

        final left = (cx - w / 2) * scaleX;
        final top = (cy - h / 2) * scaleY;
        final width = w * scaleX;
        final height = h * scaleY;

        boxes.add(Rect.fromLTWH(left, top, width, height));
        confidences.add(confidence);
      }
    }

    final List<int> nmsIndexes = _nonMaximumSuppression(boxes, confidences);

    final List<Detection> detections = [];
    for (final index in nmsIndexes) {
      detections.add(Detection(
        box: boxes[index],
        confidence: confidences[index],
        className: 'fish', // Only one class
      ));
    }

    return detections;
  }

  List<int> _nonMaximumSuppression(List<Rect> boxes, List<double> confidences) {
    if (boxes.isEmpty) return [];

    List<int> indices = List.generate(boxes.length, (i) => i);
    indices.sort((a, b) => confidences[b].compareTo(confidences[a]));

    List<int> selectedIndices = [];
    while (indices.isNotEmpty) {
      int mainIndex = indices.first;
      selectedIndices.add(mainIndex);
      indices.removeAt(0);

      List<int> remainingIndices = [];
      for (final index in indices) {
        double iou = _calculateIoU(boxes[mainIndex], boxes[index]);
        if (iou < nmsThreshold) {
          remainingIndices.add(index);
        }
      }
      indices = remainingIndices;
    }
    return selectedIndices;
  }

  double _calculateIoU(Rect rect1, Rect rect2) {
    final double intersectionLeft = max(rect1.left, rect2.left);
    final double intersectionTop = max(rect1.top, rect2.top);
    final double intersectionRight = min(rect1.right, rect2.right);
    final double intersectionBottom = min(rect1.bottom, rect2.bottom);

    final double intersectionArea =
        max(0, intersectionRight - intersectionLeft) * max(0, intersectionBottom - intersectionTop);
    final double unionArea = rect1.width * rect1.height + rect2.width * rect2.height - intersectionArea;

    return intersectionArea / unionArea;
  }

  void close() {
    _interpreter?.close();
    _isModelLoaded = false;
    print('Model closed.');
  }
}

