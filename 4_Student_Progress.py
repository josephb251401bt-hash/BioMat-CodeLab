import streamlit as st
import pandas as pd
from progress_store import get_progress, get_leaderboard

st.title("🏆 Student Progress Dashboard")
st.caption("Your achievements are shared across Biotechnology, Materials Science, and Bio-Materials.")
student_id = st.session_state.get("student_id")
if not student_id:
    st.warning("Return to the BioMat CodeLab homepage and save/load your student profile first.")
    st.stop()

progress = get_progress(student_id)
name = st.session_state.get("display_name", student_id)
st.subheader(f"Welcome, {name}!")
a, b = st.columns(2)
a.metric("Total XP", progress["total_xp"])
b.metric("Total tasks completed", progress["total_completed"])
st.progress(min(progress["total_xp"] / 1200, 1.0), text="Overall progress · 1,200 XP learning target")

st.subheader("Mission breakdown")
labels = {
    "biotechnology": "🧬 Biotechnology Quest",
    "materials_science": "⚙️ Materials Science",
    "biomaterials": "🧫 Bio-Materials Mission",
}
rows = []
for key, label in labels.items():
    rows.append({"Mission": label, "XP earned": progress["mission_xp"][key], "Tasks completed": len(progress["tasks"][key])})
st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

with st.expander("View your completed challenge IDs"):
    for key, label in labels.items():
        st.markdown(f"**{label}**")
        tasks = sorted(progress["tasks"][key], key=str)
        st.write(", ".join(tasks) if tasks else "No completed tasks yet.")

st.subheader("🥇 Leaderboard")
board = get_leaderboard(50)
if board:
    df = pd.DataFrame(board)
    df.index = range(1, len(df) + 1)
    df.index.name = "Rank"
    df = df.rename(columns={"display_name": "Student", "student_id": "Username", "total_xp": "Total XP", "completed_tasks": "Tasks completed"})
    st.dataframe(df, use_container_width=True)
else:
    st.info("No student achievements have been recorded yet.")

st.caption("Use the same student username/ID on future visits to retrieve your saved progress. Do not use a password, email address, or other sensitive personal information as the username in this classroom prototype.")
