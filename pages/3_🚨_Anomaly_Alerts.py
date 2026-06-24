import streamlit as st
import plotly.graph_objects as go
from utils.helpers import common_page_setup

st.set_page_config(
    page_title="Anomaly Alerts Panel",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run common helper setup
df_rec, df_raw, selected_month, month_data, prev_data = common_page_setup()

# Render page content
st.title("🚨 Outlier & Anomaly Detection Panel")
st.markdown("We monitor multivariate spending behaviors using Isolation Forest to categorize months with anomalous patterns, without affecting the financial health score.")

# Counts of anomalies
c_severe = (df_rec['anomaly_severity'] == 'Severe Anomaly').sum()
c_moderate = (df_rec['anomaly_severity'] == 'Moderate Anomaly').sum()
c_mild = (df_rec['anomaly_severity'] == 'Mild Anomaly').sum()

st.markdown("### Historical Anomaly Count Summaries")
s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric(label="Severe Anomalies", value=int(c_severe))
with s2:
    st.metric(label="Moderate Anomalies", value=int(c_moderate))
with s3:
    st.metric(label="Mild Anomalies", value=int(c_mild))
with s4:
    st.metric(label="Total Months Monitored", value=int(len(df_rec)))
    
st.markdown("---")

# Timeline
st.subheader("Anomaly Timeline (Overlay on Expenses)")

fig_anom = go.Figure()
# Plot expenses as a baseline
fig_anom.add_trace(go.Scatter(
    x=df_rec['year_month'], y=df_rec['total_debit'],
    name='Regular Expenses', line=dict(color='rgba(255,255,255,0.2)', width=1.5),
    mode='lines'
))

# Overlay anomalies
colors_dict = {'Mild Anomaly': '#FFB300', 'Moderate Anomaly': '#FF7043', 'Severe Anomaly': '#CF6679'}
sizes_dict = {'Mild Anomaly': 10, 'Moderate Anomaly': 14, 'Severe Anomaly': 18}

for sev in ['Mild Anomaly', 'Moderate Anomaly', 'Severe Anomaly']:
    sub = df_rec[df_rec['anomaly_severity'] == sev]
    fig_anom.add_trace(go.Scatter(
        x=sub['year_month'], y=sub['total_debit'],
        name=sev, mode='markers',
        marker=dict(color=colors_dict[sev], size=sizes_dict[sev], line=dict(color='#121212', width=1))
    ))
    
fig_anom.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickangle=-45, nticks=20),
    yaxis=dict(title="Monthly Expenses (Debit)")
)
st.plotly_chart(fig_anom, width='stretch')

# List Anomalies in table
st.subheader("List of Outlier Months (Moderate & Severe)")
outliers = df_rec[df_rec['anomaly_severity'].isin(['Moderate Anomaly', 'Severe Anomaly'])][['year_month', 'total_credit', 'total_debit', 'ending_balance', 'net_savings', 'anomaly_severity']]
st.dataframe(outliers.sort_values(by='year_month', ascending=False), width='stretch')
