import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils.helpers import common_page_setup

# In Streamlit, set_page_config must be the first command on the page
st.set_page_config(
    page_title="Personal Financial Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run common helper setup
df_rec, df_raw, selected_month, month_data, prev_data = common_page_setup()

# Render page content
st.title("📊 Dashboard Overview")
st.markdown(f"### Historical Overview & Targets for **{selected_month}**")

# Compute safe MoM deltas from the previous month row
bal_delta = month_data['ending_balance'] - prev_data['ending_balance']
cred_delta_pct = (
    (month_data['total_credit'] - prev_data['total_credit']) /
    (prev_data['total_credit'] + 1e-5) * 100
)
deb_delta_pct = (
    (month_data['total_debit'] - prev_data['total_debit']) /
    (prev_data['total_debit'] + 1e-5) * 100
)

# KPIs columns
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric(
        label="Ending Balance",
        value=f"${month_data['ending_balance']:,.2f}",
        delta=f"${bal_delta:,.2f} MoM"
    )
with kpi2:
    st.metric(
        label="Monthly Credit (Income)",
        value=f"${month_data['total_credit']:,.2f}",
        delta=f"{cred_delta_pct:.1f}% MoM"
    )
with kpi3:
    st.metric(
        label="Monthly Debit (Expenses)",
        value=f"${month_data['total_debit']:,.2f}",
        delta=f"{deb_delta_pct:.1f}% MoM",
        delta_color="inverse"
    )
with kpi4:
    st.metric(
        label="Net Monthly Savings",
        value=f"${month_data['net_savings']:,.2f}",
        delta=f"Savings Rate: {max(-999, min(999, month_data['savings_rate']*100)):.1f}%"
    )
    
st.markdown("---")

# Charts Section
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Monthly Income vs. Expenses (Historical)")
    fig_flow = go.Figure()
    fig_flow.add_trace(go.Bar(
        x=df_rec['year_month'], y=df_rec['total_credit'],
        name='Income (Credit)', marker_color='#03DAC6'
    ))
    fig_flow.add_trace(go.Bar(
        x=df_rec['year_month'], y=df_rec['total_debit'],
        name='Expenses (Debit)', marker_color='#CF6679'
    ))
    fig_flow.update_layout(
        barmode='group',
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=-45, nticks=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_flow, width='stretch')
    
with chart_col2:
    st.subheader("Ending Balance Growth Trend")
    fig_bal = px.line(
        df_rec, x='year_month', y='ending_balance',
        labels={'ending_balance': 'Balance Amount', 'year_month': 'Month'}
    )
    fig_bal.update_traces(line_color='#BB86FC', line_width=3)
    fig_bal.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=-45, nticks=20)
    )
    st.plotly_chart(fig_bal, width='stretch')
