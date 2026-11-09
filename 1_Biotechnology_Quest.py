import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
from progress_store import get_progress, award_xp

# Centered layout with responsive container
# ==========================================
# CLEAN, HIGH-CONTRAST & READABLE STYLING
# ==========================================
st.markdown("""
<style>
/* Center the main container cleanly */
.block-container {
    max-width: 840px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    margin: auto;
}

/* Crisp, clean, readable modern background */
.stApp {
    background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%);
    color: #0F172A;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Primary text readability enhancements */
h1, h2, h3, h4, p, span, label {
    color: #0F172A !important;
}

/* High-contrast solid white cards for question modules */
div[data-testid="stVerticalBlock"] > div:has(div.stRadio),
div[data-testid="stVerticalBlock"] > div:has(div.stTextInput),
div[data-testid="stVerticalBlock"] > div:has(div.stSelectbox) {
    background: #FFFFFF !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06) !important;
    margin-bottom: 20px !important;
}

/* Vibrant blue action buttons with high contrast text */
.stButton > button {
    background: linear-gradient(135deg, #0284C7 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 10px 24px !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
    transition: all 0.2s ease-in-out !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
}

/* Styled radio options */
div[role="radiogroup"] > label {
    background: #F8FAFC !important;
    padding: 12px 18px !important;
    border-radius: 10px !important;
    border: 1.5px solid #CBD5E1 !important;
    margin-bottom: 8px !important;
    transition: all 0.2s !important;
}

div[role="radiogroup"] > label:hover {
    border-color: #2563EB !important;
    background: #EFF6FF !important;
}

div[role="radiogroup"] > label p {
    color: #0F172A !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
}

/* Flowchart & step card styling */
.puzzle-card {
    background: #EFF6FF;
    border: 1.5px solid #BFDBFE;
    padding: 14px 18px;
    border-radius: 12px;
    margin-bottom: 12px;
}

.puzzle-title {
    font-weight: 700;
    color: #1E40AF !important;
    font-size: 1rem;
    margin-bottom: 4px;
}

/* Sidebar styling: light, crisp, high contrast */
section[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}

/* Improve readability of dark question/code panels: use bright green text.
   This targets Streamlit code blocks without changing the rest of the theme. */
div[data-testid="stCode"] pre,
div[data-testid="stCode"] code,
div[data-testid="stCode"] pre span,
.stCode pre,
.stCode code {
    color: #7CFC98 !important;
}

/* Streamlit syntax highlighting uses token spans; override blue token colours too. */
div[data-testid="stCode"] pre span,
div[data-testid="stCode"] code span,
div[data-testid="stCode"] .token,
div[data-testid="stCode"] [class*="token"] {
    color: #7CFC98 !important;
}

/* Keep code/question panel dark while improving contrast. */
div[data-testid="stCode"] pre {
    background-color: #17212B !important;
    border: 1px solid #355044 !important;
    border-radius: 10px !important;
}

/* Input fields styling */
.stTextInput input, .stSelectbox [data-baseweb="select"] {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
}
</style>
""", unsafe_allow_html=True)

# Image paths (strictly using the 4 provided biological images)
IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
IMG_DNA_PLATE = os.path.join(IMG_DIR, "dna_plate_analysis.png")
IMG_DNA_HELIX = os.path.join(IMG_DIR, "dna_double_helix.jpg")
IMG_MICROPIPETTE = os.path.join(IMG_DIR, "enzyme_micropipette.jpg")
IMG_PETRI_DISH = os.path.join(IMG_DIR, "petri_cell_culture.jpg")

# Shared student profile is required for persistent progress.
if not st.session_state.get("student_id"):
    st.warning("Please create/load your student profile on the BioMat CodeLab homepage first.")
    st.stop()

# Session state initialization
if "q_num" not in st.session_state:
    st.session_state.q_num = 1
if "score" not in st.session_state:
    st.session_state.score = 0
if "badges" not in st.session_state:
    st.session_state.badges = []
if "solved_qs" not in st.session_state:
    st.session_state.solved_qs = set()
if "attempts" not in st.session_state:
    st.session_state.attempts = {}
if "feedback" not in st.session_state:
    st.session_state.feedback = {}
if "dna_input" not in st.session_state:
    st.session_state.dna_input = "GAATTCATGCGATCGCTTGA"

# Restore saved Biotechnology completions and XP from the shared database.
_saved_bio = get_progress(st.session_state.student_id)
st.session_state.solved_qs = {int(q) for q in _saved_bio["tasks"]["biotechnology"]}
st.session_state.score = _saved_bio["mission_xp"]["biotechnology"]

def add_score(q_id, pts, badge_name):
    if q_id not in st.session_state.solved_qs:
        st.session_state.solved_qs.add(q_id)
        award_xp(st.session_state.student_id, "biotechnology", str(q_id), pts)
        st.session_state.score = get_progress(st.session_state.student_id)["mission_xp"]["biotechnology"]
        if badge_name not in st.session_state.badges:
            st.session_state.badges.append(badge_name)
        st.toast(f"🎉 Correct! +{pts} XP & Unlocked Badge: {badge_name}", icon="⭐")

def evaluate_answer(q_id, is_correct, pts, badge, hint_msg, right_answer_msg, success_msg="Correct! Excellent work."):
    if is_correct:
        st.session_state.attempts[q_id] = 0
        st.session_state.feedback[q_id] = ("success", f"🎉 **{success_msg}**")
        add_score(q_id, pts, badge)
    else:
        st.session_state.attempts[q_id] = st.session_state.attempts.get(q_id, 0) + 1
        if st.session_state.attempts[q_id] == 1:
            st.session_state.feedback[q_id] = ("hint", f"💡 **Hint:** {hint_msg}\n\n*Please recheck your answer and give it another try!*")
        else:
            st.session_state.feedback[q_id] = ("answer", f"❌ **Second Try Failed.**\n\n**Right Answer:**\n{right_answer_msg}")

def render_feedback(q_id):
    if q_id in st.session_state.feedback:
        status, msg = st.session_state.feedback[q_id]
        if status == "success":
            st.success(msg)
        elif status == "hint":
            st.warning(msg)
        elif status == "answer":
            st.error(msg)

def go_next():
    if st.session_state.q_num < 40:
        st.session_state.q_num += 1

def go_prev():
    if st.session_state.q_num > 1:
        st.session_state.q_num -= 1

def reset_all():
    # Restart navigation/feedback without deleting the student's saved achievements.
    st.session_state.q_num = 1
    st.session_state.attempts = {}
    st.session_state.feedback = {}
    saved = get_progress(st.session_state.student_id)
    st.session_state.solved_qs = {int(q) for q in saved["tasks"]["biotechnology"]}
    st.session_state.score = saved["mission_xp"]["biotechnology"]
    st.rerun()

# Sidebar navigation & stats
with st.sidebar:
    if os.path.exists(IMG_DNA_HELIX):
        st.image(IMG_DNA_HELIX, caption="Watson-Crick DNA Helix", use_container_width=True)
    st.title("⚡ Lab Notebook")
    st.metric("XP Energy", f"{st.session_state.score} / 400 pts")
    st.write(f"**Solved:** {len(st.session_state.solved_qs)} / 40 Quests")
    st.progress(len(st.session_state.solved_qs) / 40)

    # Level indicator
    if st.session_state.q_num <= 20:
        curr_lvl = "Level 1: Foundations"
    elif st.session_state.q_num <= 30:
        curr_lvl = "Level 2: Intermediate Data Science"
    else:
        curr_lvl = "Level 3: Advanced Bioprocess Modeling"
    st.info(f"**Current Level:** {curr_lvl}")

    st.write("---")
    st.write("🏆 **Unlocked Badges:**")
    if len(st.session_state.badges) == 0:
        st.caption("None yet. Solve quests to earn badges!")
    else:
        for item in st.session_state.badges:
            st.markdown(f"✨ **{item}**")

    st.write("---")
    pick_q = st.selectbox("⚡ Jump to Question:", list(range(1, 41)), index=st.session_state.q_num - 1)
    if pick_q != st.session_state.q_num:
        st.session_state.q_num = pick_q
        st.rerun()

