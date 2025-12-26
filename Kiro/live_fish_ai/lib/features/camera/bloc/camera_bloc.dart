import 'package:bloc/bloc.dart';
import 'package:camera/camera.dart';
import 'package:equatable/equatable.dart';
import 'package:live_fish_ai/models/detection.dart';
import 'package:live_fish_ai/services/tflite_service.dart';
import 'package:permission_handler/permission_handler.dart';

part 'camera_event.dart';
part 'camera_state.dart';

class CameraBloc extends Bloc<CameraEvent, CameraState> {
  final TfliteService _tfliteService;
  CameraController? cameraController;
  bool _isProcessing = false;

  CameraBloc({required TfliteService tfliteService})
      : _tfliteService = tfliteService,
        super(CameraInitial()) {
    on<CameraStarted>(_onCameraStarted);
    on<CameraStopped>(_onCameraStopped);
    on<CameraFrameSent>(_onCameraFrameSent);
  }

  Future<void> _onCameraStarted(
    CameraStarted event,
    Emitter<CameraState> emit,
  ) async {
    if (state is CameraReady) return;
    emit(CameraLoadInProgress());
    try {
      final status = await Permission.camera.request();
      if (status.isGranted) {
        final cameras = await availableCameras();
        if (cameras.isNotEmpty) {
          cameraController = CameraController(
            cameras.first,
            ResolutionPreset.high,
            enableAudio: false,
          );
          await cameraController!.initialize();
          cameraController!.startImageStream((image) {
            add(CameraFrameSent(image));
          });
          emit(const CameraReady()); // Emit ready state with empty detections
        } else {
          emit(const CameraLoadFailure('No cameras available.'));
        }
      } else {
        emit(const CameraLoadFailure('Camera permission denied.'));
      }
    } catch (e) {
      emit(CameraLoadFailure(e.toString()));
    }
  }

  Future<void> _onCameraStopped(
    CameraStopped event,
    Emitter<CameraState> emit,
  ) async {
    await cameraController?.stopImageStream();
    await cameraController?.dispose();
    cameraController = null;
    emit(CameraInitial());
  }

  Future<void> _onCameraFrameSent(
    CameraFrameSent event,
    Emitter<CameraState> emit,
  ) async {
    if (_isProcessing) return;
    _isProcessing = true;
    
    final detections = await _tfliteService.runInference(event.cameraImage);
    if (detections != null) {
      emit(CameraReady(detections: detections));
    }
    
    _isProcessing = false;
  }

  @override
  Future<void> close() {
    cameraController?.dispose();
    return super.close();
  }
}
