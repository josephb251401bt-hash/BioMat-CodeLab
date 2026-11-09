import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from progress_store import get_progress, award_xp

# ---------- Styling ----------
st.markdown("""
<style>
.main-title {font-size: 2.25rem; font-weight: 800; margin-bottom: 0.2rem;}
.subtitle {color: #64748b; font-size: 1.05rem;}
.lab-card {padding: 1rem; border: 1px solid #d7dee8; border-radius: 14px; background: rgba(148,163,184,0.07);}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">⚙️ Materials Science Lab</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Learn Python by solving materials-engineering challenges.</div>', unsafe_allow_html=True)
st.write("Choose a lab from the tabs below. Complete challenges to earn points and build your Materials Science skills.")

if "mse_xp" not in st.session_state:
    st.session_state.mse_xp = 0
if "mse_completed" not in st.session_state:
    st.session_state.mse_completed = set()

if not st.session_state.get("student_id"):
    st.warning("Please create/load your student profile on the BioMat CodeLab homepage first.")
    st.stop()
_saved_mse = get_progress(st.session_state.student_id)
st.session_state.mse_completed = set(_saved_mse["tasks"]["materials_science"])
st.session_state.mse_xp = _saved_mse["mission_xp"]["materials_science"]

def award(key, points):
    if key not in st.session_state.mse_completed:
        st.session_state.mse_completed.add(key)
        award_xp(st.session_state.student_id, "materials_science", key, points)
        st.session_state.mse_xp = get_progress(st.session_state.student_id)["mission_xp"]["materials_science"]
        st.success(f"Challenge completed! +{points} XP")

def status(key):
    return "✅ Completed" if key in st.session_state.mse_completed else "🔒 Not completed yet"

c1, c2, c3 = st.columns(3)
c1.metric("MSE XP", st.session_state.mse_xp)
c2.metric("Challenges completed", len(st.session_state.mse_completed))
c3.metric("Available challenges", 4)

tabs = st.tabs(["🏋️ Stress–Strain", "🧪 Alloy Design", "🔥 Heat Treatment", "🐛 Debugging Lab"])

# ---------- Stress-Strain ----------
with tabs[0]:
    st.header("🏋️ Stress–Strain Challenge")
    st.write("A tensile-testing machine applies force to a specimen. Use the measurements to calculate engineering stress, strain, and Young's modulus.")
    left, right = st.columns([1, 1])
    with left:
        force = st.number_input("Applied force (N)", min_value=0.0, value=20000.0, step=1000.0)
        area = st.number_input("Original cross-sectional area (mm²)", min_value=0.1, value=100.0, step=5.0)
        extension = st.number_input("Extension (mm)", min_value=0.0, value=0.5, step=0.1)
        original_length = st.number_input("Original gauge length (mm)", min_value=0.1, value=50.0, step=5.0)
    stress = force / area  # N/mm² = MPa
    strain = extension / original_length
    youngs = stress / strain if strain > 0 else None
    with right:
        st.subheader("Live results")
        st.metric("Engineering stress", f"{stress:,.2f} MPa")
        st.metric("Engineering strain", f"{strain:.5f} ({strain*100:.3f}%)")
        st.metric("Young's modulus", f"{youngs/1000:,.3f} GPa" if youngs is not None else "Undefined when strain = 0")
        st.caption("Assumes linear-elastic behaviour for the modulus estimate. 1 N/mm² = 1 MPa.")
    st.divider()
    st.subheader("🎯 Quick quiz")
    quiz = st.radio("If the same force is applied to a specimen with a smaller cross-sectional area, what happens to engineering stress?", [
        "Stress decreases", "Stress increases", "Stress stays the same"
    ], key="stress_quiz")
    if st.button("Check answer", key="stress_check"):
        if quiz == "Stress increases":
            st.success("Correct! Stress = Force / Area, so a smaller area gives a larger stress for the same force.")
            award("stress_quiz", 100)
        else:
            st.error("Try again. Use σ = F / A.")
    st.markdown(f"**Status:** {status('stress_quiz')}")
    st.subheader("📈 Explore a sample stress–strain curve")
    strain_pct = np.array([0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.80, 1.0])
    stress_sample = np.array([0, 100, 200, 300, 390, 440, 470, 450, 410])
    fig, ax = plt.subplots()
    ax.plot(strain_pct, stress_sample, marker="o")
    ax.set_xlabel("Engineering strain (%)")
    ax.set_ylabel("Engineering stress (MPa)")
    ax.set_title("Illustrative tensile-test curve (not experimental data)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    st.caption("Illustrative data only. Real curves depend on the material, processing, and test conditions.")

# ---------- Alloy Design ----------
with tabs[1]:
    st.header("🧪 Alloy Design Simulator")
    st.write("Explore how carbon content can influence steel properties. This is a simplified teaching model, not a material-selection or heat-treatment prediction tool.")
    carbon = st.slider("Carbon content (wt. %)", min_value=0.05, max_value=1.20, value=0.40, step=0.05)
    processing = st.selectbox("Choose a simplified processing condition", ["Normalized", "Annealed", "Quenched (illustrative trend)"])
    # Qualitative illustrative model values only
    base_strength = 300 + 420 * carbon
    base_hardness = 90 + 115 * carbon
    base_ductility = max(8, 35 - 22 * carbon)
    multipliers = {
        "Normalized": (1.0, 1.0, 1.0),
        "Annealed": (0.82, 0.88, 1.18),
        "Quenched (illustrative trend)": (1.45, 1.55, 0.58)
    }
    ms, mh, md = multipliers[processing]
    strength = base_strength * ms
    hardness = base_hardness * mh
    ductility = base_ductility * md
    a, b, c = st.columns(3)
    a.metric("Illustrative strength index", f"{strength:.0f}")
    b.metric("Illustrative hardness index", f"{hardness:.0f}")
    c.metric("Illustrative ductility index", f"{ductility:.1f}")
    st.info("These indices are generated from deliberately simplified equations to demonstrate sliders, variables, and functions in Python. They are not calibrated engineering property values.")
    st.subheader("🧩 Alloy design puzzle")
    target = st.selectbox("Your design goal", ["Balance strength and ductility", "Prioritize hardness", "Prioritize ductility"])
    if target == "Balance strength and ductility":
        correct = (0.25 <= carbon <= 0.60) and processing != "Quenched (illustrative trend)"
        hint = "Try a moderate carbon content and an annealed or normalized condition."
    elif target == "Prioritize hardness":
        correct = carbon >= 0.65 and processing == "Quenched (illustrative trend)"
        hint = "Higher carbon and a quench can increase hardness in this simplified model, but real steel may require tempering."
    else:
        correct = carbon <= 0.30 and processing == "Annealed"
        hint = "Lower carbon and annealing are a reasonable qualitative choice for ductility."
    if st.button("Evaluate my alloy", key="alloy_check"):
        if correct:
            st.success("Good design choice! Explain the trade-off: increasing hardness/strength often reduces ductility.")
            award("alloy_puzzle", 100)
        else:
            st.warning("Not the best match for this simplified puzzle. " + hint)
    st.markdown(f"**Status:** {status('alloy_puzzle')}")
    chart_df = pd.DataFrame({
        "Carbon content (wt. %)": np.round(np.arange(0.05, 1.21, 0.05), 2),
    })
    chart_df["Illustrative strength index"] = 300 + 420 * chart_df["Carbon content (wt. %)"]
    chart_df["Illustrative ductility index"] = 35 - 22 * chart_df["Carbon content (wt. %)"]
    st.line_chart(chart_df.set_index("Carbon content (wt. %)"))

# ---------- Heat Treatment ----------
with tabs[2]:
    st.header("🔥 Heat Treatment Challenge")
    st.write("Choose a heat-treatment route based on the intended outcome. Actual schedules depend on alloy composition, section size, and specifications.")
    scenario = st.selectbox("Engineering scenario", [
        "A cold-worked steel part needs improved ductility and reduced residual stress.",
        "A steel component needs a refined, more uniform microstructure after heating.",
        "A steel part needs very high hardness, and a later step can reduce brittleness.",
        "A hardened steel component is too brittle and needs improved toughness."
    ])
    answer_map = {
        "A cold-worked steel part needs improved ductility and reduced residual stress.": ("Annealing", "Annealing can soften the material and relieve stresses; the exact cycle depends on the steel."),
        "A steel component needs a refined, more uniform microstructure after heating.": ("Normalizing", "Normalizing uses heating followed by air cooling and is commonly used to refine/standardize the structure."),
        "A steel part needs very high hardness, and a later step can reduce brittleness.": ("Quenching", "Quenching can form hard martensite in suitable steels, but it can also create high stresses and brittleness."),
        "A hardened steel component is too brittle and needs improved toughness.": ("Tempering", "Tempering after hardening generally reduces brittleness and improves toughness, usually with some hardness reduction.")
    }
    choice = st.radio("Select the best matching process", ["Annealing", "Normalizing", "Quenching", "Tempering"], horizontal=True, key="heat_choice")
    if st.button("Check heat-treatment choice", key="heat_check"):
        correct, explanation = answer_map[scenario]
        if choice == correct:
            st.success(f"Correct — {correct}. {explanation}")
            award("heat_puzzle", 100)
        else:
            st.error(f"Not quite. Best answer: {correct}. {explanation}")
    st.markdown(f"**Status:** {status('heat_puzzle')}")
    with st.expander("Quick reference: what each process generally does"):
        st.markdown("""
        - **Annealing:** softens many steels, improves ductility, and can relieve stress.
        - **Normalizing:** heating followed by air cooling; often refines grain structure and improves uniformity.
        - **Quenching:** rapid cooling from a suitable temperature; may produce martensite and high hardness in hardenable steels.
        - **Tempering:** reheating quenched steel below the critical range to improve toughness and reduce brittleness.

        These are general teaching descriptions, not treatment instructions for a specific component.
        """)

# ---------- Debugging ----------
with tabs[3]:
    st.header("🐛 Materials Debugging Lab")
    st.write("A junior engineer wrote code to calculate stress, but the program contains a bug. Find the correct Python expression.")
    st.code("""force = 12000       # N
area = 60           # mm^2

stress = force * area
print(stress)""", language="python")
    fix = st.radio("Which line correctly calculates engineering stress?", [
        "stress = force * area",
        "stress = force / area",
        "stress = area / force",
        "stress = force + area"
    ], key="debug_choice")
    if st.button("Run repaired code", key="debug_check"):
        if fix == "stress = force / area":
            st.success("Bug fixed! Stress = 12000 / 60 = 200 MPa, because N/mm² is equivalent to MPa.")
            st.code("force = 12000\narea = 60\nstress = force / area\nprint(stress)  # 200.0 MPa", language="python")
            award("debug_puzzle", 100)
        else:
            st.error("Not yet. Stress is force divided by the original cross-sectional area.")
    st.markdown(f"**Status:** {status('debug_puzzle')}")
    st.subheader("Bonus: write your own answer")
    user_code = st.text_area("Write a Python function to calculate strain (extension / original length):", value="def calculate_strain(extension, original_length):\n    return extension / original_length", height=120)
    if st.button("Show expected output", key="debug_bonus"):
        st.code("extension = 0.5\noriginal_length = 50\nstrain = extension / original_length\nprint(strain)  # 0.01", language="python")
        st.caption("Compare your function with the example. This bonus does not execute arbitrary submitted code.")

st.divider()
st.markdown("**Project note:** This is a teaching prototype. Simulator values and sample graphs are illustrative; verify all scientific assumptions before using them for real engineering decisions.")
st.caption("BioMat CodeLab • Materials Science module")
