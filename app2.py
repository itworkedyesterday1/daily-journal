import streamlit as st
import pandas as pd
from datetime import date
import os

st.set_page_config(page_title="Habit Journal", layout="centered")

DATA_FILE = "habits.csv"

# Load data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Date", "Habit", "Done"])

st.title("📓 Daily Habit Journal")

# ------------------ HABIT SETUP ------------------
st.header("🧠 Define Your 10 Habits")

if "habits" not in st.session_state:
    st.session_state.habits = [""] * 10

for i in range(10):
    st.session_state.habits[i] = st.text_input(
        f"Habit {i+1}", st.session_state.habits[i]
    )

habits = [h for h in st.session_state.habits if h.strip() != ""]

if len(habits) == 0:
    st.warning("Please define at least one habit.")
    st.stop()

# ------------------ DAILY TRACKING ------------------
st.header("✅ Daily Habit Tracker")

selected_date = st.date_input("Select Date", date.today())

st.subheader("Tick habits completed / avoided today")

daily_data = []

for habit in habits:
    done = st.checkbox(habit, key=f"{habit}_{selected_date}")
    daily_data.append({
        "Date": selected_date,
        "Habit": habit,
        "Done": int(done)
    })

if st.button("Save Today's Habits"):
    df = df[df["Date"] != str(selected_date)]  # overwrite same day
    df = pd.concat([df, pd.DataFrame(daily_data)], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Habits saved for the day!")

# ------------------ MONTHLY ANALYSIS ------------------
st.header("📊 Monthly Consistency Analysis")

if not df.empty:
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M")

    selected_month = st.selectbox(
        "Select Month",
        df["Month"].astype(str).unique()
    )

    month_df = df[df["Month"].astype(str) == selected_month]

    st.subheader("📈 Habit-wise Consistency")

    habit_summary = (
        month_df.groupby("Habit")["Done"]
        .sum()
        .reset_index()
    )

    habit_summary["Consistency %"] = (
        habit_summary["Done"] / month_df["Date"].nunique() * 100
    )

    st.bar_chart(
        habit_summary.set_index("Habit")["Consistency %"]
    )

    total_possible = len(habits) * month_df["Date"].nunique()
    total_done = month_df["Done"].sum()

    overall_consistency = (total_done / total_possible) * 100

    st.subheader("🧠 Monthly Insight")
    st.write(f"✅ **Overall Consistency:** {overall_consistency:.1f}%")
    st.write(f"🔥 **Best Habit:** {habit_summary.loc[habit_summary['Done'].idxmax()]['Habit']}")
    st.write(f"⚠️ **Needs Improvement:** {habit_summary.loc[habit_summary['Done'].idxmin()]['Habit']}")

else:
    st.info("Start tracking habits to see analysis!")
