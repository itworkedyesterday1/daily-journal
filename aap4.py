import streamlit as st
import pandas as pd
from datetime import date
import calendar

st.set_page_config(page_title="Journal.io", layout="wide")

# ---------------- TITLE ----------------
st.markdown("""
<style>
.title {
    text-align:center;
    font-size:56px;
    font-weight:900;
    letter-spacing:4px;
    margin-bottom:10px;
}
</style>
<div class="title">JOURNAL.IO</div>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "habits" not in st.session_state:
    st.session_state.habits = [""] * 10   # 10 default slots

if "data" not in st.session_state:
    st.session_state.data = {}  # {(habit, day): bool}

# ---------------- MONTH / YEAR ----------------
today = date.today()
c1, c2, c3 = st.columns([1,2,1])

with c2:
    ycol, mcol = st.columns(2)
    with ycol:
        year = st.selectbox("Year", [today.year-1, today.year, today.year+1], index=1)
    with mcol:
        month = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)

month_num = list(calendar.month_name).index(month)
days_in_month = calendar.monthrange(year, month_num)[1]

st.divider()

# ---------------- GRID HEADER ----------------
header = st.columns([2] + [0.6]*31 + [0.6])
header[0].markdown("**Habit**")

for d in range(31):
    header[d+1].markdown(f"**{d+1}**")

header[-1].markdown("")

# ---------------- GRID BODY ----------------
active_habits = []

for idx, habit in enumerate(st.session_state.habits):
    row = st.columns([2] + [0.6]*31 + [0.6])

    # Habit name input
    habit_name = row[0].text_input(
        "",
        habit,
        key=f"habit_name_{idx}",
        placeholder="Enter habit"
    )

    if habit_name.strip():
        active_habits.append(habit_name)

    st.session_state.habits[idx] = habit_name

    ticks = 0

    for d in range(1, 32):
        key = (habit_name, d)

        if d <= days_in_month and habit_name.strip():
            checked = row[d].checkbox(
                "",
                key=f"{habit_name}_{d}"
            )
            st.session_state.data[key] = checked
            if checked:
                ticks += 1
                row[d].markdown("✔")
        else:
            row[d].markdown("")

    # Delete habit
    if row[-1].button("❌", key=f"del_{idx}"):
        st.session_state.habits.pop(idx)
        st.rerun()

# ---------------- ADD HABIT ROW ----------------
if st.button("➕ Add new habit"):
    st.session_state.habits.append("")

st.divider()

# ---------------- ANALYSIS ----------------
if active_habits:
    summary = []
    for habit in active_habits:
        done = sum(
            st.session_state.data.get((habit, d), False)
            for d in range(1, days_in_month+1)
        )
        consistency = (done / days_in_month) * 100
        summary.append({
            "Habit": habit,
            "Consistency": consistency
        })

    df = pd.DataFrame(summary)

    st.subheader("📌 Overview")
    st.line_chart(df.set_index("Habit"))

    overall = df["Consistency"].mean()

    best = df.loc[df["Consistency"].idxmax(), "Habit"]
    worst = df.loc[df["Consistency"].idxmin(), "Habit"]

    st.markdown(f"""
    **Overall consistency:** {overall:.1f}%  
    **Strongest habit:** {best}  
    **Weakest habit:** {worst}
    """)

    # ---------------- AI MONTHLY REFLECTION ----------------
    st.subheader("🤖 AI Monthly Reflection")

    reflection = []

    if overall >= 80:
        reflection.append("You showed strong overall discipline this month.")
    elif overall >= 50:
        reflection.append("Your consistency was moderate, with room to improve.")
    else:
        reflection.append("This month showed low consistency, suggesting habits need simplification.")

    reflection.append(
        f"Your strongest habit was **{best}**, indicating this behavior fits well into your routine."
    )

    reflection.append(
        f"The habit **{worst}** struggled most, likely due to timing, motivation, or unrealistic expectations."
    )

    reflection.append(
        "Consider focusing on 1–2 key habits next month and attaching them to an existing routine."
    )

    for r in reflection:
        st.write("• " + r)

else:
    st.info("Add habits to see monthly analysis and reflection.")
