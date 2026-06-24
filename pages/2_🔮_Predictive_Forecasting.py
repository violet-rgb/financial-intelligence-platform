import streamlit as st
import pickle
import pandas as pd
import numpy as np
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
st.markdown("Predictive analytics showing actual vs. forecasted ending balances and expenses based on walk-forward model testing.")

# Load Forecasting Model details from new models directory
try:
    with open("models/best_forecasting_model.pkl", "rb") as f:
        forecasting_pkg = pickle.load(f)
        best_model_name = forecasting_pkg.get("model_name", "ML Model")
except Exception as e:
    best_model_name = "Best ML Model"
    
st.info(f"**Current active model:** {best_model_name} (Trained and validated using Walk-forward TimeSeriesSplit)")

# ── Out of Sample Forecast ───────────────────────────────────────────────────
st.markdown("### Next Month Forecast (1-Step Ahead)")
latest_rec = df_rec.iloc[-1]

# --- Balance Forecast (existing) ---
next_month_name = str(pd.Period(latest_rec['year_month'], freq='M') + 1)
predicted_next_balance = latest_rec['forecasted_next_balance']

# --- Expense Forecast: weighted moving average of lag columns ---
# Weights: lag-1 = 0.6, lag-2 = 0.25, lag-3 = 0.15  (more recent = more weight)
w1, w2, w3 = 0.6, 0.25, 0.15
lag1 = latest_rec['total_debit_lag_1']
lag2 = latest_rec['total_debit_lag_2']
lag3 = latest_rec['total_debit_lag_3']

# Fall back to available lags if some are zero/NaN (early rows)
available = [(w1, lag1), (w2, lag2), (w3, lag3)]
valid = [(w, v) for w, v in available if pd.notna(v) and v > 0]
if valid:
    total_w = sum(w for w, _ in valid)
    predicted_next_expense = sum(w * v for w, v in valid) / total_w
else:
    predicted_next_expense = latest_rec['total_debit']   # fallback: current month

expense_delta = predicted_next_expense - latest_rec['total_debit']
expense_delta_pct = (expense_delta / (latest_rec['total_debit'] + 1e-5)) * 100

# --- Income Forecast: same approach ---
il1 = latest_rec['total_credit_lag_1']
il2 = latest_rec['total_credit_lag_2']
il3 = latest_rec['total_credit_lag_3']
available_i = [(w1, il1), (w2, il2), (w3, il3)]
valid_i = [(w, v) for w, v in available_i if pd.notna(v) and v > 0]
if valid_i:
    total_wi = sum(w for w, _ in valid_i)
    predicted_next_income = sum(w * v for w, v in valid_i) / total_wi
else:
    predicted_next_income = latest_rec['total_credit']

predicted_next_savings = predicted_next_income - predicted_next_expense

# ── KPI Row ──────────────────────────────────────────────────────────────────
f1, f2, f3, f4 = st.columns(4)
with f1:
    st.metric(
        label=f"Current Ending Balance ({latest_rec['year_month']})",
        value=f"${latest_rec['ending_balance']:,.2f}"
    )
with f2:
    st.metric(
        label=f"Forecasted Balance ({next_month_name})",
        value=f"${predicted_next_balance:,.2f}",
        delta=f"${predicted_next_balance - latest_rec['ending_balance']:,.2f} projected"
    )
with f3:
    st.metric(
        label=f"Forecasted Expenses ({next_month_name})",
        value=f"${predicted_next_expense:,.2f}",
        delta=f"{expense_delta_pct:+.1f}% vs this month",
        delta_color="inverse"   # red = expense increase is bad
    )
with f4:
    st.metric(
        label=f"Projected Net Savings ({next_month_name})",
        value=f"${predicted_next_savings:,.2f}",
        delta=f"Income est. ${predicted_next_income:,.2f}"
    )

st.markdown("---")

# ── Chart 1: Actual vs Forecasted Balance ────────────────────────────────────
st.subheader("📈 Historical Actual vs. Model-Forecasted Ending Balance")

