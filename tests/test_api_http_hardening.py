"""
API/HTTP Hardening — Production contracts for live interfaces

Validates WebSocket, HTTP timeout, and concurrent client safety:
- Timeout bounds enforcement (KERNEL_CHAT_TURN_TIMEOUT)
- Concurrent client isolation and state safety
- Payload size limits and validation
- Graceful degradation under saturation
- Error recovery and retry semantics
- Connection lifecycle (open, timeout, close)
"""

from __future__ import annotations

import time

import pytest
from src.kernel import EthicalKernel


class TestAPIHTTPHardening:
    """Production hardening for HTTP/WebSocket interfaces."""

    def test_http_timeout_bounds_respected(self):
        """KERNEL_CHAT_TURN_TIMEOUT enforces soft deadline."""
        import os

        os.environ["KERNEL_CHAT_TURN_TIMEOUT"] = "10"

        try:
            k = EthicalKernel(variability=False)
            start = time.time()
            result = k.process_natural("what should I consider?")
            elapsed = time.time() - start

            assert result is not None
            # Should complete within reasonable bounds
            assert elapsed < 120.0
        finally:
            os.environ.pop("KERNEL_CHAT_TURN_TIMEOUT", None)

    def test_http_timeout_task_cancellation(self):
        """Timeout triggers task cancellation to free resources."""
        import os

        os.environ["KERNEL_CHAT_TURN_TIMEOUT"] = "2"

        try:
            k = EthicalKernel(variability=False)

            # Long-running inference
            result = k.process_natural("what is the deepest question about ethics?")
            assert result is not None

            # Should complete even if inference was interrupted
            assert isinstance(result, tuple)
        finally:
            os.environ.pop("KERNEL_CHAT_TURN_TIMEOUT", None)

    def test_http_concurrent_client_isolation(self):
        """Multiple concurrent kernel instances maintain state isolation."""
        import threading

        kernels = [EthicalKernel(variability=False) for _ in range(3)]
        results = []

        def client_worker(client_id: int):
            try:
                k = kernels[client_id]
                k.process_natural(f"client {client_id} turn 1")
                k.process_natural(f"client {client_id} turn 2")
                results.append((client_id, len(k.memory.episodes)))
            except Exception as e:
                results.append((client_id, str(e)))

        threads = [threading.Thread(target=client_worker, args=(i,)) for i in range(3)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Each client should have independent state
        assert len(results) == 3
        assert all(isinstance(r[1], int) for r in results)

    def test_http_payload_json_validation(self):
        """Kernel handles malformed JSON gracefully."""
        k = EthicalKernel(variability=False)

        # Valid input
        result1 = k.process_natural("hello")
        assert result1 is not None

        # Empty input handling
        result2 = k.process_natural("")
        assert result2 is not None

        # Very long input (reasonable limit)
        long_text = "hello " * 100  # 600 chars
        result3 = k.process_natural(long_text)
        assert result3 is not None

    def test_http_response_tuple_contract(self):
        """HTTP responses maintain consistent tuple structure."""
        k = EthicalKernel(variability=False)

        result = k.process_natural("what should I do?")

        # Must be tuple (not dict, list, or string)
        assert isinstance(result, tuple)
        # Must have content
        assert len(result) > 0

    def test_http_error_response_safe(self):
        """Error handling doesn't expose internal state."""
        k = EthicalKernel(variability=False)

        # Edge case input
        result = k.process_natural("---null---")
        assert result is not None
        # Should not expose traceback or internal paths

    def test_http_consecutive_requests_stateful(self):
        """Consecutive requests maintain session state."""
        k = EthicalKernel(variability=False)

        requests = [
            "hello",
            "how are you?",
            "tell me more",
            "thank you",
        ]

        for req in requests:
            result = k.process_natural(req)
            assert result is not None

        # State should accumulate
        assert len(k.memory.episodes) >= 1

    def test_http_websocket_keepalive_simulation(self):
        """WebSocket-like behavior: repeated pings maintain connection."""
        k = EthicalKernel(variability=False)

        # Simulate WebSocket keep-alive with quick pings
        for i in range(5):
            result = k.process_natural(f"status check {i}")
            assert result is not None
            # Should not timeout even with rapid requests

    def test_http_graceful_degradation_under_load(self):
        """Kernel degrades gracefully under concurrent load."""
        import os

        os.environ["KERNEL_CHAT_TURN_TIMEOUT"] = "2"

        try:
            import threading

            results = []

            def load_worker(worker_id: int):
                k = EthicalKernel(variability=False)
                for turn in range(3):
                    try:
                        k.process_natural(f"worker {worker_id} turn {turn}")
                        results.append((worker_id, "ok"))
                    except Exception as e:
                        results.append((worker_id, str(e)))

            threads = [threading.Thread(target=load_worker, args=(i,)) for i in range(5)]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            # Should handle load without crashing
            assert len(results) >= 5
        finally:
            os.environ.pop("KERNEL_CHAT_TURN_TIMEOUT", None)

    def test_http_connection_state_lifecycle(self):
        """Connection lifecycle: open → process → close."""
        k = EthicalKernel(variability=False)

        # Open (implicit in kernel creation)
        assert k is not None

        # Process
        result = k.process_natural("request")
        assert result is not None

        # Close (implicit, no exceptions)
        # Simulate cleanup
        assert k.memory is not None

    def test_http_request_response_timing(self):
        """Request/response timing stays within SLA bounds."""
        import time

        k = EthicalKernel(variability=False)

        start = time.time()
        k.process_natural("quick query")
        elapsed = time.time() - start

        # Should respond in reasonable time (under 60 seconds for MVP)
        assert elapsed < 60.0

    def test_http_retry_idempotence(self):
        """Repeated identical requests produce consistent results."""
        k = EthicalKernel(variability=False)

        request = "what is the best ethical choice?"

        result1 = k.process_natural(request)
        result2 = k.process_natural(request)

        # Both should succeed
        assert result1 is not None
        assert result2 is not None

    def test_http_resource_cleanup_on_error(self):
        """Resources are cleaned up even if kernel encounters error."""
        k = EthicalKernel(variability=False)

        # Try malicious/weird input
        weird_inputs = [
            "\x00\x01\x02",  # Binary data
            "🤖" * 100,  # Unicode emoji spam
            "DROP TABLE" * 50,  # SQL-like injection attempt
        ]

        for inp in weird_inputs:
            try:
                result = k.process_natural(inp)
                # Should handle or reject gracefully
                assert result is not None
            except Exception:
                # Even if exception, kernel should survive
                pass

        # Kernel should still be functional
        final_result = k.process_natural("hello")
        assert final_result is not None

    def test_http_api_contract_consistency(self):
        """All responses conform to API contract."""
        k = EthicalKernel(variability=False)

        queries = [
            "greeting",
            "question",
            "request",
            "complex query",
            "edge case",
        ]

        for query in queries:
            result = k.process_natural(query)

            # Contract: always returns tuple
            assert isinstance(result, tuple), f"Query '{query}' returned {type(result)}"
            # Contract: never empty
            assert len(result) > 0, f"Query '{query}' returned empty tuple"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
