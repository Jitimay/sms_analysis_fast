import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'dart:developer' as developer;

class Visualization3DScreen extends StatefulWidget {
  const Visualization3DScreen({super.key});

  @override
  State<Visualization3DScreen> createState() => _Visualization3DScreenState();
}

class _Visualization3DScreenState extends State<Visualization3DScreen> {
  late final WebViewController _controller;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _initializeWebView();
  }

  void _initializeWebView() {
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            if (progress == 100) {
              setState(() {
                _isLoading = false;
              });
            }
          },
          onPageStarted: (String url) {
            setState(() {
              _isLoading = true;
            });
          },
          onPageFinished: (String url) {
            setState(() {
              _isLoading = false;
            });
          },
        ),
      )
      ..loadFlutterAsset('assets/3d_visualization/index.html');

    // Add JavaScript channels for Flutter-WebView communication
    _controller.addJavaScriptChannel(
      'FlutterChannel',
      onMessageReceived: (JavaScriptMessage message) {
        // Handle messages from JavaScript
        _handleJavaScriptMessage(message.message);
      },
    );
  }

  void _handleJavaScriptMessage(String message) {
    // Parse and handle messages from the 3D visualization
    developer.log('Message from 3D visualization: $message', name: 'AgriPulse3D');
    
    // You can update Flutter UI based on 3D interactions
    if (message.contains('satellite_clicked')) {
      _showSatelliteDetails(message);
    } else if (message.contains('region_clicked')) {
      _showRegionDetails(message);
    }
  }

  void _showSatelliteDetails(String message) {
    // Extract satellite data from message and show details
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Data Stream Details',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text('Real-time coffee price monitoring active'),
            const Text('Last update: 2 minutes ago'),
            const Text('Status: Price volatility detected'),
          ],
        ),
      ),
    );
  }

  void _showRegionDetails(String message) {
    // Extract region data from message and show details
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Region Details',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            const Text('Kayanza Province'),
            const Text('Current Status: Watch'),
            const Text('Active Alerts: 2'),
            const Text('Weather: Partly cloudy, 24°C'),
          ],
        ),
      ),
    );
  }

  void _sendDataToVisualization() {
    // Send real-time data updates to the 3D visualization
    _controller.runJavaScript('''
      // Update satellite status
      if (window.agriPulse3D) {
        window.agriPulse3D.updateSatelliteStatus('prices', 'threat');
        window.agriPulse3D.triggerPulse('prices', 'kayanza');
      }
    ''');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('AgriPulse Echo'),
        backgroundColor: const Color(0xFF6F4E37),
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              _controller.reload();
            },
          ),
          IconButton(
            icon: const Icon(Icons.fullscreen),
            onPressed: () {
              // Toggle fullscreen mode
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => _FullscreenVisualization(controller: _controller),
                ),
              );
            },
          ),
        ],
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_isLoading)
            const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(
                    color: Color(0xFF6F4E37),
                  ),
                  SizedBox(height: 16),
                  Text(
                    'Loading 3D Visualization...',
                    style: TextStyle(
                      color: Color(0xFF6F4E37),
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          FloatingActionButton(
            heroTag: "simulate",
            mini: true,
            backgroundColor: const Color(0xFF4CAF50),
            onPressed: _sendDataToVisualization,
            child: const Icon(Icons.play_arrow, color: Colors.white),
          ),
          const SizedBox(height: 8),
          FloatingActionButton(
            heroTag: "reset",
            mini: true,
            backgroundColor: const Color(0xFF6F4E37),
            onPressed: () {
              _controller.runJavaScript('location.reload()');
            },
            child: const Icon(Icons.restart_alt, color: Colors.white),
          ),
        ],
      ),
    );
  }
}

class _FullscreenVisualization extends StatelessWidget {
  final WebViewController controller;

  const _FullscreenVisualization({required this.controller});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: SafeArea(
        child: Stack(
          children: [
            WebViewWidget(controller: controller),
            Positioned(
              top: 16,
              right: 16,
              child: IconButton(
                icon: const Icon(Icons.close, color: Colors.white, size: 30),
                onPressed: () => Navigator.pop(context),
              ),
            ),
          ],
        ),
      ),
    );
  }
}