# Main header
st.title("🧬 Bio-Python Quest Lab")
st.caption("Comprehensive 40-Quest Curriculum: Foundations, Intermediate Data Science & Advanced Bioprocess Modeling")

user_dna = st.text_input("Enter DNA Sequence (A, T, G, C only):", value=st.session_state.dna_input).upper().strip()

# Validation
is_valid = True
if len(user_dna) < 6:
    is_valid = False
else:
    for base in user_dna:
        if base not in "ATGC":
            is_valid = False
            break

if not is_valid:
    st.error("Please enter at least 6 letters using only canonical bases: A, T, G, and C.")
    st.stop()
else:
    st.session_state.dna_input = user_dna

dna = st.session_state.dna_input
total_bp = len(dna)

st.write("---")
col_a, col_b, col_c = st.columns(3)
col_a.metric("Active Strand", f"{dna[:10]}..." if len(dna) > 10 else dna)
col_b.metric("Length", f"{total_bp} bp")
col_c.metric("Mission Progress", f"Stage {st.session_state.q_num} / 40")
st.progress(st.session_state.q_num / 40)
st.write("---")

# ==============================================================================
# LEVEL 1: FOUNDATIONS (QUESTIONS 1 - 20)
# ==============================================================================

# QUESTION 1
if st.session_state.q_num == 1:
    st.subheader("Question 1: The Assignment Puzzle [Fill-in-the-Blank]")
    if os.path.exists(IMG_DNA_HELIX):
        st.image(IMG_DNA_HELIX, caption="DNA Double Helix Molecular Chain", use_container_width=True)
    st.write(f"In your laboratory script, you want to store `{dna}` into a variable named `dna_seq`.")
    st.code(f"""dna_seq ___ "{dna}" """, language="python")
    op = st.selectbox("Select the missing Python assignment operator:", ["Select...", "==", "=", "->", ":="], key="q1_op")
    if st.button("Check Puzzle", key="btn1"):
        evaluate_answer(
            q_id=1, is_correct=(op == "="), pts=10, badge="Variable Beginner",
            hint_msg="In Python, assigning data to a variable uses a single character, whereas '==' tests equality.",
            right_answer_msg="Use a single equals sign: `dna = '...'` to assign the string to the variable name.",
            success_msg="A single `=` assigns a value to a variable name."
        )
    render_feedback(1)

# QUESTION 2
elif st.session_state.q_num == 2:
    st.subheader("Question 2: Match the Function to Its Return Type [Match the Following]")
    st.write("Match each built-in sequence operation to the data type it returns:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. `len('ATGC')`**")
        m1 = st.selectbox("Return type for len():", ["Select...", "Integer (int)", "Float (float)", "String (str)", "Boolean (bool)"], key="m_q2_1")
        st.markdown("**2. `'ATGC'.count('A')`**")
        m2 = st.selectbox("Return type for .count():", ["Select...", "Integer (int)", "Float (float)", "String (str)", "Boolean (bool)"], key="m_q2_2")
    with c2:
        st.markdown("**3. `'GAATTC' in 'ATGC'`**")
        m3 = st.selectbox("Return type for 'in':", ["Select...", "Integer (int)", "Float (float)", "String (str)", "Boolean (bool)"], key="m_q2_3")
        st.markdown("**4. `'atgc'.upper()`**")
        m4 = st.selectbox("Return type for .upper():", ["Select...", "Integer (int)", "Float (float)", "String (str)", "Boolean (bool)"], key="m_q2_4")
    if st.button("Check Matches", key="btn2"):
        is_corr = (m1 == "Integer (int)" and m2 == "Integer (int)" and m3 == "Boolean (bool)" and m4 == "String (str)")
        evaluate_answer(
            q_id=2, is_correct=is_corr, pts=10, badge="Type Detective",
            hint_msg="`len()` and `.count()` return whole numbers; `'in'` checks truth or falsehood; `.upper()` outputs text.",
            right_answer_msg="1. `len()` ➔ Integer (int)\n2. `.count()` ➔ Integer (int)\n3. `'in'` ➔ Boolean (bool)\n4. `.upper()` ➔ String (str)",
            success_msg="All matched correctly! `len()` & `.count()` return `int`, `'in'` returns `bool`, and `.upper()` returns `str`."
        )
    render_feedback(2)

# QUESTION 3
elif st.session_state.q_num == 3:
    st.subheader("Question 3: Assemble the Adapter Ligation Code [Reordering]")
    st.write(f"Reorder the 3 code fragments below to create a full line that appends an `'AAA'` poly-A tail to variable `strand = '{dna}'`:")
    st.markdown("<div class='puzzle-card'><div class='puzzle-title'>Target Goal:</div><code>tagged_dna = strand + 'AAA'</code></div>", unsafe_allow_html=True)
    r1 = st.selectbox("Fragment 1 (Left hand):", ["Select...", "tagged_dna =", "+ 'AAA'", "strand"], key="r3_1")
    r2 = st.selectbox("Fragment 2 (Middle):", ["Select...", "tagged_dna =", "+ 'AAA'", "strand"], key="r3_2")
    r3 = st.selectbox("Fragment 3 (Right hand):", ["Select...", "tagged_dna =", "+ 'AAA'", "strand"], key="r3_3")
    if st.button("Verify Order", key="btn3"):
        is_corr = (r1 == "tagged_dna =" and r2 == "strand" and r3 == "+ 'AAA'")
        evaluate_answer(
            q_id=3, is_correct=is_corr, pts=10, badge="Strand Gluer",
            hint_msg="Start with the assignment target (`tagged_dna =`), follow with the existing sequence (`strand`), and attach the tag (`+ 'AAA'`).",
            right_answer_msg="`tagged_dna =` ➔ `strand` ➔ `+ 'AAA'` (Forming: `tagged_dna = strand + 'AAA'`).",
            success_msg=f"Correct assembly! Expression: `{dna + 'AAA'}`."
        )
    render_feedback(3)

# QUESTION 4
elif st.session_state.q_num == 4:
    st.subheader("Question 4: Spot the String Bug [Bug Hunter Puzzle]")
    st.write("A bioinformatician wrote this buggy line to clean an incoming DNA read:")
    st.code("clean_seq = raw_read.Strip().Upper()", language="python")
    st.write("Why will Python raise an `AttributeError` on this code?")
    ans = st.radio("Choose the diagnosis:", [
        "Python method names are case-sensitive: it must be `.strip()` and `.upper()` in lowercase.",
        "Strings cannot chain two methods together on the same line.",
        "You cannot use `.strip()` on strings containing letters."
    ], key="q4")
    if st.button("Check Bug Diagnosis", key="btn4"):
        is_corr = ans.startswith("Python method names are case-sensitive")
        evaluate_answer(
            q_id=4, is_correct=is_corr, pts=10, badge="Bug Hunter",
            hint_msg="Notice the capitalization of `.Strip()` and `.Upper()`. Python treats capitalized names differently from lowercase.",
            right_answer_msg="Python method names are case-sensitive: built-in methods must be strictly lowercase (`.strip().upper()`).",
            success_msg="Built-in methods are strictly lowercase: `.strip().upper()`."
        )
    render_feedback(4)

# QUESTION 5
elif st.session_state.q_num == 5:
    st.subheader("Question 5: Nucleotide Counting [One-Word]")
    st.write(f"In your DNA strand `{dna}`, count the occurrences of Cytosine ('C').")
    st.code(f"""c_count = "{dna}".______('C')""", language="python")
    ans = st.text_input("Enter the missing method name (One word, e.g. find):", key="q5").strip().lower()
    if st.button("Check Answer", key="btn5"):
        is_corr = ans in ["count", ".count()", "count()"]
        evaluate_answer(
            q_id=5, is_correct=is_corr, pts=10, badge="Base Counter",
            hint_msg="Think of the standard 5-letter English word for tallying items: starts with 'c' and ends with 't'.",
            right_answer_msg="The string method is `count` (e.g., `dna.count('C')`).",
            success_msg=f"`.count()` found {dna.count('C')} Cytosine bases."
        )
    render_feedback(5)

