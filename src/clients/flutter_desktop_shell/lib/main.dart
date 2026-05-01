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
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF00BFA5),
          brightness: Brightness.dark,
        ),
        scaffoldBackgroundColor: const Color(0xFF0D1117),
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
  final ScrollController _payloadScrollController = ScrollController();

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

      final healthResponse = await _client
          .get(_statusUri)
          .timeout(_httpTimeout);
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
    _payloadScrollController.dispose();
    _client.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final _StatusBadgeData badge = _statusBadgeForState(_connectionState, theme);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Ethos Desktop Shell'),
        centerTitle: false,
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 12),
            child: _ConnectionBadge(data: badge),
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: LayoutBuilder(
            builder: (BuildContext context, BoxConstraints constraints) {
              final bool isWide = constraints.maxWidth >= 1050;
              final Widget statusCard = _buildStatusCard(theme, badge);
              final Widget payloadCard = _buildPayloadCard(theme);

              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(flex: 5, child: statusCard),
                    const SizedBox(width: 16),
                    Expanded(flex: 7, child: payloadCard),
                  ],
                );
              }

              return Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  statusCard,
                  const SizedBox(height: 16),
                  Expanded(child: payloadCard),
                ],
              );
            },
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard(ThemeData theme, _StatusBadgeData badge) {
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Transport Overview',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Desktop shell status and transport diagnostics',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 14),
            _ConnectionBadge(data: badge),
            const SizedBox(height: 14),
            _statusRow('Kernel URL', _defaultKernelUrl),
            const SizedBox(height: 10),
            _statusRow('Connection', badge.label),
            const SizedBox(height: 10),
            _statusRow('Retry count', _retryCount.toString()),
            const SizedBox(height: 10),
            _statusRow(
              'Last heartbeat',
              _lastHeartbeatAt?.toIso8601String() ?? 'never',
            ),
            const SizedBox(height: 10),
            _statusRow('Transport', _lastMessage),
          ],
        ),
      ),
    );
  }

  Widget _buildPayloadCard(ThemeData theme) {
    final String payloadText =
        _healthPayload == null
            ? 'Waiting for /api/status payload...'
            : const JsonEncoder.withIndent('  ').convert(_healthPayload);

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Health payload',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Monospace JSON preview with stable scroll',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: const Color(0xFF0B0F14),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: theme.colorScheme.outlineVariant),
                ),
                child: Scrollbar(
                  controller: _payloadScrollController,
                  thumbVisibility: true,
                  child: SingleChildScrollView(
                    controller: _payloadScrollController,
                    padding: const EdgeInsets.all(14),
                    child: SelectableText(
                      payloadText,
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 13,
                        height: 1.35,
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  _StatusBadgeData _statusBadgeForState(
    KernelConnectionState state,
    ThemeData theme,
  ) {
    switch (state) {
      case KernelConnectionState.connected:
        return _StatusBadgeData(
          label: 'Connected',
          textColor: theme.colorScheme.primary,
          bgColor: theme.colorScheme.primary.withOpacity(0.16),
        );
      case KernelConnectionState.retrying:
        return _StatusBadgeData(
          label: 'Retrying',
          textColor: Colors.amber.shade300,
          bgColor: Colors.amber.withOpacity(0.16),
        );
      case KernelConnectionState.offline:
        return _StatusBadgeData(
          label: 'Offline',
          textColor: theme.colorScheme.error,
          bgColor: theme.colorScheme.error.withOpacity(0.16),
        );
      case KernelConnectionState.connecting:
        return _StatusBadgeData(
          label: 'Connecting',
          textColor: theme.colorScheme.secondary,
          bgColor: theme.colorScheme.secondary.withOpacity(0.16),
        );
    }
  }

  Widget _statusRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 140,
          child: Text(
            '$label:',
            style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13),
          ),
        ),
        Expanded(
          child: SelectableText(
            value,
            style: const TextStyle(fontSize: 13),
          ),
        ),
      ],
    );
  }
}

class _StatusBadgeData {
  const _StatusBadgeData({
    required this.label,
    required this.textColor,
    required this.bgColor,
  });

  final String label;
  final Color textColor;
  final Color bgColor;
}

class _ConnectionBadge extends StatelessWidget {
  const _ConnectionBadge({required this.data});

  final _StatusBadgeData data;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        color: data.bgColor,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: data.textColor.withOpacity(0.35)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.circle, size: 10, color: data.textColor),
            const SizedBox(width: 8),
            Text(
              data.label,
              style: TextStyle(
                color: data.textColor,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.2,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
