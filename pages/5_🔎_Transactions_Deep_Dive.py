import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import common_page_setup

st.set_page_config(
    page_title="Transactions Deep-Dive",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run common helper setup
df_rec, df_raw, selected_month, month_data, prev_data = common_page_setup()

# Render page content
st.title("🔎 Transactions Deep-Dive")
st.markdown(f"Detailed categorizations and audits for transactions matching month: **{selected_month}**.")

# Filter raw data to selected month
raw_month = df_raw[df_raw['year_month'] == selected_month]

if len(raw_month) == 0:
    st.warning("No individual transaction details found in the Excel data for this month.")
    st.stop()
    
# Columns
t_col1, t_col2 = st.columns([1, 1])

with t_col1:
    st.subheader("Category Expenditure Distribution")
    
    # Group by Category (Debit Amount only)
    cat_debits = raw_month.groupby('category')['debit_amount'].sum().reset_index()
    cat_debits = cat_debits[cat_debits['debit_amount'] > 0]
    
    if len(cat_debits) > 0:
        fig_pie = px.pie(
            cat_debits, values='debit_amount', names='category',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=30, b=0, l=10, r=10),
            height=300
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No debit transactions recorded this month.")
        
with t_col2:
    st.subheader("Top 5 Expenses This Month")
    top_expenses = raw_month[raw_month['debit_amount'] > 0].sort_values(by='debit_amount', ascending=False).head(5)
    
    if len(top_expenses) > 0:
        st.write(top_expenses[['transaction_date', 'transaction_description', 'category', 'debit_amount']])
    else:
        st.info("No expenses recorded.")
        
st.markdown("---")
st.subheader("All Transactions For This Month")

# Search and Filter
search = st.text_input("🔍 Search Description or Category", "")

filtered_raw = raw_month.copy()
if search:
    filtered_raw = filtered_raw[
        filtered_raw['transaction_description'].str.contains(search, case=False) | 
        filtered_raw['category'].str.contains(search, case=False)
    ]
    
st.write(filtered_raw[['transaction_number', 'transaction_date', 'transaction_type', 'transaction_description', 'debit_amount', 'credit_amount', 'balance', 'category', 'location_city', 'location_country']])
