import streamlit as st
import pandas as pd
from datetime import date
import calendar
import os

st.set_page_config(page_title="Monthly Habit Tracker", layout="wide")

DATA_FILE = "habit_grid.csv"

# ------------------ SESSION STATE INIT ------------------
if "habit_count" not in st.session_state:
    st.session_state.habit_count = 1

if "habits" not in st.session_state:
    st.session_state.habits = [""]

# ------------------ LOAD DATA ------------------
if os.path.exists(DATA_FILE):
    saved_df = pd.read_csv(DATA_FILE)
else:
    saved_df = pd.DataFrame()

st.title("📅 Monthly Habit Tracker")

# ------------------ MONTH SELECTION ------------------
today = date.today()

year = st.selectbox(
    "Year",
    [today.year - 1, today.year, today.year + 1],
    index=1
)

month = st.selectbox(
    "Month",
    list(calendar.month_name)[1:],
    index=today.month - 1
)

month_num = list(calendar.month_name).index(month)
days_in_month = calendar.monthrange(year, month_num)[1]

st.divider()

# ------------------ HABIT INPUT (DYNAMIC + / -) ------------------
st.subheader("🧠 Your Habits")

for i in range(st.session_state.habit_count):
    if i >= len(st.session_state.habits):
        st.session_state.habits.append("")

    st.session_state.habits[i] = st.text_input(
        f"
