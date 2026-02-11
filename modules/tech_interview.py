import streamlit as st
import re
import requests

def get_combined_questions(role):
    """Forces Llama 3.2 to generate both MCQs and Theory/Coding tasks."""
    url = "http://localhost:11434/api/generate"
    
    # Precise prompt with markers to prevent the AI from stopping early
    prompt = f"""
    Act as a Senior Technical Lead. Generate exactly 20 technical questions for a {role} role.
    
    SECTION_1_MCQ:
    Provide 10 MCQs. Format: M1: [Question/Code] A) [..] B) [..] C) [..] D) [..] ANS: [Letter]
    the questions and be releted to the role  and the option should be related to the question and the answer should be correct and relevant to the question.and the option will not repated in the same question and the answer should be one of the option and the question should be clear and concise and the question should not be too long and not too short and the question should be related to the role and the question should be challenging but not impossible

    SECTION_2_THEORY:
    Provide 10 text-based Coding or Theory tasks. Format: T1: [Question/Task]  

    You MUST generate both sections. Use code snippets in both parts.
    """
    
    payload = {"model": "llama3.2", "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=180)
        return response.json().get('response', "") if response.status_code == 200 else "ERROR"
    except Exception as e:
        return f"ERROR: {str(e)}"

def app():
    st.header("💻 Technical Assessment (MCQ + Theory)")
    role = st.selectbox("Target Role", ["Python Developer", "Full Stack Developer", "Data Scientist", "DevOps Engineer", "Machine Learning Engineer"])

    if "tech_qs" not in st.session_state:
        st.session_state.tech_qs = None
        st.session_state.tech_submitted = False

    if st.button("🚀 Generate 20-Question Assessment"):
        with st.spinner("Building your interview..."):
            data = get_combined_questions(role)
            if "ERROR" in data:
                st.error("Ollama connection failed.")
            else:
                st.session_state.tech_qs = data
                # Extract MCQ Answer Key immediately
                st.session_state.mcq_key = re.findall(r"ANS:\s*([A-D])", data)
                st.session_state.tech_submitted = False
                st.rerun()

    if st.session_state.tech_qs and not st.session_state.tech_submitted:
        raw_data = st.session_state.tech_qs
        
        # Robust Regex to capture questions even if AI formatting varies
        mcq_items = re.findall(r"M\d+:(.*?)(?=M\d+:|SECTION_2_THEORY|T\d+:|$)", raw_data, re.S)
        theory_items = re.findall(r"T\d+:(.*?)(?=T\d+:|Ideal|$)", raw_data, re.S)

        with st.form("unified_interview_form"):
            st.subheader("📝 Part 1: MCQs")
            u_mcq_ans = []
            for i, q_text in enumerate(mcq_items[:10]):
                clean_q = q_text.split("ANS:")[0].strip()
                st.markdown(f"QM{i+1}:")
                st.code(clean_q) # Display code snippets properly
                u_mcq_ans.append(st.radio(f"Select Choice for M{i+1}", ["A", "B", "C", "D"], index=None, key=f"m_{i}", horizontal=True))
            
            st.divider()
            st.subheader("⌨️ Part 2: Theory & Practical Coding")
            u_theory_ans = []
            if not theory_items:
                st.warning("⚠️ Parsing error. Try generating again.")
            else:
                for i, q_text in enumerate(theory_items[:10]):
                    st.markdown(f"QT{i+1}: {q_text.strip()}") # Question text now correctly displays
                    u_theory_ans.append(st.text_area(f"Your Answer {i+1}", key=f"t_{i}", height=100))
            
            if st.form_submit_button("Submit & Calculate Accuracy"):
                # VALIDATION: Prevents hallucinated scores by blocking empty submits
                incomplete_mcq = any(x is None for x in u_mcq_ans)
                incomplete_theory = any(len(x.strip()) < 5 for x in u_theory_ans)

                if incomplete_mcq or incomplete_theory:
                    st.error("⚠️ Stop! Please answer all 20 questions (MCQs and Theory) to get your accuracy report.")
                else:
                    st.session_state.tech_submitted = True
                    st.session_state.u_mcq = u_mcq_ans
                    st.session_state.u_theory = u_theory_ans
                    st.rerun()

    if st.session_state.get("tech_submitted"):
        st.success("### 📊 Result")
        
        # 1. Calculate MCQ score (Weighted 50%)
        correct_count = sum(1 for i, choice in enumerate(st.session_state.u_mcq) if choice == st.session_state.mcq_key[i])
        mcq_points = (correct_count / 10) * 50

        # 2. AI Grading for Theory (Weighted 50%)
        with st.spinner("Llama 3.2 is grading your written answers..."):
            grade_prompt = f"""
            Grade these technical answers for a {role} role.
            the answer should be graded based on technical accuracy, depth of explanation, and relevance to the question. if the answer is correct and relevant to the question, give it a high score. if the answer is partially correct or lacks depth, give it a moderate score. if the answer is incorrect or irrelevant, give it a too low score.
            Final line MUST be: 'THEORY_SCORE: [Sum]/50'
            Answers: {st.session_state.u_theory}
            """
            try:
                res = requests.post("http://localhost:11434/api/generate", json={"model": "llama3.2", "prompt": grade_prompt, "stream": False})
                feedback = res.json().get('response', "")
                
                theory_match = re.search(r'THEORY_SCORE:\s*(\d+)', feedback)
                theory_points = int(theory_match.group(1)) if theory_match else 0
                
                total_percentage = int(mcq_points + theory_points)
                st.session_state.tech_score = total_percentage
                
                # Display Results
                st.metric("Total Technical Accuracy", f"{total_percentage}%")
                st.markdown(feedback.replace("Student", "Answer")) # term adjustment
                
            except:
                st.error("Grading failed.")