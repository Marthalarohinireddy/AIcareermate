import streamlit as st
import plotly.express as px
import pandas as pd

def app():
    # 1. Fetch real scores from session state (Default to 0 if not yet attempted)
    # These keys are synced across your local AI modules
    scores_data = {
        "Module": ["Resume", "Aptitude", "Technical", "HR Round", "JD Match"],
        "Score": [
            st.session_state.get('ats_score', 0), 
            st.session_state.get('apti_score', 0),
            st.session_state.get('tech_score', 0),
            st.session_state.get('hr_score', 0),
            st.session_state.get('jd_score', 0)
        ]
    }
    df = pd.DataFrame(scores_data)
    
    # 2. Calculate performance for attempted tests (scores > 0)
    attempted = df[df['Score'] > 0]
    avg_score = attempted["Score"].mean() if not attempted.empty else 0

    st.markdown("### 📊 PLACEMENT READINESS SCORECARD")
    
    # Top Row Metrics - Displays the current standing for each module
    cols = st.columns(5)
    for i, col in enumerate(cols):
        module_name = df["Module"][i]
        score_val = df["Score"][i]
        col.metric(module_name, f"{score_val}%")

    st.divider()

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("#### 🎯 SKILL SPREAD")
        if avg_score > 0:
            # Donut chart showing the balance of your career skills
            fig = px.pie(
                df, values='Score', names='Module', hole=0.6,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(textinfo='percent+label', hoverinfo='label+value', textfont_size=12)
            fig.update_layout(
                showlegend=False, 
                margin=dict(t=10, b=10, l=10, r=10),
                paper_bgcolor='rgba(0,0,0,0)',
                annotations=[dict(text=f'{int(avg_score)}%', x=0.5, y=0.5, font_size=24, showarrow=False, font_color="#1e293b")]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🚀 Welcome! Your readiness chart will appear here once you complete any local AI module.")

    with right:
        st.markdown("#### 💡 PLACEMENT FEEDBACK")
        if avg_score == 0:
            st.warning("No data found. Start with the **Resume AI** or **Aptitude** to begin your assessment.")
        else:
            # Identification of weakest and strongest areas
            weakest_row = attempted.loc[attempted['Score'].idxmin()]
            strongest_row = attempted.loc[attempted['Score'].idxmax()]
            
            # Dynamic Readiness Status
            if avg_score >= 75:
                status_color, status_text = "#16a34a", "READY FOR INTERVIEW"
            elif avg_score >= 50:
                status_color, status_text = "#ca8a04", "NEEDS PRACTICE"
            else:
                status_color, status_text = "#dc2626", "NOT READY"

            st.markdown(f"""
            <div style="background-color: #f8fafc; padding: 25px; border-radius: 15px; border: 1px solid #e2e8f0;">
                <p style="font-size: 0.9rem; color: #64748b; margin-bottom: 5px;">OVERALL STATUS</p>
                <h2 style="color: {status_color}; margin-top: 0px;">{status_text}</h2>
                <p style="font-size: 1.1rem; color: #1e293b;"><b>Average Readiness: {avg_score:.1f}%</b></p>
                <hr style="border: 0.1px solid #e2e8f0; margin: 15px 0;">
                <p style="color: #dc2626; font-size: 0.95rem;">🚩 <b>Priority:</b> Focus on <b>{weakest_row['Module']}</b> ({weakest_row['Score']}%). This is currently your lowest performing area.</p>
                <p style="color: #16a34a; font-size: 0.95rem;">🌟 <b>Ace:</b> You are strongest in <b>{strongest_row['Module']}</b>. Keep it up!</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Reset functionality for clean testing
            if st.button("🗑️ Reset All Scores"):
                for key in ['ats_score', 'apti_score', 'tech_score', 'hr_score', 'jd_score']:
                    if key in st.session_state:
                        st.session_state[key] = 0
                st.rerun()

    st.markdown("---")
    st.caption("Data is stored locally in your session state and resets upon logout.")