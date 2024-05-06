import streamlit as st


def view_monthly_summary(total_kwh: float, total_price: float) -> None:
    col1, col2 = st.columns(spec=[0.5, 0.5])
    with col1:
        st.metric("Estimated Monthly Usage", f"{total_kwh:.3f} kWh".replace(".", ","))
    with col2:
        st.metric(
            "Estimated Monthly Price", f"Rp. {int(total_price):,}".replace(",", ".")
        )
