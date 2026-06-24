import streamlit as st
import pandas as pd
import numpy as np
from utils.helpers import common_page_setup

def safe_get(series, key):
    """Safely get a value from a pd.Series by key, returning None if missing."""
    return series[key] if key in series.index else None

st.set_page_config(
    page_title="Actionable Recommendations",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run common helper setup
df_rec, df_raw, selected_month, month_data, prev_data = common_page_setup()

# Render page content
st.title("💡 Actionable Recommendations")
st.markdown(f"Personalized, rule-based recommendations triggered by monthly indicators for **{selected_month}**.")

# Check alert cards
def render_card(title, text, impact):
    if pd.isna(title) if not isinstance(title, str) else not title:
        return

    # Guard against NaN float values from pandas (bool(nan) is True, causing .lower() crash)
    impact_str = str(impact).lower() if pd.notna(impact) else "none"
    card_class = f"reco-{impact_str}"
    impact_label = str(impact) if pd.notna(impact) else "Info"

    st.markdown(f"""
    <div class="reco-card {card_class}">
        <span class="reco-impact impact-{impact_str}">{impact_label} Impact</span>
        <div class="reco-title">{title}</div>
        <div class="reco-text">{text if pd.notna(text) else ''}</div>
    </div>
    """, unsafe_allow_html=True)

# Display Alerts
render_card(safe_get(month_data, 'savings_alert'), safe_get(month_data, 'savings_text'), safe_get(month_data, 'savings_impact'))
render_card(safe_get(month_data, 'emergency_alert'), safe_get(month_data, 'emergency_text'), safe_get(month_data, 'emergency_impact'))

if 'bills_alert' in month_data.index:
    render_card(safe_get(month_data, 'bills_alert'), safe_get(month_data, 'bills_text'), safe_get(month_data, 'bills_impact'))

render_card(safe_get(month_data, 'anomaly_alert'), safe_get(month_data, 'anomaly_text'), safe_get(month_data, 'anomaly_impact'))
render_card(safe_get(month_data, 'forecast_alert'), safe_get(month_data, 'forecast_text'), safe_get(month_data, 'forecast_impact'))

# Download summary report
st.markdown("---")
st.subheader("Export Analysis Report")

# Prepare export dataframe
export_df = df_rec[df_rec['year_month'] == selected_month][['year_month', 'financial_health_score', 'financial_health_category', 'ending_balance', 'savings_rate', 'emergency_fund_ratio', 'anomaly_severity']]
csv_bytes = export_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label=f"📥 Download Summary Report for {selected_month}",
    data=csv_bytes,
    file_name=f"financial_report_{selected_month}.csv",
    mime="text/csv"
)
