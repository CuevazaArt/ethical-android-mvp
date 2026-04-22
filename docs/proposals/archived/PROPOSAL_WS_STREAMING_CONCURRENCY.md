# PROPOSAL: WebSocket Streaming and Concurrency (v1.0)
ID: PROPOSAL_WS_STREAMING_V10
Status: Draft
Author: Antigravity (L1)

## Context
The current `chat_server.py` implementation uses a blocking request-response model for each chat turn. While LLM calls are offloaded to a thread pool, the WebSocket session loop itself waits for the full turn result before accepting the next message. This prevents:
1. Intermediate feedback to the user (streaming).
2. Out-of-band control messages (cancellation).
3. Concurrent processing of independent sensor updates during a turn.

## Proposed Architecture

### 1. Unified Event Stream
The WebSocket protocol will shift from a single JSON response to a sequence of messages. Each message follows this schema:

```json
{
  "turn_id": "uuid-or-seq",
  "event_type": "status | perception | decision | token | final",
  "payload": { ... }
}
```

### 2. Async Kernel Pipeline
The `EthicalKernel` will be extended with an async generator:
`async def process_chat_turn_stream(...) -> AsyncGenerator[TurnEvent, None]`

This allows the kernel to yield events like:
- `PERCEPTION_START`
- `PERCEPTION_RESULT` (signals, context)
- `DECISION_RESULT` (action, verdict)
- `RESPONSE_TOKEN` (for streaming text)
- `TURN_COMPLETE` (full result)

### 3. Server-Side Concurrency
The `ws_chat` handler will use `asyncio.Task` to manage turns:
- New text incoming during a turn can either:
  a) Cancel the previous turn (default for chat).
  b) Run in parallel (for multi-stage agents).
- The session loop remains active to handle `cancel_turn` or `sensor_update` JSON.

## Implementation Roadmap
1. **[LLM]** Implement `astream_completion` in `LLMBackend` (Ollama/Anthropic).
2. **[Kernel]** Orchestrate `process_chat_turn_stream`.
3. **[Server]** Rewrite `chat_server.py` WebSocket loop with task orchestration.
4. **[Metrics]** Add metrics for streaming latency and time-to-first-token.
