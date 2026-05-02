# Model Audit Autopilot — 20 Detailed Prompts

Scope: `src/core` model runtime hardening and vertical test increments.

Execution mode:
- Autopilot checker: `python scripts/eval/model_audit_runner_20.py --report docs/collaboration/evidence/MODEL_AUDIT_AUTOPILOT_20_REPORT.json`

## Prompt Queue (Resolved 1-by-1)

1. **M01 — Safety import hardening**  
   Prompt: Add explicit decode exception support in safety gate.
2. **M02 — Safety base64 regex hoist**  
   Prompt: Move base64 regex to module scope.
3. **M03 — Safety payload length guard**  
   Prompt: Skip excessively long base64 tokens.
4. **M04 — Safety targeted exceptions**  
   Prompt: Replace broad decode `except` with bounded exceptions.
5. **M05 — Safety invalid base64 regression test**  
   Prompt: Add test ensuring invalid payload does not crash.
6. **M06 — Safety overlong base64 regression test**  
   Prompt: Add test for overlong encoded token skip path.
7. **M07 — Identity logger injection**  
   Prompt: Add module logger for identity fallback paths.
8. **M08 — Identity list coercion helper**  
   Prompt: Sanitize loaded JSON lists into string-only lists.
9. **M09 — Identity load type guards**  
   Prompt: Harden identity load against malformed payload types.
10. **M10 — Identity load warning path**  
    Prompt: Log warning when identity profile load fails.
11. **M11 — Identity reflection warning path**  
    Prompt: Log warning when LLM reflection fails.
12. **M12 — Identity chronicle warning path**  
    Prompt: Log warning when chronicle distillation fails.
13. **M13 — Identity archetype warning path**  
    Prompt: Log warning when archetype distillation fails.
14. **M14 — Identity malformed JSON test**  
    Prompt: Add regression test for malformed identity file.
15. **M15 — Identity reflection exception test**  
    Prompt: Add regression test for LLM reflection exceptions.
16. **M16 — Status callable typing**  
    Prompt: Type `_check` callback for static safety.
17. **M17 — Status timeout handling**  
    Prompt: Handle subprocess timeout cleanly in status self-test.
18. **M18 — Status stdout encoding guard**  
    Prompt: Avoid `None` encoding attribute errors.
19. **M19 — Sleep latency telemetry**  
    Prompt: Record reflection latency in ms and clamp non-finite values.
20. **M20 — Sleep telemetry tests**  
    Prompt: Add stats and `note_activity` tests for daemon behavior.

## Evidence

- `docs/collaboration/evidence/MODEL_AUDIT_AUTOPILOT_20_REPORT.json`
