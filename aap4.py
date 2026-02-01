import streamlit as st
import pandas as pd
from datetime import date
import calendar
import os

st.set_page_config(page_title="Journal.io", layout="wide")

DATA_FILE = "habit_grid.csv"

# ------------------ CSS FOR 3D TITLE ------------------
st.markdown("""
<style>
.title {
    text-align: center;
    font-size: 64px;
    font-weight: 900;
    letter-spacing: 4px;
    color: #111;
    text-shadow:
        2px 2px 0 #ccc,
        4px 4px 0 #999,
        6px 6px 10px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">JOURNAL.IO</div>', unsafe_allow_html=True)

# ------------------ SESSION STATE ------------------
if "habit_count" not in st.session_state:
    st.session_state.habit_count = 1

if "habits" not in st.session_state:
    st.session_state.habits = [""]

# ------------------ MONTH & YEAR ROW ------------------
today = date.today()

c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    col_y, col_m = st.columns(2)

    with col_y:
        year = st.selectbox(
            "Year",
            [today.year - 1, today.year, today.year + 1],
            index=1
        )

    with col_m:
        month = st.selectbox(
            "Month",
            list(calendar.month_name)[1:],
            index=today.month - 1
        )

month_num = list(calendar.month_name).index(month)
days_in_month = calendar.monthrange(year, month_num)[1]

st.divider()

# ------------------ HABIT INPUT ------------------
st.subheader("🧠 Your Habits")

for i in range(st.session_state.habit_count):
    if i >= len(st.session_state.habits):
        st.session_state.habits.append("")

    st.session_state.habits[i] = st.text_input(
        f"Habit {i + 1}",
        st.session_state.habits[i]
    )

btn1, btn2 = st.columns(2)

with btn1:
    if st.session_state.habit_count < 10:
        if st.button("➕ Add Habit"):
            st.session_state.habit_count += 1

with btn2:
    if st.session_state.habit_count > 1:
        if st.button("➖ Delete Habit"):
            st.session_state.habit_count -= 1
            st.session_state.habits.pop()

# Clean habit list
habits = [h.strip() for h in st.session_state.habits if h.strip() != ""]

if not habits:
    st.warning("Please add at least one habit.")
    st.stop()

st.divider()

# ------------------ GRID ------------------
st.subheader("✅ Monthly Habit Grid")

# Header
header = st.columns([1.5] + [0.5] * 31 + [1])
header[0].markdown("**Habit**")

for d in range(31):
    header[d + 1].markdown(f"**{d + 1}**")

header[-1].markdown("**%**")

habit_results = []

for habit in habits:
    row = st.columns([1.5] + [0.5] * 31 + [1])
    row[0].markdown(habit)

    ticks = 0

    for d in range(1, 32):
        key = f"{habit}_{year}_{month}_{d}"

        if d <= days_in_month:
            checked = row[d].checkbox("", key=key)
            if checked:
                ticks += 1
        else:
            row[d].markdown("—")

    consistency = (ticks / days_in_month) * 100
    habit_results.append(consistency)

    row[-1].markdown(f"**{int(consistency)}%**")

# ------------------ SAVE ------------------
if st.button("💾 Save Month"):
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
    st.success("✅ Saved successfully!")

st.divider()

# ------------------ SUMMARY ------------------
st.subheader("📊 Monthly Consistency")

summary = pd.DataFrame({
    "Habit": habits,
    "Consistency %": habit_results
})

st.bar_chart(summary.set_index("Habit"))

overall = sum(habit_results) / len(habit_results)
st.markdown(f"### 🧠 Overall Consistency: **{overall:.1f}%**")

best = summary.loc[summary["Consistency %"].idxmax(), "Habit"]
worst = summary.loc[summary["Consistency %"].idxmin(), "Habit"]

st.write(f"🔥 Best Habit: **{best}**")
st.write(f"⚠️ Needs Improvement: **{worst}**")
