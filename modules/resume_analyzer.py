import streamlit as st
from PyPDF2 import PdfReader
import re
import requests

def get_ai_analysis(resume_text):
    """Sends resume text to local Llama 3.2 for ATS auditing."""
    url = "http://localhost:11434/api/generate"
    
    prompt = f"""
    Act as an ATS Auditor. Analyze this resume: {resume_text}

    STEP 1: SECTION SCORES
    - Summary: [10 or 0]
    - Education: [10 or 0]
    - Skills: [10 or 0]
    - Projects: [10 or 0]
    - Experience: [10 or 0]
    - Achievements: [10 or 0]
    - Certifications: [10 or 9]
    - Keywords: [10 or 0]
    - Formatting: [10 or 9]
    - Contact Information: [10 or 9]
    FINAL_TOTAL_SCORE: [Sum]/100   

    Logic: If a section is missing, give 0. If present, give 5-10 based on completeness and relevance.
        the score should be based on how well the resume meets ATS standards. A perfect resume with all sections and strong content gets 100. A resume missing key sections or with poor formatting scores much lower. Be strict but fair in scoring.

    STEP 2: GAP ANALYSIS
    identify the misssing sections
    Identify what is missing or needs improvement.

    STEP 3: OVERALL FEEDBACK
    Provide a final professional summary.

     
    """ 
    payload = {"model": "llama3.2", "prompt": prompt, "stream": False}
    try:
        response = requests.post(url, json=payload, timeout=90)
        return response.json().get('response', "") if response.status_code == 200 else "ERROR: API Failure"
    except Exception as e:
        return f"ERROR: {str(e)}"

def app():
    st.header("📄 AI Resume Intelligence")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

    if uploaded_file and st.button("🚀 Run Analysis"):
        with st.spinner("Analyzing resume content..."):
            reader = PdfReader(uploaded_file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            
            report = get_ai_analysis(text)
            
            if "ERROR" in report:
                st.error(report)
            else:
                # --- FIXED EXTRACTION LOGIC FOR DECIMALS ---
                score = 0.0
                
                # This Regex pattern now captures whole numbers AND decimals (like 76.5)
                # It specifically looks for the number following 'FINAL TOTAL SCORE'
                score_match = re.search(r"FINAL_TOTAL_SCORE[:\*]*\s*([0-9]*\.?[0-9]+)", report, re.IGNORECASE)

                if score_match:
                    score = float(score_match.group(1))
                else:
                    # Fallback: find any number followed by /100 that might be a decimal
                    fallback_match = re.search(r"([0-9]*\.?[0-9]+)\s*/\s*100", report)
                    if fallback_match:
                        score = float(fallback_match.group(1))

                st.session_state.ats_score = score
                
                # --- UI DISPLAY ---
                # Using st.metric with the float value
                st.metric("Total ATS Score", f"{score}/100")
                
                # Progress bar needs a float between 0.0 and 1.0
                progress_val = min(float(score) / 100.0, 1.0)
                st.progress(progress_val)

                st.divider()

                st.subheader("🤝 Overall Analysis")
                st.success(report.strip()) 

if __name__ == "__main__":
    app()