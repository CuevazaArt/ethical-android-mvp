"""Runtime ASGI façade must alias the canonical chat application (Bloque 32.1)."""


def test_runtime_chat_server_app_is_core_app() -> None:
    from src.chat_server import app as core_app
    from src.chat_server import run_chat_server as core_run
    from src.runtime.chat_server import (
        api_docs_enabled,
        chat_lifespan,
    )
    from src.runtime.chat_server import (
        app as runtime_app,
    )
    from src.runtime.chat_server import (
        run_chat_server as facade_run,
    )

    assert runtime_app is core_app
    assert core_app.router.lifespan_context is chat_lifespan
    assert api_docs_enabled() in (True, False)
    assert facade_run is core_run
