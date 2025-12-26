part of 'camera_bloc.dart';

abstract class CameraState extends Equatable {
  const CameraState();

  @override
  List<Object> get props => [];
}

class CameraInitial extends CameraState {}

class CameraLoadInProgress extends CameraState {}

class CameraReady extends CameraState {
  final List<Detection> detections;

  const CameraReady({this.detections = const []});

  @override
  List<Object> get props => [detections];
}

class CameraLoadFailure extends CameraState {
  final String message;

  const CameraLoadFailure(this.message);

  @override
  List<Object> get props => [message];
}
