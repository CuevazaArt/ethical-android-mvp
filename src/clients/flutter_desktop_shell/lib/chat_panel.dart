import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

/// V2.119 (A1): real chat surface for the desktop shell.
///
/// Streams typed frames over `/ws/chat`, exposing user turns, Ethos replies,
/// and lightweight decision metadata (action, context, latency).
class ChatPanel extends StatefulWidget {
  const ChatPanel({
    super.key,
    this.startTransport = true,
    this.kernelBaseUrl,
    this.channelFactory,
    this.httpClient,
  });

  /// When false, the panel renders idle without opening a WebSocket.
  /// Used by widget tests so they do not require a live kernel server.
  final bool startTransport;

  /// Override of the kernel base URL (defaults to `KERNEL_BASE_URL` build env
  /// or `http://127.0.0.1:8000`).
  final String? kernelBaseUrl;

  /// Optional injection seam for tests: provides the [WebSocketChannel] given
  /// the resolved `ws://.../ws/chat` URI.
  final WebSocketChannel Function(Uri wsUri)? channelFactory;

  /// Optional injection seam for tests: provides the HTTP client used by the
  /// push-to-talk action so a `MockClient` can stub `/api/voice_turn` calls.
  final http.Client? httpClient;

  @override
  State<ChatPanel> createState() => _ChatPanelState();
}

enum ChatConnectionState { idle, connecting, connected, retrying, error }

class ChatMessage {
  ChatMessage({
    required this.role,
    required this.text,
    this.latencyMs,
    this.action,
    this.context,
    this.blocked = false,
  });

  /// One of: `user`, `ethos`, `system`.
  final String role;
  String text;
  double? latencyMs;
  String? action;
  String? context;
  bool blocked;
  final List<String> tokens = <String>[];

  String displayText() => text.isNotEmpty ? text : tokens.join();
}

