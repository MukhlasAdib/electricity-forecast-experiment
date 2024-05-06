from typing import List, Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st
from darts import TimeSeries


def view_monthly_summary(
    total_kwh: float, total_price: float, average_daily_kwh: float
) -> None:
    col1, col2 = st.columns(spec=[0.5, 0.5])
    with col1:
        st.metric(
            "Estimated Monthly Usage",
            f"{total_kwh:.3f} kWh".replace(".", ","),
            delta=f"{average_daily_kwh:.3f} kWh / day",
            delta_color="off",
        )
    with col2:
        st.metric(
            "Estimated Monthly Price", f"Rp. {int(total_price):,}".replace(",", ".")
        )


def view_device_portion(device_total_usage: pd.DataFrame) -> None:
    st.markdown("#### Device Contribution")
    fig = px.pie(device_total_usage, values="Price (Rp)", names="Device")
    st.plotly_chart(fig)


def view_choose_day_to_forecast() -> Tuple[int, bool]:
    st.markdown("#### Forecast Data")
    st.markdown("Days ahead to forecast")
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        forecast_days = st.number_input(
            "Days ahead to forecast", min_value=1, label_visibility="collapsed"
        )
    with col2:
        do_inference = st.button("Create forecast")
    return int(forecast_days), do_inference


def view_forecast_data_selection(series: TimeSeries) -> Optional[str]:
    selected_device = st.selectbox(
        label="Device",
        options=[*[str(c) for c in series.components], "All"],
        placeholder="Select device...",
        label_visibility="collapsed",
        key="ms_forc",
    )
    return selected_device


def view_forecast_minutely_usage(combined_data: pd.DataFrame):
    time_column = "Datetime"
    fig = px.line(
        combined_data,
        x=time_column,
        y="Power (W)",
        color="source",
    )
    st.plotly_chart(fig)
