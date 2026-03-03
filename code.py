# ==========================================
# LIFE SYSTEM X – PYTHON PRO BUILD v5.0
# Streamlit + SQLite + Pandas + Matplotlib
# Optimized – Stable – Personal OS System
# ==========================================

import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import math

# ===================== CONFIG =====================
DB_NAME = "life_system_x.db"
XP_PER_TASK = 20
GOOD_DAY_BONUS = 30
GREAT_DAY_BONUS = 60

st.set_page_config(page_title="Life System X", layout="wide")

# ===================== DATABASE =====================

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            tasks INTEGER,
            focus INTEGER,
            stress INTEGER,
            xp INTEGER
        )
    """)
    conn.commit()
    conn.close()


def insert_log(date, tasks, focus, stress, xp):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO logs (date, tasks, focus, stress, xp) VALUES (?, ?, ?, ?, ?)",
        (date, tasks, focus, stress, xp),
    )
    conn.commit()
    conn.close()


def load_logs():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY date ASC", conn)
    conn.close()
    return df


# ===================== ENGINE =====================

def calculate_xp(tasks, focus, stress):
    xp = tasks * XP_PER_TASK
    if focus >= 8 and stress <= 4:
        xp += GREAT_DAY_BONUS
    elif focus >= 6:
        xp += GOOD_DAY_BONUS
    return xp


def calculate_level(total_xp):
    if total_xp <= 0:
        return 0
    return int(math.sqrt(total_xp) / 5)


def burnout_risk(avg_stress, avg_focus):
    if avg_stress >= 8 and avg_focus <= 4:
        return "HIGH"
    elif avg_stress >= 6:
        return "MEDIUM"
    return "LOW"


def calculate_streak(df):
    if df.empty:
        return 0

    df_sorted = df.sort_values(by="date", ascending=False)
    streak = 0
    for _, row in df_sorted.iterrows():
        if row["tasks"] >= 4:
            streak += 1
        else:
            break
    return streak


# ===================== INIT =====================
init_db()

st.title("🚀 LIFE SYSTEM X – PYTHON PRO")
st.markdown("Personal Operating System – Discipline • Focus • Growth")


# ===================== INPUT SECTION =====================
st.subheader("📌 Daily Log")

col1, col2, col3 = st.columns(3)

with col1:
    tasks = st.number_input("Tasks Completed", min_value=0, step=1)

with col2:
    focus = st.slider("Focus Level", 1, 10, 5)

with col3:
    stress = st.slider("Stress Level", 1, 10, 5)


if st.button("Save Log"):
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    xp = calculate_xp(tasks, focus, stress)
    insert_log(today, tasks, focus, stress, xp)
    st.success("Log saved successfully!")


# ===================== LOAD DATA =====================
df = load_logs()

if not df.empty:
    total_xp = df["xp"].sum()
    level = calculate_level(total_xp)
    avg_focus = df["focus"].mean()
    avg_stress = df["stress"].mean()
    burnout = burnout_risk(avg_stress, avg_focus)
    streak = calculate_streak(df)

    st.divider()
    st.subheader("📊 Dashboard")

    d1, d2, d3, d4 = st.columns(4)

    d1.metric("Level", level)
    d2.metric("Total XP", total_xp)
    d3.metric("Streak (≥4 tasks)", streak)
    d4.metric("Burnout Risk", burnout)

    # ===================== CHART =====================
    st.divider()
    st.subheader("📈 30 Day XP Progress")

    df["cumulative_xp"] = df["xp"].cumsum()
    last30 = df.tail(30)

    fig, ax = plt.subplots()
    ax.plot(last30["date"], last30["cumulative_xp"])
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative XP")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # ===================== DATA TABLE =====================
    st.divider()
    st.subheader("📂 Full Data Logs")
    st.dataframe(df, use_container_width=True)

    # ===================== RESET =====================
    if st.button("Reset All Data"):
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM logs")
        conn.commit()
        conn.close()
        st.warning("All data cleared. Please refresh.")

else:
    st.info("No data yet. Start logging today!")