# QUESTION 6
elif st.session_state.q_num == 6:
    st.subheader("Question 6: Base Pair Sum Puzzle [Fill-in-the-Blank]")
    st.write(f"Strand: `{dna}`")
    st.write("Complete the expression to sum Guanines and Cytosines:")
    st.code(f"""gc_sum = "{dna}".count('G') ___ "{dna}".count('C')""", language="python")
    op6 = st.selectbox("Choose the operator:", ["Select...", "+", "-", "*", "&"], key="q6")
    if st.button("Check Operator", key="btn6"):
        is_corr = (op6 == "+")
        total_gc = dna.count('G') + dna.count('C')
        evaluate_answer(
            q_id=6, is_correct=is_corr, pts=10, badge="Sum Expert",
            hint_msg="You want the total sum of G and C counts. Which basic mathematical symbol performs numerical addition?",
            right_answer_msg="Use the addition symbol `+`: `dna.count('G') + dna.count('C')`.",
            success_msg=f"`+` adds the integer base counts together (Total: {total_gc} bases)."
        )
    render_feedback(6)

# QUESTION 7
elif st.session_state.q_num == 7:
    st.subheader("Question 7: GC-Content Precedence [Equating & Ordering]")
    if os.path.exists(IMG_DNA_PLATE):
        st.image(IMG_DNA_PLATE, caption="Nucleotide Base Stacking & Thermal Stability", use_container_width=True)
    st.write("Which expression calculates GC percentage without mathematical precedence errors?")
    ans = st.radio("Choose the correctly bracketed equation:", [
        f"gc = '{dna}'.count('G') + '{dna}'.count('C') / len('{dna}') * 100",
        f"gc = (('{dna}'.count('G') + '{dna}'.count('C')) / len('{dna}')) * 100",
        f"gc = len('{dna}') / ('{dna}'.count('G') + '{dna}'.count('C')) * 100"
    ], key="q7")
    if st.button("Check Answer", key="btn7"):
        is_corr = ans.startswith(f"gc = (('{dna}'.count('G')")
        gc_val = ((dna.count('G') + dna.count('C')) / len(dna)) * 100
        evaluate_answer(
            q_id=7, is_correct=is_corr, pts=10, badge="Math Whiz",
            hint_msg="Division runs before addition unless you group `(G + C)` with parentheses first.",
            right_answer_msg="`gc = ((dna.count('G') + dna.count('C')) / len(dna)) * 100`.",
            success_msg=f"Parentheses ensure addition happens first before division. GC% = {round(gc_val, 1)}%."
        )
    render_feedback(7)

# QUESTION 8
elif st.session_state.q_num == 8:
    st.subheader("Question 8: Exponential Doubling Symbol [One-Word / Symbol]")
    st.write(r"In bacterial growth modeling ($N = N_0 	imes 2^n$), doubling relies on exponentiation.")
    st.code("final_cells = n0 * (2 __ generations)", language="python")
    sym = st.text_input("Enter the exact Python exponent operator symbol (e.g. ^ or **):", key="q8").strip()
    if st.button("Check Symbol", key="btn8"):
        is_corr = (sym == "**")
        evaluate_answer(
            q_id=8, is_correct=is_corr, pts=10, badge="Exponent Master",
            hint_msg="Multiplication is `*`. Doubling that symbol gives Python's power operator.",
            right_answer_msg="The exponent symbol in Python is two asterisks: `**` (e.g., `2 ** generations`).",
            success_msg="`**` is Python's exponentiation operator (e.g. `2 ** 3 = 8`)."
        )
    render_feedback(8)

# QUESTION 9
elif st.session_state.q_num == 9:
    st.subheader("Question 9: First Base Extraction [Indexing Puzzle]")
    st.write(f"Active Strand: `{dna}`")
    st.write("In Python, sequence indices begin at 0.")
    st.code(f"""first_nuc = "{dna}"[___]""", language="python")
    idx_ans = st.text_input("Enter the single index digit needed to get the very first nucleotide:", key="q9").strip()
    if st.button("Verify Index", key="btn9"):
        is_corr = (idx_ans == "0")
        evaluate_answer(
            q_id=9, is_correct=is_corr, pts=10, badge="Index Detective",
            hint_msg="Python sequences start at index 0.",
            right_answer_msg="The first index is `0` (e.g., `dna[0]`).",
            success_msg=f"Index `[0]` retrieves the first base: `{dna[0]}`."
        )
    render_feedback(9)

# QUESTION 10
elif st.session_state.q_num == 10:
    st.subheader("Question 10: Codon Reading Window [Slicing Puzzle]")
    st.write(f"Active Strand: `{dna}`")
    st.write("We want to slice the first 3 nucleotides (`[0, 1, 2]`) to form the starting codon.")
    st.code(f"""start_codon = "{dna}"[0:___]""", language="python")
    stop_val = st.text_input("What is the stop index in `[0:stop]`? (Remember the stop index is excluded):", key="q10").strip()
    if st.button("Check Slice Bound", key="btn10"):
        is_corr = (stop_val == "3")
        evaluate_answer(
            q_id=10, is_correct=is_corr, pts=10, badge="Slicer",
            hint_msg="Slicing `[start:stop]` stops right before the stop index. To include index 2, the stop must be 3.",
            right_answer_msg="The stop index must be `3` (e.g., `dna[0:3]` includes indices 0, 1, and 2).",
            success_msg=f"Slicing `[0:3]` extracts bases 0, 1, and 2: `{dna[0:3]}`."
        )
    render_feedback(10)

# QUESTION 11
elif st.session_state.q_num == 11:
    st.subheader("Question 11: Antiparallel Reverse Slicing [Code Puzzle]")
    st.write(f"Strand: `{dna}`")
    st.write("How do we step backwards through a string in Python?")
    st.code(f"""reversed_strand = "{dna}"[::___]""", language="python")
    step_ans = st.text_input("Enter the step value to invert the string (e.g. -1):", key="q11").strip()
    if st.button("Test Step Value", key="btn11"):
        is_corr = (step_ans == "-1")
        evaluate_answer(
            q_id=11, is_correct=is_corr, pts=10, badge="Reverse Slicer",
            hint_msg="To move backwards one character at a time, use a negative step of 1.",
            right_answer_msg="The step value is `-1` inside `[::-1]`.",
            success_msg=f"Slicing with `[::-1]` steps backwards through the string: `{dna[::-1]}`."
        )
    render_feedback(11)

# QUESTION 12
elif st.session_state.q_num == 12:
    st.subheader("Question 12: Match Conditionals to Thresholds [Match the Following]")
    st.write("Match each conditional comparison symbol to its biological logic:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. `gc_pct >= 50`**")
        m12_1 = st.selectbox("Meaning of >= :", ["Select...", "At least 50% (threshold met or exceeded)", "Strictly below 50%", "Exactly 50% check"], key="m12_1")
        st.markdown("**2. `gc_pct < 50`**")
        m12_2 = st.selectbox("Meaning of < :", ["Select...", "At least 50% (threshold met or exceeded)", "Strictly below 50%", "Exactly 50% check"], key="m12_2")
    with c2:
        st.markdown("**3. `gc_pct == 50`**")
        m12_3 = st.selectbox("Meaning of == :", ["Select...", "At least 50% (threshold met or exceeded)", "Strictly below 50%", "Exactly 50% check"], key="m12_3")
    if st.button("Check Condition Matches", key="btn12"):
        is_corr = (m12_1 == "At least 50% (threshold met or exceeded)" and m12_2 == "Strictly below 50%" and m12_3 == "Exactly 50% check")
        evaluate_answer(
            q_id=12, is_correct=is_corr, pts=10, badge="Logic Builder",
            hint_msg="`>=` means greater than or equal to, `<` means strictly less than, and `==` checks for exact equality.",
            right_answer_msg="1. `>=` ➔ At least 50%\n2. `<` ➔ Strictly below 50%\n3. `==` ➔ Exactly 50% check",
            success_msg="All matched correctly! `>=` is greater-or-equal, `<` is less-than, and `==` checks exact equality."
        )
    render_feedback(12)

