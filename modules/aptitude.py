import streamlit as st
import re
import requests
import json

def get_ollama_questions(topic, level):
    """Calls local Ollama (Llama 3.2) to generate MCQ questions."""
    url = "http://localhost:11434/api/generate"
    
    prompt = (
        f"Generate 15 Multiple Choice Questions for {topic} at {level} level. "
        "Format each question strictly as: Q: [text] A) [opt] B) [opt] C) [opt] D) [opt] ANS: [Letter]" \
        "The questions should be clear, concise, and relevant to the topic and difficulty level. Avoid overly ambiguous or trick questions. Ensure the correct answer is one of the options and that all options are plausible to maintain challenge." \
        
    )
    
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', "")
        else:
            return f"ERROR: Ollama returned status {response.status_code}"
    except Exception as e:
        return f"ERROR: Connection failed. Is Ollama running? {str(e)}"

def app():
    # Optional: Add a custom header image for the logo
    # st.image("assets/aptitude_logo.png", width=100) 
    st.header("🧠 AI Aptitude Test")
    st.markdown("---")
     
    
    # UI Banner
    st.markdown("""
    <div style="background-color: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0ea5e9; margin-bottom: 25px;">
        💡 <b>Pro-Tip:</b> Most placement filters require at least 70% in Aptitude. Aim for <b>11/15</b> to be in the safe zone!
    </div>
    """, unsafe_allow_html=True)

    # 1. Setup Session State
    if "test_data" not in st.session_state:
        st.session_state.test_data = None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False

    # 2. Sidebar options
    level = st.sidebar.selectbox("Select Difficulty", ["Easy", "Medium", "Hard"])
    topic = st.sidebar.selectbox("Select Topic", ["Logical Reasoning", "Quantitative Aptitude", "Verbal Ability"])

    if st.button("🚀 Generate 15-Question Test"):
        with st.spinner(f"Llama 3.2 is preparing {level} {topic} questions locally..."):
            # Call local Ollama instead of Gemini
            test_response = get_ollama_questions(topic, level)
            
            if "ERROR" not in test_response:
                st.session_state.test_data = test_response
                st.session_state.submitted = False
                st.rerun()
            else:
                st.error(test_response)

    # 3. The Quiz Form
    if st.session_state.test_data and not st.session_state.submitted:
        # Split questions based on your original regex
        blocks = re.split(r'Q\d*[:.]?', st.session_state.test_data)[1:]
        
        with st.form("quiz_form"):
            user_answers = {}
            correct_keys = []

            for i, block in enumerate(blocks):
                if not block.strip(): continue
                
                lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
                if len(lines) < 2: continue 
                
                question = lines[0]
                options = [l for l in lines if re.match(r'^[A-D]\)', l.upper())]
                
                # Robust Answer extraction
                ans_line = [l for l in lines if "ANS:" in l.upper()]
                ans = "A" # Default fallback
                if ans_line:
                    found_ans = re.search(r'ANS:\s*([A-D])', ans_line[0].upper())
                    if found_ans:
                        ans = found_ans.group(1)
                
                correct_keys.append(ans)

                st.markdown(f"Q{i+1}: {question}")
                user_answers[i] = st.radio(f"Choose option for Q{i+1}", options, index=None, key=f"ans_{i}")
                st.divider()

            if st.form_submit_button("✅ Submit and See Score"):
                score = 0
                for i in range(len(correct_keys)):
                    if user_answers.get(i) and user_answers[i].strip().startswith(correct_keys[i]):
                        score += 1
                
                final_percentage = int((score / len(correct_keys)) * 100) if correct_keys else 0
                st.session_state.apti_score = final_percentage
                st.session_state.final_count = score
                st.session_state.submitted = True
                st.rerun()

    # 4. Result Screen
    if st.session_state.submitted:
        st.balloons()
        score = st.session_state.get('final_count', 0)
        percentage = st.session_state.get('apti_score', 0)
        
        st.success(f"### 🎉 Quiz Completed! Your Score: {score} / 15 ({percentage}%)")
        
        if percentage < 70:
            st.warning("Keep practicing! You need at least 70% to clear most company cut-offs.")
        else:
            st.info("Excellent work! You are currently meeting the aptitude criteria for top companies.")

        if st.button("🔄 Take a Different Test"):
            st.session_state.submitted = False
            st.session_state.test_data = None
            st.rerun()