import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def view_live_total(current_total: float, previous_total: float) -> None:
    fig = go.Figure()
    fig.add_trace(
        go.Indicator(
            mode="number+delta",
            value=current_total,
            title="<span style='font-size:1.7em'>Current Usage</span>",
            number={"suffix": " W", "font.size": 40},
            delta={"reference": previous_total, "suffix": " W"},
        )
    )
    fig.update_layout(
        autosize=False, width=200, height=120, margin=dict(l=0, r=0, b=0, t=50, pad=0)
    )
    st.plotly_chart(fig, use_container_width=True)


def view_live_components(data: pd.DataFrame):
    data = data.copy()
    data["Time"] = "Last"
    fig = px.bar(
        data,
        x="Percentage (%)",
        y="Time",
        color="Device",
        orientation="h",
        text="Device",
        hover_data=["Power (W)"],
    )
    fig.update_traces(
        textfont_size=20,
        textangle=0,
        textposition="inside",
        cliponaxis=False,
    )
    fig.update_layout(
        autosize=False,
        width=200,
        height=100,
        margin=dict(l=0, r=0, b=0, t=0, pad=4),
        showlegend=False,
        yaxis=dict(visible=False),
        xaxis=dict(visible=False),
        uniformtext_minsize=8,
        uniformtext_mode="hide",
    )
    st.plotly_chart(fig, use_container_width=True)
