from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st
from darts import TimeSeries


def view_select_year_and_month(
    available_months: Dict[str, List[str]],
) -> Optional[Tuple[str, str]]:
    st.markdown("### Select year and month")
    col1, col2, _ = st.columns(spec=[0.4, 0.4, 0.2])
    with col1:
        year = st.selectbox(
            label="Select year",
            options=list(available_months.keys()),
            index=None,
            placeholder="Select year...",
            label_visibility="collapsed",
        )
    if year is None:
        return None
    with col2:
        month = st.selectbox(
            label="Select month",
            options=available_months.get(year, []),
            index=None,
            placeholder="Select month...",
            label_visibility="collapsed",
        )
    if month is None:
        return None
    return year, month


def view_usage_of_the_month(series: TimeSeries):
    st.markdown("### Power Usage Plot")
    comp_names = st.multiselect(
        label="Device",
        options=series.components,
        format_func=lambda x: x.replace(" (W)", ""),
        placeholder="Select device...",
        label_visibility="collapsed",
    )
    if len(comp_names) <= 0:
        return

    comp_data_list = [
        series.univariate_component(n)
        .pd_dataframe()
        .reset_index()
        .rename(columns={n: "Power (W)"})
        for n in comp_names
    ]
    for d, n in zip(comp_data_list, comp_names):
        d.insert(1, column="Device", value=n)
    comp_data = pd.concat(comp_data_list, axis=0)
    fig = px.line(comp_data, x="Datetime", y="Power (W)", color="Device")
    st.plotly_chart(fig)
