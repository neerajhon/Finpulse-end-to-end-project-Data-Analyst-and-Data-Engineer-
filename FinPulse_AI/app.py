import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# -----------------
# DB Connection
# -----------------
DB_URI = "postgresql+psycopg2://postgres:postgres@localhost:5432/finpulse"
engine = create_engine(DB_URI)

# -----------------
# Page Config
# -----------------
st.set_page_config(
    page_title="🚨 Fraud Detection Dashboard",
    page_icon="🚨",
    layout="wide"
)

# -----------------
# Load Data
# -----------------
@st.cache_data(ttl=60)
def load_data():
    query = "SELECT * FROM fraud_predictions ORDER BY timestamp DESC"
    return pd.read_sql(query, engine)

df = load_data()

# -----------------
# Sidebar KPIs
# -----------------
st.sidebar.title("📊 Key Metrics")

total_txns = len(df)
fraud_txns = df[df['prediction'] == 1].shape[0]
fraud_rate = round((fraud_txns / total_txns) * 100, 2) if total_txns > 0 else 0
avg_score = round(df['score'].mean(), 3)
max_score = round(df['score'].max(), 3)
min_score = round(df['score'].min(), 3)

st.sidebar.metric("Total Transactions", f"{total_txns:,}")
st.sidebar.metric("Fraudulent Transactions", f"{fraud_txns:,}")
st.sidebar.metric("Fraud Rate (%)", fraud_rate)
st.sidebar.metric("Avg Fraud Score", avg_score)
st.sidebar.metric("Max Fraud Score", max_score)
st.sidebar.metric("Min Fraud Score", min_score)
st.sidebar.markdown("---")
st.sidebar.caption("⚡ Data refreshes every 60s")

# -----------------
# Top Filters
# -----------------
st.title("🚨 Real-Time Fraud Detection Dashboard")

col_filter1, col_filter2 = st.columns(2)

with col_filter1:
    if "timestamp" in df.columns:
        min_date = df["timestamp"].min()
        max_date = df["timestamp"].max()
        date_range = st.date_input("📅 Date Range", [min_date, max_date])
        if len(date_range) == 2:
            start_date, end_date = date_range
            df = df[(df["timestamp"].dt.date >= start_date) & (df["timestamp"].dt.date <= end_date)]

with col_filter2:
    status_filter = st.multiselect(
        "🔍 Prediction Type",
        options=["Fraud", "Non-Fraud"],
        default=["Fraud", "Non-Fraud"]
    )
    if "Fraud" not in status_filter:
        df = df[df["prediction"] == 0]
    elif "Non-Fraud" not in status_filter:
        df = df[df["prediction"] == 1]

st.markdown("---")

# -----------------
# 6 Visualizations
# -----------------

# 1️⃣ Fraud Score Distribution
col1, col2 = st.columns(2)
with col1:
    fig1 = px.histogram(df, x="score", color="prediction", nbins=20,
                        labels={"score": "Fraud Score", "prediction": "Prediction"},
                        color_discrete_map={0: "lightblue", 1: "red"})
    fig1.update_layout(template="plotly_dark", bargap=0.2)
    st.subheader("📉 Fraud Score Distribution")
    st.plotly_chart(fig1, use_container_width=True)

# 2️⃣ Fraud vs Non-Fraud Pie Chart
with col2:
    pie_df = df["prediction"].replace({0: "Non-Fraud", 1: "Fraud"}).value_counts().reset_index()
    pie_df.columns = ["Type", "Count"]
    fig2 = px.pie(pie_df, values="Count", names="Type", hole=0.4,
                  color="Type", color_discrete_map={"Fraud": "red", "Non-Fraud": "lightblue"})
    fig2.update_layout(template="plotly_dark")
    st.subheader("🥧 Fraud vs Non-Fraud")
    st.plotly_chart(fig2, use_container_width=True)

# 3️⃣ Fraud Score Trend
fig3 = px.line(df.sort_values("timestamp"), x="timestamp", y="score",
               color="prediction", markers=True,
               labels={"score": "Fraud Score", "timestamp": "Time"})
fig3.update_layout(template="plotly_dark")
st.subheader("📊 Fraud Score Trend")
st.plotly_chart(fig3, use_container_width=True)

# 4️⃣ Risk Level Distribution
df['risk_level'] = pd.cut(df['score'], bins=[0, 0.4, 0.7, 1],
                          labels=["Low", "Medium", "High"])
fig4 = px.histogram(df, x="risk_level", color="prediction",
                    barmode="group", color_discrete_map={0: "lightblue", 1: "red"})
fig4.update_layout(template="plotly_dark")
st.subheader("⚠️ Risk Level Distribution")
st.plotly_chart(fig4, use_container_width=True)

# 5️⃣ Hourly Fraud Activity
if "timestamp" in df.columns:
    df['hour'] = df['timestamp'].dt.hour
    fig5 = px.bar(df.groupby('hour')['prediction'].mean().reset_index(),
                  x="hour", y="prediction", labels={"prediction": "Fraud Rate"},
                  title="Hourly Fraud Rate")
    fig5.update_layout(template="plotly_dark")
    st.subheader("🕒 Hourly Fraud Rate")
    st.plotly_chart(fig5, use_container_width=True)

# 6️⃣ Cumulative Fraud Transactions
if "timestamp" in df.columns:
    df_sorted = df.sort_values("timestamp")
    df_sorted["cumulative_fraud"] = (df_sorted["prediction"] == 1).cumsum()
    fig6 = px.area(df_sorted, x="timestamp", y="cumulative_fraud",
                   labels={"cumulative_fraud": "Cumulative Fraud Cases"},
                   title="Cumulative Fraud Cases Over Time")
    fig6.update_layout(template="plotly_dark")
    st.subheader("📈 Cumulative Fraud Cases")
    st.plotly_chart(fig6, use_container_width=True)


# Top Risky Transactions
st.subheader("🔥 Top Risky Transactions")
top_risky = df[df['prediction'] == 1].sort_values(by="score", ascending=False).head(10)
st.dataframe(top_risky, use_container_width=True)

# -----------------
# Transactions Table
# -----------------
st.markdown("---")
st.subheader("🔍 Search Transactions")
search_term = st.text_input("Enter Transaction ID")
if search_term:
    filtered_df = df[df['transaction_id'].str.contains(search_term, case=False)]
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.dataframe(df.head(50), use_container_width=True)
