// Widget tests for the Ethos desktop shell.
//
// V2.119 (A1): the shell now renders a Chat | Diagnostics segmented control,
// defaulting to Chat. Diagnostics-focused tests switch tabs explicitly so the
// existing diagnostics surface is still validated.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_desktop_shell/main.dart';

Future<void> _switchToDiagnostics(WidgetTester tester) async {
  await tester.tap(find.text('Diagnostics'));
  await tester.pumpAndSettle();
}

void main() {
  testWidgets('default tab is chat panel', (WidgetTester tester) async {
    await tester.pumpWidget(const KernelDesktopApp(startTransport: false));

    expect(find.text('Ethos Desktop Shell'), findsOneWidget);
    expect(find.text('Chat'), findsOneWidget);
    expect(find.text('Diagnostics'), findsOneWidget);
    expect(find.text('Chat with Ethos'), findsOneWidget);
    expect(find.text('Transport disabled for tests.'), findsOneWidget);
    expect(
      find.text('No conversation yet. Send a message to begin.'),
      findsOneWidget,
    );
  });

  testWidgets('diagnostics tab still renders transport surface', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KernelDesktopApp(startTransport: false));
    await _switchToDiagnostics(tester);

    expect(find.text('Offline'), findsWidgets);
    expect(find.text('Transport disabled for tests.'), findsOneWidget);
    expect(find.text('Connection states'), findsOneWidget);
    expect(find.text('Connected'), findsWidgets);
    expect(find.text('Retrying'), findsWidgets);
    expect(find.text('Check now'), findsOneWidget);
    expect(find.text('Last manual probe:'), findsOneWidget);
    expect(find.text('Diagnostics timeline'), findsOneWidget);
    expect(find.text('Severity counters:'), findsOneWidget);
    expect(find.text('High: 0'), findsOneWidget);
    expect(find.text('Med: 0'), findsOneWidget);
    expect(find.text('Low: 0'), findsOneWidget);
    expect(find.text('Focus high'), findsOneWidget);
    expect(find.text('Reset filters'), findsOneWidget);
    expect(find.text('high event(s) require triage.'), findsNothing);
    expect(find.text('All'), findsOneWidget);
    expect(find.text('Transport'), findsOneWidget);
    expect(find.text('Manual'), findsOneWidget);
    expect(find.text('Severity: All'), findsOneWidget);
    expect(find.text('High'), findsOneWidget);
    expect(find.text('Med'), findsOneWidget);
    expect(find.text('Low'), findsOneWidget);
    expect(find.text('Clear timeline'), findsOneWidget);
    expect(find.text('Showing 0 event(s)'), findsOneWidget);
    expect(find.text('Export snapshot'), findsOneWidget);
    expect(find.text('Export blocked summary'), findsOneWidget);
    expect(find.text('Export incident note'), findsOneWidget);
    expect(find.text('Pin latest high'), findsOneWidget);
    expect(find.text('Clear pin'), findsOneWidget);
    expect(find.text('Export pinned note'), findsOneWidget);
    expect(find.text('Export actions'), findsOneWidget);
    expect(find.text('Pin actions'), findsOneWidget);
    expect(find.text('Pinned high event note'), findsOneWidget);
    expect(find.text('No pinned high event.'), findsOneWidget);
    expect(find.text('INFO'), findsOneWidget);
    expect(find.text('Diagnostics: idle.'), findsOneWidget);
    expect(find.text('Short'), findsOneWidget);
    expect(find.text('Medium'), findsOneWidget);
    expect(
      find.text('No events yet. Use Check now to seed diagnostics.'),
      findsOneWidget,
    );
    expect(find.text('Run check now'), findsOneWidget);
    expect(find.text('Voice loop surface'), findsOneWidget);
    expect(find.text('Mic off'), findsWidgets);
    expect(
      find.text('Waiting for backend to emit voice_turn_state.'),
      findsOneWidget,
    );
    expect(find.text('Re-entry readiness gates'), findsOneWidget);
    expect(find.text('G1 UNKNOWN'), findsWidgets);
    expect(find.text('MVP checkpoint'), findsOneWidget);
    expect(find.text('PENDING'), findsWidgets);
    expect(
      find.text('Waiting for server gate payload to evaluate readiness.'),
      findsOneWidget,
    );
    expect(find.text('Gate source:'), findsOneWidget);
    expect(find.text('fallback (waiting for reentry_gates)'), findsOneWidget);
    expect(find.text('No gate metadata available yet.'), findsOneWidget);
    expect(find.text('Health payload'), findsOneWidget);
    expect(find.text('Copy JSON'), findsOneWidget);
    expect(find.text('No payload action yet.'), findsOneWidget);
    expect(find.text('Waiting for /api/status payload...'), findsOneWidget);
  });

  testWidgets('voice panel shows backend binding status text', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KernelDesktopApp(startTransport: false));
    await _switchToDiagnostics(tester);
    expect(find.text('Voice source:'), findsOneWidget);
    expect(
      find.text('fallback (waiting for backend voice state)'),
      findsOneWidget,
    );
    expect(
      find.text('Waiting for backend to emit voice_turn_state.'),
      findsOneWidget,
    );
  });

  testWidgets('diagnostics timeline exposes deterministic severity badges', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KernelDesktopApp(startTransport: false));
    await _switchToDiagnostics(tester);

    final Finder checkNowFinder = find.text('Check now');
    await tester.ensureVisible(checkNowFinder);
    await tester.tap(checkNowFinder);
    await tester.pump();

    expect(find.text('MANUAL'), findsOneWidget);
    expect(find.text('MED'), findsOneWidget);

    final Finder severityMedChip = find.widgetWithText(FilterChip, 'Med');
    await tester.ensureVisible(severityMedChip);
    await tester.tap(severityMedChip);
    await tester.pump();
    expect(find.text('Showing 1 event(s)'), findsOneWidget);
    expect(find.text('High: 1'), findsOneWidget);
    expect(find.text('Med: 1'), findsOneWidget);
    expect(find.text('Low: 0'), findsOneWidget);
    expect(find.text('1 high event(s) require triage.'), findsOneWidget);

    final Finder focusHighButton = find.widgetWithText(
      OutlinedButton,
      'Focus high',
    );
    await tester.ensureVisible(focusHighButton);
    await tester.tap(focusHighButton);
    await tester.pump();
    expect(find.text('Showing 1 event(s)'), findsOneWidget);

    final Finder resetFiltersButton = find.widgetWithText(
      OutlinedButton,
      'Reset filters',
    );
    await tester.ensureVisible(resetFiltersButton);
    await tester.tap(resetFiltersButton);
    await tester.pump();
    expect(find.text('Showing 2 event(s)'), findsOneWidget);

    final Finder blockedSummaryButton = find.widgetWithText(
      OutlinedButton,
      'Export blocked summary',
    );
    await tester.ensureVisible(blockedSummaryButton);
    await tester.tap(blockedSummaryButton);
    await tester.pump();
    expect(find.textContaining('summary'), findsOneWidget);

    final Finder incidentNoteButton = find.widgetWithText(
      OutlinedButton,
      'Export incident note',
    );
    await tester.ensureVisible(incidentNoteButton);
    await tester.tap(incidentNoteButton);
    await tester.pump();
    expect(find.textContaining('incident note'), findsOneWidget);

    final Finder pinLatestHighButton = find.widgetWithText(
      OutlinedButton,
      'Pin latest high',
    );
    await tester.ensureVisible(pinLatestHighButton);
    await tester.tap(pinLatestHighButton);
    await tester.pump();
    expect(find.textContaining('Pinned high event:'), findsOneWidget);

    final Finder copyPinnedNoteButton = find.widgetWithText(
      OutlinedButton,
      'Export pinned note',
    );
    await tester.ensureVisible(copyPinnedNoteButton);
    await tester.tap(copyPinnedNoteButton);
    await tester.pump();
    expect(find.textContaining('pinned note'), findsOneWidget);

    final Finder clearPinButton = find.widgetWithText(
      OutlinedButton,
      'Clear pin',
    );
    await tester.ensureVisible(clearPinButton);
    await tester.tap(clearPinButton);
    await tester.pump();
    expect(find.text('No pinned high event.'), findsOneWidget);
  });
}
