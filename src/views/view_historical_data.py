from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st
from darts import TimeSeries


def view_title_and_daily_toggle() -> bool:
    st.markdown("### Monthly Usage")
    return st.toggle("Daily")


def view_device_to_show_selection(series: TimeSeries) -> List[str]:
    return st.multiselect(
        label="Device",
        options=[*series.components, "All (W)"],
        format_func=lambda x: x.replace(" (W)", ""),
        placeholder="Select device...",
        label_visibility="collapsed",
    )


def view_usage_of_the_month(monthly_usage: pd.DataFrame):
    fig = px.line(monthly_usage, x="Datetime", y="Power (W)", color="Device")
    st.plotly_chart(fig)
