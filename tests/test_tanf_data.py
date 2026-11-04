from pathlib import Path

import pandas as pd
import pytest

from tanf_data import (
    DATA_DIR,
    STATE_NAMES,
    load_caseload_data,
    validate_caseload_data,
)


@pytest.fixture(scope="module")
def caseload() -> pd.DataFrame:
    return load_caseload_data(DATA_DIR)


def test_loads_all_states_and_three_fiscal_years(caseload: pd.DataFrame) -> None:
    assert set(caseload["state"]) == set(STATE_NAMES)
    assert set(caseload["fiscal_year"]) == {2022, 2023, 2024}
    assert caseload.groupby(["fiscal_year", "state"])["month"].nunique().eq(12).all()


def test_fiscal_year_windows_are_october_through_september(caseload: pd.DataFrame) -> None:
    for year, rows in caseload.groupby("fiscal_year"):
        assert rows["month"].min() == pd.Timestamp(year - 1, 10, 1)
        assert rows["month"].max() == pd.Timestamp(year, 9, 1)


def test_recipient_counts_reconcile(caseload: pd.DataFrame) -> None:
    assert (
        caseload["total_recipients"] == caseload["adults"] + caseload["children"]
    ).all()


def test_validator_rejects_duplicate_observations(caseload: pd.DataFrame) -> None:
    duplicate = pd.concat([caseload, caseload.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate"):
        validate_caseload_data(duplicate)


def test_validator_rejects_invalid_recipient_totals(caseload: pd.DataFrame) -> None:
    invalid = caseload.copy()
    invalid.loc[0, "total_recipients"] += 1
    with pytest.raises(ValueError, match="adults plus children"):
        validate_caseload_data(invalid)
