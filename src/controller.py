from pathlib import Path

import streamlit as st

from src.controller_utils import get_df_of_historical_data
from src.models.data_handler import DataHandler
from src.views import view_data_selection, view_historical_data


def control_data_selection(data_path: Path) -> DataHandler:
    data = DataHandler(data_path)
    data.load_data()
    year_month = view_data_selection.view_year_month_selection(
        data.get_years_and_months()
    )
    if year_month is None:
        st.error("Cannot retrieve selected year and month")
        st.stop()
    data.set_year_and_month(*year_month)
    return data


def control_historical_data(data: DataHandler) -> None:
    is_daily = view_historical_data.view_title_and_daily_toggle()
    if data.month_series_minutely is None or data.month_series_daily is None:
        st.warning("No data selected yet...")
        return
    selected_devices = view_historical_data.view_device_to_show_selection(
        data.month_series_minutely
    )
    month_usage = get_df_of_historical_data(
        data.month_series_daily if is_daily else data.month_series_minutely,
        selected_devices,
    )
    if month_usage is None:
        st.warning("No device selected yet...")
        st.stop()
    view_historical_data.view_usage_of_the_month(month_usage)
