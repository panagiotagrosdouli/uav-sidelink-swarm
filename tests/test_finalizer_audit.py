import pandas as pd

from tools.finalize_campaign import _audit_dataframe, _is_count_column


def test_count_suffix_is_not_treated_as_probability_metric():
    assert _is_count_column("mean_bler_n")
    assert _is_count_column("mean_first_tx_success_probability_n")
    df = pd.DataFrame({
        "mean_bler_n": [100],
        "mean_bler_mean": [0.25],
        "mean_first_tx_success_probability_n": [100],
        "mean_first_tx_success_probability_mean": [0.75],
    })
    checks = {row["column"]: row for row in _audit_dataframe("x", df)}
    assert checks["mean_bler_n"]["status"] == "pass"
    assert checks["mean_first_tx_success_probability_n"]["status"] == "pass"


def test_actual_probability_outside_bounds_fails():
    df = pd.DataFrame({"mean_bler_mean": [1.2]})
    checks = _audit_dataframe("x", df)
    assert checks[0]["status"] == "fail"
