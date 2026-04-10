"""
Ethical Android **runtime** entrypoints: long-lived process wiring.

The ethical policy remains exclusively in ``EthicalKernel`` (``src.kernel``).
This package only exposes how the ASGI server and optional read-only helpers start.

See docs/RUNTIME_CONTRACT.md and docs/RUNTIME_FASES.md.
"""

from ..chat_server import get_uvicorn_bind, run_chat_server

__all__ = ["get_uvicorn_bind", "run_chat_server"]