# QUESTION 13
elif st.session_state.q_num == 13:
    st.subheader("Question 13: Restriction Enzyme Search [One-Word]")
    if os.path.exists(IMG_MICROPIPETTE):
        st.image(IMG_MICROPIPETTE, caption="Enzyme Digestion Assay Preparation", use_container_width=True)
    st.write(f"Strand: `{dna}`")
    st.write("Check if EcoRI motif (`'GAATTC'`) is present in the plasmid sequence:")
    st.code("""if "GAATTC" _____ dna_sequence:\n    print("Cleavage site found!")""", language="python")
    ans13 = st.text_input("Enter the 2-letter Python membership operator (One word):", key="q13").strip().lower()
    if st.button("Check Operator", key="btn13"):
        is_corr = (ans13 == "in")
        found = "GAATTC" in dna
        evaluate_answer(
            q_id=13, is_correct=is_corr, pts=10, badge="Motif Scout",
            hint_msg="Think of the 2-letter English preposition used in membership checks: `if motif __ sequence:`.",
            right_answer_msg="The keyword is `in`.",
            success_msg=f"`in` checks substring presence. Cleavage site in your strand: **{found}**."
        )
    render_feedback(13)

# QUESTION 14
elif st.session_state.q_num == 14:
    st.subheader("Question 14: Locate Cut Site Coordinate [Method Puzzle]")
    st.write("Which method returns the starting 0-based integer index of a motif, or -1 if absent?")
    ans = st.radio("Choose the method:", [
        f"cut_pos = '{dna}'.find('GAATTC')",
        f"cut_pos = '{dna}'.index_of('GAATTC')",
        f"cut_pos = locate('{dna}', 'GAATTC')"
    ], key="q14")
    if st.button("Check Answer", key="btn14"):
        is_corr = ans.startswith(f"cut_pos = '{dna}'.find")
        idx = dna.find("GAATTC")
        evaluate_answer(
            q_id=14, is_correct=is_corr, pts=10, badge="Coordinate Finder",
            hint_msg="Which string method starts with 'f' and returns the index position of the substring?",
            right_answer_msg="Use `.find('GAATTC')` (e.g. `cut_pos = dna.find('GAATTC')`).",
            success_msg=f"`.find()` returns the starting index: {idx}."
        )
    render_feedback(14)

# QUESTION 15
elif st.session_state.q_num == 15:
    st.subheader("Question 15: Watson-Crick Base Pairing [Match the Columns]")
    if os.path.exists(IMG_DNA_HELIX):
        st.image(IMG_DNA_HELIX, caption="Watson-Crick Nitrogenous Base Pairs", use_container_width=True)
    st.write("Map each DNA nitrogenous base to its complementary partner in a Python Dictionary:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Base: Adenine (A)**")
        m1 = st.selectbox("Complementary partner for 'A':", ["Select...", "Cytosine (C)", "Thymine (T)", "Guanine (G)"], key="m15_1")
        st.markdown("**Base: Thymine (T)**")
        m2 = st.selectbox("Complementary partner for 'T':", ["Select...", "Adenine (A)", "Cytosine (C)", "Guanine (G)"], key="m15_2")
    with col2:
        st.markdown("**Base: Guanine (G)**")
        m3 = st.selectbox("Complementary partner for 'G':", ["Select...", "Adenine (A)", "Cytosine (C)", "Thymine (T)"], key="m15_3")
        st.markdown("**Base: Cytosine (C)**")
        m4 = st.selectbox("Complementary partner for 'C':", ["Select...", "Adenine (A)", "Guanine (G)", "Thymine (T)"], key="m15_4")
    if st.button("Check Watson-Crick Pairs", key="btn15"):
        is_corr = (m1 == "Thymine (T)" and m2 == "Adenine (A)" and m3 == "Cytosine (C)" and m4 == "Guanine (G)")
        evaluate_answer(
            q_id=15, is_correct=is_corr, pts=10, badge="Dictionary Matcher",
            hint_msg="Watson-Crick pairing: Adenine pairs with Thymine (A:T), and Guanine pairs with Cytosine (G:C).",
            right_answer_msg="A pairs with T, T pairs with A, G pairs with C, and C pairs with G.",
            success_msg="All pairs matched! Watson-Crick rule: A:T and G:C."
        )
    render_feedback(15)

# QUESTION 16
elif st.session_state.q_num == 16:
    st.subheader("Question 16: Central Dogma Pipeline [Flowchart Reordering]")
    st.write("Reorder the algorithmic execution steps of transcribing and translating a sequence in Python:")
    st.markdown("<div class='flowchart-step'>[Stage 1] ➔ [Stage 2] ➔ [Stage 3]</div>", unsafe_allow_html=True)
    s1 = st.selectbox("Stage 1:", ["Select...", "Read user DNA input sequence", "Transcribe T -> U into mRNA", "Translate codons using dictionary"], key="s16_1")
    s2 = st.selectbox("Stage 2:", ["Select...", "Read user DNA input sequence", "Transcribe T -> U into mRNA", "Translate codons using dictionary"], key="s16_2")
    s3 = st.selectbox("Stage 3:", ["Select...", "Read user DNA input sequence", "Transcribe T -> U into mRNA", "Translate codons using dictionary"], key="s16_3")
    if st.button("Verify Pipeline Order", key="btn16"):
        is_corr = (s1 == "Read user DNA input sequence" and s2 == "Transcribe T -> U into mRNA" and s3 == "Translate codons using dictionary")
        evaluate_answer(
            q_id=16, is_correct=is_corr, pts=10, badge="Flowchart Architect",
            hint_msg="Begin with raw DNA sequence input, transcribe it into mRNA, then translate codons to amino acids.",
            right_answer_msg="Stage 1: Read user DNA input sequence ➔ Stage 2: Transcribe T -> U into mRNA ➔ Stage 3: Translate codons using dictionary.",
            success_msg="Biological data pipeline ordered properly: DNA Input ➔ mRNA Transcription ➔ Peptide Translation."
        )
    render_feedback(16)

