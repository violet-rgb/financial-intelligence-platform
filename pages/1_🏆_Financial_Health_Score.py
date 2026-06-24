import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils.helpers import common_page_setup

st.set_page_config(
    page_title="Financial Health Rating",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run common helper setup
df_rec, df_raw, selected_month, month_data, prev_data = common_page_setup()

# Render page content
st.title("🏆 Financial Health Rating")
st.markdown("This score is calculated using domain-weighted ratios spanning savings, safety buffer, consistency, fixed bills, and balance trends.")

# ── Anomaly Caution Banner ──────────────────────────────────────────────────
anomaly_sev = str(month_data.get('anomaly_severity', '')).strip()

_anomaly_styles = {
    'Severe Anomaly': {
        'icon': '🚨', 'label': 'SEVERE ANOMALY DETECTED',
        'bg': 'rgba(207, 102, 121, 0.15)', 'border': '#CF6679', 'text': '#FF8A9B'
    },
    'Moderate Anomaly': {
        'icon': '⚠️', 'label': 'MODERATE ANOMALY DETECTED',
        'bg': 'rgba(255, 112, 67, 0.15)', 'border': '#FF7043', 'text': '#FF9A7A'
    },
    'Mild Anomaly': {
        'icon': '⚡', 'label': 'MILD ANOMALY DETECTED',
        'bg': 'rgba(255, 179, 0, 0.12)', 'border': '#FFB300', 'text': '#FFD54F'
    },
}

if anomaly_sev in _anomaly_styles:
    s = _anomaly_styles[anomaly_sev]
    st.markdown(f"""
    <div style="
        background: {s['bg']};
        border: 1.5px solid {s['border']};
        border-left: 6px solid {s['border']};
        border-radius: 8px;
        padding: 14px 20px;
        margin-bottom: 18px;
        display: flex;
        align-items: center;
        gap: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    ">
        <span style="font-size: 26px;">{s['icon']}</span>
        <div>
            <div style="font-size: 13px; font-weight: 800; letter-spacing: 1.5px; color: {s['text']};">
                {s['label']}
            </div>
            <div style="font-size: 13px; color: #CCCCCC; margin-top: 3px;">
                Unusual spending behaviour was detected in <strong style="color:{s['text']};">{selected_month}</strong> 
                using Isolation Forest multivariate analysis. Review the 
                <a href="/Anomaly_Alerts" style="color:{s['border']}; text-decoration:underline;">Anomaly Alerts</a> page for details.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
# ────────────────────────────────────────────────────────────────────────────

col_score, col_radar = st.columns([1, 1])

with col_score:
    st.subheader(f"Health Score for {selected_month}")
    
    # Circular Gauge Chart
    score_val = month_data['financial_health_score']
    
    # Determine gauge color
    if score_val >= 80:
        gauge_color = "green"
    elif score_val >= 60:
        gauge_color = "lightgreen"
    elif score_val >= 40:
        gauge_color = "orange"
    else:
        gauge_color = "red"
        
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = score_val,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': f"Rating: {month_data['financial_health_category']}", 'font': {'size': 20}},
        gauge = {
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': gauge_color},
            'steps': [
                {'range': [0, 40], 'color': "rgba(207, 102, 121, 0.15)"},
                {'range': [40, 60], 'color': "rgba(255, 179, 0, 0.15)"},
                {'range': [60, 80], 'color': "rgba(3, 218, 198, 0.15)"},
                {'range': [80, 100], 'color': "rgba(0, 255, 0, 0.1)"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': score_val
            }
        }
    ))
    fig_gauge.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=0, l=30, r=30),
        height=300
    )
    st.plotly_chart(fig_gauge, width='stretch')
    
    # Brief breakdown table
    st.markdown("### Sub-components details:")
    st.write(pd.DataFrame({
        "Metric Sub-score": ["Savings Rate Score (30%)", "Emergency Fund Score (30%)", "Savings Consistency Score (20%)", "Expense Ratio Score (10%)", "Balance Trend Score (10%)"],
        "Score Value": [
            f"{month_data['savings_rate_score']:.1f}/100",
            f"{month_data['emergency_fund_score']:.1f}/100",
            f"{month_data['savings_consistency_score']:.1f}/100",
            f"{month_data['expense_ratio_score']:.1f}/100",
            f"{month_data['balance_trend_score']:.1f}/100"
        ]
    }))

with col_radar:
    st.subheader("Sub-Score Breakdown")
    
    # Horizontal Bar Chart for sub-scores
    categories = ["Savings Rate", "Emergency Buffer", "Savings Consistency", "Expense Ratio", "Balance Growth Trend"]
    scores = [
        month_data['savings_rate_score'],
        month_data['emergency_fund_score'],
        month_data['savings_consistency_score'],
        month_data['expense_ratio_score'],
        month_data['balance_trend_score']
    ]
    
    fig_sub = go.Figure(go.Bar(
        x=scores, y=categories,
        orientation='h',
        marker=dict(
            color=['#03DAC6', '#BB86FC', '#3700B3', '#FFB300', '#CF6679'],
            line=dict(color='#2D2D2D', width=1)
        )
    ))
    
    fig_sub.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 100]),
        margin=dict(t=30, b=30, l=150, r=30)
    )
    st.plotly_chart(fig_sub, width='stretch')
    
st.markdown("---")
st.subheader("Historical Health Score Trend")
fig_score_trend = px.line(df_rec, x='year_month', y='financial_health_score')
fig_score_trend.update_traces(line_color='#03DAC6', line_width=2.5)
fig_score_trend.update_layout(
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(tickangle=-45, nticks=20),
    yaxis=dict(range=[0, 100])
)
st.plotly_chart(fig_score_trend, width='stretch')
