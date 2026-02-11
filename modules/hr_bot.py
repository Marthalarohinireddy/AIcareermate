import streamlit as st
from streamlit_mic_recorder import mic_recorder
import re
import requests
import json

def get_hr_feedback(questions, answers):
    """Sends all responses to local Ollama (Llama 3.2) for HR evaluation."""
    url = "http://localhost:11434/api/generate"
    
    combined_text = ""
    for q, a in zip(questions, answers):
        combined_text += f"Q: {q}\nA: {a}\n---\n"
    
    prompt = f"""
    Act as an HR Director. Evaluate these 5 interview responses.
    For each answer, provide:
    
    - Feedback: (1 concise sentence)
    
 
    
    RESPONSES:
    {combined_text}
    """
    
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
            return f"Error: Ollama status {response.status_code}"
    except Exception as e:
        return f"Local Connection Error: {str(e)}"

def app():
    st.header("🤝 HR Interview")

    hr_questions = [
        "Tell me about yourself and your background.",
        "What is your greatest professional strength and how does it help you?",
        "Describe a time you handled a conflict with a teammate.",
        "Why do you want to work for this specific company?",
        "Where do you see yourself in the next 5 years?"
    ]

    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'hr_answers' not in st.session_state:
        st.session_state.hr_answers = []
    # Store calculated scores based on duration
    if 'voice_scores' not in st.session_state:
        st.session_state.voice_scores = []

    if st.session_state.current_step >= len(hr_questions):
        st.success("🎉 Interview Completed!")
        with st.spinner("Local Llama 3.2 is evaluating..."):
            feedback_text = get_hr_feedback(hr_questions, st.session_state.hr_answers)
            
            if "Error" in feedback_text:
                st.error(feedback_text)
            else:
                st.markdown("### 📊 Performance Report")
                
                # Logic: If voice was used, override AI score with your duration logic
                if st.session_state.voice_scores:
                    # Average of the duration-based scores
                    final_pct = sum(st.session_state.voice_scores) / len(st.session_state.voice_scores)
                else:
                    # Fallback to AI extraction if only text was used
                    match = re.search(r"OVERALL_HIREABILITY:\s*(\d+)%", feedback_text)
                    final_pct = int(match.group(1)) if match else 0

                st.session_state.hr_score = final_pct
                st.metric("Hireability Rating", f"{final_pct}%")
                st.progress(final_pct / 100)
                st.info(feedback_text)

        if st.button("🔄 Restart Interview"):
            st.session_state.current_step = 0
            st.session_state.hr_answers = []
            st.session_state.voice_scores = []
            st.rerun()
        return

    progress = (st.session_state.current_step) / len(hr_questions)
    st.progress(progress)
    st.write(f"**Question {st.session_state.current_step + 1} of 5**")
    
    current_q = hr_questions[st.session_state.current_step]
    st.subheader(current_q)

    tab1, tab2 = st.tabs(["💬 Text Mode", "🎤 Voice Mode"])
    
    with tab1:
        text_ans = st.text_area("Type your response here:", key=f"text_{st.session_state.current_step}")
        if st.button("Submit Text Answer"):
            if text_ans.strip():
                st.session_state.hr_answers.append(text_ans)
                st.session_state.current_step += 1
                st.rerun()

    with tab2:
        st.write("Record your voice answer:")
        audio = mic_recorder(
            start_prompt="Start Recording", 
            stop_prompt="Stop & Save", 
            key=f"mic_{st.session_state.current_step}"
        )
        
        if audio:
            st.audio(audio['bytes'])
            if st.button("Confirm Voice Answer"):
                # Estimate duration based on byte size
                audio_size = len(audio['bytes'])
                
                # 12MB is approx 2 minutes; 100KB is approx 10 seconds (depending on encoding)
                # We use a threshold to apply your 80% or 5% rule
                if audio_size > 12000000: # Over 2 mins
                    score_impact = 85 
                elif audio_size < 300000: # Under 10 seconds
                    score_impact = 5
                else:
                    score_impact = 60 # Default middle ground
                
                st.session_state.voice_scores.append(score_impact)
                st.session_state.hr_answers.append(f"[Voice Recorded: {audio_size} bytes]")
                st.session_state.current_step += 1
                st.rerun()