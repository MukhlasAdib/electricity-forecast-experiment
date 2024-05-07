import calendar
import datetime
from typing import Optional, Tuple

import pandas as pd
from darts import TimeSeries

from src.controller.historical_utils import (
    get_df_of_historical_data,
    get_total_usage_per_device,
)
from src.models.forecaster import AverageForecaster


def get_days_remaining_of_the_month(current_date: datetime.datetime) -> float:
    num_days = calendar.monthrange(current_date.year, current_date.month)[1]
    current_days = (
        current_date.day + (current_date.hour / 24) + (current_date.minute / 1440)
    )
    return num_days - current_days


def calculate_forecasted_usage_data(
    forecaster: AverageForecaster,
    series_daily: TimeSeries,
    last_datetime: datetime.datetime,
    price_per_kwh: float,
) -> Optional[pd.DataFrame]:
    forecasted_usage = forecaster.predict(
        get_days_remaining_of_the_month(last_datetime)
    )
    if forecasted_usage is None:
        return None

    forecast_df = pd.DataFrame(columns=["Device", "Usage (kWh)"])
    for _, row in get_total_usage_per_device(series_daily, price_per_kwh).iterrows():
        device = str(row["Device"])
        if device not in forecasted_usage:
            continue
        new_row = {
            "Device": device,
            "Usage (kWh)": forecasted_usage[device] + row["Usage (kWh)"],
        }
        forecast_df = pd.concat([forecast_df, pd.DataFrame.from_records([new_row])])
    forecast_df["Price (Rp)"] = forecast_df["Usage (kWh)"] * price_per_kwh
    return forecast_df


def calculate_forecasted_total_usage(
    forecast_data: pd.DataFrame,
) -> Tuple[float, float]:
    sum_data = forecast_data.sum(axis=0)
    return sum_data["Usage (kWh)"], sum_data["Price (Rp)"]


def combine_past_and_future_data(
    future_series: TimeSeries, past_series: TimeSeries, selected_device: Optional[str]
) -> Optional[pd.DataFrame]:
    if selected_device is None:
        selected_devices = []
    else:
        selected_devices = [selected_device]
    past_df = get_df_of_historical_data(past_series, selected_devices, False)
    if past_df is None:
        return None
    future_df = get_df_of_historical_data(future_series, selected_devices, False)
    if future_df is None:
        return None
    past_df["source"] = "Historical"
    future_df["source"] = "Forecast"
    return pd.concat([past_df, future_df], axis=0)


def generate_daily_data_from_minutely(minutely_data: pd.DataFrame):
    daily_data = minutely_data.copy()
    daily_data["Date"] = daily_data["Datetime"].apply(
        lambda x: x.replace(hour=0, minute=0, second=0, microsecond=0)
    )
    all_data = []
    for _, dev_data in daily_data.groupby("Device", as_index=False):
        dev_agg = dev_data.groupby("Date", as_index=False).aggregate(
            {"Power (W)": "sum", "source": "last"}
        )
        all_data.append(dev_agg)
    daily_data = pd.concat(all_data, axis=0)
    daily_data["Usage (kWh)"] = daily_data["Power (W)"] * 5 / 60 / 1000
    del daily_data["Power (W)"]
    last_past_data = daily_data.loc[daily_data["source"] == "Historical", :].iloc[-1, :]
    last_past_data["source"] = "Forecast"
    daily_data = pd.concat(
        [daily_data, last_past_data.to_frame().T], axis=0
    ).sort_values("Date")
    return daily_data


def calculate_total_forecast_series(
    daily_data: pd.DataFrame, price_per_kwh: float
) -> Tuple[float, float]:
    total_kwh = daily_data["Usage (kWh)"].sum()
    total_price = total_kwh * price_per_kwh
    return total_kwh, total_price
