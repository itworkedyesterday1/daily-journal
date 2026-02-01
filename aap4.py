import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="Journal.io", layout="centered")

# ---------- TITLE ----------
st.markdown("""
<h1 style='text-align:center;'>JOURNAL.IO</h1>
<p style='text-align:center; color:gray;'>A quiet guide for better days</p>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "habits" not in st.session_state:
    st.session_state.habits = ["Exercise", "Read", "Sleep on time"]

if "log" not in st.session_state:
    st.session_state.log = []

today = date.today()

# ---------- DAILY CHECK-IN ----------
st.subheader("🕊️ Daily Check-In")

energy = st.selectbox("Energy today", ["Low", "Medium", "High"])
focus = st.selectbox("Focus today", ["Low", "Medium", "High"])

# ---------- HABIT TRACKER ----------
st.subheader("✅ Habits")

daily_entry = {"date": today, "energy": energy, "focus": focus, "habits": {}}

for habit in st.session_state.habits:
    done = st.checkbox(habit)

    why = None
    if not done:
        why = st.selectbox(
            f"Why was '{habit}' missed?",
            ["Low energy", "Low time", "Low interest"],
            key=habit
        )

    daily_entry["habits"][habit] = {
        "done": done,
        "why": why
    }

if st.button("Save Day"):
    st.session_state.log.append(daily_entry)
    st.success("Day saved. No judgment. Just data.")

st.divider()

# ---------- DAILY FORECAST ----------
st.subheader("☁️ Tomorrow’s Forecast")

if len(st.session_state.log) >= 3:
    recent = st.session_state.log[-3:]
    avg_done = sum(
        sum(h["done"] for h in day["habits"].values())
        for day in recent
    ) / (len(recent) * len(st.session_state.habits))

    if avg_done > 0.7:
        st.write("Energy: High • Best window: Morning")
    elif avg_done > 0.4:
        st.write("Energy: Medium • Pace yourself")
    else:
        st.write("Energy: Low • Focus on recovery")
else:
    st.write("Not enough data yet.")

st.divider()

# ---------- SILENT PROGRESS ----------
st.subheader("📈 Silent Progress")

if st.session_state.log:
    df = []
    for day in st.session_state.log:
        completed = sum(h["done"] for h in day["habits"].values())
        df.append(completed)

    st.line_chart(df)
    st.caption("Progress isn’t streaks. It’s stability.")

st.divider()

# ---------- AI REFLECTION ----------
st.subheader("✍️ Reflection (AI-assisted)")

if st.session_state.log:
    last = st.session_state.log[-1]
    misses = [
        h for h, v in last["habits"].items()
        if not v["done"]
    ]

    draft = "Today wasn’t perfect — and that’s okay.\n\n"

    if misses:
        draft += f"You missed {', '.join(misses)}. "
        draft += "The reason matters more than the miss.\n"
    else:
        draft += "You showed up for yourself today.\n"

    draft += "\nWhat would make tomorrow 1% easier?"

    reflection = st.text_area("Edit if you want", draft, height=150)
else:
    st.write("Save a day to generate reflection.")

st.divider()

# ---------- FUTURE YOU ----------
st.subheader("🔮 A Note from You, 30 Days Ahead")

if len(st.session_state.log) >= 5:
    consistency = sum(
        sum(h["done"] for h in d["habits"].values())
        for d in st.session_state.log
    ) / (len(st.session_state.log) * len(st.session_state.habits))

    if consistency > 0.6:
        st.write(
            "If you keep this pace, your confidence compounds quietly. "
            "Don’t rush. Just stay."
        )
    else:
        st.write(
            "If this continues, burnout is likely. "
            "Reduce the load — not your standards."
        )
else:
    st.write("Your future self is still forming.")
