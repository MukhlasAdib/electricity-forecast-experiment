import streamlit as st

from src.arg_parser import AppArguments, parse_args
from src.data_processing import DataHandler
from src.view_data import view_select_year_and_month, view_usage_of_the_month


def main(args: AppArguments) -> None:
    data = DataHandler(args.data)
    data.load_data()
    year_month = view_select_year_and_month(data.get_years_and_months())
    if year_month is None:
        return
    data.set_year_and_month(*year_month)
    if data.month_series_minutely is None:
        st.error("Failed extracting data")
        return
    view_usage_of_the_month(data.month_series_minutely)


if __name__ == "__main__":
    main(parse_args())
