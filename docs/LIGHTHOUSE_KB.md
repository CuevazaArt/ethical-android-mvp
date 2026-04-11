# Lighthouse KB (`KERNEL_LIGHTHOUSE_KB_PATH`)

Operational reference for the **optional** local JSON used by `verify_against_lighthouse` (`src/modules/reality_verification.py`). Same **contract** as premise advisory: **tone / metacognitive hints only** — no MalAbs bypass, no change to `final_action`.

## Environment

| Variable | Effect |
|----------|--------|
| `KERNEL_LIGHTHOUSE_KB_PATH` | Filesystem path to a UTF-8 JSON file. If unset or file missing, verification returns `status: none`. |
| `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION` | When `1`, WebSocket responses include `reality_verification` (see `chat_server`). |

The KB is **cached** by path + `mtime`; use `clear_lighthouse_cache()` in tests after rewriting the file.

## JSON schema (minimal)

```json
{
  "version": 1,
  "entries": [
    {
      "id": "stable_string_id",
      "keywords_all": ["word1", "word2"],
      "user_falsification_markers": ["bad phrase", "other phrase"],
      "truth_summary": "Short anchor text for the LLM hint (optional but recommended)."
    }
  ]
}
```

| Field | Rule |
|-------|------|
| `entries` | Array of objects; non-objects skipped. |
| `keywords_all` | **Every** string must appear as a substring of the user text (case-insensitive). Empty or missing → entry skipped. |
| `user_falsification_markers` | **At least one** must appear as substring (case-insensitive) to count as a “contradiction” hit. |
| `truth_summary` | Appended to the communication hint; keep it short. |

**First matching entry wins** (top-to-bottom order).

## Limits and honesty

- **Not** a fact database, classifier, or medical/legal authority — only **pattern triggers** for conservative doubt.
- **No** cap on file size or entry count in code; keep files small for latency and auditability.
- **False negatives:** paraphrase, typos, mixed languages, or missing keywords → no match.
- **False positives:** broad `keywords_all` sets increase collision risk; prefer narrower keywords + specific falsification markers.

## Fixture and tests

Example file used in CI: `tests/fixtures/lighthouse/demo_kb.json` (multiple demo entries). Run tests with `pytest tests/test_reality_verification.py`.

Design discussion: [discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md](discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md).
