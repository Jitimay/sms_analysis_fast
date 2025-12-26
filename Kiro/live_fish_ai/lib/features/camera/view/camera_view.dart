
import 'package:camera/camera.dart';
import 'package:flutter/material.dart' hide BoxPainter;
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:live_fish_ai/features/camera/bloc/camera_bloc.dart';
import 'package:live_fish_ai/features/camera/view/box_painter.dart';
import 'package:live_fish_ai/features/catch_log/view/catch_log_view.dart';

class CameraView extends StatelessWidget {
  const CameraView({super.key});

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;

    return Scaffold(
      appBar: AppBar(
        title: const Text('LiveFish AI'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CatchLogView()),
              );
            },
          ),
        ],
      ),
      body: BlocBuilder<CameraBloc, CameraState>(
        builder: (context, state) {
          if (state is CameraLoadInProgress || state is CameraInitial) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Initializing Camera...'),
                ],
              ),
            );
          }
          if (state is CameraLoadFailure) {
            return Center(
              child: Text('Error: ${state.message}'),
            );
          }
          if (state is CameraReady) {
             final cameraController = context.read<CameraBloc>().cameraController;
            if (cameraController == null || !cameraController.value.isInitialized) {
              return const Center(child: Text('Camera not available.'));
            }

            return Stack(
              children: [
                CameraPreview(cameraController),
                CustomPaint(
                  painter: BoxPainter(
                    detections: state.detections,
                    previewSize: cameraController.value.previewSize!,
                    screenSize: screenSize,
                  ),
                ),
              ],
            );
          }
          return Container(); // Should not be reached
        },
      ),
    );
  }
}

