import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const KernelDesktopApp());
}

class KernelDesktopApp extends StatelessWidget {
  const KernelDesktopApp({super.key, this.startTransport = true});

  final bool startTransport;

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Ethos Desktop Shell',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
      ),
      home: TransportStatusPage(startTransport: startTransport),
    );
  }
}

enum KernelConnectionState { connecting, connected, retrying, offline }

class TransportStatusPage extends StatefulWidget {
  const TransportStatusPage({super.key, required this.startTransport});

  final bool startTransport;

  @override
  State<TransportStatusPage> createState() => _TransportStatusPageState();
}

class _TransportStatusPageState extends State<TransportStatusPage> {
  static const String _defaultKernelUrl = String.fromEnvironment(
    'KERNEL_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );
  static const Duration _heartbeatEvery = Duration(seconds: 2);
  static const Duration _httpTimeout = Duration(seconds: 2);
  static const Duration _maxBackoff = Duration(seconds: 8);

  final http.Client _client = http.Client();

  KernelConnectionState _connectionState = KernelConnectionState.connecting;
  Timer? _heartbeatTimer;
  Timer? _retryTimer;
  int _retryCount = 0;
  DateTime? _lastHeartbeatAt;
  Map<String, dynamic>? _healthPayload;
  String _lastMessage = 'Startup...';

  Uri get _pingUri => Uri.parse('$_defaultKernelUrl/api/ping');
  Uri get _statusUri => Uri.parse('$_defaultKernelUrl/api/status');

  @override
  void initState() {
    super.initState();
    if (widget.startTransport) {
      _startTransport();
    } else {
      _lastMessage = 'Transport disabled for tests.';
      _connectionState = KernelConnectionState.offline;
    }
  }

  void _startTransport() {
    _log('startup -> probing kernel at $_defaultKernelUrl');
    _probeAndSchedule();
  }

  Future<void> _probeAndSchedule() async {
    _retryTimer?.cancel();
    await _probeOnce();
    if (!mounted) {
      return;
    }
    if (_connectionState == KernelConnectionState.connected) {
      _startHeartbeatLoop();
    } else {
      _scheduleRetry();
    }
  }

  void _startHeartbeatLoop() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(_heartbeatEvery, (_) {
      unawaited(_probeOnce());
    });
  }

  Future<void> _probeOnce() async {
    if (!mounted) {
      return;
    }
    try {
      final pingResponse = await _client.get(_pingUri).timeout(_httpTimeout);
      if (pingResponse.statusCode != 200) {
        throw Exception('Ping failed with HTTP ${pingResponse.statusCode}');
      }

      final healthResponse = await _client.get(_statusUri).timeout(_httpTimeout);
      if (healthResponse.statusCode != 200) {
        throw Exception('Status failed with HTTP ${healthResponse.statusCode}');
      }

      final dynamic decoded = jsonDecode(healthResponse.body);
      if (decoded is! Map<String, dynamic>) {
        throw Exception('Invalid health payload shape');
      }

      setState(() {
        _connectionState = KernelConnectionState.connected;
        _lastHeartbeatAt = DateTime.now();
        _retryCount = 0;
        _healthPayload = decoded;
        _lastMessage = 'connected';
      });

      _log('connected -> health payload received: ${jsonEncode(decoded)}');
    } catch (error) {
      _heartbeatTimer?.cancel();
      if (!mounted) {
        return;
      }
      setState(() {
        _connectionState = KernelConnectionState.retrying;
        _lastMessage = 'retrying after error: $error';
      });
      _log('connection lost -> scheduling retry, reason: $error');
      _scheduleRetry();
    }
  }

  void _scheduleRetry() {
    _retryTimer?.cancel();
    _retryCount += 1;

    final int exponent = (_retryCount - 1).clamp(0, 4);
    final int delaySeconds = 1 << exponent;
    final Duration delay = Duration(seconds: delaySeconds);
    final Duration boundedDelay = delay > _maxBackoff ? _maxBackoff : delay;

    _retryTimer = Timer(boundedDelay, () {
      unawaited(_probeAndSchedule());
    });
  }

  void _log(String message) {
    debugPrint('[flutter-desktop-shell] $message');
  }

  @override
  void dispose() {
    _heartbeatTimer?.cancel();
    _retryTimer?.cancel();
    _client.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ethos Desktop Shell'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _statusRow('Kernel URL', _defaultKernelUrl),
            const SizedBox(height: 8),
            _statusRow('Connection', _connectionState.name),
            const SizedBox(height: 8),
            _statusRow('Retry count', _retryCount.toString()),
            const SizedBox(height: 8),
            _statusRow('Last heartbeat', _lastHeartbeatAt?.toIso8601String() ?? 'never'),
            const SizedBox(height: 8),
            _statusRow('Transport', _lastMessage),
            const SizedBox(height: 16),
            const Text(
              'Health payload',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.black26),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: SingleChildScrollView(
                  child: SelectableText(
                    _healthPayload == null
                        ? 'Waiting for /api/status payload...'
                        : const JsonEncoder.withIndent('  ').convert(_healthPayload),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statusRow(String label, String value) {
    return Row(
      children: [
        SizedBox(
          width: 130,
          child: Text(
            '$label:',
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ),
        Expanded(child: SelectableText(value)),
      ],
    );
  }
}
