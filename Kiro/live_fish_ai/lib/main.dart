import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:live_fish_ai/features/camera/bloc/camera_bloc.dart';
import 'package:live_fish_ai/features/camera/view/camera_view.dart';
import 'package:live_fish_ai/services/tflite_service.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Hive.initFlutter();

  final tfliteService = TfliteService();
  await tfliteService.loadModel();

  runApp(
    RepositoryProvider.value(
      value: tfliteService,
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'LiveFish AI',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: BlocProvider(
        create: (context) => CameraBloc(
          tfliteService: context.read<TfliteService>(),
        )..add(CameraStarted()), // Start the camera immediately
        child: const CameraView(),
      ),
    );
  }
}

