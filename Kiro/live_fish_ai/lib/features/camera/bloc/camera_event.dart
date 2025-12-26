part of 'camera_bloc.dart';

abstract class CameraEvent extends Equatable {
  const CameraEvent();

  @override
  List<Object> get props => [];
}

class CameraStarted extends CameraEvent {}

class CameraStopped extends CameraEvent {}

class CameraFrameSent extends CameraEvent {
  final CameraImage cameraImage;

  const CameraFrameSent(this.cameraImage);

  @override
  List<Object> get props => [cameraImage];
}
