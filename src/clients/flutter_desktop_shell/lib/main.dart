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
  VoiceUiState _voiceUiState = VoiceUiState.micOff;
  String _voiceEventSource = 'placeholder';
  DateTime? _lastVoiceStateAt;

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
      });
      return;
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

  void _advanceVoicePlaceholder() {
    const List<VoiceUiState> cycle = <VoiceUiState>[
      VoiceUiState.micOff,
      VoiceUiState.listening,
      VoiceUiState.transcribing,
      VoiceUiState.responding,
    ];
    final int currentIndex = cycle.indexOf(_voiceUiState);
    final int nextIndex = currentIndex == -1
        ? 0
        : (currentIndex + 1) % cycle.length;
    setState(() {
      _voiceUiState = cycle[nextIndex];
      _voiceEventSource = 'placeholder';
      _lastVoiceStateAt = DateTime.now();
    });
    _log('voice_ui -> ${_voiceUiState.name} (placeholder)');
  }

  void _resetVoicePlaceholder() {
    setState(() {
      _voiceUiState = VoiceUiState.micOff;
      _voiceEventSource = 'placeholder';
      _lastVoiceStateAt = DateTime.now();
    });
    _log('voice_ui -> ${_voiceUiState.name} (placeholder reset)');
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
              final Widget voiceCard = _buildVoiceCard(theme);
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
                          voiceCard,
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
                    voiceCard,
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
                  : 'placeholder (manual cycle)',
            ),
            const SizedBox(height: 8),
            _statusRow(
              'Last voice update',
              _lastVoiceStateAt?.toIso8601String() ?? 'never',
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                FilledButton.icon(
                  onPressed: _advanceVoicePlaceholder,
                  icon: const Icon(Icons.skip_next_rounded, size: 16),
                  label: const Text('Next state'),
                ),
                OutlinedButton.icon(
                  onPressed: _resetVoicePlaceholder,
                  icon: const Icon(Icons.restart_alt_rounded, size: 16),
                  label: const Text('Reset'),
                ),
              ],
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

class _ConnectionBadge extends StatelessWidget {
  const _ConnectionBadge({required this.data});

  final _StatusBadgeData data;

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
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
