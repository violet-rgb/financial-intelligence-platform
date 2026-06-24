# 💳 Personal Financial Intelligence Platform

An advanced, publication-quality financial analytics and predictive forecasting platform built with Streamlit, Plotly, and Machine Learning. The platform monitors multivariate spending behaviors, computes domain-weighted financial health scores, forecasts future balances/expenses/incomes, and delivers personalized actionable recommendations.

---

## 🌟 Key Features

*   **📊 Dashboard Overview**: High-level KPIs showing Ending Balance, Monthly Credits, Monthly Debits, Net Savings, and historical trends for income vs. expenses.
*   **🏆 Financial Health Rating**: A dynamic gauge and horizontal bar chart breakdown of the user's financial health score (weighted across savings rate, emergency buffer, savings consistency, expense ratio, and balance growth trend).
*   **🔮 Predictive Forecasting**: A machine learning-powered engine (Gradient Boosting / Walk-forward validation) predicting next month's ending balance, expenses (using Weighted Moving Averages), and income.
*   **🚨 Outlier & Anomaly Detection**: Multivariate outlier identification using **Isolation Forest** to flag unusual monthly spending patterns without affecting baseline health scores.
*   **💡 Actionable Recommendations**: Automated, rule-based recommendation cards categorized by impact level (High, Medium, Info) and a summary report exporter.
*   **🔎 Transactions Deep-Dive**: Detailed spending category distribution pie charts, top 5 monthly expenses, and searchable/filterable transactional databases.

---

## 🛠️ Technology Stack

*   **Frontend / UI**: [Streamlit](https://streamlit.io/) (using customized dark-mode glassmorphic theme styling)
*   **Data Visualization**: [Plotly Express & Plotly Graph Objects](https://plotly.com/) (interactive publication-quality plots)
*   **Data Engineering**: [Pandas](https://pandas.pydata.org/) & [NumPy](https://numpy.org/)
*   **Machine Learning**: [Scikit-Learn](https://scikit-learn.org/) (Isolation Forest, Gradient Boosting, walk-forward timeseries splits)

---

## 🚀 Local Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/violet-rgb/financial-intelligence-platform.git
cd financial-intelligence-platform
```

### 2. Install dependencies
Ensure you have Python 3.10+ installed. Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Run the application
Start the Streamlit local development server:
```bash
streamlit run Dashboard_Overview.py
```
Open your browser and navigate to `http://localhost:8501`.

---

## 🌐 Cloud Deployment (Streamlit Community Cloud)

This application is optimized for free, one-click hosting on **Streamlit Community Cloud**:

1.  Visit [Streamlit Community Cloud](https://share.streamlit.io/) and log in with your GitHub account.
2.  Click **New app** (or **Create app**).
3.  Select this repository: `violet-rgb/financial-intelligence-platform`.
4.  Set the Branch to `master`.
5.  Set the Main file path to `Dashboard_Overview.py`.
6.  Click **Deploy!**

*Note: Streamlit Community Cloud will automatically build dependencies from `requirements.txt` and rebuild on every `git push` to `master`.*
