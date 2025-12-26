import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:image/image.dart' as img;

// Function to convert CameraImage to img.Image
// This is a standard and somewhat complex function to handle YUV to RGB conversion.
img.Image? convertCameraImage(CameraImage cameraImage) {
  if (cameraImage.format.group != ImageFormatGroup.yuv420) {
    return null;
  }

  final int width = cameraImage.width;
  final int height = cameraImage.height;

  final int uvRowStride = cameraImage.planes[1].bytesPerRow;
  final int uvPixelStride = cameraImage.planes[1].bytesPerPixel!;

  final image = img.Image(width: width, height: height);

  for (int y = 0; y < height; y++) {
    for (int x = 0; x < width; x++) {
      final int uvIndex =
          uvPixelStride * (x / 2).floor() + uvRowStride * (y / 2).floor();
      final int index = y * width + x;

      final yp = cameraImage.planes[0].bytes[index];
      final up = cameraImage.planes[1].bytes[uvIndex];
      final vp = cameraImage.planes[2].bytes[uvIndex];

      int r = (yp + vp * 1436 / 1024 - 179).round().clamp(0, 255);
      int g = (yp - up * 46549 / 131072 + 44 - vp * 93604 / 131072 + 91)
          .round()
          .clamp(0, 255);
      int b = (yp + up * 1814 / 1024 - 227).round().clamp(0, 255);

      image.setPixelRgba(x, y, r, g, b, 255);
    }
  }
  return image;
}
