from io import BytesIO
import streamlit as st

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except:
    letter = None
    canvas = None

from modules.ats_scorer import calculate_ats_score
from modules.interview_eval import evaluate_interview_answer
from modules.interview_gen import generate_interview_questions
from modules.job_api import fetch_jobs
from modules.resume_improver import improve_resume_text, clean_resume_text, generate_latex_resume
from utils.parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CareerLens", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
body {background:#f8fafc;}
.block-container {padding-top: 90px; padding-bottom: 90px; max-width:1200px;}

.navbar {
    position: fixed;
    top:0; left:0; right:0;
    background:white;
    padding:16px 40px;
    border-bottom:1px solid #e2e8f0;
    z-index:1000;
    font-weight:700;
    font-size:20px;
}

.footer {
    position:fixed;
    bottom:0; left:0; right:0;
    background:white;
    border-top:1px solid #e2e8f0;
    padding:12px;
    text-align:center;
}
.footer a {
    margin:0 15px;
    color:#2563eb;
    text-decoration:none;
}

.card {
    background:white;
    padding:24px;
    border-radius:14px;
    border:1px solid #e2e8f0;
    box-shadow:0 4px 20px rgba(0,0,0,0.05);
    margin-bottom:20px;
}

.stat {
    text-align:center;
    padding:20px;
    border-radius:12px;
    border:1px solid #e2e8f0;
}
.stat h2 { margin:0; color:#2563eb; }
.stat p { color:#64748b; }

.tag {
    display:inline-block;
    padding:6px 12px;
    border-radius:20px;
    font-size:12px;
    margin:4px;
}
.match { background:#dcfce7; color:#166534; }
.miss { background:#fee2e2; color:#991b1b; }
.all { background:#dbeafe; color:#1e40af; }
</style>
""", unsafe_allow_html=True)

# ---------------- NAVBAR ----------------
st.markdown('<div class="navbar">CareerLens</div>', unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------
page = st.radio("", ["Dashboard", "Jobs", "Interview"], horizontal=True)

# ---------------- INPUT ----------------
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf"])

with col2:
    job_description = st.text_area("Job Description")

# ---------------- PROCESS ----------------
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    skills = extract_skills(text)

    result = None
    if job_description:
        result = calculate_ats_score(text, job_description)

    # ================= DASHBOARD =================
    if page == "Dashboard":
        st.header("Career Dashboard")
        st.caption("AI-powered insights based on your resume")

        if result:
            c1, c2, c3 = st.columns(3)

            with c1:
                st.markdown(f'<div class="stat"><h2>{result["score"]}%</h2><p>ATS Score</p></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="stat"><h2>{len(result["matched_skills"])}</h2><p>Matched</p></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="stat"><h2>{len(result["missing_skills"])}</h2><p>Missing</p></div>', unsafe_allow_html=True)

            # CARD
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Resume Analysis")

            # Progress bar
            st.progress(result['score'] / 100)

            # Skills
            st.write("Detected")
            for s in skills:
                st.markdown(f'<span class="tag all">{s}</span>', unsafe_allow_html=True)

            st.write("Matched")
            for s in result["matched_skills"]:
                st.markdown(f'<span class="tag match">{s}</span>', unsafe_allow_html=True)

            st.write("Missing")
            for s in result["missing_skills"]:
                st.markdown(f'<span class="tag miss">{s}</span>', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Resume Improve
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Improve Resume")

        if st.button("Improve Resume"):
            st.session_state["improved"] = improve_resume_text(text)

        if "improved" in st.session_state:
            st.text_area("", st.session_state["improved"], height=250)

            cleaned = clean_resume_text(st.session_state["improved"])

            col1, col2 = st.columns(2)

            with col1:
                if letter:
                    pdf = BytesIO()
                    pdf_canvas = canvas.Canvas(pdf, pagesize=letter)
                    for i, line in enumerate(cleaned.split("\n")):
                        pdf_canvas.drawString(40, 750 - i*15, line)
                    pdf_canvas.save()
                    st.download_button("Download PDF", pdf.getvalue(), "resume.pdf")

            with col2:
                latex = generate_latex_resume(cleaned)
                st.download_button("Download LaTeX", latex, "resume.tex")

        st.markdown('</div>', unsafe_allow_html=True)

    # ================= JOBS =================
    elif page == "Jobs":
        st.header("Job Finder")

        role = st.selectbox("Role", ["Data Analyst","Data Scientist","ML Engineer"])
        city = st.selectbox("City", ["Mumbai","Pune","Remote"])

        if st.button("Find Jobs"):
            jobs = fetch_jobs(role, city)

            for job in jobs:
                st.markdown(f"""
                <div class="card">
                    <b>{job['title']}</b><br>
                    {job['company']}<br>
                    <small>{job['location']}</small><br><br>
                    <a href="{job.get('apply_link','#')}">Apply</a>
                </div>
                """, unsafe_allow_html=True)

    # ================= INTERVIEW =================
    elif page == "Interview":
        st.header("Interview Prep")

        role = st.selectbox("Role", ["Data Analyst","ML Engineer"])

        if st.button("Generate Questions"):
            st.session_state["qs"] = generate_interview_questions(role, skills)

        if "qs" in st.session_state:
            for i, q in enumerate(st.session_state["qs"]):
                st.markdown('<div class="card">', unsafe_allow_html=True)

                st.markdown(f"**Q{i+1}. {q}**")

                ans = st.text_area("Your Answer", key=f"a{i}")

                if st.button("Check Answer", key=f"check_{i}"):
                    res = evaluate_interview_answer(q, ans)
                    st.success(f"Score: {res['score']}/10")
                    st.write(res["feedback"])

                st.markdown('</div>', unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("""
<div class="footer">
    <a href="https://www.linkedin.com/in/mahek-shaikh-797767344/" target="_blank">LinkedIn</a>
    <a href="https://github.com/shaikh-mahek06" target="_blank">GitHub</a>
    <a href="mailto:shaikhmahek0604@gmail.com">Email</a>
</div>
""", unsafe_allow_html=True)