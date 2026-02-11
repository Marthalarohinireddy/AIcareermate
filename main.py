import streamlit as st
from streamlit_option_menu import option_menu
import json
import os

# 1. IMPORT ALL MODULES
# Ensure these filenames match exactly what is in your 'modules' folder
from modules import home, aptitude, resume_analyzer, tech_interview, hr_bot, jd_extractor

# --- PAGE CONFIG ---
st.set_page_config(page_title="Career Mate AI", page_icon="🎯", layout="wide")

# --- USER AUTHENTICATION LOGIC ---
USER_DB = "user_registry.json"

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, "r") as f:
            try:
                return json.load(f)
            except:
                return {"admin": "1234"}
    return {"admin": "1234"}

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f)

# Initialize Session States for scores and login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Ensure all score keys exist to prevent errors in Dashboard
for key in ['ats_score', 'apti_score', 'tech_score', 'hr_score', 'jd_score']:
    if key not in st.session_state:
        st.session_state[key] = 0

# --- LOGIN / SIGNUP UI ---
if not st.session_state.logged_in:
    st.title("🚀 Career Mate AI")
    auth_mode = st.radio("Choose Mode", ["Login", "Sign Up"], horizontal=True)
    
    users = load_users()
    
    with st.container(border=True):
        u_name = st.text_input("Username")
        u_pass = st.text_input("Password", type="password")
        
        if auth_mode == "Login":
            if st.button("Login", use_container_width=True):
                if u_name in users and users[u_name] == u_pass:
                    st.session_state.logged_in = True
                    st.session_state.username = u_name
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        else:
            if st.button("Register", use_container_width=True):
                if u_name in users:
                    st.warning("User already exists!")
                elif u_name and u_pass:
                    users[u_name] = u_pass
                    save_users(users)
                    st.success("Registration successful! Please Login.")

# --- MAIN APPLICATION UI ---
else:
    with st.sidebar:
        st.title(f"👋 Hello, {st.session_state.username}!")
        selected = option_menu(
            menu_title="Main Menu",
            # Labels for your modules
             options=["Dashboard", "Resume AI", "JD Match", "Aptitude Test", "Technical Interview", "HR Round"],
        # Match these icons 1:1 with the options above
        icons=["speedometer2", "file-earmark-text", "search", "think", "code-slash", "people"], 
        menu_icon="cast",
        default_index=0,
            styles={
                "nav-link-selected": {"background-color": "#ff4b4b"}, # Highlight color for the active tab
            }
        ) 
        
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # ROUTING LOGIC (Names must match the 'options' list EXACTLY)
    if selected == "Dashboard":
        home.app()
    elif selected == "Resume AI":
        resume_analyzer.app()
    elif selected == "JD Match":
        # This calls your jd_extractor.py module
        jd_extractor.app()
    elif selected == "Aptitude Test":
        aptitude.app()
    elif selected == "Technical Interview":
        tech_interview.app()
    elif selected == "HR Round":
        hr_bot.app()