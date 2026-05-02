// V2.119 (A1): widget tests for the new chat panel.

import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:stream_channel/stream_channel.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import 'package:flutter_desktop_shell/chat_panel.dart';

class _FakeWebSocketSink implements WebSocketSink {
  _FakeWebSocketSink(this._channel);

  final _FakeWebSocketChannel _channel;
  final List<dynamic> sent = <dynamic>[];

  @override
  void add(dynamic data) {
    sent.add(data);
  }

  @override
  void addError(Object error, [StackTrace? stackTrace]) {}

  @override
  Future<dynamic> addStream(Stream<dynamic> stream) async {
    await for (final dynamic event in stream) {
      sent.add(event);
    }
  }

  @override
  Future<dynamic> close([int? closeCode, String? closeReason]) async {
    await _channel._controller.close();
  }

  @override
  Future<dynamic> get done => _channel._controller.done;
}

class _FakeWebSocketChannel extends StreamChannelMixin<dynamic>
    implements WebSocketChannel {
  _FakeWebSocketChannel() {
    _sink = _FakeWebSocketSink(this);
  }

  final StreamController<dynamic> _controller =
      StreamController<dynamic>.broadcast();
  late final _FakeWebSocketSink _sink;

  void emit(Map<String, dynamic> frame) {
    _controller.add(jsonEncode(frame));
  }

  @override
  Stream<dynamic> get stream => _controller.stream;

  @override
  WebSocketSink get sink => _sink;

  @override
  int? get closeCode => null;

  @override
  String? get closeReason => null;

  @override
  String? get protocol => null;

  @override
  Future<void> get ready async => null;
}

Widget _harness({required ChatPanel child}) {
  return MaterialApp(
    home: Scaffold(body: SizedBox(width: 800, height: 600, child: child)),
  );
}

