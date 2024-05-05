import calendar
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import streamlit as st
from darts import TimeSeries


class DataHandler:
    def __init__(self, data_path: Path) -> None:
        self.data_path = data_path

        self.data: Optional[pd.DataFrame] = None
        self.year: Optional[int] = None
        self.month: Optional[int] = None
        self.month_data: Optional[pd.DataFrame] = None
        self.month_data_minutely: Optional[pd.DataFrame] = None
        self.month_series_minutely: Optional[TimeSeries] = None

    def load_data(self) -> None:
        self.read_csv()

    def read_csv(self) -> None:
        data = pd.read_csv(self.data_path)
        data["Power (W)"] = data["Voltage (V)"] * data["Ampere (A)"]
        data["Datetime"] = pd.to_datetime(data["Timestamp"], format="%Y-%m-%d %H:%M:%S")
        data.insert(
            loc=1,
            column="Minute of day",
            value=data["Datetime"].apply(lambda x: x.minute + (x.hour * 60)),
        )
        self.data = data

    def get_years_and_months(self) -> Dict[str, List[str]]:
        out = {}
        if self.data is None:
            return out
        for year, data_year in self.data.groupby(self.data["Datetime"].dt.year):
            month_list = list(data_year["Datetime"].dt.month.unique())
            out[str(year)] = [calendar.month_name[m] for m in month_list]
        return out

    def set_year_and_month(self, year: str, month: str) -> None:
        if self.data is None:
            return
        self.year = int(year)
        self.month = list(calendar.month_name).index(month)
        year_filter = self.data["Datetime"].dt.year == self.year
        month_filter = self.data["Datetime"].dt.month == self.month
        self.month_data = self.data.loc[
            year_filter & month_filter, ["Datetime", "Power (W)", "Device ID"]
        ].copy()
        self._set_month_minutely_data()

    def _set_month_minutely_data(self) -> None:
        if self.month_data is None:
            return

        pivot_data = []
        for dev_id, d in self.month_data.groupby("Device ID"):
            assert isinstance(d, pd.DataFrame)
            del d["Device ID"]
            d = d.rename(columns={"Power (W)": f"{dev_id} (W)"})
            pivot_data.append(d)
        data_min = pivot_data[0]
        for d in pivot_data[1:]:
            data_min = pd.merge(data_min, d)
        self.month_data_minutely = data_min
        self.month_series_minutely = TimeSeries.from_dataframe(
            data_min,
            time_col="Datetime",
            value_cols=[c for c in data_min.columns if c.endswith("(W)")],
            fill_missing_dates=True,
        )
