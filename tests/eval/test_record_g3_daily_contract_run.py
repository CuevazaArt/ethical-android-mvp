from scripts.eval.record_g3_daily_contract_run import _has_entry_for_day


def test_has_entry_for_day_true_when_matching_month_and_day() -> None:
    rows = [
        {
            "month": "2026-05",
            "executed_at": "2026-05-02T09:00:00Z",
            "exit_code": 0,
        }
    ]
    assert _has_entry_for_day(rows, month="2026-05", day_key="2026-05-02") is True


def test_has_entry_for_day_false_when_day_missing() -> None:
    rows = [
        {
            "month": "2026-05",
            "executed_at": "2026-05-01T09:00:00Z",
            "exit_code": 0,
        }
    ]
    assert _has_entry_for_day(rows, month="2026-05", day_key="2026-05-02") is False


def test_has_entry_for_day_false_when_month_mismatch() -> None:
    rows = [
        {
            "month": "2026-04",
            "executed_at": "2026-05-02T09:00:00Z",
            "exit_code": 0,
        }
    ]
    assert _has_entry_for_day(rows, month="2026-05", day_key="2026-05-02") is False
