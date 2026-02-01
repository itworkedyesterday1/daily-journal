import streamlit as st
import pandas as pd
from datetime import date
import calendar
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

st.set_page_config(page_title="Journal.io", layout="wide")

DATA_FILE = "habit_grid.csv"

# ---------- TITLE ----------
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
}
</style>
<div class="title">JOURNAL.IO</div>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "habit_count" not in st.session_state:
    st.session_state.habit_count = 1
if "habits" not in st.session_state:
    st.session_state.habits = [""]

# ---------- MONTH / YEAR ----------
today = date.today()
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    y, m = st.columns(2)
    with y:
        year = st.selectbox("Year", [today.year-1, today.year, today.year+1], index=1)
    with m:
        month = st.selectbox("Month", list(calendar.month_name)[1:], index=today.month-1)

month_num = list(calendar.month_name).index(month)
days_in_month = calendar.monthrange(year, month_num)[1]

st.divider()

# ---------- GRID HEADER + BUTTONS ----------
hcol, addcol, delcol = st.columns([6, 1, 1])

with hcol:
    st.subheader("✅ Monthly Habit Grid")

with addcol:
    if st.session_state.habit_count < 10:
        if st.button("➕ Add"):
            st.session_state.habit_count += 1
            st.session_state.habits.append("")

with delcol:
    if st.session_state.habit_count > 1:
        if st.button("➖ Delete"):
            st.session_state.habit_count -= 1
            st.session_state.habits.pop()

# ---------- HABIT INPUT INLINE ----------
for i in range(st.session_state.habit_count):
    st.session_state.habits[i] = st.text_input(
        f"Habit {i+1}", st.session_state.habits[i]
    )

habits = [h for h in st.session_state.habits if h.strip()]
if not habits:
    st.warning("Add at least one habit.")
    st.stop()

# ---------- GRID ----------
header = st.columns([1.8] + [0.5]*31 + [1])
header[0].markdown("**Habit**")
for d in range(31):
    header[d+1].markdown(f"**{d+1}**")
header[-1].markdown("**%**")

habit_results = []
weekly_results = []

for habit in habits:
    row = st.columns([1.8] + [0.5]*31 + [1])
    row[0].markdown(habit)

    ticks = 0
    weekly = [0, 0, 0, 0, 0]

    for d in range(1, 32):
        key = f"{habit}_{year}_{month}_{d}"

        if d <= days_in_month:
            checked = row[d].checkbox("", key=key)
            if checked:
                ticks += 1
                weekly[(d-1)//7] += 1
                row[d].markdown("🟢")
            else:
                row[d].markdown("🔴")
        else:
            row[d].markdown("—")

    consistency = (ticks / days_in_month) * 100
    habit_results.append(consistency)
    weekly_results.append(weekly)

    row[-1].markdown(f"**{int(consistency)}%**")

# ---------- SAVE ----------
if st.button("💾 Save Month"):
    rows = []
    for habit in habits:
        for d in range(1, days_in_month+1):
            rows.append({
                "Year": year,
                "Month": month,
                "Day": d,
                "Habit": habit,
                "Done": int(st.session_state.get(f"{habit}_{year}_{month}_{d}", False))
            })
    pd.DataFrame(rows).to_csv(DATA_FILE, index=False)
    st.success("Saved successfully!")

st.divider()

# ---------- OVERVIEW ----------
st.subheader("📌 Overview")

summary = pd.DataFrame({
    "Habit": habits,
    "Consistency %": habit_results
})

st.line_chart(summary.set_index("Habit"))

overall = sum(habit_results) / len(habit_results)
best = summary.loc[summary["Consistency %"].idxmax(), "Habit"]
worst = summary.loc[summary["Consistency %"].idxmin(), "Habit"]

st.markdown(f"""
- **Overall Consistency:** {overall:.1f}%  
- **Best Habit:** {best}  
- **Needs Improvement:** {worst}
""")

# ---------- PDF EXPORT ----------
def generate_pdf():
    file = f"Journal_{month}_{year}.pdf"
    c = canvas.Canvas(file, pagesize=A4)
    text = c.beginText(40, 800)
    text.setFont("Helvetica", 12)

    text.textLine(f"Journal.io – {month} {year}")
    text.textLine("")

    for i, habit in enumerate(habits):
        text.textLine(f"{habit}: {int(habit_results[i])}%")

    c.drawText(text)
    c.save()
    return file

if st.button("📄 Export Month as PDF"):
    pdf = generate_pdf()
    st.success("PDF generated!")
    st.download_button("Download PDF", open(pdf, "rb"), file_name=pdf)
