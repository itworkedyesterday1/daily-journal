import streamlit as st
import pandas as pd
from datetime import date
import os
import calendar

st.set_page_config(page_title="Monthly Habit Tracker", layout="wide")

DATA_FILE = "habit_grid.csv"

# Load or create data
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame()

st.title("📅 Monthly Habit Tracker")

# ------------------ MONTH SELECTION ------------------
today = date.today()
year = st.selectbox("Year", [today.year - 1, today.year, today.year + 1])
month = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month - 1)

month_num = list(calendar.month_name).index(month)
days_in_month = calendar.monthrange(year, month_num)[1]

st.divider()

# ------------------ HABIT INPUT ------------------
st.subheader("🧠 Your Habits (Max 10)")

habits = []
for i in range(10):
    habit = st.text_input(f"Habit {i+1}", key=f"habit_{i}")
    if habit.strip():
        habits.append(habit)

if len(habits) == 0:
    st.warning("Please enter at least one habit.")
    st.stop()

# Initialize month data
month_key = f"{year}-{month_num}"

if month_key not in df.columns:
    df["Habit"] = habits
    for day in range(1, days_in_month + 1):
        df[f"Day {day}"] = 0

# ------------------ GRID ------------------
st.subheader("✅ Daily Habit Grid")

header_cols = st.columns([2] + [1] * days_in_month + [2])
header_cols[0].markdown("**Habit**")
for d in range(days_in_month):
    header_cols[d + 1].markdown(f"**{d+1}**")
header_cols[-1].markdown("**Result %**")

habit_results = []

for i, habit in enumerate(habits):
    row = st.columns([2] + [1] * days_in_month + [2])
    row[0].markdown(habit)

    ticks = 0

    for d in range(1, days_in_month + 1):
        key = f"{habit}_{year}_{month}_{d}"
        checked = row[d].checkbox("", key=key)
        if checked:
            ticks += 1
        df.loc[i, f"Day {d}"] = int(checked)

    consistency = (ticks / days_in_month) * 100
    habit_results.append(consistency)
    row[-1].markdown(f"**{consistency:.0f}%**")

# ------------------ SAVE ------------------
if st.button("💾 Save Month Data"):
    df["Habit"] = habits
    df.to_csv(DATA_FILE, index=False)
    st.success("Month data saved successfully!")

st.divider()

# ------------------ SUMMARY ------------------
st.subheader("📊 Monthly Consistency Summary")

summary_df = pd.DataFrame({
    "Habit": habits,
    "Consistency %": habit_results
})

st.bar_chart(summary_df.set_index("Habit"))

overall = sum(habit_results) / len(habit_results)
st.markdown(f"### 🧠 Overall Consistency: **{overall:.1f}%**")

best = summary_df.loc[summary_df["Consistency %"].idxmax(), "Habit"]
worst = summary_df.loc[summary_df["Consistency %"].idxmin(), "Habit"]

st.write(f"🔥 Best Habit: **{best}**")
st.write(f"⚠️ Needs Improvement: **{worst}**")
