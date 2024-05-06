from typing import Dict, List, Optional, Tuple

import streamlit as st


def view_year_month_selection(
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