fig_f = go.Figure()
fig_f.add_trace(go.Scatter(
    x=df_rec['year_month'], y=df_rec['ending_balance'],
    name='Actual Ending Balance', line=dict(color='#BB86FC', width=2.5)
))
fig_f.add_trace(go.Scatter(
    x=df_rec['year_month'], y=df_rec['forecasted_next_balance'].shift(1),
    name=f'Model Forecast (t-1)', line=dict(color='#FFB300', width=2, dash='dash')
))
# Highlight next-month forecast point
fig_f.add_trace(go.Scatter(
    x=[next_month_name], y=[predicted_next_balance],
    name=f'Next Month Forecast',
    mode='markers',
    marker=dict(color='#FFB300', size=14, symbol='star',
                line=dict(color='#FFFFFF', width=1))
))
fig_f.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickangle=-45, nticks=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_f, use_container_width=True)
st.caption("Note: Forecast line is shifted by +1 month to align the prediction made at month t-1 with the actual outcome at month t.")

st.markdown("---")

# ── Chart 2: Actual vs Projected Expense ─────────────────────────────────────
st.subheader("💸 Historical Actual vs. Projected Next-Month Expenses")

# Build a historical weighted MA series for comparison
df_exp = df_rec[['year_month', 'total_debit', 'total_debit_lag_1',
                  'total_debit_lag_2', 'total_debit_lag_3']].copy()

def wma_expense(row):
    vals = [(w1, row['total_debit_lag_1']),
            (w2, row['total_debit_lag_2']),
            (w3, row['total_debit_lag_3'])]
    valid_v = [(w, v) for w, v in vals if pd.notna(v) and v > 0]
    if not valid_v:
        return np.nan
    tw = sum(w for w, _ in valid_v)
    return sum(w * v for w, v in valid_v) / tw

df_exp['projected_expense'] = df_exp.apply(wma_expense, axis=1)

# Append next-month forecast row
next_row = pd.DataFrame({
    'year_month': [next_month_name],
    'total_debit': [np.nan],
    'projected_expense': [predicted_next_expense]
})
df_exp = pd.concat([df_exp, next_row], ignore_index=True)

fig_e = go.Figure()
fig_e.add_trace(go.Scatter(
    x=df_exp['year_month'], y=df_exp['total_debit'],
    name='Actual Expenses', line=dict(color='#CF6679', width=2.5)
))
fig_e.add_trace(go.Scatter(
    x=df_exp['year_month'], y=df_exp['projected_expense'],
    name='Projected Expenses (WMA)', line=dict(color='#FFB300', width=2, dash='dot')
))
# Highlight next-month star
fig_e.add_trace(go.Scatter(
    x=[next_month_name], y=[predicted_next_expense],
    name='Next Month Projection',
    mode='markers',
    marker=dict(color='#FFB300', size=14, symbol='star',
                line=dict(color='#FFFFFF', width=1))
))
fig_e.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickangle=-45, nticks=20),
    yaxis_title="Amount ($)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig_e, use_container_width=True)

# ── Expense Breakdown Context ─────────────────────────────────────────────────
st.markdown("---")
st.subheader("🗂️ Current Month Expense Category Breakdown")
st.caption("Reference for what's driving this month's spend — use this to anticipate next month's budget needs.")

spend_cols = [c for c in df_rec.columns if c.startswith('spend_') and not c.endswith('_to_income')]
spend_labels = [c.replace('spend_', '').replace('_', ' ').title() for c in spend_cols]
spend_values = [month_data[c] for c in spend_cols]

# Filter out zero values for a cleaner chart
pairs = [(l, v) for l, v in zip(spend_labels, spend_values) if v > 0]
if pairs:
    labels, values = zip(*pairs)
    fig_pie = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        marker=dict(colors=[
            '#BB86FC', '#CF6679', '#FFB300', '#03DAC6',
            '#6200EE', '#018786', '#B00020', '#FF7597',
            '#A0A0A0', '#4FC3F7'
        ]),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<extra></extra>'
    ))
    fig_pie.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        annotations=[dict(
            text=f"<b>${sum(values):,.0f}</b><br>Total",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color='#FFFFFF')
        )]
    )
    st.plotly_chart(fig_pie, use_container_width=True)
