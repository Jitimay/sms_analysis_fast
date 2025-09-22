import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../api.dart';
import '../main.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phone = TextEditingController(text: "+25700000000");
  final _pass = TextEditingController();
  bool _loading = false;
  String? _error;

  Future<void> _doLogin() async {
    setState(() { _loading = true; _error = null; });
    try {
      final ok = await Api.I.login(_phone.text.trim(), _pass.text);
      if (!mounted) return;
      if (ok) {
        context.read<AuthState>().setAuthed(true);
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        setState(() { _error = "Invalid credentials"; });
      }
    } catch (e) {
      setState(() { _error = "Login failed: $e"; });
    } finally {
      if (mounted) setState(() { _loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 420),
          child: Card(
            elevation: 2,
            margin: const EdgeInsets.all(16),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                const Text("SMS Analyst Admin", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
                const SizedBox(height: 12),
                TextField(controller: _phone, decoration: const InputDecoration(labelText: "Phone (+257...)")),
                const SizedBox(height: 8),
                TextField(controller: _pass, obscureText: true, decoration: const InputDecoration(labelText: "Password")),
                const SizedBox(height: 16),
                if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
                const SizedBox(height: 8),
                FilledButton(
                  onPressed: _loading ? null : _doLogin,
                  child: _loading ? const CircularProgressIndicator() : const Text("Sign in"),
                ),
              ]),
            ),
          ),
        ),
      ),
    );
  }
}
