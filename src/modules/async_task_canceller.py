"""
Async task cancellation manager — improved resource cleanup for KERNEL_CHAT_TURN_TIMEOUT.

Tracks in-flight asyncio tasks and cancels them explicitly when chat turn timeout
is exceeded, freeing worker pool slots and memory immediately instead of waiting
for cooperative signals.

Integrates with LLM HTTP async-aware backends to ensure true cancellation of
httpx.AsyncClient requests when deadline passes.
"""

from __future__ import annotations

import asyncio
import contextvars
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

_log = logging.getLogger(__name__)

_current_turn_task: contextvars.ContextVar[asyncio.Task | None] = contextvars.ContextVar(
	"_current_turn_task", default=None
)




@asynccontextmanager
async def tracked_turn_context(turn_id: int) -> AsyncIterator[None]:
	"""
	Context manager to track current turn's main task for explicit cancellation.

	Uses contextvars to avoid race conditions across concurrent tasks.

	Usage:
		async with tracked_turn_context(turn_id):
			result = await kernel.process_chat_turn_async(...)
	"""
	current = asyncio.current_task()
	token = _current_turn_task.set(current)
	try:
		yield
	finally:
		_current_turn_task.reset(token)


def cancel_turn_task(turn_id: int) -> bool:
	"""
	Explicitly cancel the turn's task if it's still running.

	Returns True if cancellation was requested, False if task already completed.
	Call this when KERNEL_CHAT_TURN_TIMEOUT fires to aggressively free resources.
	"""
	task = _current_turn_task.get()
	if task is None or task.done():
		return False

	try:
		task.cancel()
		_log.debug("Explicit task cancellation requested for turn %s", turn_id)
		return True
	except Exception as e:
		_log.warning("Failed to cancel turn task %s: %s", turn_id, e)
		return False


async def wait_for_with_explicit_cancel(
	coro,
	timeout: float | None,
	turn_id: int,
) -> any:
	"""
	Wrapper around asyncio.wait_for that also calls cancel_turn_task on timeout.

	More aggressive cleanup than just setting an event; explicitly cancels the
	underlying task to free resources immediately.
	"""
	if timeout is None:
		async with tracked_turn_context(turn_id):
			return await coro

	async with tracked_turn_context(turn_id):
		try:
			return await asyncio.wait_for(coro, timeout=timeout)
		except asyncio.TimeoutError:
			cancel_turn_task(turn_id)
			raise
