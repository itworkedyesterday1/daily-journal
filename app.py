import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Daily Journal Tracker", layout="centered")

DATA_FILE = "journal.csv"

# Load data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Date", "Actions", "Mood", "Productivity"])

st.title("📓 Daily Journal Tracker")

# ------------------ DAILY ENTRY ------------------
st.header("📝 Today's Entry")

entry_date = st.date_input("Date", date.today())
actions = st.text_area("What did you do today?")
mood = st.slider("Mood (1 = Bad, 10 = Great)", 1, 10, 5)
productivity = st.slider("Productivity (1 = Low, 10 = High)", 1, 10, 5)

if st.button("Save Entry"):
    new_entry = {
        "Date": entry_date,
        "Actions": actions,
        "Mood": mood,
        "Productivity": productivity
    }
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Entry saved!")

# ------------------ MONTHLY ANALYSIS ------------------
st.header("📊 Monthly Analysis")

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    selected_month = st.selectbox(
        "Select Month",
        df["Month"].astype(str).unique()
    )

    month_df = df[df["Month"].astype(str) == selected_month]

    st.subheader("📈 Mood Trend")
    st.line_chart(month_df.set_index("Date")["Mood"])

    st.subheader("⚡ Productivity Trend")
    st.line_chart(month_df.set_index("Date")["Productivity"])

    st.subheader("🧠 Insights")
    st.write(f"⭐ Average Mood: **{month_df['Mood'].mean():.1f}**")
    st.write(f"🚀 Average Productivity: **{month_df['Productivity'].mean():.1f}**")
    st.write(f"📅 Most Productive Day: **{month_df.loc[month_df['Productivity'].idxmax()]['Date'].date()}**")

else:
    st.info("No data yet. Start journaling today!")
