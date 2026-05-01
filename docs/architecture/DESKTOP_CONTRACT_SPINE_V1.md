# Desktop Contract Spine v1

This document defines the canonical envelope for desktop migration capabilities:
`audio_perception`, `video_perception`, and `voice_turn`.

## Version

- `version`: `1.0`
- Compatibility target: Desktop-first rollout while mobile/web remain in freeze lane.

## Canonical Envelope (all capabilities)

Each payload MUST follow this top-level shape:

```json
{
  "version": "1.0",
  "contract": "audio_perception | video_perception | voice_turn",
  "request": {},
  "response": {},
  "error": null,
  "latency_ms": 0.0
}
```

Required keys:
- `version` (`string`)
- `contract` (`string`, enum)
- `request` (`object`)
- `response` (`object`)
- `error` (`object | null`)
- `latency_ms` (`number`, `>= 0`)

Error object (when not null):
- `code` (`string`) — stable machine-readable identifier.
- `message` (`string`) — human-readable detail.
- `retryable` (`boolean`) — caller retry hint.

## Capability Contracts

### `audio_perception`

Request required fields:
- `audio_b64` (`string`)
- `sample_rate_hz` (`integer`, `8000..96000`)

Response required fields:
- `transcript` (`string`)
- `confidence` (`number`, `0..1`)

### `video_perception`

Request required fields:
- `frame_b64` (`string`)
- `frame_format` (`string`, enum: `jpeg`, `png`)
- `width` (`integer`, `>= 1`)
- `height` (`integer`, `>= 1`)

Response required fields:
- `labels` (`array[string]`)
- `motion` (`number`, `0..1`)
- `faces_detected` (`integer`, `>= 0`)

### `voice_turn`

Request required fields:
- `utterance` (`string`)

Response required fields:
- `reply_text` (`string`)
- `should_listen` (`boolean`)

## Compatibility Note (Mobile/Web Freeze)

- Mobile Nomad and browser dashboards are frozen for net-new feature work.
- Frozen platforms MUST keep this envelope shape unchanged.
- Adapters may omit optional capability-specific fields, but MUST NOT remove or rename envelope keys.
- Any schema evolution after v1 must be additive and versioned (for example, `1.1`) to avoid drift.
