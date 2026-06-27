"""Walk-forward fold schedule for daytrade threshold calibration.

Yearly expanding-window folds with purge gap. Mirrors the convention used in
``optimize_put_alpha.py`` (``_make_fold_splits``, ``_purge_train``) and
``day-model`` (``purged_tssplit``).

``trade_return`` is a same-day target (features at decision-bar close → exit at
14:30 same day), so forward leakage from trade completion is zero days; the
purge gap is a safety boundary only.

A fold is dropped if its train window has fewer than ``min_train_days`` (so
588000ETF, which starts 2021, only contributes folds where it has enough
history) or its test window has fewer than ``min_test_days``.
"""
from __future__ import annotations

import pandas as pd


MIN_TRAIN_DAYS_DEFAULT = 252   # 1 trading-year burn-in before the first fold
MIN_TEST_DAYS_DEFAULT = 20
PURGE_DAYS_DEFAULT = 1         # trade_return is same-day; 1 day is safety only
FIRST_TEST_YEAR_DEFAULT = 2021


def make_yearly_folds(
    dates,
    min_train_days: int = MIN_TRAIN_DAYS_DEFAULT,
    min_test_days: int = MIN_TEST_DAYS_DEFAULT,
    purge_days: int = PURGE_DAYS_DEFAULT,
    first_test_year: int = FIRST_TEST_YEAR_DEFAULT,
) -> list[dict]:
    """Expanding-window yearly folds.

    For each test year ``Y >= first_test_year``:
      train = all dates strictly before ``Y`` (purge gap applied to the cutoff)
      test  = all dates in calendar year ``Y``

    Returns folds sorted by ``test_year``. Each fold dict::

        {
          "test_year": int,
          "train_end":   Timestamp,   # exclusive cutoff: trades with index <= train_end are train
          "test_start":  Timestamp,   # inclusive
          "test_end":    Timestamp,   # inclusive
          "n_train_days": int,
          "n_test_days":  int,
        }
    """
    dates = pd.to_datetime(dates).sort_values()
    if len(dates) == 0:
        return []
    years = sorted(set(dates.year))
    test_years = [y for y in years if y >= first_test_year]
    folds = []
    for ty in test_years:
        test_dates = dates[dates.year == ty]
        if len(test_dates) < min_test_days:
            continue
        train_dates = dates[dates.year < ty]
        if len(train_dates) < min_train_days:
            continue
        test_start = test_dates.min()
        test_end = test_dates.max()
        train_end = test_start - pd.Timedelta(days=purge_days)
        folds.append({
            "test_year": int(ty),
            "train_end": train_end,
            "test_start": test_start,
            "test_end": test_end,
            "n_train_days": int(len(train_dates)),
            "n_test_days": int(len(test_dates)),
        })
    return folds


def filter_train(trades_df: pd.DataFrame, fold: dict) -> pd.DataFrame:
    """Return rows with index <= fold['train_end'] (or empty if train_end is NaT)."""
    if trades_df is None or len(trades_df) == 0:
        return trades_df
    cutoff = fold["train_end"]
    if pd.isna(cutoff):
        return trades_df.iloc[0:0]
    return trades_df[trades_df.index <= cutoff]


def filter_test(trades_df: pd.DataFrame, fold: dict) -> pd.DataFrame:
    """Return rows with test_start <= index <= test_end."""
    if trades_df is None or len(trades_df) == 0:
        return trades_df
    mask = (trades_df.index >= fold["test_start"]) & (trades_df.index <= fold["test_end"])
    return trades_df[mask]


if __name__ == "__main__":
    # Smoke test: print folds for a synthetic date range
    idx = pd.bdate_range("2015-04-07", "2026-06-17")
    folds = make_yearly_folds(idx)
    print(f"{'Year':<6}{'TrainEnd':<14}{'TestStart':<14}{'TestEnd':<14}{'NTrain':>8}{'NTest':>6}")
    for f in folds:
        print(f"{f['test_year']:<6}{str(f['train_end'].date()):<14}"
              f"{str(f['test_start'].date()):<14}{str(f['test_end'].date()):<14}"
              f"{f['n_train_days']:>8}{f['n_test_days']:>6}")