void main() {
  testWidgets('idle render with transport disabled', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      _harness(child: const ChatPanel(startTransport: false)),
    );

    expect(find.text('Chat with Ethos'), findsOneWidget);
    expect(find.text('Chat idle'), findsOneWidget);
    expect(find.text('Transport disabled for tests.'), findsOneWidget);
    expect(
      find.text('No conversation yet. Send a message to begin.'),
      findsOneWidget,
    );
    final FilledButton sendButton = tester.widget(
      find.byKey(const Key('chatSend')),
    );
    expect(sendButton.onPressed, isNull);
  });

  testWidgets('streams metadata + tokens + done into a chat bubble', (
    WidgetTester tester,
  ) async {
    final _FakeWebSocketChannel fake = _FakeWebSocketChannel();
    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: true,
          channelFactory: (_) => fake,
        ),
      ),
    );
    await tester.pump();
    expect(find.text('Chat connected'), findsOneWidget);

    fake.emit(<String, dynamic>{
      'type': 'metadata',
      'context': 'everyday_ethics',
      'evaluation': <String, dynamic>{
        'chosen': 'comfort_user',
        'verdict': 'Neutral',
      },
    });
    await tester.pump();

    fake.emit(<String, dynamic>{'type': 'token', 'content': 'Hola'});
    fake.emit(<String, dynamic>{'type': 'token', 'content': ' mundo'});
    await tester.pump();
    expect(find.textContaining('Hola mundo'), findsOneWidget);

    fake.emit(<String, dynamic>{
      'type': 'done',
      'message': 'Hola mundo',
      'latency': <String, dynamic>{'total': 432.0},
      'blocked': false,
      'trace': <String, dynamic>{
        'malabs': 'pass',
        'context': 'everyday_ethics',
        'action': 'comfort_user',
        'mode': 'D_delib',
        'score': 0.62,
        'verdict': 'Good',
        'weights': <double>[0.4, 0.35, 0.25],
        'memory_used': <Map<String, dynamic>>[
          <String, dynamic>{
            'id': 'ep-1',
            'summary': 'antes hablamos',
            'context': 'everyday_ethics',
          },
          <String, dynamic>{
            'id': 'ep-2',
            'summary': 'segundo recuerdo',
            'context': 'everyday_ethics',
          },
        ],
      },
    });
    await tester.pumpAndSettle();

    expect(find.textContaining('action: comfort_user'), findsOneWidget);
    expect(find.textContaining('mode: D_delib'), findsOneWidget);
    expect(find.textContaining('score: 0.62'), findsOneWidget);
    expect(find.textContaining('verdict: Good'), findsOneWidget);
    expect(find.textContaining('ctx: everyday_ethics'), findsOneWidget);
    expect(find.textContaining('latency: 432ms'), findsOneWidget);
    expect(find.byKey(const Key('chatMemoryChip')), findsOneWidget);
    expect(find.textContaining('memory: 2 episodes'), findsOneWidget);
  });

  testWidgets('send button posts a chat_text frame to the socket', (
    WidgetTester tester,
  ) async {
    final _FakeWebSocketChannel fake = _FakeWebSocketChannel();
    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: true,
          channelFactory: (_) => fake,
        ),
      ),
    );
    await tester.pump();

    await tester.enterText(find.byKey(const Key('chatInput')), 'ping');
    await tester.tap(find.byKey(const Key('chatSend')));
    await tester.pump();

    expect(fake._sink.sent, hasLength(1));
    final dynamic raw = fake._sink.sent.single;
    final Map<String, dynamic> frame = jsonDecode(raw as String);
    expect(frame['type'], 'chat_text');
    expect((frame['payload'] as Map)['text'], 'ping');
    expect(find.text('ping'), findsOneWidget);
  });

  testWidgets('transitions to retrying when the socket closes', (
    WidgetTester tester,
  ) async {
    final _FakeWebSocketChannel fake = _FakeWebSocketChannel();
    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: true,
          channelFactory: (_) => fake,
        ),
      ),
    );
    await tester.pump();
    expect(find.text('Chat connected'), findsOneWidget);

    await fake._controller.close();
    await tester.pump();
    expect(find.text('Chat retrying'), findsOneWidget);
  });

  testWidgets('Speak posts voice_turn envelope and renders latency badge', (
    WidgetTester tester,
  ) async {
    Uri? capturedUri;
    Map<String, dynamic>? capturedBody;
    final MockClient client = MockClient((http.Request request) async {
      capturedUri = request.url;
      capturedBody = jsonDecode(request.body) as Map<String, dynamic>;
      return http.Response(
        jsonEncode(<String, dynamic>{
          'version': '1.0',
          'contract': 'voice_turn',
          'request': capturedBody!['request'],
          'response': <String, dynamic>{
            'reply_text': 'Estoy aquí.',
            'should_listen': true,
            'trace': <String, dynamic>{
              'malabs': 'pass',
              'context': 'everyday_ethics',
              'action': 'comfort_user',
              'mode': 'D_delib',
              'score': 0.55,
              'verdict': 'Good',
              'weights': <double>[0.4, 0.35, 0.25],
            },
          },
          'error': null,
          'latency_ms': 712.0,
        }),
        200,
        headers: <String, String>{'content-type': 'application/json'},
      );
    });

    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: false,
          httpClient: client,
        ),
      ),
    );

    await tester.enterText(find.byKey(const Key('chatInput')), 'hola voz');
    await tester.tap(find.byKey(const Key('chatSpeak')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(capturedUri, isNotNull);
    expect(capturedUri!.path, '/api/voice_turn');
    expect(capturedBody!['contract'], 'voice_turn');
    expect((capturedBody!['request'] as Map)['utterance'], 'hola voz');

    expect(find.text('hola voz'), findsOneWidget);
    expect(find.text('Estoy aquí.'), findsOneWidget);
    expect(find.textContaining('latency: 712ms'), findsOneWidget);
    expect(find.textContaining('action: voice_turn'), findsOneWidget);
    expect(find.textContaining('mode: D_delib'), findsOneWidget);
    expect(find.textContaining('score: 0.55'), findsOneWidget);
    expect(find.textContaining('verdict: Good'), findsOneWidget);
    expect(find.text('voice_turn ok (listen)'), findsOneWidget);
  });

  testWidgets('Why-this-answer expander reveals human-readable trace', (
    WidgetTester tester,
  ) async {
    final _FakeWebSocketChannel fake = _FakeWebSocketChannel();
    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: true,
          channelFactory: (_) => fake,
        ),
      ),
    );
    await tester.pump();

    fake.emit(<String, dynamic>{
      'type': 'metadata',
      'context': 'everyday_ethics',
      'evaluation': <String, dynamic>{
        'chosen': 'comfort_user',
        'verdict': 'Good',
      },
    });
    fake.emit(<String, dynamic>{'type': 'token', 'content': 'Hola'});
    fake.emit(<String, dynamic>{
      'type': 'done',
      'message': 'Hola',
      'latency': <String, dynamic>{'total': 100.0},
      'blocked': false,
      'trace': <String, dynamic>{
        'malabs': 'pass',
        'context': 'everyday_ethics',
        'action': 'comfort_user',
        'mode': 'D_delib',
        'score': 0.55,
        'verdict': 'Good',
        'weights': <double>[0.40, 0.35, 0.25],
        'memory_used': <Map<String, dynamic>>[
          <String, dynamic>{
            'id': 'ep-1',
            'summary': 'recordamos hablar de música',
            'context': 'everyday_ethics',
          },
        ],
      },
    });
    await tester.pumpAndSettle();

    final Finder expander = find.byKey(const Key('chatWhyExpander'));
    expect(expander, findsOneWidget);
    expect(find.text('Why this answer'), findsOneWidget);

    await tester.tap(expander);
    await tester.pumpAndSettle();

    expect(find.text('MalAbs: pass'), findsOneWidget);
    expect(
      find.text('Action: comfort_user (mode D_delib, score 0.55)'),
      findsOneWidget,
    );
    expect(
      find.text(
        'Hypothesis weights: util 0.40, deon 0.35, virtue 0.25',
      ),
      findsOneWidget,
    );
    expect(find.text('Memory: 1 episode(s) used'), findsOneWidget);
    expect(
      find.text('  • recordamos hablar de música'),
      findsOneWidget,
    );
  });

  testWidgets('Thumbs-up posts feedback envelope and toggles state', (
    WidgetTester tester,
  ) async {
    Uri? voiceUri;
    Map<String, dynamic>? feedbackBody;
    final MockClient client = MockClient((http.Request request) async {
      if (request.url.path == '/api/voice_turn') {
        voiceUri = request.url;
        return http.Response(
          jsonEncode(<String, dynamic>{
            'version': '1.0',
            'contract': 'voice_turn',
            'request': <String, dynamic>{'utterance': 'hola'},
            'response': <String, dynamic>{
              'reply_text': 'Hola.',
              'should_listen': true,
              'trace': <String, dynamic>{
                'malabs': 'pass',
                'context': 'everyday_ethics',
                'action': 'comfort_user',
                'mode': 'D_delib',
                'score': 0.4,
                'verdict': 'Good',
                'turn_id': 'voice-99',
                'weights': <double>[0.4, 0.35, 0.25],
              },
            },
            'error': null,
            'latency_ms': 150.0,
          }),
          200,
        );
      }
      if (request.url.path == '/api/feedback') {
        feedbackBody = jsonDecode(request.body) as Map<String, dynamic>;
        return http.Response(
          jsonEncode(<String, dynamic>{
            'ok': true,
            'posterior_assisted': false,
            'stats': <String, dynamic>{
              'action': feedbackBody!['action'],
              'up': 1,
              'down': 0,
            },
          }),
          200,
        );
      }
      return http.Response('not found', 404);
    });

    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: false,
          httpClient: client,
        ),
      ),
    );

    await tester.enterText(find.byKey(const Key('chatInput')), 'hola');
    await tester.tap(find.byKey(const Key('chatSpeak')));
    await tester.pump();
    await tester.pumpAndSettle();
    expect(voiceUri, isNotNull);

    final Finder thumbsUp = find.byKey(const Key('chatThumbsUp'));
    expect(thumbsUp, findsOneWidget);
    await tester.tap(thumbsUp);
    await tester.pump();
    await tester.pumpAndSettle();

    expect(feedbackBody, isNotNull);
    expect(feedbackBody!['turn_id'], 'voice-99');
    expect(feedbackBody!['action'], 'comfort_user');
    expect(feedbackBody!['signal'], 1);
    expect(
      find.text('Feedback +1 recorded for comfort_user'),
      findsOneWidget,
    );
  });

  testWidgets('Speak surfaces server-side voice_turn errors as blocked bubble', (
    WidgetTester tester,
  ) async {
    final MockClient client = MockClient((http.Request request) async {
      return http.Response(
        jsonEncode(<String, dynamic>{
          'version': '1.0',
          'contract': 'voice_turn',
          'request': <String, dynamic>{'utterance': 'x'},
          'response': <String, dynamic>{
            'reply_text': '',
            'should_listen': false,
          },
          'error': <String, dynamic>{
            'code': 'EMPTY_UTTERANCE',
            'message': 'utterance must not be empty',
            'retryable': false,
          },
          'latency_ms': 0.0,
        }),
        400,
      );
    });

    await tester.pumpWidget(
      _harness(
        child: ChatPanel(
          startTransport: false,
          httpClient: client,
        ),
      ),
    );

    await tester.enterText(find.byKey(const Key('chatInput')), 'something');
    await tester.tap(find.byKey(const Key('chatSpeak')));
    await tester.pump();
    await tester.pumpAndSettle();

    expect(
      find.textContaining('[EMPTY_UTTERANCE]'),
      findsOneWidget,
    );
    expect(find.text('voice_turn error (400)'), findsOneWidget);
  });
}
