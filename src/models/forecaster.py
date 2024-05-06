from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
import streamlit as st
from darts import TimeSeries
from darts.models import LightGBMModel

from src.constants import DEFAULT_DATA_SAMPLING_MINUTE


class AverageForecaster:
    def __init__(self):
        self.means: Optional[Dict[str, float]] = None

    @property
    def total_daily_average(self) -> float:
        if self.means is None:
            return 0
        return sum(self.means.values())

    def fit(self, daily_df: pd.DataFrame) -> "AverageForecaster":
        out = {}
        mean_data = daily_df.mean()
        for name in daily_df.mean().index:
            if name == "Date":
                continue
            out[name] = mean_data[name]
        self.means = out
        return self

    def predict(self, days: float) -> Optional[Dict[str, float]]:
        if self.means is None:
            return None
        out = {}
        for n, v in self.means.items():
            out[n] = v * days
        out["All"] = sum(out.values())
        return out


class LGBMForecaster:
    def __init__(
        self, model_path: Path, sampling_minute: int = DEFAULT_DATA_SAMPLING_MINUTE
    ) -> None:
        self.model: LightGBMModel = LightGBMModel.load(model_path)  # type: ignore
        self.sampling_minute = sampling_minute

    def predict(self, series: TimeSeries, day_horizon: int):
        horizon_samples = int(day_horizon * 24 * 60 / self.sampling_minute)
        if not isinstance(start_time := series.start_time(), pd.Timestamp):
            return None
        start_time.to_pydatetime()
        minute_df = (
            series.univariate_component(0)
            .append_values(np.array([0] * horizon_samples))
            .pd_dataframe()
            .reset_index()
            .loc[:, ["Datetime"]]
        )
        minute_df["Minute"] = minute_df["Datetime"].apply(
            lambda x: x.minute + (x.hour * 60)
        )
        minute_series = TimeSeries.from_dataframe(
            minute_df, time_col="Datetime", value_cols="Minute"
        )
        return self.model.predict(
            horizon_samples,
            series=series,
            future_covariates=minute_series,
        )
