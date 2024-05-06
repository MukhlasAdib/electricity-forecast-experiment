from typing import List, Optional

import pandas as pd
from darts import TimeSeries


def get_df_of_historical_data(
    series: TimeSeries, selected_devices: List[str]
) -> Optional[pd.DataFrame]:
    if len(selected_devices) <= 0:
        return None
    comp_data_list = []
    if "All (W)" in selected_devices:
        comp_data_list.append(
            series.sum(axis=1)
            .pd_dataframe()
            .reset_index()
            .rename(columns={"components_sum": "Power (W)"})
        )
    comp_data_list.extend(
        [
            series.univariate_component(n)
            .pd_dataframe()
            .reset_index()
            .rename(columns={n: "Power (W)"})
            for n in selected_devices
            if n != "All (W)"
        ]
    )
    for d, n in zip(comp_data_list, selected_devices):
        d.insert(1, column="Device", value=n)
    return pd.concat(comp_data_list, axis=0)
