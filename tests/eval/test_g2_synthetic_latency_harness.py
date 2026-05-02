from __future__ import annotations

from scripts.eval.g2_synthetic_latency_harness import (
    build_provisional_report,
    build_synthetic_samples,
)


def test_build_synthetic_samples_returns_positive_totals() -> None:
    samples = build_synthetic_samples()

    assert len(samples) >= 10
    assert all(sample["source"] == "synthetic_fixture" for sample in samples)
    assert all(float(sample["total_ms"]) >= 0.0 for sample in samples)


def test_build_provisional_report_marks_report_as_provisional() -> None:
    samples = build_synthetic_samples()
    report = build_provisional_report(samples=samples, target_p95_ms=2500.0)

    assert report["provisional"] is True
    assert report["status"] == "PROVISIONAL"
    assert report["sample_count"] == len(samples)
    assert float(report["p95_ms"]) > 0.0
    assert float(report["target_p95_ms"]) == 2500.0
