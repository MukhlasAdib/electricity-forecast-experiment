from copy import deepcopy
from typing import List, Optional, Tuple

import pandas as pd
from darts import TimeSeries


def get_df_of_historical_data(
    series: TimeSeries, selected_devices: List[str], is_daily: bool
) -> Optional[pd.DataFrame]:
    device = deepcopy(selected_devices)
    if len(device) <= 0:
        return None
    var_name = "Usage (kWh)" if is_daily else "Power (W)"
    comp_data_list = []
    if "All" in device:
        comp_data_list.append(
            series.sum(axis=1)
            .pd_dataframe()
            .reset_index()
            .rename(columns={"components_sum": var_name})
        )
        device.remove("All")
        device = ["All", *device]

    comp_data_list.extend(
        [
            series.univariate_component(n)
            .pd_dataframe()
            .reset_index()
            .rename(columns={n: var_name})
            for n in device
            if n != "All"
        ]
    )
    for d, n in zip(comp_data_list, device):
        d.insert(1, column="Device", value=n)
    return pd.concat(comp_data_list, axis=0)


def calculate_total_month_usage(
    daily_data: TimeSeries, price_per_kwh: float
) -> Tuple[float, float]:
    total_kwh = daily_data.sum(axis=1).sum(axis=0).values()[0, 0]
    total_price = total_kwh * price_per_kwh
    return total_kwh, total_price


def get_total_usage_per_device(
    series: TimeSeries, price_per_kwh: float
) -> pd.DataFrame:
    total_data = series.sum(axis=0).pd_dataframe().transpose().reset_index()
    total_data.columns = ["Device", "Usage (kWh)"]
    total_data["Price (Rp)"] = total_data["Usage (kWh)"] * price_per_kwh
    return total_data
