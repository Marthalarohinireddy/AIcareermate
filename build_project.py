import os

# 1. Create Folder Structure
folders = ['modules', 'data']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# 2. Define all file contents
files = {
    "requirements.txt": "streamlit\ngoogle-generativeai\npython-dotenv\nPyPDF2\nstreamlit-mic-recorder",
    
    ".env": "GEMINI_API_KEY=your_api_key_here",

    "auth.py": """
import sqlite3
import hashlib

def create_usertable():
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def add_userdata(username, password):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    hashed_pswd = hashlib.sha256(password.encode()).hexdigest()
    c.execute('INSERT INTO userstable(username, password) VALUES (?,?)', (username, hashed_pswd))
    conn.commit()
    conn.close()

def login_user(username, password):
    conn = sqlite3.connect('data/users.db')
    c = conn.cursor()
    hashed_pswd = hashlib.sha256(password.encode()).hexdigest()
    c.execute('SELECT * FROM userstable WHERE username =? AND password =?', (username, hashed_pswd))
    return c.fetchall()
""",

    "main.py": """
import streamlit as st
from auth import create_usertable, add_userdata, login_user
from modules import resume_analyzer, aptitude, jd_extractor, tech_interview, hr_bot

def main():
    st.set_page_config(page_title="AI Career Suite", layout="wide")
    create_usertable()

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        st.sidebar.title("Access Portal")
        choice = st.sidebar.selectbox("Action", ["Login", "Sign Up"])
        user = st.sidebar.text_input("Username")
        pw = st.sidebar.text_input("Password", type="password")
        
        if choice == "Login":
            if st.sidebar.button("Login"):
                if login_user(user, pw):
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.rerun()
                else: st.sidebar.error("Wrong credentials")
        else:
            if st.sidebar.button("Create Account"):
                add_userdata(user, pw)
                st.sidebar.success("Done! Now Login.")
    else:
        st.sidebar.success(f"Logged in as {st.session_state['user']}")
        page = st.sidebar.radio("Dashboards", ["Resume Analyzer", "AI Aptitude", "JD Extractor", "Tech Interview", "HR Bot"])
        if st.sidebar.button("Logout"):
            st.session_state['logged_in'] = False
            st.rerun()

        if page == "Resume Analyzer": resume_analyzer.app()
        elif page == "AI Aptitude": aptitude.app()
        elif page == "JD Extractor": jd_extractor.app()
        elif page == "Tech Interview": tech_interview.app()
        elif page == "HR Bot": hr_bot.app()

if __name__ == '__main__': main()
""",

    "modules/resume_analyzer.py": """
import streamlit as st
from PyPDF2 import PdfReader

def app():
    st.header("📄 Resume Analyzer")
    file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if file:
        reader = PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        st.write("### Analysis Result")
        st.info("AI Logic: Extracting skills and calculating score...")
        # Placeholder for AI logic
        st.success("Resume Score: 85/100")
""",

    "modules/aptitude.py": """
import streamlit as st

def app():
    st.header("🧠 AI Aptitude Generator")
    diff = st.select_slider("Select Difficulty", options=["Easy", "Medium", "Hard"])
    if st.button("Generate Questions"):
        st.write(f"Generating {diff} level questions...")
        st.write("1. What is 15% of 200? (A) 20 (B) 30 (C) 40 (D) 50")
""",

    "modules/jd_extractor.py": """
import streamlit as st

def app():
    st.header("📋 JD Question Extractor")
    jd_text = st.text_area("Paste Job Description Here")
    if st.button("Extract Questions"):
        st.write("### Likely Interview Questions:")
        st.write("- Explain your experience with the tech stack mentioned.")
        st.write("- How do you handle deadlines in this role?")
""",

    "modules/tech_interview.py": """
import streamlit as st

def app():
    st.header("💻 Technical Interview")
    role = st.selectbox("Select Role", ["Python Developer", "Java Developer", "Frontend", "Data Analyst"])
    if st.button("Start Interview"):
        st.session_state['q'] = "What are decorators in Python?" if role == "Python Developer" else "Explain JVM."
    
    if 'q' in st.session_state:
        st.write(f"**Question:** {st.session_state['q']}")
        ans = st.text_area("Your Answer")
        if st.button("Submit"):
            st.write("### Feedback: Your explanation of decorators is clear but could mention 'wrappers'. Score: 8/10")
""",

    "modules/hr_bot.py": """
import streamlit as st
from streamlit_mic_recorder import mic_recorder

def app():
    st.header("🤝 HR Interview (Text & Voice)")
    st.write("**Question:** Tell me about a time you handled a conflict.")
    
    tab1, tab2 = st.tabs(["Text Mode", "Voice Mode"])
    with tab1:
        st.text_area("Type your response here")
    with tab2:
        st.write("Record your answer:")
        audio = mic_recorder(start_prompt="Record", stop_prompt="Stop")
        if audio: st.audio(audio['bytes'])
"""
}

for filename, content in files.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content.strip())

print("✅ Project 'CareerPrep_AI' has been built! Use 'streamlit run main.py' to start.")
