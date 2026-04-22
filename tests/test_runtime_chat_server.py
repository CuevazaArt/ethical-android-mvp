"""Runtime ASGI façade must alias the canonical chat application (Bloque 32.1)."""


def test_runtime_chat_server_app_is_core_app() -> None:
    from src.chat_server import app as core_app
    from src.chat_server import run_chat_server as core_run
    from src.runtime.chat_server import (
        api_docs_enabled,
    )
    from src.runtime.chat_server import (
        app as runtime_app,
    )
    from src.runtime.chat_server import (
        run_chat_server as facade_run,
    )

    assert runtime_app is core_app
    # ``lifespan`` is wrapped (e.g. merged) by Starlette; do not assert identity to ``chat_lifespan``.
    assert core_app.router.lifespan is not None
    assert api_docs_enabled() in (True, False)
    assert facade_run is core_run


def test_server_module_app_reexports_chat_server_app() -> None:
    """Bloque 34.5: ``src.server.app`` re-exports the same object as ``src.chat_server``."""
    from src.chat_server import app as from_chat
    from src.server.app import app as from_server_pkg

    assert from_server_pkg is from_chat
