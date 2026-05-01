// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_desktop_shell/main.dart';

void main() {
  testWidgets('renders desktop shell transport view', (WidgetTester tester) async {
    await tester.pumpWidget(const KernelDesktopApp(startTransport: false));

    expect(find.text('Ethos Desktop Shell'), findsOneWidget);
    expect(find.text('Transport disabled for tests.'), findsOneWidget);
    expect(find.text('Health payload'), findsOneWidget);
  });
}
