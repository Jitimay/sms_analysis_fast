import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'api.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Api.I.init();
  runApp(const App());
}

class AuthState extends ChangeNotifier {
  bool _authed = false;
  bool get authed => _authed;
  void setAuthed(bool v) { _authed = v; notifyListeners(); }
}

class App extends StatelessWidget {
  const App({super.key});
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthState(),
      child: MaterialApp(
        title: 'SMS Analyst Admin',
        theme: ThemeData(useMaterial3: true),
        home: const LoginScreen(),
        routes: {
          '/home': (_) => const HomeScreen(),
          '/login': (_) => const LoginScreen(),
        },
      ),
    );
  }
}
