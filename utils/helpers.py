import streamlit as st
import pandas as pd
import numpy as np

def inject_custom_css():
    st.markdown("""
    <style>
        /* Main Background */
        .stApp {
            background-color: #121212;
            color: #FFFFFF;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #1E1E1E !important;
            border-right: 1px solid #2D2D2D;
        }
        
        /* Metrics panel */
        div[data-testid="metric-container"] {
            background-color: #1E1E1E;
            border: 1px solid #2D2D2D;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        
        div[data-testid="stMetricValue"] {
            font-size: 32px;
            font-weight: 700;
            color: #BB86FC !important;
        }
        
        div[data-testid="stMetricLabel"] {
            color: #A0A0A0 !important;
            font-weight: 500;
        }

        /* Custom Recommendation Cards */
        .reco-card {
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
            border-left: 5px solid;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
        }
        .reco-high {
            background-color: rgba(207, 102, 121, 0.1);
            border-left-color: #CF6679;
            border: 1px solid rgba(207, 102, 121, 0.3);
        }
        .reco-medium {
            background-color: rgba(255, 179, 0, 0.1);
            border-left-color: #FFB300;
            border: 1px solid rgba(255, 179, 0, 0.3);
        }
        .reco-info {
            background-color: rgba(3, 218, 198, 0.1);
            border-left-color: #03DAC6;
            border: 1px solid rgba(3, 218, 198, 0.3);
        }
        .reco-none {
            background-color: rgba(255, 255, 255, 0.05);
            border-left-color: #888888;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .reco-title {
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 6px;
        }
        .reco-impact {
            font-size: 11px;
            text-transform: uppercase;
            font-weight: 700;
            float: right;
            padding: 2px 6px;
            border-radius: 4px;
        }
        .impact-high { background-color: #CF6679; color: #121212; }
        .impact-medium { background-color: #FFB300; color: #121212; }
        .impact-info { background-color: #03DAC6; color: #121212; }
        .impact-none { background-color: #888888; color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # Load recommendations data from the new location
    df_rec = pd.read_csv("data/recommendations.csv")
    
    # Load raw transactions from the new location
    excel_path = "data/laramee26openBankTransactionData.xlsx"
    df_raw = pd.read_excel(excel_path)
    df_raw = df_raw.iloc[::-1].reset_index(drop=True)
    df_raw.columns = df_raw.columns.str.strip().str.replace(' ', '_').str.lower()
    df_raw['debit_amount'] = df_raw['debit_amount'].fillna(0.0)
    df_raw['credit_amount'] = df_raw['credit_amount'].fillna(0.0)
    df_raw['category'] = df_raw['category'].fillna('Others')
    df_raw['transaction_date'] = pd.to_datetime(df_raw['transaction_date'], format='%d/%m/%Y')
    df_raw['year_month'] = df_raw['transaction_date'].dt.to_period('M').astype(str)
    
    return df_rec, df_raw

def initialize_sidebar(df_rec):
    st.sidebar.title("💳 Financial Intelligence")
    st.sidebar.markdown("*Publication Quality Analytics*")
    st.sidebar.markdown("---")
    
    # Target month list selection (defaults to latest)
    months_list = sorted(df_rec['year_month'].unique(), reverse=True)
    
    # Persist the selected month in session state across all pages
    if 'selected_month' not in st.session_state:
        st.session_state['selected_month'] = months_list[0]
        
    # We must handle the index manually to match the session_state value
    try:
        current_index = months_list.index(st.session_state['selected_month'])
    except ValueError:
        current_index = 0
        
    selected_month = st.sidebar.selectbox(
        "Select Target Month", 
        months_list, 
        index=current_index
    )
    
    # Sync selectbox change back to session state
    st.session_state['selected_month'] = selected_month
    
    # Filter data to selected month
    month_idx = df_rec[df_rec['year_month'] == selected_month].index[0]
    month_data = df_rec.loc[month_idx]
    
    # Safely get previous month row for MoM deltas
    prev_data = df_rec.loc[month_idx - 1] if month_idx > 0 else month_data
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Selected Month Summary:**")
    st.sidebar.text(f"Month: {selected_month}")
    st.sidebar.text(f"Health Score: {month_data['financial_health_score']:.1f}/100")
    st.sidebar.text(f"Health Category: {month_data['financial_health_category']}")
    st.sidebar.text(f"Anomaly Level: {month_data['anomaly_severity']}")
    
    return selected_month, month_data, prev_data

def common_page_setup():
    inject_custom_css()
    try:
        df_rec, df_raw = load_data()
    except Exception as e:
        st.error(f"Error loading datasets. Ensure paths are correct. Details: {e}")
        st.stop()
        
    selected_month, month_data, prev_data = initialize_sidebar(df_rec)
    return df_rec, df_raw, selected_month, month_data, prev_data
