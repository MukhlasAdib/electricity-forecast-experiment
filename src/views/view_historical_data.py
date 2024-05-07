from typing import List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st
from darts import TimeSeries


def view_monthly_summary(total_kwh: float, total_price: float) -> None:
    col1, col2 = st.columns(spec=[0.5, 0.5])
    with col1:
        st.metric("Monthly Usage", f"{total_kwh:.3f} kWh".replace(".", ","))
    with col2:
        st.metric("Monthly Price", f"Rp. {int(total_price):,}".replace(",", "."))


def view_device_portion(device_total_usage: pd.DataFrame) -> None:
    st.markdown("#### Device Contribution")
    fig = px.pie(device_total_usage, values="Price (Rp)", names="Device")
    st.plotly_chart(fig)


def view_historical_data_selection(series: TimeSeries) -> Tuple[List[str], bool]:
    st.markdown("#### Historical Data")
    col1, col2 = st.columns(spec=[0.8, 0.2])
    with col1:
        selected_devices = st.multiselect(
            label="Device",
            options=[*series.components, "All"],
            placeholder="Select device...",
            label_visibility="collapsed",
            key="ms_hist",
        )
    with col2:
        is_daily = st.toggle("Daily", key="tog_hist")
    return selected_devices, is_daily


def view_usage_of_the_month(monthly_usage: pd.DataFrame, is_daily: bool):
    time_column = "Datetime" if not is_daily else "Date"
    data_column = "Power (W)" if not is_daily else "Usage (kWh)"
    fig = px.line(
        monthly_usage,
        x=time_column,
        y=data_column,
        color="Device",
    )
    fig.update_layout(yaxis_range=[0, 1.2 * max(monthly_usage[data_column])])
    st.plotly_chart(fig)
