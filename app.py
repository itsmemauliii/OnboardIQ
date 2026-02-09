# app.py
import streamlit as st
import sqlite3
import random
import time
from streamlit.components.v1 import html

# -------------------------
# DATABASE SETUP
# -------------------------
conn = sqlite3.connect("onboardiq.db", check_same_thread=False)
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
    "Cheese - Configure Settings",
    "Toppings - Upload Data",
    "Bake - Test Workflow",
    "Serve - Go Live"
]

COLORS = ["#FFB347", "#FF9933", "#FFD700", "#FF4500", "#FF6347", "#FF69B4"]

CHEESY_LINES = [
    "Oops, chef 😅We can’t skip a slice. Let’s add that before serving.",
    "Every slice counts. Don’t leave your users hungry for success!",
    "Keep rolling, chef! Your onboarding masterpiece awaits 👨‍🍳✨.",
    "Your pizza’s almost ready… just a few more layers of brilliance.",
    "Smells like success already. Don’t burn it!"
]

# -------------------------
# PAGE SETUP
# -------------------------
st.set_page_config(layout="wide", page_title="OnboardIQ", page_icon="🍕")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "completed" not in st.session_state:
    st.session_state.completed = []

if "section" not in st.session_state:
    st.session_state.section = "User"

# -------------------------
# NAVIGATION SECTIONS
# -------------------------
st.sidebar.title("🍕 OnboardIQ Sections")
section = st.sidebar.radio("Navigate to:", ["User", "Admin", "About App"])
st.session_state.section = section

# -------------------------
# ANIMATED SLICE PIZZA FUNCTION
# -------------------------
def render_pizza_animation():
    completed = len(st.session_state.completed)
    num_slices = len(STAGES)
    # SVG pie slices
    svg_slices = ""
    start_angle = 0
    for i in range(num_slices):
        end_angle = start_angle + (360 / num_slices)
        color = COLORS[i] if i < completed else "#f2f2f2"
        svg_slices += f"""
        <path d="
            M 150 150
            L {150 + 150 * round(random.uniform(0.9,1),2) * round(random.uniform(0.95,1),2)*st.session_state.completed.count(STAGES[i])*0.1} {150 + 150 * round(random.uniform(0.9,1),2)}
            A 150 150 0 0 1 {150 + 150 * round(random.uniform(0.9,1),2)} {150 - 150 * round(random.uniform(0.9,1),2)}
            Z
        " fill="{color}" stroke="#fff" stroke-width="2">
            <animate attributeName="fill" from="#f2f2f2" to="{color}" dur="1s" fill="freeze"/>
        </path>
        """
        start_angle = end_angle
    html(f"""
    <div style="text-align:center;">
        <svg width="300" height="300" viewBox="0 0 300 300">
            {svg_slices}
            <circle cx="150" cy="150" r="140" fill="transparent" stroke="#333" stroke-width="2"/>
        </svg>
        <h3>{int((completed / num_slices)*100)}% Progress</h3>
    </div>
    """, height=350)

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
                cursor.execute("INSERT INTO progress (user, stage) VALUES (?, ?)", ("demo_user", stage))
                conn.commit()
                human_line = random.choice(CHEESY_LINES)
                # Confetti for final milestone
                if len(st.session_state.completed) == len(STAGES):
                    st.balloons()
                return f"✅ {stage} completed! {human_line}"
            else:
                return f"You already finished {stage} 👍"
    return random.choice([
        "Let’s focus on the next slice chef 🍕",
        "Try asking about Dough, Sauce, Cheese, Toppings, Bake, or Serve.",
        "We’re building your success pizza step by step 👨‍🍳"
    ])

# -------------------------
# USER SECTION
# -------------------------
if st.session_state.section == "User":
    st.title("🍕 OnboardIQ – AI-Powered Onboarding Intelligence")
    st.write("Guide users to success, slice by slice 👨‍🍳💼")

    col1, col2 = st.columns([2, 1])

    with col1:
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

        user_input = st.chat_input("Ask your onboarding assistant...")

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            cursor.execute("INSERT INTO chats (message) VALUES (?)", (user_input,))
            conn.commit()
            response = generate_response(user_input)
            time.sleep(0.5)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    with col2:
        render_pizza_animation()
        if len(st.session_state.completed) == len(STAGES):
            st.success("🎉 All onboarding milestones completed! Users are live 🚀")

# -------------------------
# ADMIN SECTION
# -------------------------
if st.session_state.section == "Admin":
    st.title("📊 OnboardIQ Admin Dashboard")
    st.write("Track user onboarding progress and milestones")

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

# -------------------------
# ABOUT APP SECTION
# -------------------------
if st.session_state.section == "About App":
    st.title("🍕 About OnboardIQ")
    st.write("""
**OnboardIQ** transforms SaaS onboarding into an interactive, gamified journey.

- Users progress **slice by slice** through milestones.
- **Animated pizza** shows progress visually.
- **Cheesy humanized chatbot lines** keep users engaged.
- **Admin dashboard** tracks completion rates and milestone bottlenecks.
- Built entirely in **Streamlit**, no external APIs.

This is designed to **increase activation and reduce drop-offs** while keeping onboarding fun and human.
    """)
    st.info("Navigation: Use the sidebar to switch between User, Admin, and About sections.")
