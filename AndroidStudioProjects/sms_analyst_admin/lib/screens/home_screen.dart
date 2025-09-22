import 'package:flutter/material.dart';
import '../api.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? _stats;
  List<dynamic>? _users;
  String? _error;
  bool _loading = true;

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final st = await Api.I.stats();
      final us = await Api.I.users();
      if (!mounted) return;
      setState(() { _stats = st; _users = us; });
    } catch (e) {
      setState(() { _error = "Load failed: $e"; });
    } finally {
      if (mounted) setState(() { _loading = false; });
    }
  }

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Dashboard"),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text(_error!))
              : Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    children: [
                      Row(children: [
                        _MetricCard(label: "Users", value: "${_stats?['users'] ?? 0}"),
                        _MetricCard(label: "Tx", value: "${_stats?['transactions'] ?? 0}"),
                        _MetricCard(label: "Opps", value: "${_stats?['opportunities'] ?? 0}"),
                        _MetricCard(label: "Opt-ins", value: "${_stats?['opt_ins'] ?? 0}"),
                      ]),
                      const SizedBox(height: 12),
                      const Align(alignment: Alignment.centerLeft, child: Text("Recent Users", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold))),
                      const SizedBox(height: 8),
                      Expanded(
                        child: ListView.separated(
                          itemCount: _users?.length ?? 0,
                          separatorBuilder: (_, __) => const Divider(height: 1),
                          itemBuilder: (_, i) {
                            final u = _users![i];
                            return ListTile(
                              title: Text(u['phone'] ?? ''),
                              subtitle: Text("${u['role']} • ${u['created_at']}"),
                              leading: const Icon(Icons.person),
                            );
                          },
                        ),
                      ),
                    ],
                  ),
                ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label;
  final String value;
  const _MetricCard({required this.label, required this.value});
  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(children: [
            Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(label),
          ]),
        ),
      ),
    );
  }
}
