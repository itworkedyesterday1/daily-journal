import streamlit as st
import pandas as pd
from datetime import date
import os
import calendar

st.set_page_config(page_title="Monthly Habit Tracker", layout="wide")

DATA_FILE = "habit_grid.csv"

# ------------------ SESSION STATE INIT ------------------
if "habit_count" not in st.session_state:
    st.session_state.habit_count = 1

if "habits" not in st.session_state:
    st.session_state.habits = [""]

# ------------------ LOAD DATA ------------------
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

# ------------------ HABIT INPUT (DYNAMIC) ------------------
st.subheader("🧠 Your Habits")

for i in range(st.session_state.habit_count):
    if i >= len(st.session_state.habits):
        st.session_state.habits.append("")

    st.session_state.habits[i] = st.text_input(
        f"Habit {i+1}", st.session_state.habits[i]
    )

# Add habit button
if st.session_state.habit_count < 10:
    if st.button("➕ Add Habit"):
        st.session_state.habit_count += 1

habits = [h for h in st.session_state.habits if h.strip() != ""]

if len(habits) == 0:
    st.warning("Please enter at least one habit.")
    st.stop()

st.divider()

# ------------------ GRID ------------------
st.subheader("✅ Monthly Habit Grid")

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

    consistency = (ticks / days_in_month) * 100
    habit_results.append(consistency)
    row[-1].markdown(f"**{consistency:.0f}%**")

# ------------------ SAVE ------------------
if st.button("💾 Save Month Data"):
    rows = []
    for habit in habits:
        for d in range(1, days_in_month + 1):
            key = f"{habit}_{year}_{month}_{d}"
            rows.append({
                "Year": year,
                "Month": month,
                "Day": d,
                "Habit": habit,
                "Done": int(st.session_state.get(key, False))
            })

    pd.DataFrame(rows).to_csv(DATA_FILE, index=False)
    st.success("✅ Month data saved!")

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

st.write(f"🔥 Best Habit: **{best}**"
