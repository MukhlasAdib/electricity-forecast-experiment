from pathlib import Path

import streamlit as st

from src.controller.forecast_utils import (
    calculate_forecasted_total_usage,
    calculate_forecasted_usage_data,
    calculate_total_forecast_series,
    combine_past_and_future_data,
    generate_daily_data_from_minutely,
)
from src.controller.historical_utils import (
    calculate_total_month_usage,
    get_df_of_historical_data,
    get_total_usage_per_device,
)
from src.data.data_handler import DataHandler
from src.data.forecaster import AverageForecaster, LGBMForecaster
from src.views import (
    view_data_selection,
    view_forecast_data,
    view_historical_data,
    view_live_data,
)


def control_data_selection(data_path: Path) -> DataHandler:
    if "data" not in st.session_state:
        st.session_state["data"] = DataHandler(data_path)
    data: DataHandler = st.session_state["data"]
    data.load_data()
    price_per_kwh = view_data_selection.view_input_kwh()
    data.set_price_per_kwh(price_per_kwh)
    year_month = view_data_selection.view_year_month_selection(
        data.get_years_and_months()
    )
    if year_month is None or data.price_per_kwh <= 0:
        st.warning("The data have not been selected yet...")
        st.stop()
    data.set_year_and_month(*year_month)
    return data


def control_main_data(data: DataHandler, model_path: Path) -> None:
    control_live_data(data)
    tab1, tab2 = st.tabs(["Historical", "Forecast"])
    with tab1:
        control_historical_data(data)
    with tab2:
        control_forecast_data(data, model_path)


def control_live_data(data: DataHandler) -> None:
    if data.month_series_minutely is None:
        st.warning("Data has not been loaded...")
        return
    current_total = data.month_series_minutely[-1].sum(axis=1).values()[0, 0]
    previous_total = data.month_series_minutely[-2].sum(axis=1).values()[0, 0]
    view_live_data.view_live_total(
        current_total,
        previous_total,
    )
    latest_data = data.month_series_minutely[-1].pd_dataframe().T.reset_index()
    latest_data.columns = ["Device", "Power (W)"]
    latest_data["Percentage (%)"] = latest_data["Power (W)"].apply(
        lambda x: x * 100 / current_total
    )
    view_live_data.view_live_components(latest_data)


def control_forecast_data(data: DataHandler, model_path: Path) -> None:
    if (
        data.month_data_daily is None
        or data.month_series_daily is None
        or data.last_data_datetime is None
        or data.month_series_minutely is None
    ):
        st.warning("Data has not been loaded...")
        return

    if "avg_forecaster" not in st.session_state:
        st.session_state["avg_forecaster"] = AverageForecaster().fit(
            data.month_data_daily
        )
    avg_forecaster: AverageForecaster = st.session_state["avg_forecaster"]
    if "min_forecaster" not in st.session_state:
        st.session_state["min_forecaster"] = LGBMForecaster(model_path)
    min_forecaster: LGBMForecaster = st.session_state["min_forecaster"]

    forecast_data = calculate_forecasted_usage_data(
        avg_forecaster,
        data.month_series_daily,
        data.last_data_datetime,
        data.price_per_kwh,
    )
    if forecast_data is None:
        st.warning("Cannot calculate forecast data...")
        return

    forecast_usage, forecast_price = calculate_forecasted_total_usage(forecast_data)
    view_forecast_data.view_monthly_summary(
        forecast_usage, forecast_price, avg_forecaster.total_daily_average
    )

    forecast_days, do_inference = view_forecast_data.view_choose_day_to_forecast(
        data.last_data_datetime.date()
    )
    if do_inference:
        st.session_state["forecasted"] = min_forecaster.predict(
            data.month_series_minutely, forecast_days
        )
    if "forecasted" not in st.session_state:
        st.warning("No forecast have been made...")
        return
    forecasted = st.session_state["forecasted"]

    selected_device, is_daily = view_forecast_data.view_forecast_data_selection(
        data.month_series_minutely
    )
    combined_data = combine_past_and_future_data(
        forecasted, data.month_series_minutely, selected_device
    )
    if combined_data is None:
        st.warning("No device selected yet...")
        return
    combined_data_daily = generate_daily_data_from_minutely(combined_data)
    view_forecast_data.view_monthly_summary_by_forecast(
        *calculate_total_forecast_series(combined_data_daily, data.price_per_kwh)
    )
    view_forecast_data.view_forecast_usage(
        combined_data_daily if is_daily else combined_data
    )


def control_historical_data(data: DataHandler) -> None:
    if data.month_series_minutely is None or data.month_series_daily is None:
        st.warning("No data selected yet...")
        return

    view_historical_data.view_monthly_summary(
        *calculate_total_month_usage(data.month_series_daily, data.price_per_kwh)
    )
    view_historical_data.view_device_portion(
        get_total_usage_per_device(data.month_series_daily, data.price_per_kwh)
    )

    selected_devices, is_daily = view_historical_data.view_historical_data_selection(
        data.month_series_minutely
    )
    month_usage = get_df_of_historical_data(
        data.month_series_daily if is_daily else data.month_series_minutely,
        selected_devices,
        is_daily,
    )
    if month_usage is None:
        st.warning("No device selected yet...")
        return
    view_historical_data.view_usage_of_the_month(month_usage, is_daily)
