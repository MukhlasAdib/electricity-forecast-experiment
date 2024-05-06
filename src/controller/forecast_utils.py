import calendar
import datetime
from typing import Optional, Tuple

import pandas as pd
from darts import TimeSeries

from src.controller.historical_utils import get_total_usage_per_device
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
