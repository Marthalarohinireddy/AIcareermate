import streamlit as st
import re
import requests

def get_ollama_response(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {"model": "llama3.2", "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=120)
        return response.json().get('response', "") if response.status_code == 200 else f"ERROR: {response.status_code}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def app():
    st.title("🎯 Job Description Based Test")
    st.info("The AI will evaluate your answers directly based on the Job Description standards.")
    
    jd_input = st.text_area("📋 Paste the Job Description here:", height=200, key="jd_area")

    if "questions" not in st.session_state:
        st.session_state.questions = []
        st.session_state.results = None

    # 1. GENERATION LOGIC
    if st.button("🚀 Generate Questions"):
        if not jd_input.strip():
            st.warning("Please paste the Job Description first!")
        else:
            with st.spinner("Analyzing JD and generating questions..."):
                prompt = f"""
                Act as a Technical Interviewer. Analyze this JD and generate EXACTLY 5 challenging technical questions.
                Format:
                Q1: [Question]
                Q2: [Question]
                Q3: [Question]
                Q4: [Question]
                Q5: [Question]


 
 

                JD: {jd_input}
                """
                raw_text = get_ollama_response(prompt)
                
                if "ERROR" not in raw_text:
                    # Cleanly extract only the questions
                    st.session_state.questions = re.findall(r"Q\d+: (.*?)(?=Q\d+:|$)", raw_text, re.S)
                    st.session_state.results = None
                    st.rerun()

    # 2. INTERVIEW FORM
    if st.session_state.questions:
        st.divider()
        with st.form("interview_form"):
            responses = []
            for i, q in enumerate(st.session_state.questions):
                st.markdown(f"**Question {i+1}:** {q.strip()}")
                responses.append(st.text_area(f"Your Answer {i+1}", key=f"ans_{i}"))
            
            if st.form_submit_button("✅ Evaluate My Answers"):
                with st.spinner("AI is checking your accuracy..."):
                    # The evaluation prompt now asks the AI to judge based on JD knowledge
                    eval_prompt = f"""
                    You are an expert interviewer. Evaluate the user's answers against the following Job Description: for every answer-if the answer is well-aligned with the JD requirements, give it a high score(7-8). If it's partially aligned, give it a moderate score (4-6). If it's not aligned at all, give it a low score (0-2).
                    JD: {jd_input}

                    for each answer if the answer is not aligned with the JD, penalize it(0-2). Score each answer out of 10 based on how well it matches the JD requirements. Provide concise feedback for improvement.
                    """
                    for i in range(len(responses)):
                        eval_prompt += f"\nQ: {st.session_state.questions[i]}\nUser Answer: {responses[i]}\n"
                    
                    eval_prompt += "\nFormat: Q[Number]: [Score]/10 - [Feedback]"
                    
                    st.session_state.results = get_ollama_response(eval_prompt)
                    st.rerun()

    # 3. ACCURACY REPORT
    if st.session_state.results:
        st.success("### 📊 Accuracy Report")
        st.markdown(st.session_state.results)
        
        # Pull scores to sync with your Dashboard
        scores = re.findall(r'(\d+)/10', st.session_state.results)
        if scores:
            avg = sum(int(s) for s in scores) / len(scores)
            st.session_state.jd_score = int(avg * 10) # Storing 0-100 score
            st.metric("Overall Accuracy", f"{avg:.1f}/10")