class _ChatPanelState extends State<ChatPanel> {
  static const String _defaultKernelUrl = String.fromEnvironment(
    'KERNEL_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );
  static const Duration _maxBackoff = Duration(seconds: 8);

  WebSocketChannel? _channel;
  StreamSubscription<dynamic>? _subscription;
  Timer? _retryTimer;
  int _retryCount = 0;
  http.Client? _httpClient;
  bool _ownsHttpClient = false;

  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final List<ChatMessage> _messages = <ChatMessage>[];
  ChatConnectionState _state = ChatConnectionState.idle;
  String _statusLine = 'Idle';
  ChatMessage? _activeStream;
  bool _voiceTurnInFlight = false;

  String get _baseUrl => widget.kernelBaseUrl ?? _defaultKernelUrl;

  Uri get _wsUri {
    final Uri httpUri = Uri.parse(_baseUrl);
    final String scheme = httpUri.scheme == 'https' ? 'wss' : 'ws';
    return Uri(
      scheme: scheme,
      host: httpUri.host,
      port: httpUri.hasPort ? httpUri.port : null,
      path: '/ws/chat',
    );
  }

  @override
  void initState() {
    super.initState();
    if (widget.httpClient != null) {
      _httpClient = widget.httpClient;
      _ownsHttpClient = false;
    } else {
      _httpClient = http.Client();
      _ownsHttpClient = true;
    }
    if (widget.startTransport) {
      _connect();
    } else {
      _statusLine = 'Transport disabled for tests.';
      _state = ChatConnectionState.idle;
    }
  }

  @override
  void dispose() {
    _retryTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    if (_ownsHttpClient) {
      _httpClient?.close();
    }
    _inputController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _connect() {
    if (!mounted) {
      return;
    }
    setState(() {
      _state = ChatConnectionState.connecting;
      _statusLine = 'Connecting to ${_wsUri.toString()}';
    });
    try {
      final WebSocketChannel channel = widget.channelFactory != null
          ? widget.channelFactory!(_wsUri)
          : WebSocketChannel.connect(_wsUri);
      _channel = channel;
      _subscription = channel.stream.listen(
        _onWsMessage,
        onError: _onWsError,
        onDone: _onWsDone,
        cancelOnError: true,
      );
      setState(() {
        _state = ChatConnectionState.connected;
        _statusLine = 'Connected';
        _retryCount = 0;
      });
    } catch (error) {
      _onWsError(error);
    }
  }

  void _onWsMessage(dynamic raw) {
    if (!mounted) {
      return;
    }
    Map<String, dynamic>? decoded;
    try {
      final dynamic value = jsonDecode(raw is String ? raw : raw.toString());
      if (value is Map<String, dynamic>) {
        decoded = value;
      } else if (value is Map) {
        decoded = value.cast<String, dynamic>();
      }
    } catch (_) {
      decoded = null;
    }
    if (decoded == null) {
      return;
    }

    final String type = decoded['type']?.toString() ?? '';
    switch (type) {
      case 'metadata':
        final Map<String, dynamic>? evaluation =
            (decoded['evaluation'] is Map)
            ? (decoded['evaluation'] as Map).cast<String, dynamic>()
            : null;
        setState(() {
          final ChatMessage placeholder = ChatMessage(
            role: 'ethos',
            text: '',
            context: decoded?['context']?.toString(),
            action: evaluation?['chosen']?.toString(),
          );
          _activeStream = placeholder;
          _messages.add(placeholder);
        });
        _scrollToBottom();
        break;
      case 'token':
        final String content = decoded['content']?.toString() ?? '';
        final ChatMessage? active = _activeStream;
        if (active == null || content.isEmpty) {
          break;
        }
        setState(() {
          active.tokens.add(content);
        });
        _scrollToBottom();
        break;
      case 'clear_tokens':
        final ChatMessage? active = _activeStream;
        if (active == null) {
          break;
        }
        setState(() {
          active.tokens.clear();
        });
        break;
      case 'done':
        final dynamic latency = decoded['latency'];
        double? totalMs;
        if (latency is Map && latency['total'] is num) {
          totalMs = (latency['total'] as num).toDouble();
        }
        final String message = decoded['message']?.toString() ?? '';
        final bool blocked = decoded['blocked'] == true;
        setState(() {
          final ChatMessage? active = _activeStream;
          if (active != null) {
            if (active.tokens.isEmpty && message.isNotEmpty) {
              active.tokens.add(message);
            }
            active.text = active.tokens.join();
            active.latencyMs = totalMs;
            active.blocked = blocked;
          } else if (message.isNotEmpty) {
            _messages.add(
              ChatMessage(
                role: 'ethos',
                text: message,
                latencyMs: totalMs,
                blocked: blocked,
              ),
            );
          }
          _statusLine = blocked
              ? 'Blocked: ${decoded?['reason'] ?? 'safety'}'
              : 'Connected';
          _activeStream = null;
        });
        _scrollToBottom();
        break;
      default:
        break;
    }
  }

  void _onWsError(Object? error) {
    if (!mounted) {
      return;
    }
    setState(() {
      _state = ChatConnectionState.retrying;
      _statusLine = 'Disconnected: $error';
    });
    _scheduleRetry();
  }

  void _onWsDone() {
    if (!mounted) {
      return;
    }
    setState(() {
      _state = ChatConnectionState.retrying;
      _statusLine = 'Connection closed';
    });
    _scheduleRetry();
  }

  void _scheduleRetry() {
    _retryTimer?.cancel();
    _subscription?.cancel();
    _channel?.sink.close();
    _channel = null;
    _retryCount += 1;
    final int exponent = (_retryCount - 1).clamp(0, 4);
    final int delaySeconds = 1 << exponent;
    final Duration delay = Duration(seconds: delaySeconds);
    final Duration boundedDelay = delay > _maxBackoff ? _maxBackoff : delay;
    _retryTimer = Timer(boundedDelay, () {
      if (!mounted) {
        return;
      }
      _connect();
    });
  }

  void _send() {
    final String text = _inputController.text.trim();
    if (text.isEmpty || _state != ChatConnectionState.connected) {
      return;
    }
    final WebSocketChannel? channel = _channel;
    if (channel == null) {
      return;
    }
    final Map<String, dynamic> frame = <String, dynamic>{
      'type': 'chat_text',
      'payload': <String, dynamic>{'text': text},
    };
    setState(() {
      _messages.add(ChatMessage(role: 'user', text: text));
      _statusLine = 'Sent';
    });
    channel.sink.add(jsonEncode(frame));
    _inputController.clear();
    _scrollToBottom();
  }

  Future<void> _speak() async {
    if (_voiceTurnInFlight) {
      return;
    }
    final String text = _inputController.text.trim();
    if (text.isEmpty) {
      return;
    }
    final http.Client? client = _httpClient;
    if (client == null) {
      return;
    }
    final Uri voiceUri = Uri.parse('$_baseUrl/api/voice_turn');
    final Map<String, dynamic> envelope = <String, dynamic>{
      'version': '1.0',
      'contract': 'voice_turn',
      'request': <String, dynamic>{'utterance': text},
      'response': <String, dynamic>{},
      'error': null,
      'latency_ms': 0.0,
    };
    setState(() {
      _voiceTurnInFlight = true;
      _messages.add(ChatMessage(role: 'user', text: text));
      _statusLine = 'Speaking (HTTP voice_turn)...';
    });
    _inputController.clear();
    _scrollToBottom();
    try {
      final http.Response response = await client
          .post(
            voiceUri,
            headers: const <String, String>{
              'Content-Type': 'application/json',
            },
            body: jsonEncode(envelope),
          )
          .timeout(const Duration(seconds: 30));
      final dynamic decoded = jsonDecode(response.body);
      if (decoded is Map<String, dynamic>) {
        _handleVoiceTurnResponse(response.statusCode, decoded);
      } else if (decoded is Map) {
        _handleVoiceTurnResponse(
          response.statusCode,
          decoded.cast<String, dynamic>(),
        );
      } else {
        _appendVoiceError('Malformed voice_turn response payload.');
      }
    } catch (error) {
      _appendVoiceError('voice_turn failed: $error');
    } finally {
      if (mounted) {
        setState(() {
          _voiceTurnInFlight = false;
        });
      }
    }
  }

  void _handleVoiceTurnResponse(int status, Map<String, dynamic> body) {
    final dynamic err = body['error'];
    final dynamic latency = body['latency_ms'];
    final double? latencyMs = latency is num ? latency.toDouble() : null;
    if (err is Map) {
      final String code = err['code']?.toString() ?? 'UNKNOWN';
      final String message = err['message']?.toString() ?? 'voice_turn failed';
      setState(() {
        _messages.add(
          ChatMessage(
            role: 'ethos',
            text: '[$code] $message',
            latencyMs: latencyMs,
            blocked: true,
          ),
        );
        _statusLine = 'voice_turn error ($status)';
      });
      _scrollToBottom();
      return;
    }
    final dynamic response = body['response'];
    String reply = '';
    bool shouldListen = true;
    String? audioB64;
    if (response is Map) {
      reply = response['reply_text']?.toString() ?? '';
      final dynamic listen = response['should_listen'];
      if (listen is bool) {
        shouldListen = listen;
      }
      audioB64 = response['audio_b64']?.toString();
    }
    setState(() {
      _messages.add(
        ChatMessage(
          role: 'ethos',
          text: reply.isEmpty ? '[empty reply]' : reply,
          latencyMs: latencyMs,
          action: 'voice_turn',
        ),
      );
      _statusLine = shouldListen
          ? 'voice_turn ok (listen)'
          : 'voice_turn ok (mic off)';
    });
    _scrollToBottom();
    if (audioB64 != null && audioB64.isNotEmpty) {
      // Audio payload is recorded for future playback (deferred to a later
      // block). Keeping the field accessible avoids silently dropping it.
      debugPrint('[chat-panel] voice_turn audio_b64 length=${audioB64.length}');
    }
  }

  void _appendVoiceError(String message) {
    setState(() {
      _messages.add(
        ChatMessage(role: 'ethos', text: message, blocked: true),
      );
      _statusLine = message;
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) {
        return;
      }
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 120),
        curve: Curves.easeOut,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: BorderSide(color: theme.colorScheme.outlineVariant),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Text(
                  'Chat with Ethos',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                _ChatStatusBadge(state: _state),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              _statusLine,
              style: theme.textTheme.bodySmall?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: _messages.isEmpty
                  ? Center(
                      child: Text(
                        'No conversation yet. Send a message to begin.',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    )
                  : ListView.separated(
                      controller: _scrollController,
                      itemCount: _messages.length,
                      separatorBuilder: (_, __) => const SizedBox(height: 8),
                      itemBuilder: (BuildContext context, int index) {
                        return _ChatBubble(message: _messages[index]);
                      },
                    ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    key: const Key('chatInput'),
                    controller: _inputController,
                    decoration: InputDecoration(
                      hintText: 'Type your message...',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      isDense: true,
                    ),
                    onSubmitted: (_) => _send(),
                  ),
                ),
                const SizedBox(width: 8),
                FilledButton.icon(
                  key: const Key('chatSend'),
                  onPressed: _state == ChatConnectionState.connected
                      ? _send
                      : null,
                  icon: const Icon(Icons.send_rounded),
                  label: const Text('Send'),
                ),
                const SizedBox(width: 8),
                OutlinedButton.icon(
                  key: const Key('chatSpeak'),
                  onPressed: _voiceTurnInFlight ? null : _speak,
                  icon: _voiceTurnInFlight
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.record_voice_over_rounded),
                  label: const Text('Speak'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatStatusBadge extends StatelessWidget {
  const _ChatStatusBadge({required this.state});

  final ChatConnectionState state;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    late final String label;
    late final Color color;
    switch (state) {
      case ChatConnectionState.idle:
        label = 'Chat idle';
        color = theme.colorScheme.onSurfaceVariant;
        break;
      case ChatConnectionState.connecting:
        label = 'Chat connecting';
        color = theme.colorScheme.secondary;
        break;
      case ChatConnectionState.connected:
        label = 'Chat connected';
        color = theme.colorScheme.primary;
        break;
      case ChatConnectionState.retrying:
        label = 'Chat retrying';
        color = Colors.amber.shade300;
        break;
      case ChatConnectionState.error:
        label = 'Chat error';
        color = theme.colorScheme.error;
        break;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.16),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.w600,
          fontSize: 12,
        ),
      ),
    );
  }
}

class _ChatBubble extends StatelessWidget {
  const _ChatBubble({required this.message});

  final ChatMessage message;

  @override
  Widget build(BuildContext context) {
    final ThemeData theme = Theme.of(context);
    final bool isUser = message.role == 'user';
    final Color bubbleColor = isUser
        ? theme.colorScheme.primary.withValues(alpha: 0.18)
        : message.blocked
        ? theme.colorScheme.error.withValues(alpha: 0.18)
        : theme.colorScheme.surfaceContainerHighest;
    final Alignment alignment = isUser
        ? Alignment.centerRight
        : Alignment.centerLeft;
    final String body = message.displayText();

    final List<Widget> meta = <Widget>[];
    if (message.action != null && message.action!.isNotEmpty) {
      meta.add(_metaChip('action: ${message.action}', theme));
    }
    if (message.context != null && message.context!.isNotEmpty) {
      meta.add(_metaChip('ctx: ${message.context}', theme));
    }
    if (message.latencyMs != null) {
      meta.add(
        _metaChip(
          'latency: ${message.latencyMs!.toStringAsFixed(0)}ms',
          theme,
        ),
      );
    }
    if (message.blocked) {
      meta.add(_metaChip('blocked', theme));
    }

    return Align(
      alignment: alignment,
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: bubbleColor,
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: isUser
                ? CrossAxisAlignment.end
                : CrossAxisAlignment.start,
            children: [
              SelectableText(
                body.isEmpty ? '...' : body,
                style: theme.textTheme.bodyMedium,
              ),
              if (meta.isNotEmpty) ...[
                const SizedBox(height: 6),
                Wrap(spacing: 6, runSpacing: 4, children: meta),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _metaChip(String text, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: theme.colorScheme.surface.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: theme.colorScheme.outlineVariant),
      ),
      child: Text(
        text,
        style: theme.textTheme.labelSmall?.copyWith(
          color: theme.colorScheme.onSurfaceVariant,
        ),
      ),
    );
  }
}
