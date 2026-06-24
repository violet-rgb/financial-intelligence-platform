import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
from utils.helpers import common_page_setup

st.set_page_config(
    page_title="Time-Series Forecasting",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run common helper setup
df_rec, df_raw, selected_month, month_data, prev_data = common_page_setup()

# Render page content
st.title("🔮 Time-Series Forecasting")
st.markdown("Predictive analytics showing actual vs. forecasted ending balances based on walk-forward model testing.")

# Load Forecasting Model details from new models directory
try:
    with open("models/best_forecasting_model.pkl", "rb") as f:
        forecasting_pkg = pickle.load(f)
        best_model_name = forecasting_pkg.get("model_name", "ML Model")
except Exception as e:
    best_model_name = "Best ML Model"
    
st.info(f"**Current active model:** {best_model_name} (Trained and validated using Walk-forward TimeSeriesSplit)")

# Out of Sample Forecast
st.markdown("### Next Month Forecast (1-Step Ahead)")
latest_rec = df_rec.iloc[-1]

# Make next month prediction
next_month_name = str(pd.Period(latest_rec['year_month'], freq='M') + 1)
predicted_next_val = latest_rec['forecasted_next_balance']

f1, f2, f3 = st.columns(3)
with f1:
    st.metric(
        label=f"Current Ending Balance ({latest_rec['year_month']})",
        value=f"${latest_rec['ending_balance']:,.2f}"
    )
with f2:
    st.metric(
        label=f"Forecasted Ending Balance ({next_month_name})",
        value=f"${predicted_next_val:,.2f}",
        delta=f"${predicted_next_val - latest_rec['ending_balance']:,.2f} projected"
    )
with f3:
    st.metric(
        label="Forecast Horizon",
        value="1 Month Ahead"
    )
    
st.markdown("---")

# Plot Actual vs. Forecasted
st.subheader("Historical Actual vs. Model-Forecasted Ending Balance")

fig_f = go.Figure()
fig_f.add_trace(go.Scatter(
    x=df_rec['year_month'], y=df_rec['ending_balance'],
    name='Actual Ending Balance', line=dict(color='#BB86FC', width=2.5)
))
fig_f.add_trace(go.Scatter(
    x=df_rec['year_month'], y=df_rec['forecasted_next_balance'].shift(1),
    name=f'Model Forecast (t-1)', line=dict(color='#FFB300', width=2, dash='dash')
))
fig_f.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickangle=-45, nticks=20)
)
st.plotly_chart(fig_f, use_container_width=True)
st.caption("Note: Forecast line is shifted by +1 month to align the prediction made at month t-1 with the actual outcome at month t.")
