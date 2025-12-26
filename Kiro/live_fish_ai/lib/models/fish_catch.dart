class FishCatch {
  final String id;
  final String species;
  final double length;
  final double confidence;
  final DateTime timestamp;
  // final Uint8List image; // We can add image data later

  FishCatch({
    required this.id,
    required this.species,
    required this.length,
    required this.confidence,
    required this.timestamp,
    // required this.image,
  });
}
