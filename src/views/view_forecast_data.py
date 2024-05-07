import calendar
import datetime
from typing import Optional, Tuple

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
    st.markdown(
        "*the above estimation is calculated simply based on the current average usage"
    )


def view_choose_day_to_forecast(last_date: datetime.date) -> Tuple[datetime.date, bool]:
    st.markdown("#### Forecast Data")
    st.markdown("Forecast until")
    last_day_of_month = calendar.monthrange(last_date.year, last_date.month)[1]
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        forecast_day = st.date_input(
            "Forecast until",
            value=last_date + datetime.timedelta(days=1),
            min_value=last_date + datetime.timedelta(days=1),
            max_value=last_date.replace(day=last_day_of_month),
            label_visibility="collapsed",
        )
    with col2:
        do_inference = st.button("Create forecast")
    if isinstance(forecast_day, tuple) or forecast_day is None:
        raise ValueError("Error when parsing input date")
    return forecast_day, do_inference


def view_forecast_data_selection(series: TimeSeries) -> Tuple[Optional[str], bool]:
    col1, col2 = st.columns(spec=[0.7, 0.3])
    selected_device = None
    with col1:
        selected_device = st.selectbox(
            label="Device",
            options=[*series.components, "All"],
            placeholder="Select device...",
            label_visibility="collapsed",
            key="ms_forc",
        )
    with col2:
        is_daily = st.toggle("Daily", key="tog_forc")
    return selected_device, is_daily


def view_monthly_summary_by_forecast(total_kwh: float, total_price: float) -> None:
    col1, col2 = st.columns(spec=[0.5, 0.5])
    with col1:
        st.metric(
            "Total After Forecast",
            f"{total_kwh:.3f} kWh".replace(".", ","),
            delta_color="off",
        )
    with col2:
        st.metric("Price After Forecast", f"Rp. {int(total_price):,}".replace(",", "."))


def view_forecast_usage(combined_data: pd.DataFrame):
    time_column = "Date" if "Date" in combined_data.columns else "Datetime"
    data_column = (
        "Usage (kWh)" if "Usage (kWh)" in combined_data.columns else "Power (W)"
    )
    fig = px.line(
        combined_data,
        x=time_column,
        y=data_column,
        color="source",
    )
    fig.update_layout(yaxis_range=[0, 1.2 * max(combined_data[data_column])])
    st.plotly_chart(fig)
