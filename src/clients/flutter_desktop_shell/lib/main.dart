import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
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
  static const List<String> _gateOrder = <String>['G1', 'G2', 'G3', 'G4', 'G5'];
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
  DateTime? _lastManualProbeAt;
  Map<String, dynamic>? _healthPayload;
  String _lastMessage = 'Startup...';
  bool _manualProbeInFlight = false;
  VoiceUiState _voiceUiState = VoiceUiState.micOff;
  String _voiceEventSource = 'placeholder';
  DateTime? _lastVoiceStateAt;
  bool _hasServerVoiceState = false;
  bool _payloadHasFocus = false;
  String _payloadActionMessage = 'No payload action yet.';
  String _diagnosticsActionMessage = 'No diagnostics export yet.';
  final List<_DiagnosticEvent> _diagnosticEvents = <_DiagnosticEvent>[];
  _DiagnosticFilter _diagnosticFilter = _DiagnosticFilter.all;
  _DiagnosticSeverityFilter _diagnosticSeverityFilter =
      _DiagnosticSeverityFilter.all;
  _DiagnosticDepth _diagnosticDepth = _DiagnosticDepth.medium;
  Map<String, String> _readinessGates = <String, String>{
    'G1': 'unknown',
    'G2': 'unknown',
    'G3': 'unknown',
    'G4': 'unknown',
    'G5': 'unknown',
  };
  Map<String, _GateDetailData> _gateDetails = <String, _GateDetailData>{};
  String _gateSource = 'fallback';

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
      _updateVoiceStateFromHealth(decoded);
      _updateGateReadinessFromHealth(decoded);

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

  Future<void> _runManualProbe() async {
    if (_manualProbeInFlight || !mounted) {
      return;
    }
    setState(() {
      _manualProbeInFlight = true;
      _connectionState = KernelConnectionState.connecting;
      _lastMessage = 'manual probe requested';
      _lastManualProbeAt = DateTime.now();
    });
    _log('manual probe requested by operator');
    _heartbeatTimer?.cancel();
    _retryTimer?.cancel();
    await _probeAndSchedule();
    if (!mounted) {
      return;
    }
    setState(() {
      _manualProbeInFlight = false;
    });
  }

  void _log(String message) {
    debugPrint('[flutter-desktop-shell] $message');
    _recordDiagnosticEvent(message);
  }

  void _recordDiagnosticEvent(String message) {
    if (!mounted) {
      return;
    }
    setState(() {
      _diagnosticEvents.insert(
        0,
        _DiagnosticEvent(
          at: DateTime.now(),
          message: message,
          type: _diagnosticTypeForMessage(message),
          severity: _diagnosticSeverityForMessage(message),
        ),
      );
      while (_diagnosticEvents.length > _diagnosticDepth.maxEntries) {
        _diagnosticEvents.removeLast();
      }
    });
  }

  _DiagnosticFilter _diagnosticTypeForMessage(String message) {
    final String text = message.toLowerCase();
    if (text.contains('manual probe')) {
      return _DiagnosticFilter.manual;
    }
    return _DiagnosticFilter.transport;
  }

  _DiagnosticSeverity _diagnosticSeverityForMessage(String message) {
    final String text = message.toLowerCase();
    if (text.contains('connection lost') ||
        text.contains('retrying after error') ||
        text.contains('failed')) {
      return _DiagnosticSeverity.high;
    }
    if (text.contains('manual probe') || text.contains('retry')) {
      return _DiagnosticSeverity.medium;
    }
    return _DiagnosticSeverity.low;
  }

  void _focusHighSeverityDiagnostics() {
    if (!mounted) {
      return;
    }
    setState(() {
      _diagnosticFilter = _DiagnosticFilter.all;
      _diagnosticSeverityFilter = _DiagnosticSeverityFilter.high;
    });
  }

  void _resetDiagnosticsFilters() {
    if (!mounted) {
      return;
    }
    setState(() {
      _diagnosticFilter = _DiagnosticFilter.all;
      _diagnosticSeverityFilter = _DiagnosticSeverityFilter.all;
    });
  }

  void _updateVoiceStateFromHealth(Map<String, dynamic> payload) {
    final dynamic explicitState =
        payload['voice_state'] ??
        payload['voice_turn_state'] ??
        (payload['voice_turn'] is Map<String, dynamic>
            ? payload['voice_turn']['state']
            : null);
    final VoiceUiState? parsed = _parseVoiceState(explicitState);
    final bool sttAvailable = payload['stt_available'] == true;

    if (parsed != null) {
      if (!mounted) {
        return;
      }
      setState(() {
        _voiceUiState = parsed;
        _voiceEventSource = 'server';
        _lastVoiceStateAt = DateTime.now();
        _hasServerVoiceState = true;
      });
      return;
    }

    if (_hasServerVoiceState) {
      if (!mounted) {
        return;
      }
      setState(() {
        _hasServerVoiceState = false;
      });
    }

    if (!sttAvailable && _voiceUiState != VoiceUiState.micOff) {
      if (!mounted) {
        return;
      }
      setState(() {
        _voiceUiState = VoiceUiState.micOff;
        _voiceEventSource = 'health_fallback';
        _lastVoiceStateAt = DateTime.now();
      });
    }
  }

  void _updateGateReadinessFromHealth(Map<String, dynamic> payload) {
    final dynamic raw = payload['reentry_gates'];
    final dynamic rawDetails = payload['reentry_gates_details'];
    final bool hasStatuses = raw is Map;
    final bool hasDetails = rawDetails is Map;
    if (!hasStatuses && !hasDetails) {
      if (_gateSource != 'fallback') {
        setState(() {
          _gateSource = 'fallback';
          _gateDetails = <String, _GateDetailData>{};
        });
      }
      return;
    }
    final Map<String, String> next = <String, String>{};
    final Map<String, _GateDetailData> details = <String, _GateDetailData>{};
    for (final String gate in _gateOrder) {
      final dynamic value = hasStatuses
          ? raw[gate] ?? raw[gate.toLowerCase()]
          : null;
      final String normalized = _normalizeGateStatus(value);
      next[gate] = normalized;
      if (hasDetails) {
        final dynamic detailRaw =
            rawDetails[gate] ?? rawDetails[gate.toLowerCase()];
        if (detailRaw is Map<String, dynamic>) {
          details[gate] = _parseGateDetail(
            detailRaw,
            fallbackStatus: normalized,
          );
        }
      }
    }
    setState(() {
      _readinessGates = next;
      _gateDetails = details;
      _gateSource = hasDetails ? 'server_details' : 'server';
    });
  }

  String _normalizeGateStatus(dynamic value) {
    if (value == null) {
      return 'unknown';
    }
    if (value is bool) {
      return value ? 'pass' : 'fail';
    }
    final String text = value.toString().trim().toLowerCase();
    if (text.contains('pass')) {
      return 'pass';
    }
    if (text.contains('progress') || text.contains('pending')) {
      return 'in_progress';
    }
    if (text.contains('fail')) {
      return 'fail';
    }
    return 'unknown';
  }

  _GateDetailData _parseGateDetail(
    Map<String, dynamic> raw, {
    required String fallbackStatus,
  }) {
    final String status = _normalizeGateStatus(raw['status'] ?? fallbackStatus);
    final String source = (raw['source'] ?? 'n/a').toString();
    final String summary = (raw['summary'] ?? 'No summary').toString();
    final bool stale = raw['stale'] == true;
    DateTime? updatedAt;
    final dynamic updatedRaw = raw['updated_at'];
    if (updatedRaw is String) {
      updatedAt = DateTime.tryParse(updatedRaw);
    }
    return _GateDetailData(
      status: status,
      source: source,
      summary: summary,
      updatedAt: updatedAt,
      stale: stale,
    );
  }

  VoiceUiState? _parseVoiceState(dynamic raw) {
    if (raw is! String) {
      return null;
    }
    switch (raw.toLowerCase()) {
      case 'mic_off':
      case 'idle':
      case 'off':
        return VoiceUiState.micOff;
      case 'listening':
        return VoiceUiState.listening;
      case 'transcribing':
        return VoiceUiState.transcribing;
      case 'responding':
      case 'speaking':
        return VoiceUiState.responding;
      default:
        return null;
    }
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
    final _StatusBadgeData badge = _statusBadgeForState(
      _connectionState,
      theme,
    );

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
              final Widget diagnosticsCard = _buildDiagnosticsCard(theme);
              final Widget voiceCard = _buildVoiceCard(theme);
              final Widget gatesCard = _buildGateReadinessCard(theme);
              final Widget payloadCard = _buildPayloadCard(theme);

              if (isWide) {
                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      flex: 5,
                      child: Column(
                        children: [
                          statusCard,
                          const SizedBox(height: 16),
                          diagnosticsCard,
                          const SizedBox(height: 16),
                          voiceCard,
                          const SizedBox(height: 16),
                          gatesCard,
                        ],
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(flex: 7, child: payloadCard),
                  ],
                );
              }

              return SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    statusCard,
                    const SizedBox(height: 16),
                    diagnosticsCard,
                    const SizedBox(height: 16),
                    voiceCard,
                    const SizedBox(height: 16),
                    gatesCard,
                    const SizedBox(height: 16),
                    SizedBox(height: 360, child: payloadCard),
                  ],
                ),
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
            Text(
              'Connection states',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _ConnectionBadge(
                  data: _statusBadgeForState(
                    KernelConnectionState.connected,
                    theme,
                  ),
                ),
                _ConnectionBadge(
                  data: _statusBadgeForState(
                    KernelConnectionState.retrying,
                    theme,
                  ),
                ),
                _ConnectionBadge(
                  data: _statusBadgeForState(
                    KernelConnectionState.offline,
                    theme,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
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
            _statusRow(
              'Last manual probe',
              _lastManualProbeAt?.toIso8601String() ?? 'never',
            ),
            const SizedBox(height: 10),
            _statusRow('Transport', _lastMessage),
            const SizedBox(height: 14),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton.icon(
                  onPressed: _manualProbeInFlight
                      ? null
                      : () {
                          unawaited(_runManualProbe());
                        },
                  icon: const Icon(Icons.refresh_rounded, size: 18),
                  label: Text(
                    _manualProbeInFlight ? 'Checking...' : 'Check now',
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDiagnosticsCard(ThemeData theme) {
    final int highSeverityCount = _diagnosticEvents
        .where((event) => event.severity == _DiagnosticSeverity.high)
        .length;
    final int mediumSeverityCount = _diagnosticEvents
        .where((event) => event.severity == _DiagnosticSeverity.medium)
        .length;
    final int lowSeverityCount = _diagnosticEvents
        .where((event) => event.severity == _DiagnosticSeverity.low)
        .length;

    final List<_DiagnosticEvent> visibleEvents = _diagnosticEvents.where((
      event,
    ) {
      final bool matchesType =
          _diagnosticFilter == _DiagnosticFilter.all ||
          event.type == _diagnosticFilter;
      if (!matchesType) {
        return false;
      }
      if (_diagnosticSeverityFilter == _DiagnosticSeverityFilter.all) {
        return true;
      }
      return event.severity == _diagnosticSeverityFilter.severity;
    }).toList();
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
              'Diagnostics timeline',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'Most recent transport and UI events.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                Text(
                  'Severity counters:',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  'High: $highSeverityCount',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.error,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  'Med: $mediumSeverityCount',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: Colors.amber.shade300,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  'Low: $lowSeverityCount',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: highSeverityCount == 0
                      ? null
                      : _focusHighSeverityDiagnostics,
                  icon: const Icon(Icons.priority_high_rounded, size: 16),
                  label: const Text('Focus high'),
                ),
                OutlinedButton.icon(
                  onPressed: _resetDiagnosticsFilters,
                  icon: const Icon(Icons.filter_alt_off_rounded, size: 16),
                  label: const Text('Reset filters'),
                ),
              ],
            ),
            if (highSeverityCount > 0) ...[
              const SizedBox(height: 8),
              DecoratedBox(
                decoration: BoxDecoration(
                  color: theme.colorScheme.error.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: theme.colorScheme.error.withValues(alpha: 0.35),
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 10,
                  ),
                  child: Row(
                    children: [
                      Icon(
                        Icons.warning_amber_rounded,
                        size: 16,
                        color: theme.colorScheme.error,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          '$highSeverityCount high-severity event(s) require triage.',
                          style: theme.textTheme.bodySmall?.copyWith(
                            color: theme.colorScheme.error,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilterChip(
                  label: const Text('All'),
                  selected: _diagnosticFilter == _DiagnosticFilter.all,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticFilter = _DiagnosticFilter.all;
                    });
                  },
                ),
                FilterChip(
                  label: const Text('Transport'),
                  selected: _diagnosticFilter == _DiagnosticFilter.transport,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticFilter = _DiagnosticFilter.transport;
                    });
                  },
                ),
                FilterChip(
                  label: const Text('Manual'),
                  selected: _diagnosticFilter == _DiagnosticFilter.manual,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticFilter = _DiagnosticFilter.manual;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilterChip(
                  label: const Text('Severity: All'),
                  selected:
                      _diagnosticSeverityFilter == _DiagnosticSeverityFilter.all,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticSeverityFilter = _DiagnosticSeverityFilter.all;
                    });
                  },
                ),
                FilterChip(
                  label: const Text('High'),
                  selected: _diagnosticSeverityFilter ==
                      _DiagnosticSeverityFilter.high,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticSeverityFilter = _DiagnosticSeverityFilter.high;
                    });
                  },
                ),
                FilterChip(
                  label: const Text('Med'),
                  selected: _diagnosticSeverityFilter ==
                      _DiagnosticSeverityFilter.medium,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticSeverityFilter =
                          _DiagnosticSeverityFilter.medium;
                    });
                  },
                ),
                FilterChip(
                  label: const Text('Low'),
                  selected:
                      _diagnosticSeverityFilter == _DiagnosticSeverityFilter.low,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticSeverityFilter = _DiagnosticSeverityFilter.low;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.center,
              children: [
                OutlinedButton.icon(
                  onPressed: _diagnosticEvents.isEmpty
                      ? null
                      : () {
                          setState(() {
                            _diagnosticEvents.clear();
                          });
                        },
                  icon: const Icon(Icons.cleaning_services_rounded, size: 16),
                  label: const Text('Clear timeline'),
                ),
                Text(
                  'Showing ${visibleEvents.length} event(s)',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                OutlinedButton.icon(
                  onPressed: () {
                    unawaited(_copyDiagnosticsSnapshot(visibleEvents));
                  },
                  icon: const Icon(Icons.copy_all_rounded, size: 16),
                  label: const Text('Copy snapshot'),
                ),
                OutlinedButton.icon(
                  onPressed: () {
                    unawaited(_copyBlockedSummary());
                  },
                  icon: const Icon(Icons.report_problem_rounded, size: 16),
                  label: const Text('Copy blocked summary'),
                ),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              _diagnosticsActionMessage,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                ChoiceChip(
                  label: const Text('Short'),
                  selected: _diagnosticDepth == _DiagnosticDepth.short,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticDepth = _DiagnosticDepth.short;
                      while (_diagnosticEvents.length >
                          _diagnosticDepth.maxEntries) {
                        _diagnosticEvents.removeLast();
                      }
                    });
                  },
                ),
                ChoiceChip(
                  label: const Text('Medium'),
                  selected: _diagnosticDepth == _DiagnosticDepth.medium,
                  onSelected: (_) {
                    setState(() {
                      _diagnosticDepth = _DiagnosticDepth.medium;
                    });
                  },
                ),
              ],
            ),
            const SizedBox(height: 10),
            if (visibleEvents.isEmpty)
              Text(
                'No diagnostics events yet.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              )
            else
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: visibleEvents.map((event) {
                  final _StatusBadgeData eventBadge = _diagnosticEventBadgeData(
                    event.type,
                    theme,
                  );
                  final _StatusBadgeData severityBadge = _diagnosticSeverityBadge(
                    event.severity,
                    theme,
                  );
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _ConnectionBadge(data: eventBadge),
                        const SizedBox(width: 6),
                        _ConnectionBadge(data: severityBadge),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            '${event.at.toIso8601String()}  •  ${event.message}',
                            style: theme.textTheme.bodySmall?.copyWith(
                              color: theme.colorScheme.onSurface,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }

  _StatusBadgeData _diagnosticEventBadgeData(
    _DiagnosticFilter type,
    ThemeData theme,
  ) {
    switch (type) {
      case _DiagnosticFilter.manual:
        return _StatusBadgeData(
          label: 'MANUAL',
          textColor: theme.colorScheme.secondary,
          bgColor: theme.colorScheme.secondary.withValues(alpha: 0.16),
        );
      case _DiagnosticFilter.transport:
        return _StatusBadgeData(
          label: 'TRANSPORT',
          textColor: theme.colorScheme.primary,
          bgColor: theme.colorScheme.primary.withValues(alpha: 0.16),
        );
      case _DiagnosticFilter.all:
        return _StatusBadgeData(
          label: 'EVENT',
          textColor: theme.colorScheme.onSurfaceVariant,
          bgColor: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.14),
        );
    }
  }

  _StatusBadgeData _diagnosticSeverityBadge(
    _DiagnosticSeverity severity,
    ThemeData theme,
  ) {
    switch (severity) {
      case _DiagnosticSeverity.high:
        return _StatusBadgeData(
          label: 'HIGH',
          textColor: theme.colorScheme.error,
          bgColor: theme.colorScheme.error.withValues(alpha: 0.16),
        );
      case _DiagnosticSeverity.medium:
        return _StatusBadgeData(
          label: 'MED',
          textColor: Colors.amber.shade300,
          bgColor: Colors.amber.withValues(alpha: 0.16),
        );
      case _DiagnosticSeverity.low:
        return _StatusBadgeData(
          label: 'LOW',
          textColor: theme.colorScheme.primary,
          bgColor: theme.colorScheme.primary.withValues(alpha: 0.16),
        );
    }
  }

  Widget _buildPayloadCard(ThemeData theme) {
    final String payloadText = _healthPayload == null
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
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                OutlinedButton.icon(
                  onPressed: () {
                    unawaited(_copyPayloadToClipboard(payloadText));
                  },
                  icon: const Icon(Icons.content_copy_rounded, size: 16),
                  label: const Text('Copy JSON'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              _payloadActionMessage,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: DecoratedBox(
                decoration: BoxDecoration(
                  color: const Color(0xFF0B0F14),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _payloadHasFocus
                        ? theme.colorScheme.primary
                        : theme.colorScheme.outlineVariant,
                    width: _payloadHasFocus ? 1.4 : 1,
                  ),
                ),
                child: Focus(
                  onFocusChange: (bool hasFocus) {
                    if (!mounted) {
                      return;
                    }
                    setState(() {
                      _payloadHasFocus = hasFocus;
                    });
                  },
                  child: Semantics(
                    label: 'Health JSON payload panel',
                    hint: 'Scrollable and selectable status payload',
                    textField: true,
                    readOnly: true,
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
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _copyPayloadToClipboard(String payloadText) async {
    try {
      await Clipboard.setData(ClipboardData(text: payloadText));
      if (!mounted) {
        return;
      }
      setState(() {
        _payloadActionMessage = 'Payload copied to clipboard.';
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _payloadActionMessage = 'Unable to copy payload on this platform.';
      });
    }
  }

  Future<void> _copyDiagnosticsSnapshot(List<_DiagnosticEvent> events) async {
    final String snapshot = _buildDiagnosticsSnapshot(events);
    try {
      await Clipboard.setData(ClipboardData(text: snapshot));
      if (!mounted) {
        return;
      }
      setState(() {
        _diagnosticsActionMessage = 'Diagnostics snapshot copied.';
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _diagnosticsActionMessage = 'Unable to copy diagnostics snapshot.';
      });
    }
  }

  Future<void> _copyBlockedSummary() async {
    final List<_DiagnosticEvent> highEvents = _diagnosticEvents
        .where((event) => event.severity == _DiagnosticSeverity.high)
        .toList(growable: false);
    if (highEvents.isEmpty) {
      if (!mounted) {
        return;
      }
      setState(() {
        _diagnosticsActionMessage = 'No high-severity events to export.';
      });
      return;
    }
    final String snapshot = _buildBlockedSummary(highEvents);
    try {
      await Clipboard.setData(ClipboardData(text: snapshot));
      if (!mounted) {
        return;
      }
      setState(() {
        _diagnosticsActionMessage = 'High-severity summary copied.';
      });
    } catch (_) {
      if (!mounted) {
        return;
      }
      setState(() {
        _diagnosticsActionMessage = 'Unable to copy high-severity summary.';
      });
    }
  }

  String _buildDiagnosticsSnapshot(List<_DiagnosticEvent> events) {
    final String connection = _connectionState.name;
    final String voice = _voiceUiState.name;
    final String gateSource = _gateSource;
    final List<String> eventLines = events
        .map((event) => '- ${event.at.toIso8601String()} :: ${event.message}')
        .toList();
    final String eventsSection = eventLines.isEmpty
        ? '- no events'
        : eventLines.join('\n');
    return [
      'Ethos Flutter diagnostics snapshot',
      'connection: $connection',
      'voice_state: $voice',
      'retry_count: $_retryCount',
      'gate_source: $gateSource',
      'visible_events: ${events.length}',
      'events:',
      eventsSection,
    ].join('\n');
  }

  String _buildBlockedSummary(List<_DiagnosticEvent> highEvents) {
    final List<String> eventLines = highEvents
        .map((event) => '- ${event.at.toIso8601String()} :: ${event.message}')
        .toList(growable: false);
    return [
      'Ethos Flutter blocked-summary',
      'status: BLOCKED',
      'high_events: ${highEvents.length}',
      'retry_count: $_retryCount',
      'gate_source: $_gateSource',
      'events:',
      eventLines.join('\n'),
    ].join('\n');
  }

  Widget _buildVoiceCard(ThemeData theme) {
    final _VoiceStateData activeState = _voiceStateData(_voiceUiState, theme);
    const List<VoiceUiState> orderedStates = <VoiceUiState>[
      VoiceUiState.micOff,
      VoiceUiState.listening,
      VoiceUiState.transcribing,
      VoiceUiState.responding,
    ];

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
              'Voice loop surface',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'UI machine-state only in this block (no STT/TTS backend changes).',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 14),
            Row(
              children: [
                Icon(activeState.icon, color: activeState.accent, size: 18),
                const SizedBox(width: 8),
                Text(
                  activeState.label,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    color: activeState.accent,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: orderedStates.map((VoiceUiState state) {
                final _VoiceStateData data = _voiceStateData(state, theme);
                final bool isActive = state == _voiceUiState;
                return _MachineStateChip(
                  icon: data.icon,
                  label: data.label,
                  active: isActive,
                  activeColor: data.accent,
                );
              }).toList(),
            ),
            const SizedBox(height: 12),
            _statusRow(
              'Voice source',
              _voiceEventSource == 'server'
                  ? 'server event'
                  : _voiceEventSource == 'health_fallback'
                  ? 'health fallback (stt unavailable)'
                  : 'fallback (waiting for backend voice state)',
            ),
            const SizedBox(height: 8),
            _statusRow(
              'Last voice update',
              _lastVoiceStateAt?.toIso8601String() ?? 'never',
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Icon(
                  _hasServerVoiceState
                      ? Icons.cloud_done_rounded
                      : Icons.cloud_off_rounded,
                  size: 16,
                  color: _hasServerVoiceState
                      ? theme.colorScheme.primary
                      : theme.colorScheme.onSurfaceVariant,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _hasServerVoiceState
                        ? 'Voice state is bound to backend status payload.'
                        : 'Waiting for backend to emit voice_turn_state.',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGateReadinessCard(ThemeData theme) {
    final _StatusBadgeData checkpointBadge = _mvpCheckpointBadgeData(theme);
    final String checkpointDetail = _mvpCheckpointDetail();
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
              'Re-entry readiness gates',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              'G1..G5 status for mobile/web reopen criteria.',
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Text(
                  'MVP checkpoint',
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(width: 8),
                _ConnectionBadge(data: checkpointBadge),
              ],
            ),
            const SizedBox(height: 6),
            Text(
              checkpointDetail,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _gateOrder.map((String gate) {
                final String status = _readinessGates[gate] ?? 'unknown';
                final _StatusBadgeData data = _gateBadgeData(
                  gate,
                  status,
                  theme,
                );
                return _ConnectionBadge(data: data);
              }).toList(),
            ),
            const SizedBox(height: 12),
            if (_gateDetails.isEmpty)
              Text(
                'No gate metadata available yet.',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              )
            else
              Column(
                children: _gateOrder.map((String gate) {
                  final _GateDetailData? detail = _gateDetails[gate];
                  if (detail == null) {
                    return const SizedBox.shrink();
                  }
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _statusRow('$gate summary', detail.summary),
                        const SizedBox(height: 6),
                        _statusRow('$gate source', detail.source),
                        const SizedBox(height: 6),
                        _statusRow(
                          '$gate updated',
                          detail.updatedAt?.toIso8601String() ?? 'unknown',
                        ),
                        const SizedBox(height: 6),
                        _statusRow(
                          '$gate freshness',
                          detail.stale ? 'stale' : 'fresh',
                        ),
                      ],
                    ),
                  );
                }).toList(),
              ),
            const SizedBox(height: 4),
            _statusRow(
              'Gate source',
              _gateSource == 'server_details'
                  ? 'server payload (/api/status reentry_gates_details)'
                  : _gateSource == 'server'
                  ? 'server payload (/api/status reentry_gates)'
                  : 'fallback (waiting for reentry_gates)',
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
          bgColor: theme.colorScheme.primary.withValues(alpha: 0.16),
        );
      case KernelConnectionState.retrying:
        return _StatusBadgeData(
          label: 'Retrying',
          textColor: Colors.amber.shade300,
          bgColor: Colors.amber.withValues(alpha: 0.16),
        );
      case KernelConnectionState.offline:
        return _StatusBadgeData(
          label: 'Offline',
          textColor: theme.colorScheme.error,
          bgColor: theme.colorScheme.error.withValues(alpha: 0.16),
        );
      case KernelConnectionState.connecting:
        return _StatusBadgeData(
          label: 'Connecting',
          textColor: theme.colorScheme.secondary,
          bgColor: theme.colorScheme.secondary.withValues(alpha: 0.16),
        );
    }
  }

  _VoiceStateData _voiceStateData(VoiceUiState state, ThemeData theme) {
    switch (state) {
      case VoiceUiState.micOff:
        return _VoiceStateData(
          label: 'Mic off',
          icon: Icons.mic_off_rounded,
          accent: theme.colorScheme.error,
        );
      case VoiceUiState.listening:
        return _VoiceStateData(
          label: 'Listening',
          icon: Icons.hearing_rounded,
          accent: theme.colorScheme.primary,
        );
      case VoiceUiState.transcribing:
        return _VoiceStateData(
          label: 'Transcribing',
          icon: Icons.graphic_eq_rounded,
          accent: Colors.amber.shade300,
        );
      case VoiceUiState.responding:
        return _VoiceStateData(
          label: 'Responding',
          icon: Icons.record_voice_over_rounded,
          accent: theme.colorScheme.tertiary,
        );
    }
  }

  _StatusBadgeData _gateBadgeData(String gate, String status, ThemeData theme) {
    switch (status) {
      case 'pass':
        return _StatusBadgeData(
          label: '$gate PASS',
          textColor: theme.colorScheme.primary,
          bgColor: theme.colorScheme.primary.withValues(alpha: 0.16),
        );
      case 'in_progress':
        return _StatusBadgeData(
          label: '$gate IN PROGRESS',
          textColor: Colors.amber.shade300,
          bgColor: Colors.amber.withValues(alpha: 0.16),
        );
      case 'fail':
        return _StatusBadgeData(
          label: '$gate FAIL',
          textColor: theme.colorScheme.error,
          bgColor: theme.colorScheme.error.withValues(alpha: 0.16),
        );
      default:
        return _StatusBadgeData(
          label: '$gate UNKNOWN',
          textColor: theme.colorScheme.onSurfaceVariant,
          bgColor: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.14),
        );
    }
  }

  _StatusBadgeData _mvpCheckpointBadgeData(ThemeData theme) {
    switch (_mvpCheckpointState()) {
      case 'ready':
        return _StatusBadgeData(
          label: 'READY',
          textColor: theme.colorScheme.primary,
          bgColor: theme.colorScheme.primary.withValues(alpha: 0.16),
        );
      case 'degraded':
        return _StatusBadgeData(
          label: 'DEGRADED',
          textColor: Colors.amber.shade300,
          bgColor: Colors.amber.withValues(alpha: 0.16),
        );
      case 'blocked':
        return _StatusBadgeData(
          label: 'BLOCKED',
          textColor: theme.colorScheme.error,
          bgColor: theme.colorScheme.error.withValues(alpha: 0.16),
        );
      default:
        return _StatusBadgeData(
          label: 'PENDING',
          textColor: theme.colorScheme.onSurfaceVariant,
          bgColor: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.14),
        );
    }
  }

  String _mvpCheckpointState() {
    if (_gateSource == 'fallback') {
      return 'pending';
    }
    final List<String> statuses = _gateOrder
        .map((String gate) => _readinessGates[gate] ?? 'unknown')
        .toList();
    if (statuses.any((String status) => status == 'fail')) {
      return 'blocked';
    }
    if (statuses.every((String status) => status == 'pass')) {
      if (_gateDetails.isEmpty) {
        return 'ready';
      }
      final bool anyStale = _gateOrder
          .map((String gate) => _gateDetails[gate])
          .whereType<_GateDetailData>()
          .any((detail) => detail.stale);
      return anyStale ? 'degraded' : 'ready';
    }
    if (statuses.any((String status) => status == 'unknown')) {
      return 'pending';
    }
    return 'degraded';
  }

  String _mvpCheckpointDetail() {
    switch (_mvpCheckpointState()) {
      case 'ready':
        return 'All gates are passing and evidence is current.';
      case 'degraded':
        return 'No hard fail, but at least one gate is in progress or stale.';
      case 'blocked':
        return 'At least one gate failed. Re-entry remains blocked.';
      default:
        return 'Waiting for server gate payload to evaluate readiness.';
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
          child: SelectableText(value, style: const TextStyle(fontSize: 13)),
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

enum VoiceUiState { micOff, listening, transcribing, responding }

class _VoiceStateData {
  const _VoiceStateData({
    required this.label,
    required this.icon,
    required this.accent,
  });

  final String label;
  final IconData icon;
  final Color accent;
}

class _GateDetailData {
  const _GateDetailData({
    required this.status,
    required this.source,
    required this.summary,
    required this.updatedAt,
    required this.stale,
  });

  final String status;
  final String source;
  final String summary;
  final DateTime? updatedAt;
  final bool stale;
}

class _DiagnosticEvent {
  const _DiagnosticEvent({
    required this.at,
    required this.message,
    required this.type,
    required this.severity,
  });

  final DateTime at;
  final String message;
  final _DiagnosticFilter type;
  final _DiagnosticSeverity severity;
}

enum _DiagnosticFilter { all, transport, manual }

enum _DiagnosticSeverity { high, medium, low }

enum _DiagnosticSeverityFilter {
  all(null),
  high(_DiagnosticSeverity.high),
  medium(_DiagnosticSeverity.medium),
  low(_DiagnosticSeverity.low);

  const _DiagnosticSeverityFilter(this.severity);

  final _DiagnosticSeverity? severity;
}

enum _DiagnosticDepth {
  short(4),
  medium(8);

  const _DiagnosticDepth(this.maxEntries);

  final int maxEntries;
}

class _ConnectionBadge extends StatelessWidget {
  const _ConnectionBadge({required this.data});

  final _StatusBadgeData data;

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Connection status ${data.label}',
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: data.bgColor,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: data.textColor.withValues(alpha: 0.35)),
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
      ),
    );
  }
}

class _MachineStateChip extends StatelessWidget {
  const _MachineStateChip({
    required this.icon,
    required this.label,
    required this.active,
    required this.activeColor,
  });

  final IconData icon;
  final String label;
  final bool active;
  final Color activeColor;

  @override
  Widget build(BuildContext context) {
    final Color textColor = active
        ? activeColor
        : Theme.of(context).colorScheme.onSurfaceVariant;
    final Color background = active
        ? activeColor.withValues(alpha: 0.18)
        : Colors.white.withValues(alpha: 0.03);

    return DecoratedBox(
      decoration: BoxDecoration(
        color: background,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: textColor.withValues(alpha: active ? 0.45 : 0.25),
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: textColor),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                color: textColor,
                fontSize: 12,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
