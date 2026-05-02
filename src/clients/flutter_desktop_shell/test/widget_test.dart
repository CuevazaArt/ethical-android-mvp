// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_desktop_shell/main.dart';

void main() {
  testWidgets('renders desktop shell transport view', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const KernelDesktopApp(startTransport: false));

    expect(find.text('Ethos Desktop Shell'), findsOneWidget);
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
    expect(find.text('high-severity event(s) require triage.'), findsNothing);
    expect(find.text('All'), findsOneWidget);
    expect(find.text('Transport'), findsOneWidget);
    expect(find.text('Manual'), findsOneWidget);
    expect(find.text('Severity: All'), findsOneWidget);
    expect(find.text('High'), findsOneWidget);
    expect(find.text('Med'), findsOneWidget);
    expect(find.text('Low'), findsOneWidget);
    expect(find.text('Clear timeline'), findsOneWidget);
    expect(find.text('Showing 0 event(s)'), findsOneWidget);
    expect(find.text('Copy snapshot'), findsOneWidget);
    expect(find.text('Copy blocked summary'), findsOneWidget);
    expect(find.text('Copy incident note'), findsOneWidget);
    expect(find.text('Pin latest high'), findsOneWidget);
    expect(find.text('Clear pin'), findsOneWidget);
    expect(find.text('Copy pinned note'), findsOneWidget);
    expect(find.text('Export actions'), findsOneWidget);
    expect(find.text('Pin actions'), findsOneWidget);
    expect(find.text('Pinned high event note'), findsOneWidget);
    expect(find.text('No pinned high event.'), findsOneWidget);
    expect(find.text('Diagnostics: no export yet.'), findsOneWidget);
    expect(find.text('Short'), findsOneWidget);
    expect(find.text('Medium'), findsOneWidget);
    expect(find.text('No diagnostics events yet.'), findsOneWidget);
    expect(
      find.text('Tip: use Check now to seed a fresh diagnostics sample.'),
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

    await tester.tap(find.text('Check now'));
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
    expect(find.text('1 high-severity event(s) require triage.'), findsOneWidget);

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
      'Copy blocked summary',
    );
    await tester.ensureVisible(blockedSummaryButton);
    await tester.tap(blockedSummaryButton);
    await tester.pump();
    expect(find.textContaining('summary'), findsOneWidget);

    final Finder incidentNoteButton = find.widgetWithText(
      OutlinedButton,
      'Copy incident note',
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
      'Copy pinned note',
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