# QUESTION 17
elif st.session_state.q_num == 17:
    st.subheader("Question 17: Bacterial Doubling Simulation (While Loop)")
    if os.path.exists(IMG_PETRI_DISH):
        st.image(IMG_PETRI_DISH, caption="Microbial Colony Formation on Agar Plates", use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        n0 = st.number_input("Starting Inoculum (N0 cells):", min_value=10, value=100, step=50)
    with c2:
        target_cells = st.number_input("Target Population:", min_value=200, value=1600, step=200)
    cur, elapsed = n0, 0
    t_hist, p_hist = [0], [n0]
    while cur < target_cells:
        cur *= 2
        elapsed += 20
        t_hist.append(elapsed)
        p_hist.append(cur)
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.plot(t_hist, p_hist, 'ro-', linewidth=2)
    ax.set_xlabel("Time (mins)")
    ax.set_ylabel("Cell Population")
    ax.set_title("Bacterial Exponential Doubling Curve")
    ax.grid(True, linestyle=":")
    st.pyplot(fig)
    ans = st.radio("When does the `while cells < target:` loop stop executing?", [
        "When cells < target evaluates to False",
        "When cells < target evaluates to True",
        "After exactly 10 iterations"
    ], key="q17")
    if st.button("Check Loop Logic", key="btn17"):
        is_corr = (ans == "When cells < target evaluates to False")
        evaluate_answer(
            q_id=17, is_correct=is_corr, pts=10, badge="Loop Master",
            hint_msg="A while-loop executes repeatedly while its condition is True. It stops once the condition is no longer met.",
            right_answer_msg="The loop stops when the condition `cells < target` evaluates to `False`.",
            success_msg=f"Loop stops once population reaches or exceeds target ({cur} cells in {elapsed} mins)."
        )
    render_feedback(17)

# QUESTION 18
elif st.session_state.q_num == 18:
    st.subheader("Question 18: Assemble a Codon Reading Loop [Reordering Puzzle]")
    mrna_str = dna.replace("T", "U")
    st.write(f"mRNA: `{mrna_str}`")
    st.write("Reorder the 3 lines of code to form a functional Python loop that slices 3-letter codons:")
    p1 = st.selectbox("Line 1 (Loop Header):", ["Select...", "print(codon)", "for i in range(0, len(mrna), 3):", "codon = mrna[i:i+3]"], key="r18_1")
    p2 = st.selectbox("Line 2 (Slicing):", ["Select...", "print(codon)", "for i in range(0, len(mrna), 3):", "codon = mrna[i:i+3]"], key="r18_2")
    p3 = st.selectbox("Line 3 (Print Output):", ["Select...", "print(codon)", "for i in range(0, len(mrna), 3):", "codon = mrna[i:i+3]"], key="r18_3")
    if st.button("Check Loop Assembly", key="btn18"):
        is_corr = (p1 == "for i in range(0, len(mrna), 3):" and p2 == "codon = mrna[i:i+3]" and p3 == "print(codon)")
        evaluate_answer(
            q_id=18, is_correct=is_corr, pts=10, badge="Codon Looper",
            hint_msg="First write the `for` loop header stepping by 3, then extract the codon slice inside the loop body, then print it.",
            right_answer_msg="Line 1: `for i in range(0, len(mrna), 3):` ➔ Line 2: `codon = mrna[i:i+3]` ➔ Line 3: `print(codon)`.",
            success_msg="Correct loop assembly! `step=3` advances the frame by 3 bases each cycle."
        )
    render_feedback(18)

# QUESTION 19
elif st.session_state.q_num == 19:
    st.subheader("Question 19: Enzyme Kinetics & Function Output [One-Word]")
    if os.path.exists(IMG_MICROPIPETTE):
        st.image(IMG_MICROPIPETTE, caption="Substrate Titration & Reaction Velocity Assay", use_container_width=True)
    st.write(r"Michaelis-Menten: $V = \frac{V_{\max}[S]}{K_m + [S]}$, Double-Reciprocal: $\frac{1}{V} = \frac{K_m}{V_{\max}}\frac{1}{[S]} + \frac{1}{V_{\max}}$")
    vmax, km = 100.0, 15.0
    s_vals = [2.0, 5.0, 10.0, 25.0, 50.0, 100.0]
    inv_s = [1.0 / s for s in s_vals]
    inv_v = [(km + s) / (vmax * s) for s in s_vals]
    fig, ax = plt.subplots(figsize=(6, 2.5))
    ax.plot(inv_s, inv_v, 'bs-', linewidth=2)
    ax.set_xlabel("1/[S]")
    ax.set_ylabel("1/V")
    ax.set_title("Lineweaver-Burk Double Reciprocal Plot")
    ax.grid(True)
    st.pyplot(fig)
    st.code("""def calc_velocity(s, vmax=100.0, km=15.0):\n    v = (vmax * s) / (km + s)\n    ______ v""", language="python")
    ans19 = st.text_input("Enter the single Python keyword that sends the computed velocity value back from the function (One word):", key="q19").strip().lower()
    if st.button("Check Answer", key="btn19"):
        is_corr = (ans19 == "return")
        evaluate_answer(
            q_id=19, is_correct=is_corr, pts=10, badge="Enzyme Modeler",
            hint_msg="Think of the 6-letter keyword starting with 'r' used to send a value back from a function.",
            right_answer_msg="The keyword is `return`.",
            success_msg="`return` hands the computed numeric result back to the caller."
        )
    render_feedback(19)

# QUESTION 20
elif st.session_state.q_num == 20:
    st.subheader("Question 20: Build a Reusable Bio-Function [Reordering Puzzle]")
    st.write("Reorder the 3 lines to create a clean, reusable function that calculates GC content:")
    f1 = st.selectbox("Line 1 (Function Signature):", ["Select...", "return gc_percent", "def calculate_gc(seq):", "gc_percent = ((seq.count('G') + seq.count('C')) / len(seq)) * 100"], key="f20_1")
    f2 = st.selectbox("Line 2 (Formula Calculation):", ["Select...", "return gc_percent", "def calculate_gc(seq):", "gc_percent = ((seq.count('G') + seq.count('C')) / len(seq)) * 100"], key="f20_2")
    f3 = st.selectbox("Line 3 (Return Statement):", ["Select...", "return gc_percent", "def calculate_gc(seq):", "gc_percent = ((seq.count('G') + seq.count('C')) / len(seq)) * 100"], key="f20_3")
    if st.button("Verify Function Assembly", key="btn20"):
        is_corr = (f1 == "def calculate_gc(seq):" and f2 == "gc_percent = ((seq.count('G') + seq.count('C')) / len(seq)) * 100" and f3 == "return gc_percent")
        evaluate_answer(
            q_id=20, is_correct=is_corr, pts=10, badge="Function Builder",
            hint_msg="A Python function starts with `def ...:`, followed by calculation lines in the body, and ends with `return ...`.",
            right_answer_msg="Line 1: `def calculate_gc(seq):` ➔ Line 2: `gc_percent = ((seq.count('G') + seq.count('C')) / len(seq)) * 100` ➔ Line 3: `return gc_percent`.",
            success_msg="You assembled a full reusable Python function!"
        )
    render_feedback(20)

# ==============================================================================
# LEVEL 2: INTERMEDIATE DATA SCIENCE & ALGORITHMS (QUESTIONS 21 - 30)
# ==============================================================================

# QUESTION 21: LIST COMPREHENSIONS FOR OLIGONUCLEOTIDES
elif st.session_state.q_num == 21:
    st.subheader("Question 21: Filter Primer Lengths [List Comprehension Puzzle]")
    st.write("In PCR assay design, primers must be between 18 and 25 bp. Given `primers = ['ATGCGATCG', 'ATGCGATCGATCGATCGTAA', 'ATGC']`:")
    st.code("valid_primers = [p for p in primers if 18 <= len(p) <= 25]", language="python")
    ans21 = st.radio("What does this list comprehension produce?", [
        "A list containing only the primer strings whose length is between 18 and 25 bp inclusive.",
        "A list of boolean True/False flags of length equal to primers.",
        "An integer count of the total valid primers."
    ], key="q21")
    if st.button("Check Answer", key="btn21"):
        is_corr = ans21.startswith("A list containing only the primer strings")
        evaluate_answer(
            q_id=21, is_correct=is_corr, pts=10, badge="Comprehension Coder",
            hint_msg="`[item for item in list if condition]` extracts and keeps elements that satisfy the `if` test into a new list.",
            right_answer_msg="It filters the original list and returns a new list containing only matching primer strings.",
            success_msg="List comprehensions provide a concise way to filter and transform biological datasets."
        )
    render_feedback(21)

# QUESTION 22: PURINE VS PYRIMIDINE RATIO
elif st.session_state.q_num == 22:
    st.subheader("Question 22: Purine-to-Pyrimidine Ratio [Fill-in-the-Blank]")
    st.write(f"In your strand `{dna}`, Purines are A and G; Pyrimidines are C and T.")
    st.code("""purines = dna.count('A') + dna.count('G')\npyrimidines = dna.count('C') + dna.count('T')\nratio = purines ___ pyrimidines""", language="python")
    op22 = st.selectbox("Select the division operator to compute the ratio:", ["Select...", "/", "//", "%", "**"], key="q22")
    if st.button("Check Operator", key="btn22"):
        is_corr = (op22 == "/")
        evaluate_answer(
            q_id=22, is_correct=is_corr, pts=10, badge="Biochemical Analyst",
            hint_msg="We want a floating-point decimal ratio, not an integer floor (`//`) or remainder (`%`).",
            right_answer_msg="Use standard float division `/`.",
            success_msg="Float division `/` computes precise biochemical stoichiometric ratios."
        )
    render_feedback(22)

# QUESTION 23: DICTIONARY COMPREHENSION FOR AMINO ACID CHARGES
elif st.session_state.q_num == 23:
    st.subheader("Question 23: Isoelectric Charge Mapping [Match the Following]")
    st.write("Match each amino acid residue to its net ionic side-chain charge at physiological pH 7.4:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Lysine (K) / Arginine (R)**")
        ch1 = st.selectbox("Charge for K & R:", ["Select...", "+1 (Basic/Cationic)", "-1 (Acidic/Anionic)", "0 (Neutral/Zwitterionic)"], key="ch1")
        st.markdown("**2. Aspartate (D) / Glutamate (E)**")
        ch2 = st.selectbox("Charge for D & E:", ["Select...", "+1 (Basic/Cationic)", "-1 (Acidic/Anionic)", "0 (Neutral/Zwitterionic)"], key="ch2")
    with c2:
        st.markdown("**3. Alanine (A) / Valine (V)**")
        ch3 = st.selectbox("Charge for A & V:", ["Select...", "+1 (Basic/Cationic)", "-1 (Acidic/Anionic)", "0 (Neutral/Zwitterionic)"], key="ch3")
    if st.button("Check Charge Matching", key="btn23"):
        is_corr = (ch1 == "+1 (Basic/Cationic)" and ch2 == "-1 (Acidic/Anionic)" and ch3 == "0 (Neutral/Zwitterionic)")
        evaluate_answer(
            q_id=23, is_correct=is_corr, pts=10, badge="Charge Modeler",
            hint_msg="Lysine and Arginine have amino side chains (positive at pH 7.4); Aspartate and Glutamate have carboxylates (negative).",
            right_answer_msg="Lys/Arg ➔ +1, Asp/Glu ➔ -1, Ala/Val ➔ 0.",
            success_msg="Residue charge dictionaries enable bioinformatic net isoelectric point (pI) estimation."
        )
    render_feedback(23)

# QUESTION 24: LAMBDA FUNCTIONS FOR PROTEIN MOLECULAR WEIGHT
elif st.session_state.q_num == 24:
    st.subheader("Question 24: Anonymous Lambda Calculator [One-Word]")
    st.write("On average, each amino acid residue weighs 110 Daltons. In Python, small inline functions are created with a 6-letter keyword:")
    st.code("calc_mw = ______ num_residues: num_residues * 110", language="python")
    ans24 = st.text_input("Enter the Python keyword for anonymous functions (One word):", key="q24").strip().lower()
    if st.button("Check Answer", key="btn24"):
        is_corr = (ans24 == "lambda")
        evaluate_answer(
            q_id=24, is_correct=is_corr, pts=10, badge="Lambda Specialist",
            hint_msg="Starts with 'l' and represents the Greek letter λ.",
            right_answer_msg="The keyword is `lambda`.",
            success_msg="`lambda` functions allow quick functional transformations over sequence streams."
        )
    render_feedback(24)

# QUESTION 25: ZIP FUNCTION FOR BASE PAIR ALIGNMENT
elif st.session_state.q_num == 25:
    st.subheader("Question 25: Pairwise Alignment Iterator [One-Word]")
    st.write("To iterate through two aligned DNA sequences simultaneously base-by-base:")
    st.code("""seq1 = "ATGC"\nseq2 = "ACGC"\nfor base1, base2 in ___(seq1, seq2):\n    if base1 != base2: print("Mismatch!")""", language="python")
    ans25 = st.text_input("Enter the 3-letter built-in Python function that pairs elements together:", key="q25").strip().lower()
    if st.button("Check Answer", key="btn25"):
        is_corr = (ans25 == "zip")
        evaluate_answer(
            q_id=25, is_correct=is_corr, pts=10, badge="Alignment Master",
            hint_msg="Think of a jacket closure mechanism with teeth interlocking.",
            right_answer_msg="The function is `zip()`.",
            success_msg="`zip()` pairs parallel iterables together to detect point mutations and SNPs."
        )
    render_feedback(25)

# QUESTION 26: FASTA FILE PARSING WORKFLOW
elif st.session_state.q_num == 26:
    st.subheader("Question 26: FASTA Line Parsing [Flowchart Reordering]")
    st.write("Reorder the steps of reading and storing sequences from a multi-FASTA text file:")
    st.markdown("<div class='flowchart-step'>[Step 1] ➔ [Step 2] ➔ [Step 3]</div>", unsafe_allow_html=True)
    fs1 = st.selectbox("Step 1:", ["Select...", "Open file with 'with open(filename) as f:'", "Check 'if line.startswith(">")' to extract header", "Accumulate nucleotide lines into sequence string"], key="fs1")
    fs2 = st.selectbox("Step 2:", ["Select...", "Open file with 'with open(filename) as f:'", "Check 'if line.startswith(">")' to extract header", "Accumulate nucleotide lines into sequence string"], key="fs2")
    fs3 = st.selectbox("Step 3:", ["Select...", "Open file with 'with open(filename) as f:'", "Check 'if line.startswith(">")' to extract header", "Accumulate nucleotide lines into sequence string"], key="fs3")
    if st.button("Verify FASTA Pipeline", key="btn26"):
        is_corr = (fs1.startswith("Open file") and fs2.startswith("Check 'if line.startswith") and fs3.startswith("Accumulate nucleotide"))
        evaluate_answer(
            q_id=26, is_correct=is_corr, pts=10, badge="FASTA Parser",
            hint_msg="First open the file context, then detect header tags (`>`), then concatenate the sequence lines beneath.",
            right_answer_msg="Step 1: Open file ➔ Step 2: Check for '>' header ➔ Step 3: Accumulate sequence lines.",
            success_msg="Correct FASTA parsing architecture established."
        )
    render_feedback(26)

# QUESTION 27: MONOD GROWTH KINETICS
elif st.session_state.q_num == 27:
    st.subheader("Question 27: Monod Specific Growth Rate [Equating]")
    st.write(r"In bioprocess engineering, Monod kinetics defines cell specific growth rate: $\mu = \frac{\mu_{\max} S}{K_s + S}$.")
    st.write("Which Python function properly computes $\mu$?")
    ans27 = st.radio("Select the implementation:", [
        "def calc_mu(s, mu_max=0.5, ks=2.0): return (mu_max * s) / (ks + s)",
        "def calc_mu(s, mu_max=0.5, ks=2.0): return mu_max * s / ks + s",
        "def calc_mu(s, mu_max=0.5, ks=2.0): return (ks + s) / (mu_max * s)"
    ], key="q27")
    if st.button("Check Monod Implementation", key="btn27"):
        is_corr = ans27.startswith("def calc_mu(s, mu_max=0.5, ks=2.0): return (mu_max * s) / (ks + s)")
        evaluate_answer(
            q_id=27, is_correct=is_corr, pts=10, badge="Bioprocess Engineer",
            hint_msg="Ensure parentheses isolate the denominator `(ks + s)` from the numerator.",
            right_answer_msg="`def calc_mu(s, mu_max=0.5, ks=2.0): return (mu_max * s) / (ks + s)`.",
            success_msg="Monod equation models substrate-limited chemostat and fermenter operations."
        )
    render_feedback(27)

# QUESTION 28: OPEN READING FRAME (ORF) SEARCH
elif st.session_state.q_num == 28:
    st.subheader("Question 28: ORF Start and Stop Coordinate Slicing [Bug Hunter]")
    st.write("A student wrote this loop to find the start codon index:")
    st.code("""start_index = dna.find("AUG")\nstop_index = dna.find("UAA")\norf = dna[start_index : stop_index]""", language="python")
    st.write("Why is the stop codon missing from the extracted `orf` slice?")
    ans28 = st.radio("Choose the reason:", [
        "In Python slicing `[start:stop]`, the stop boundary is excluded, so we must slice up to `stop_index + 3`.",
        "`dna.find()` always searches from the right end of the strand.",
        "Stop codons cannot be converted into substrings."
    ], key="q28")
    if st.button("Check ORF Diagnosis", key="btn28"):
        is_corr = ans28.startswith("In Python slicing `[start:stop]`, the stop boundary is excluded")
        evaluate_answer(
            q_id=28, is_correct=is_corr, pts=10, badge="Genomics Sleuth",
            hint_msg="Remember slice notation `[start:stop]` omits the characters at index `stop`. The stop codon has 3 letters.",
            right_answer_msg="Because `stop_index` is non-inclusive, write `dna[start_index : stop_index + 3]` to include the 3-letter stop codon.",
            success_msg="Understanding slice non-inclusivity prevents truncated peptide predictions."
        )
    render_feedback(28)

# QUESTION 29: TRY/EXCEPT FOR INVALID BASES
elif st.session_state.q_num == 29:
    st.subheader("Question 29: Exception Handling [Fill-in-the-Blank]")
    st.write("When looking up an ambiguous base (e.g. `'N'`) in a codon table, which Python structure catches `KeyError` gracefully?")
    st.code("""____:\n    amino_acid = codon_table[codon]\nexcept KeyError:\n    amino_acid = 'Unknown'""", language="python")
    ans29 = st.text_input("Enter the 3-letter Python keyword that opens an exception-handling block:", key="q29").strip().lower()
    if st.button("Check Answer", key="btn29"):
        is_corr = (ans29 == "try")
        evaluate_answer(
            q_id=29, is_correct=is_corr, pts=10, badge="Robust Developer",
            hint_msg="Paired with `except`, this 3-letter keyword means 'attempt'.",
            right_answer_msg="The keyword is `try`.",
            success_msg="`try...except` blocks prevent bioinformatics pipelines from crashing on ambiguous sequencer reads."
        )
    render_feedback(29)

# QUESTION 30: LOGISTIC CELL GROWTH EQUATION
elif st.session_state.q_num == 30:
    st.subheader("Question 30: Carrying Capacity Modeling [Equating]")
    st.write(r"Unlike unbounded exponential growth, limited bioreactors follow logistic growth: $\frac{dN}{dt} = rN\left(1 - \frac{N}{K}\right)$.")
    st.write("What happens to $\frac{dN}{dt}$ when cell population $N$ reaches the carrying capacity $K$?")
    ans30 = st.radio("Select the steady-state outcome:", [
        "dN/dt becomes 0 (growth ceases as carrying capacity is saturated)",
        "dN/dt accelerates to infinity",
        "dN/dt becomes negative infinity"
    ], key="q30")
    if st.button("Check Logistic Logic", key="btn30"):
        is_corr = ans30.startswith("dN/dt becomes 0")
        evaluate_answer(
            q_id=30, is_correct=is_corr, pts=10, badge="Biokinetics Pro",
            hint_msg="When $N = K$, the term $(1 - N/K)$ becomes $(1 - 1) = 0$.",
            right_answer_msg="dN/dt becomes 0 because $(1 - N/K) = 0$, reaching stationary phase.",
            success_msg="Logistic growth models nutrient depletion and toxic metabolite accumulation."
        )
    render_feedback(30)

# ==============================================================================
# LEVEL 3: ADVANCED BIOPROCESS & BIOINFORMATICS (QUESTIONS 31 - 40)
# ==============================================================================

# QUESTION 31: HAMMING DISTANCE BETWEEN TWO STRANDS
elif st.session_state.q_num == 31:
    st.subheader("Question 31: Hamming Distance Calculator [Reordering]")
    st.write("Reorder the 3 lines to compute the number of point mutation mismatches between equal-length strands:")
    h1 = st.selectbox("Line 1:", ["Select...", "return mismatches", "mismatches = sum(1 for a, b in zip(seq1, seq2) if a != b)", "def hamming_distance(seq1, seq2):"], key="h1")
    h2 = st.selectbox("Line 2:", ["Select...", "return mismatches", "mismatches = sum(1 for a, b in zip(seq1, seq2) if a != b)", "def hamming_distance(seq1, seq2):"], key="h2")
    h3 = st.selectbox("Line 3:", ["Select...", "return mismatches", "mismatches = sum(1 for a, b in zip(seq1, seq2) if a != b)", "def hamming_distance(seq1, seq2):"], key="h3")
    if st.button("Verify Hamming Assembly", key="btn31"):
        is_corr = (h1.startswith("def hamming") and h2.startswith("mismatches =") and h3.startswith("return"))
        evaluate_answer(
            q_id=31, is_correct=is_corr, pts=10, badge="Phylogenetics Architect",
            hint_msg="Function signature first, followed by mismatch tallying using `zip`, and finally `return`.",
            right_answer_msg="Line 1: `def hamming_distance` ➔ Line 2: `mismatches = sum(...)` ➔ Line 3: `return mismatches`.",
            success_msg="Hamming distance is the fundamental metric for molecular evolution and phylogenetic trees."
        )
    render_feedback(31)

# QUESTION 32: NUMPY VECTORS FOR FERMENTATION ARRAYS
elif st.session_state.q_num == 32:
    st.subheader("Question 32: Vectorized Bioprocess Arrays [One-Word]")
    st.write("Instead of slow Python lists, scientific bioprocess simulations use the standard numerical array library:")
    st.code("import ______ as np\ntime_points = np.linspace(0, 24, 100)", language="python")
    ans32 = st.text_input("Enter the library name (One word):", key="q32").strip().lower()
    if st.button("Check Answer", key="btn32"):
        is_corr = (ans32 == "numpy")
        evaluate_answer(
            q_id=32, is_correct=is_corr, pts=10, badge="NumPy Engineer",
            hint_msg="Short for 'Numerical Python'.",
            right_answer_msg="The library is `numpy`.",
            success_msg="`numpy` powers C-speed vectorized numerical integration in computational biology."
        )
    render_feedback(32)

# QUESTION 33: FED-BATCH DILUTION RATE
elif st.session_state.q_num == 33:
    st.subheader("Question 33: Continuous Chemostat Dilution Rate [Equating]")
    st.write(r"In a continuous stirred-tank bioreactor (CSTR), the dilution rate $D$ depends on volumetric feed rate $F$ and culture volume $V$: $D = \frac{F}{V}$.")
    st.write("If dilution rate $D > \mu_{\max}$, what catastrophic bioprocess event occurs?")
    ans33 = st.radio("Choose the outcome:", [
        "Culture washout (cells exit faster than maximum reproductive capacity)",
        "Overgrowth and foaming",
        "Cell death due to zero oxygen transfer"
    ], key="q33")
    if st.button("Check Chemostat Outcome", key="btn33"):
        is_corr = ans33.startswith("Culture washout")
        evaluate_answer(
            q_id=33, is_correct=is_corr, pts=10, badge="Bioreactor Operator",
            hint_msg="If outflow rate exceeds maximum growth rate, cells are washed out of the vessel.",
            right_answer_msg="Culture washout occurs because cells cannot divide fast enough to replace outgoing volume.",
            success_msg="Maintaining $D < \mu_{\max}$ is the core steady-state design criterion in industrial fermentation."
        )
    render_feedback(33)

# QUESTION 34: BIOINFORMATICS RECURSION - FIBONACCI RABBITS
elif st.session_state.q_num == 34:
    st.subheader("Question 34: Mendel's Population Recursion [Base Case Puzzle]")
    st.write("In recursive modeling of breeding pairs ($F_n = F_{n-1} + F_{n-2}$), what happens if a base case (`if n <= 2: return 1`) is omitted?")
    ans34 = st.radio("Choose the Python runtime failure:", [
        "RecursionError: maximum recursion depth exceeded (stack overflow)",
        "ZeroDivisionError",
        "TypeError: unsupported operand"
    ], key="q34")
    if st.button("Check Recursion Failure", key="btn34"):
        is_corr = ans34.startswith("RecursionError")
        evaluate_answer(
            q_id=34, is_correct=is_corr, pts=10, badge="Recursion Specialist",
            hint_msg="Without an exit condition, a recursive function calls itself indefinitely until system memory limit is reached.",
            right_answer_msg="`RecursionError: maximum recursion depth exceeded`.",
            success_msg="Every recursive biological model requires terminating base cases."
        )
    render_feedback(34)

# QUESTION 35: OBJECT-ORIENTED PLASMID CLASS
elif st.session_state.q_num == 35:
    st.subheader("Question 35: OOP Plasmid Class Constructor [One-Word]")
    st.write("In Python Object-Oriented Programming (OOP), what special double-underscore method initializes a new `Plasmid` instance?")
    st.code("""class Plasmid:\n    def ______(self, name, length):\n        self.name = name\n        self.length = length""", language="python")
    ans35 = st.text_input("Enter the constructor method name without parentheses (e.g. __init__):", key="q35").strip().lower()
    if st.button("Check Constructor", key="btn35"):
        is_corr = (ans35 in ["__init__", "init", "__init"])
        evaluate_answer(
            q_id=35, is_correct=is_corr, pts=10, badge="OOP Bio-Programmer",
            hint_msg="Double underscore followed by 'init' followed by double underscore.",
            right_answer_msg="The method is `__init__`.",
            success_msg="OOP allows encapsulation of sequence properties, restriction maps, and resistance markers."
        )
    render_feedback(35)

# QUESTION 36: MASS BALANCE DIFFERENTIAL EQUATION
elif st.session_state.q_num == 36:
    st.subheader("Question 36: Substrate Consumption Mass Balance [Match the Following]")
    st.write(r"Match each biological parameter in the substrate consumption equation $\frac{dS}{dt} = -\frac{1}{Y_{X/S}}\mu X - m X$ to its definition:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. $Y_{X/S}$**")
        p36_1 = st.selectbox("Meaning of Y_X/S:", ["Select...", "Biomass yield coefficient on substrate (g cells / g substrate)", "Maintenance coefficient (g substrate / g cells / hr)", "Specific growth rate"], key="p36_1")
        st.markdown("**2. $m$**")
        p36_2 = st.selectbox("Meaning of m:", ["Select...", "Biomass yield coefficient on substrate (g cells / g substrate)", "Maintenance coefficient (g substrate / g cells / hr)", "Specific growth rate"], key="p36_2")
    with c2:
        st.markdown("**3. $\mu$**")
        p36_3 = st.selectbox("Meaning of mu:", ["Select...", "Biomass yield coefficient on substrate (g cells / g substrate)", "Maintenance coefficient (g substrate / g cells / hr)", "Specific growth rate"], key="p36_3")
    if st.button("Check Mass Balance Matches", key="btn36"):
        is_corr = (p36_1.startswith("Biomass yield") and p36_2.startswith("Maintenance coefficient") and p36_3.startswith("Specific growth"))
        evaluate_answer(
            q_id=36, is_correct=is_corr, pts=10, badge="Mass Balance Modeler",
            hint_msg="$Y_{X/S}$ is yield, $m$ is non-growth maintenance energy, and $\mu$ is growth rate.",
            right_answer_msg="1. $Y_{X/S}$ ➔ Yield coefficient\n2. $m$ ➔ Maintenance coefficient\n3. $\mu$ ➔ Specific growth rate.",
            success_msg="Dynamic mass balances govern automated industrial bioreactor feed pumps."
        )
    render_feedback(36)

# QUESTION 37: GENE EXPRESSION LOG2 FOLD CHANGE
elif st.session_state.q_num == 37:
    st.subheader("Question 37: RNA-Seq Fold Change [Equating]")
    st.write("In transcriptomics, differential expression is quantified by log2 fold change: $\text{L2FC} = \log_2\left(\frac{\text{treated}}{\text{control}}\right)$.")
    st.write("Which Python expression calculates this using `math.log2`?")
    ans37 = st.radio("Choose the expression:", [
        "l2fc = math.log2(treated / control)",
        "l2fc = math.log2(treated) - math.log2(control)",
        "Both of the above are mathematically equivalent"
    ], key="q37")
    if st.button("Check Transcriptomic Expression", key="btn37"):
        is_corr = (ans37 == "Both of the above are mathematically equivalent")
        evaluate_answer(
            q_id=37, is_correct=is_corr, pts=10, badge="Transcriptomics Pro",
            hint_msg="Recall logarithm quotient rules: $\log(A/B) = \log(A) - \log(B)$.",
            right_answer_msg="Both are mathematically equivalent by logarithm quotient identity.",
            success_msg="Log2 fold changes normalize RNA-seq ratios around zero for volcano plots."
        )
    render_feedback(37)

# QUESTION 38: RUN-LENGTH ENCODING FOR GENOMIC REPEATS
elif st.session_state.q_num == 38:
    st.subheader("Question 38: Homopolymer Compression [Algorithm Puzzle]")
    st.write("Homopolymer tracts (e.g. `'AAAAAA'`) cause nanopore sequencing errors. In run-length encoding (RLE), how is `'AAAAAA'` represented?")
    ans38 = st.radio("Choose the RLE compressed format:", [
        "('A', 6)",
        "('A', 1, 2, 3, 4, 5, 6)",
        "('A', 'A')"
    ], key="q38")
    if st.button("Check Compression Format", key="btn38"):
        is_corr = (ans38 == "('A', 6)")
        evaluate_answer(
            q_id=38, is_correct=is_corr, pts=10, badge="Genomic Compressor",
            hint_msg="RLE records the repeating character followed by the count of consecutive occurrences.",
            right_answer_msg="`('A', 6)` or `'A6'` stores character and run length.",
            success_msg="Run-length compression reduces memory footprints in de Bruijn genome assemblers."
        )
    render_feedback(38)

# QUESTION 39: ENZYME INHIBITION LINEWEAVER-BURK INTERPRETATION
elif st.session_state.q_num == 39:
    st.subheader("Question 39: Competitive Inhibition Kinetics [Match the Following]")
    st.write("Match how a competitive enzyme inhibitor alters Michaelis-Menten kinetic constants:")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**1. Apparent $K_m$**")
        inh1 = st.selectbox("Effect on Km:", ["Select...", "Increases (weaker substrate affinity)", "Unchanged", "Decreases"], key="inh1")
    with c2:
        st.markdown("**2. Apparent $V_{\max}$**")
        inh2 = st.selectbox("Effect on Vmax:", ["Select...", "Unchanged (high substrate outcompetes inhibitor)", "Decreases", "Increases"], key="inh2")
    if st.button("Check Inhibition Matches", key="btn39"):
        is_corr = (inh1.startswith("Increases") and inh2.startswith("Unchanged"))
        evaluate_answer(
            q_id=39, is_correct=is_corr, pts=10, badge="Enzyme Pharmacologist",
            hint_msg="Competitive inhibitors bind to the active site: substrate can still achieve $V_{\max}$ at high concentrations, but requires higher $[S]$ ($K_m$ increases).",
            right_answer_msg="Apparent $K_m$ increases; $V_{\max}$ remains unchanged.",
            success_msg="Lineweaver-Burk plots differentiate competitive, uncompetitive, and non-competitive enzyme inhibition."
        )
    render_feedback(39)

# QUESTION 40: DYNAMIC PROGRAMMING SEQUENCE ALIGNMENT MATRIX
elif st.session_state.q_num == 40:
    st.subheader("Question 40: Needleman-Wunsch Alignment Matrix [Algorithm Architecture]")
    st.write("In Needleman-Wunsch global sequence alignment, each cell $M[i, j]$ takes the maximum of three possible moves:")
    st.markdown("<div class='puzzle-card'><div class='puzzle-title'>Recurrence:</div><code>M[i,j] = max(Diagonal + Score, Top + Gap, Left + Gap)</code></div>", unsafe_allow_html=True)
    ans40 = st.radio("What biological event does a move from the Diagonal cell $M[i-1, j-1]$ represent?", [
        "Base match or mismatch between seq1[i] and seq2[j]",
        "Insertion gap in seq1",
        "Deletion gap in seq2"
    ], key="q40")
    if st.button("Verify Dynamic Programming Event", key="btn40"):
        is_corr = ans40.startswith("Base match or mismatch")
        evaluate_answer(
            q_id=40, is_correct=is_corr, pts=10, badge="Bio-Algorithm Legend",
            hint_msg="Diagonal step aligns both residues simultaneously without introducing an indel gap.",
            right_answer_msg="Diagonal transition represents aligning the two characters (match or substitution mismatch).",
            success_msg="You completed the entire 40-question Bio-Python curriculum!"
        )
        if is_corr:
            st.balloons()
            st.write("---")
            st.write("🎓 **Grand Master Certification Unlocked!**")
            st.write(f"**Final Total Score:** {st.session_state.score} / 400 pts")
            st.write("All Badges Earned:", ", ".join(st.session_state.badges))
            if st.button("Restart Complete Curriculum"):
                reset_all()
    render_feedback(40)

# ==============================================================================
# BOTTOM NAVIGATION BUTTONS
# ==============================================================================
st.write("---")
b_left, _, b_right = st.columns([2, 4, 2])

with b_left:
    if st.session_state.q_num > 1:
        st.button("⬅ Previous Question", on_click=go_prev)

with b_right:
    if st.session_state.q_num < 40:
        st.button("Next Question ➡", on_click=go_next)
