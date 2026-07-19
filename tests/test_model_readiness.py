from datetime import date, timedelta

from cocoa_data.modeling.readiness import evaluate_rows


def row(day: date, **changes):
    value = {
        "source": "seagri", "observation_date": day.isoformat(), "price": 100,
        "available_at": f"{(day + timedelta(days=1)).isoformat()}T03:00:00Z",
        "information_set": "historical_observation",
    }
    value.update(changes)
    return value


def test_model_gate_blocks_short_history() -> None:
    result = evaluate_rows([row(date(2025, 1, 1) + timedelta(days=index)) for index in range(215)])
    assert result["ready"] is False
    assert result["local_valid_dates"] == 215


def test_model_gate_requires_both_750_dates_and_three_year_span() -> None:
    start = date(2022, 1, 1)
    rows = [row(start + timedelta(days=round(index * 1095 / 749))) for index in range(750)]
    assert evaluate_rows(rows)["ready"] is True


def test_model_gate_rejects_unknown_publication_timing() -> None:
    start = date(2022, 1, 1)
    rows = [row(start + timedelta(days=round(index * 1095 / 749))) for index in range(750)]
    rows[0]["available_at"] = None
    assert evaluate_rows(rows)["ready"] is False
