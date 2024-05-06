import streamlit as st

from src.arg_parser import AppArguments, parse_args
from src.controller.controller import control_data_selection, control_main_data


def main(args: AppArguments) -> None:
    st.markdown(
        "<h1 style='text-align: center; color: bllack;'>Electricity Monitor</h1>",
        unsafe_allow_html=True,
    )
    data = control_data_selection(args.data)
    control_main_data(data)


if __name__ == "__main__":
    main(parse_args())
