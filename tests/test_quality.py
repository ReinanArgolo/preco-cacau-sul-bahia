from datetime import date

from cocoa_data.quality.checks import extreme_movements


def test_extreme_movement_is_flagged_for_manual_review() -> None:
    rows = [(date(2026, 1, day), 100.0 + day) for day in range(1, 15)]
    rows.append((date(2026, 1, 15), 250.0))
    assert extreme_movements(rows)
