import streamlit as st
import pandas as pd
from progress_store import init_db, register_student, get_progress, get_leaderboard

st.set_page_config(
    page_title="BioMat CodeLab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


init_db()

with st.sidebar:
    st.subheader("👤 Student profile")
    saved_id = st.session_state.get("student_id", "")
    saved_name = st.session_state.get("display_name", "")
    student_id_input = st.text_input("Student username / ID", value=saved_id, help="Use the same ID each time to retrieve your progress.")
    display_name_input = st.text_input("Display name", value=saved_name)
    if st.button("Save / load profile", type="primary", use_container_width=True):
        try:
            st.session_state.student_id = register_student(student_id_input, display_name_input)
            st.session_state.display_name = display_name_input.strip()
            st.success("Profile loaded. Your saved progress is ready.")
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))

student_id = st.session_state.get("student_id")
if student_id:
    progress = get_progress(student_id)
    st.sidebar.metric("🌟 Total XP", progress["total_xp"])
    st.sidebar.caption(f"Completed tasks: {progress['total_completed']}")
else:
    progress = None
    st.sidebar.info("Create/load a student profile to save XP across visits.")

st.markdown("""
<style>
.hero {
    padding: 2rem 2.2rem;
    border-radius: 20px;
    background: linear-gradient(120deg, #102f45, #176b70);
    color: white;
    margin-bottom: 1.2rem;
}
.hero h1 { color: white !important; font-size: 2.5rem; margin-bottom: .35rem; }
.hero p { color: white !important; font-size: 1.08rem; margin: 0; }
.tile {
    border: 1px solid rgba(120,140,160,.35);
    border-radius: 16px;
    padding: 1.2rem;
    min-height: 180px;
    background: rgba(120,140,160,.06);
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🔬 BioMat CodeLab</h1>
  <p>Learn Python by solving real-world challenges in Biotechnology,
  Materials Science, and Bio-materials Engineering.</p>
</div>
""", unsafe_allow_html=True)

st.write("Welcome! Choose a mission from the **Pages** menu in the sidebar. Each mission combines beginner-friendly Python concepts with scientific applications.")

a, b, c = st.columns(3)
with a:
    st.markdown("""<div class="tile"><h2>🧬 Biotechnology Quest</h2>
    <p>Practice Python through DNA, enzymes, cells, bioinformatics, and bioprocess-related challenges.</p></div>""", unsafe_allow_html=True)
with b:
    st.markdown("""<div class="tile"><h2>⚙️ Materials Science</h2>
    <p>Explore stress and strain, alloy design, heat treatment, and debugging through engineering problems.</p></div>""", unsafe_allow_html=True)
with c:
    st.markdown("""<div class="tile"><h2>🧫 Bio-Materials Mission</h2>
    <p>Analyze scaffold properties, filter candidate materials, visualize trade-offs, and defend a design.</p></div>""", unsafe_allow_html=True)

st.subheader("How to use the platform")
st.markdown("""
1. Open the sidebar and select one of the three missions.
2. Work through the activities and read the Python explanations.
3. Use the interactive controls, quizzes, and visualizations.
4. Complete the challenges and compare your results.
""")

st.info("Tip: Start with the Biotechnology Quest or Materials Science Mission if you are new to Python. The Bio-Materials Mission brings biological and materials concepts together in a final design exercise.")

if progress is not None:
    st.subheader("🏆 Your unified progress")
    cols = st.columns(4)
    cols[0].metric("Total XP", progress["total_xp"])
    cols[1].metric("Biotechnology XP", progress["mission_xp"]["biotechnology"])
    cols[2].metric("Materials Science XP", progress["mission_xp"]["materials_science"])
    cols[3].metric("Bio-Materials XP", progress["mission_xp"]["biomaterials"])
    st.progress(min(progress["total_xp"] / 1200, 1.0), text="Overall learning progress (illustrative 1,200 XP target)")
    st.subheader("🥇 Student leaderboard")
    board = get_leaderboard()
    if board:
        board_df = pd.DataFrame(board)
        board_df.index = range(1, len(board_df) + 1)
        board_df.index.name = "Rank"
        board_df = board_df.rename(columns={"display_name":"Student", "student_id":"Username", "total_xp":"Total XP", "completed_tasks":"Tasks completed"})
        st.dataframe(board_df, use_container_width=True)
    st.caption("Progress is stored in a local SQLite database in this project folder.")
else:
    st.info("Enter a student username/ID and display name in the sidebar, then select Save / load profile. Your mission scores will then be stored under that profile.")

st.caption("BioMat CodeLab · Interdisciplinary Python learning platform · Student educational project")
