import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.core.sleep import PsiSleepDaemon


@pytest.mark.asyncio
async def test_psi_sleep_daemon():
    daemon = PsiSleepDaemon(idle_threshold_seconds=0)
    daemon._identity.reflect = AsyncMock()
    daemon._unreflected_turns = 3
    daemon._last_activity = 0  # guarantees idle

    # Monkey-patch the loop sleep time so tests run fast

    async def fast_loop():
        while daemon._running:
            await asyncio.sleep(0.01)
            # copy loop logic just to call it?
            # No, just monkeypatch sleep inside the module
            pass

    real_sleep = asyncio.sleep
    with patch("src.core.sleep.asyncio.sleep") as mock_sleep:
        # We need mock_sleep to actually yield
        async def yield_sleep(*args):
            await real_sleep(0.01)

        mock_sleep.side_effect = yield_sleep

        await daemon.start()
        await real_sleep(0.1)
        await daemon.stop()

    daemon._identity.reflect.assert_called_once()
    assert daemon._unreflected_turns == 0
