# app.py
import streamlit as st
import sqlite3
import random
import time
from streamlit.components.v1 import html
import math

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
if st.session_state.current_user:
    cursor.execute("SELECT stage FROM progress WHERE user = ?", (st.session_state.current_user,))
    completed_stages = [row[0] for row in cursor.fetchall()]
    st.session_state.completed = completed_stages

if st.session_state.current_user is None:
    st.title("🍕 Welcome to OnboardIQ")
    username = st.text_input("Enter your username to start your session", key="login")
    if st.button("Login"):
        if username.strip() != "":
            st.session_state.current_user = username.strip()
            st.experimental_rerun()

# -------------------------
# ONBOARDING STAGES + FLAVORS
# -------------------------
STAGES = [
    "Dough - Create Account",
    "Sauce - Connect Workspace",
    "Cheese - Configure Settings",
    "Toppings - Upload Data",
    "Bake - Test Workflow",
    "Serve - Go Live"
]

FLAVORS = [
    "🍕 Margherita",
    "🌶 Pepperoni",
    "🧀 Cheesy",
    "🥦 Veggie",
    "🔥 Bake & Blend",
    "👑 Supreme Serve"
]

COLORS = ["#FFB347", "#FF9933", "#FFD700", "#FF4500", "#FF6347", "#FF69B4"]

CHEESY_LINES = [
    "Oops, chef 😅We can’t skip a slice. Let’s add that before serving.",
    "Every slice counts. Don’t leave your users hungry for success!",
    "Keep rolling, chef! Your onboarding masterpiece awaits 👨‍🍳✨.",
    "Your pizza’s almost ready… just a few more layers of brilliance.",
    "Smells like success already, Don’t burn it!"
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
# NAVIGATION
# -------------------------
st.sidebar.title("🍕 OnboardIQ Sections")
section = st.sidebar.radio("Navigate to:", ["User", "Admin", "About App"])
st.session_state.section = section

# -------------------------
# HELPER: POLAR TO CARTESIAN
# -------------------------
def polar_to_cartesian(cx, cy, r, angle):
    rad = math.radians(angle)
    x = cx + r * math.cos(rad)
    y = cy + r * math.sin(rad)
    return x, y

# -------------------------
# RENDER ANIMATED PIZZA WITH LABELS INSIDE SLICES
# -------------------------
def render_pizza_with_labels():
    num_slices = len(STAGES)
    cx, cy, r = 150, 150, 140
    svg_slices = ""

    for i in range(num_slices):
        start_angle = (i / num_slices) * 360
        end_angle = ((i + 1) / num_slices) * 360
        color = COLORS[i] if i < len(st.session_state.completed) else "#f2f2f2"

        x1, y1 = polar_to_cartesian(cx, cy, r, start_angle)
        x2, y2 = polar_to_cartesian(cx, cy, r, end_angle)
        large_arc = 1 if (end_angle - start_angle) > 180 else 0

        # Mid-angle for label
        mid_angle = (start_angle + end_angle) / 2
        label_x, label_y = polar_to_cartesian(cx, cy, r * 0.6, mid_angle)
        flavor_label = FLAVORS[i]

        path = f"""
        <path d="M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z"
              fill="{color}" stroke="#fff" stroke-width="2">
            <title>{flavor_label}</title>
            <animate attributeName="fill" from="#f2f2f2" to="{color}" dur="0.8s" fill="freeze"/>
        </path>
        <text x="{label_x}" y="{label_y}" font-size="14" text-anchor="middle" alignment-baseline="middle"
              fill="#333" font-weight="bold">{flavor_label}</text>
        """
        svg_slices += path

    html(f"""
    <div style="text-align:center;">
        <svg width="300" height="300" viewBox="0 0 300 300">
            {svg_slices}
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="#333" stroke-width="2"/>
        </svg>
        <h3>{int(len(st.session_state.completed)/num_slices*100)}% Progress</h3>
        <p style="font-weight:bold;">Hover on slices to see tooltip flavor names!</p>
    </div>
    """, height=380)

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
    st.title("🍕 OnboardIQ")
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
            time.sleep(0.3)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    with col2:
        render_pizza_with_labels()
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
# ABOUT SECTION
# -------------------------
if st.session_state.section == "About App":
    st.title("🍕 About OnboardIQ")
    st.write("""
**OnboardIQ** transforms SaaS onboarding into an interactive, gamified journey.

- Users progress **slice by slice** through milestones.
- **Animated pizza slices** fill clockwise as milestones complete.
- **Flavor labels appear inside slices** with emoji + name.
- **Cheesy humanized chatbot lines** keep users engaged.
- **Admin dashboard** tracks completion rates and bottlenecks.
- Built entirely in **Streamlit**, no external APIs.

This is designed to **increase activation and reduce drop-offs** while keeping onboarding fun and human.
    """)
    st.info("Use the sidebar to navigate between User, Admin, and About App sections.")
