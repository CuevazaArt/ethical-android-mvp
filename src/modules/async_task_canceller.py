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
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

_log = logging.getLogger(__name__)

_current_turn_task: asyncio.Task | None = None
_turn_task_lock = asyncio.Lock()


async def _get_turn_task_lock() -> asyncio.Lock:
	"""Get or create the turn task lock in the running loop."""
	global _turn_task_lock
	try:
		loop = asyncio.get_running_loop()
	except RuntimeError:
		return _turn_task_lock
	if not isinstance(_turn_task_lock, asyncio.Lock) or _turn_task_lock._loop is None:
		_turn_task_lock = asyncio.Lock()
	return _turn_task_lock


@asynccontextmanager
async def tracked_turn_context(turn_id: int) -> AsyncIterator[None]:
	"""
	Context manager to track current turn's main task for explicit cancellation.

	Usage:
		async with tracked_turn_context(turn_id):
			result = await kernel.process_chat_turn_async(...)
	"""
	global _current_turn_task
	current = asyncio.current_task()
	_current_turn_task = current
	try:
		yield
	finally:
		_current_turn_task = None


def cancel_turn_task(turn_id: int) -> bool:
	"""
	Explicitly cancel the turn's task if it's still running.

	Returns True if cancellation was requested, False if task already completed.
	Call this when KERNEL_CHAT_TURN_TIMEOUT fires to aggressively free resources.
	"""
	if _current_turn_task is None or _current_turn_task.done():
		return False

	try:
		_current_turn_task.cancel()
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
