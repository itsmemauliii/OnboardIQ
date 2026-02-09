import streamlit as st
import sqlite3
import random
import time

# -------------------------
# DATABASE
# -------------------------

conn = sqlite3.connect("pizza_onboarding.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    stage TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT
)
""")

conn.commit()

# -------------------------
# ONBOARDING STAGES
# -------------------------

STAGES = [
    "Dough - Create Account",
    "Sauce - Connect Workspace",
    "Cheese - Create First Project",
    "Toppings - Add Automation",
    "Bake - Test Workflow",
    "Serve - Go Live"
]

# -------------------------
# PAGE SETUP
# -------------------------

st.set_page_config(layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "completed" not in st.session_state:
    st.session_state.completed = []

if "view" not in st.session_state:
    st.session_state.view = "user"

# -------------------------
# SIDEBAR SWITCH
# -------------------------

st.sidebar.title("🍕 Control Panel")

if st.sidebar.button("User View"):
    st.session_state.view = "user"

if st.sidebar.button("Admin View"):
    st.session_state.view = "admin"

# -------------------------
# 3D PIZZA PROGRESS
# -------------------------

def render_pizza():
    completed = len(st.session_state.completed)
    percent = int((completed / len(STAGES)) * 100)

    st.markdown(f"""
    <div style="text-align:center;">
        <div style="
            width:250px;
            height:250px;
            border-radius:50%;
            background:conic-gradient(
                #ff9933 {percent}%,
                #f2f2f2 {percent}% 100%
            );
            box-shadow:0 15px 35px rgba(0,0,0,0.3);
            margin:auto;
        ">
        </div>
        <h3>{percent}% Cooked</h3>
    </div>
    """, unsafe_allow_html=True)

# -------------------------
# CHATBOT LOGIC
# -------------------------

def generate_response(user_input):

    lower = user_input.lower()

    for stage in STAGES:
        keyword = stage.split(" - ")[0].lower()

        if keyword in lower:
            if stage not in st.session_state.completed:
                st.session_state.completed.append(stage)
                cursor.execute("INSERT INTO progress (user, stage) VALUES (?, ?)", ("demo", stage))
                conn.commit()
                return f"Nice! {stage} completed 👨‍🍳🔥"
            else:
                return f"You already finished {stage} 👍"

    return random.choice([
        "Let’s focus on the next slice chef 🍕",
        "Try asking about Dough, Sauce, Cheese, Toppings, Bake, or Serve.",
        "We’re building your success pizza step by step 👨‍🍳"
    ])

# -------------------------
# USER VIEW
# -------------------------

if st.session_state.view == "user":

    st.title("🍕 OnboardIQ")
    st.write("Let’s cook your success pizza 👨‍🍳")

    col1, col2 = st.columns([2, 1])

    with col1:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        user_input = st.chat_input("Ask your pizza chef...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            cursor.execute("INSERT INTO chats (message) VALUES (?)", (user_input,))
            conn.commit()

            response = generate_response(user_input)

            time.sleep(0.5)

            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    with col2:
        render_pizza()

        if len(st.session_state.completed) == len(STAGES):
            st.success("🍕 Pizza Fully Cooked! You’re Live!")
            st.balloons()

# -------------------------
# ADMIN VIEW
# -------------------------

if st.session_state.view == "admin":

    st.title("🍳 Admin Dashboard")

    cursor.execute("SELECT COUNT(*) FROM chats")
    total_chats = cursor.fetchone()[0]

    cursor.execute("SELECT stage, COUNT(*) FROM progress GROUP BY stage")
    stage_data = cursor.fetchall()

    st.metric("Total Chat Messages", total_chats)

    st.subheader("Slice Completion Stats")

    for stage, count in stage_data:
        st.write(f"{stage} → {count} completions")

    cursor.execute("SELECT COUNT(DISTINCT user) FROM progress")
    users = cursor.fetchone()[0]

    st.metric("Users Started Onboarding", users)
