import 'package:flutter/material.dart';

class CatchLogView extends StatelessWidget {
  const CatchLogView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Catch Log'),
      ),
      body: const Center(
        child: Text('List of catches will be displayed here.'),
      ),
    );
  }
}
