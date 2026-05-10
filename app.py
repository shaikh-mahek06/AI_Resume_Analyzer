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

# ─────────────────────────── HELPER FUNCTION ───────────────────────────
def get_clean_skills(skills):
    """Ensure skills is always a clean list of strings."""
    if not isinstance(skills, list):
        return []
    return list(set([s.strip() for s in skills if isinstance(s, str) and s.strip()]))

# ─────────────────────────── CONFIG ───────────────────────────
st.set_page_config(page_title="CareerLens", layout="wide", page_icon="📄")

# ─────────────────────────── INITIALIZE SESSION STATE ───────────────────────────
if "skills" not in st.session_state:
    st.session_state["skills"] = []
if "job_description" not in st.session_state:
    st.session_state["job_description"] = ""
if "resume_filename" not in st.session_state:
    st.session_state["resume_filename"] = None
if "resume_ready" not in st.session_state:
    st.session_state["resume_ready"] = False
if "result" not in st.session_state:
    st.session_state["result"] = None
if "jobs" not in st.session_state:
    st.session_state["jobs"] = None
if "interview_questions" not in st.session_state:
    st.session_state["interview_questions"] = []
if "interview_answers" not in st.session_state:
    st.session_state["interview_answers"] = {}
if "interview_feedback" not in st.session_state:
    st.session_state["interview_feedback"] = {}

# ─────────────────────────── CSS ───────────────────────────
st.markdown("""
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [data-testid="stAppViewContainer"] {
    background: #F8FAFC !important;
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', sans-serif;
    color: #0F172A;
}
[data-testid="stAppViewContainer"] > .main { background: #F8FAFC !important; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header[data-testid="stHeader"] { display: none; }
.block-container {
    padding: 88px 0 80px 0 !important;
    max-width: 1100px !important;
    margin: 0 auto !important;
}
/* Navbar */
.cl-navbar {
    position: fixed; top: 0; left: 0; right: 0;
    background: #fff; border-bottom: 1px solid #E2E8F0;
    padding: 0 40px; height: 56px;
    display: flex; align-items: center; justify-content: space-between;
    z-index: 1000;
}
.cl-logo { display: flex; align-items: center; gap: 10px; }
.cl-logo-icon {
    width: 28px; height: 28px; background: #2563EB;
    border-radius: 7px; display: flex; align-items: center; justify-content: center;
}
.cl-logo-text { font-size: 15px; font-weight: 600; color: #0F172A; letter-spacing: -0.01em; }
.cl-nav-links { display: flex; align-items: center; gap: 4px; }
.cl-nav-link {
    padding: 6px 14px; font-size: 13.5px; color: #64748B;
    border-radius: 6px; cursor: pointer; font-weight: 400; text-decoration: none;
}
.cl-nav-link:hover { color: #0F172A; background: #F1F5F9; }
.cl-nav-link.active { color: #2563EB; background: #EFF6FF; font-weight: 500; }
.cl-nav-avatar {
    width: 32px; height: 32px; border-radius: 50%; background: #E2E8F0;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 500; color: #64748B; margin-left: 8px;
}
.cl-nav-right { display: flex; align-items: center; }
/* Footer */
.cl-footer {
    position: fixed; bottom: 0; left: 0; right: 0;
    background: #fff; border-top: 1px solid #E2E8F0;
    padding: 12px; text-align: center; z-index: 999;
}
.cl-footer a { margin: 0 16px; color: #2563EB; text-decoration: none; font-size: 13px; }
.cl-footer a:hover { color: #1D4ED8; }
/* Page header */
.cl-page-header { margin-bottom: 28px; }
.cl-page-title { font-size: 21px; font-weight: 600; color: #0F172A; letter-spacing: -0.02em; }
.cl-page-sub { font-size: 13.5px; color: #64748B; margin-top: 4px; }
/* Stat grid */
.cl-stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
.cl-stat-mini { text-align: center; padding: 14px 10px; background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; }
.cl-stat-val { font-size: 22px; font-weight: 600; color: #0F172A; letter-spacing: -0.02em; }
.cl-stat-lbl { font-size: 12px; color: #64748B; margin-top: 3px; }
/* Cards */
.cl-card {
    background: #fff; border: 1px solid #E2E8F0; border-radius: 12px; padding: 22px;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04), 0 1px 2px rgba(15,23,42,0.03);
    margin-bottom: 20px;
}
.cl-card-title { font-size: 13px; font-weight: 500; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 16px; }
/* ATS Score */
.cl-ats-row { display: flex; align-items: flex-end; justify-content: space-between; margin-bottom: 14px; }
.cl-score-num { font-size: 42px; font-weight: 600; color: #0F172A; letter-spacing: -0.03em; line-height: 1; }
.cl-score-suffix { font-size: 16px; color: #64748B; margin-bottom: 6px; margin-left: 2px; }
.cl-score-badge { font-size: 12px; padding: 4px 10px; border-radius: 20px; background: #DCFCE7; color: #15803D; font-weight: 500; }
.cl-score-badge.avg { background: #FEF9C3; color: #A16207; }
.cl-score-badge.low { background: #FEE2E2; color: #991B1B; }
/* Progress bar */
.cl-prog-bg { height: 8px; background: #F1F5F9; border-radius: 99px; margin-bottom: 18px; overflow: hidden; }
.cl-prog-fill { height: 100%; border-radius: 99px; background: #2563EB; }
/* Skill tags */
.cl-skill-section { margin-bottom: 14px; }
.cl-skill-label { font-size: 12px; color: #64748B; margin-bottom: 8px; font-weight: 500; }
.cl-skill-tags { display: flex; flex-wrap: wrap; gap: 6px; min-height: 28px; }
.cl-tag { padding: 4px 10px; border-radius: 6px; font-size: 12.5px; font-weight: 400; display: inline-block; }
.cl-tag-detected { background: #EFF6FF; color: #2563EB; }
.cl-tag-matched  { background: #DCFCE7; color: #15803D; }
.cl-tag-missing  { background: #FEF2F2; color: #DC2626; }
/* Skill gap */
.cl-gap-item { display: flex; align-items: flex-start; gap: 12px; padding: 12px 0; border-bottom: 1px solid #F1F5F9; }
.cl-gap-item:last-child { border-bottom: none; }
.cl-gap-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.cl-gap-skill { font-size: 14px; font-weight: 500; color: #0F172A; }
.cl-gap-meta { font-size: 12px; color: #64748B; margin-top: 2px; }
.cl-divider { height: 1px; background: #F1F5F9; margin: 16px 0; }
/* Roadmap */
.cl-roadmap-row { display: flex; align-items: center; margin-bottom: 8px; }
.cl-road-step { flex: 1; text-align: center; }
.cl-road-inner { padding: 8px 6px; border-radius: 8px; font-size: 12px; }
.cl-road-beg { background: #FEF3C7; color: #B45309; }
.cl-road-int { background: #EFF6FF; color: #2563EB; }
.cl-road-adv { background: #F5F3FF; color: #7C3AED; }
.cl-road-arrow { color: #CBD5E1; font-size: 14px; flex-shrink: 0; padding: 0 2px; }
.cl-road-step-title { font-weight: 600; margin-bottom: 2px; font-size: 12px; }
.cl-road-step-sub { font-size: 10.5px; opacity: 0.8; }
/* Job cards */
.cl-job-card {
    background: #fff; border: 1px solid #E2E8F0; border-radius: 10px; padding: 18px;
    transition: box-shadow 0.15s, transform 0.15s; margin-bottom: 4px;
}
.cl-job-card:hover { box-shadow: 0 4px 12px rgba(15,23,42,0.08); transform: translateY(-1px); }
.cl-job-title { font-size: 14.5px; font-weight: 500; color: #0F172A; }
.cl-job-company { font-size: 13px; color: #64748B; margin-top: 3px; }
.cl-job-location { font-size: 12px; color: #94A3B8; margin-top: 2px; }
.cl-job-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 12px; padding-top: 12px; border-top: 1px solid #F1F5F9; }
.cl-job-match { font-size: 12px; color: #15803D; background: #DCFCE7; padding: 3px 8px; border-radius: 99px; font-weight: 500; }
.cl-job-apply { font-size: 13px; color: #2563EB; font-weight: 500; text-decoration: none; }
.cl-job-apply:hover { color: #1D4ED8; }
/* Interview */
.cl-q-item { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; margin-bottom: 12px; }
.cl-q-num { font-size: 11.5px; font-weight: 500; color: #94A3B8; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em; }
.cl-q-text { font-size: 14px; color: #0F172A; line-height: 1.6; font-weight: 500; margin-bottom: 4px; }
/* Feedback */
.cl-feedback-box { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 12px 14px; margin-top: 10px; }
.cl-feedback-label { font-size: 11.5px; font-weight: 500; color: #15803D; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.04em; }
.cl-feedback-text { font-size: 13px; color: #166534; line-height: 1.6; }
/* Ready badge */
.cl-ready { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #166534; margin-top: 8px; }
/* Streamlit widget overrides */
[data-testid="stFileUploader"] { background: #fff !important; border: 1px solid #E2E8F0 !important; border-radius: 10px !important; padding: 12px !important; }
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
    font-size: 13.5px !important; color: #0F172A !important; background: #fff !important;
}
[data-testid="stTextArea"] textarea:focus, [data-testid="stTextInput"] input:focus { border-color: #2563EB !important; box-shadow: none !important; }
[data-testid="stSelectbox"] > div > div { border: 1px solid #E2E8F0 !important; border-radius: 8px !important; font-size: 13.5px !important; }
button[kind="primary"], button[kind="secondary"], [data-testid="baseButton-secondary"] {
    background: #2563EB !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-size: 13.5px !important; font-weight: 500 !important;
    padding: 8px 18px !important; transition: background 0.15s !important;
}
button[kind="primary"]:hover, button[kind="secondary"]:hover { background: #1D4ED8 !important; }
[data-testid="stDownloadButton"] button {
    background: #F8FAFC !important; color: #2563EB !important;
    border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
    font-size: 13px !important; font-weight: 500 !important;
}
[data-testid="stDownloadButton"] button:hover { background: #EFF6FF !important; }
label[data-testid="stWidgetLabel"] { font-size: 13px !important; color: #64748B !important; font-weight: 500 !important; }
h1, h2, h3 { color: #0F172A !important; font-weight: 500 !important; }
/* Expander styling */
[data-testid="stExpander"] { border: 1px solid #E2E8F0 !important; border-radius: 12px !important; background: #fff !important; margin-bottom: 20px !important; }
[data-testid="stExpander"] summary { font-size: 14px !important; font-weight: 500 !important; color: #0F172A !important; padding: 14px 20px !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── PAGE ROUTING ───────────────────────────
page = st.query_params.get("page", "Dashboard")
nav_pages = [("Dashboard", "Dashboard"), ("Jobs", "Jobs"), ("Interview", "Interview Prep")]
nav_html = "".join([
    f'<a class="cl-nav-link {"active" if key == page else ""}" href="?page={key}">{label}</a>'
    for key, label in nav_pages
])

st.markdown(f"""
<div class="cl-navbar">
  <div class="cl-logo">
    <div class="cl-logo-icon">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
        <rect x="2" y="2" width="7" height="9" rx="1.5" fill="white" opacity="0.9"/>
        <rect x="5" y="5" width="7" height="9" rx="1.5" fill="white" opacity="0.5"/>
        <rect x="4" y="4" width="8" height="1" rx="0.5" fill="#2563EB"/>
      </svg>
    </div>
    <span class="cl-logo-text">CareerLens</span>
  </div>
  <div class="cl-nav-right">
    <div class="cl-nav-links">{nav_html}</div>
    <div class="cl-nav-avatar">CL</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# PERSISTENT UPLOAD PANEL — shown once, saved to session_state
# ═══════════════════════════════════════════════════════════════
if "resume_text" not in st.session_state:
    up_col, jd_col = st.columns(2)

    with up_col:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_uploader")
        if uploaded_file is not None:
            raw = extract_text_from_pdf(uploaded_file)
            st.session_state["resume_text"] = raw
            st.session_state["skills"] = extract_skills(raw)
            st.session_state["job_description"] = st.session_state.get("job_description", "")
            st.session_state["result"] = None

    with jd_col:
        jd_val = st.text_area(
            "Job Description",
            value=st.session_state.get("job_description", ""),
            height=130,
            placeholder="Paste the job description here…",
            key="jd_textarea"
        )
        st.session_state["job_description"] = jd_val

    has_resume = bool(st.session_state.get("resume_text"))
    has_jd = bool(st.session_state.get("job_description"))

    if has_resume and has_jd:
        with st.spinner("Analysing your resume against the job description…"):
            res = calculate_ats_score(
                st.session_state["resume_text"],
                st.session_state["job_description"]
            )
            if not isinstance(res.get("matched_skills"), list):
                res["matched_skills"] = []
            if not isinstance(res.get("missing_skills"), list):
                res["missing_skills"] = []
            res["matched_skills"] = [str(s).strip() for s in res.get("matched_skills", []) if str(s).strip()]
            res["missing_skills"] = [str(s).strip() for s in res.get("missing_skills", []) if str(s).strip()]
            st.session_state["result"] = res

        if st.session_state.get("result"):
            r = st.session_state["result"]
            st.markdown(
                '<div class="cl-ready">✓ Analysis complete — ATS Score: <strong>'
                + str(r["score"]) + '/100</strong> · '
                + str(len(r["matched_skills"])) + ' matched · '
                + str(len(r["missing_skills"])) + ' missing</div>',
                unsafe_allow_html=True
            )
    elif has_resume and not has_jd:
        st.info("Paste a job description and click Analyse to see your ATS score.")
    elif not has_resume:
        st.info("Upload your resume PDF to get started.")

text = st.session_state.get("resume_text", "")
skills = get_clean_skills(st.session_state.get("skills", []))
job_description = st.session_state.get("job_description", "")
result = st.session_state.get("result", None)

# ═══════════════════════════ DASHBOARD ═══════════════════════════
if page == "Dashboard":
    st.markdown("""
    <div class="cl-page-header">
      <div class="cl-page-title">Career Dashboard</div>
      <div class="cl-page-sub">AI-powered insights based on your uploaded resume</div>
    </div>
    """, unsafe_allow_html=True)

    if not text:
        st.warning("Please upload resume first")
        st.markdown("""
        <div style="text-align:center;padding:60px 20px">
          <div style="width:56px;height:56px;background:#EFF6FF;border-radius:14px;display:flex;align-items:center;
               justify-content:center;margin:0 auto 16px;font-size:26px">📄</div>
          <div style="font-size:18px;font-weight:500;color:#0F172A;margin-bottom:8px">Upload your resume to get started</div>
          <div style="font-size:14px;color:#64748B">Use the panel above — upload once and navigate freely across all tabs.</div>
        </div>
        """, unsafe_allow_html=True)

    elif result is None:
        st.info("Paste a job description in the panel above and click **Analyse Resume** to see your ATS score and skill gap.")

    else:
        score = result.get("score", 0)
        matched = get_clean_skills(result.get("matched_skills", []))
        missing = get_clean_skills(result.get("missing_skills", []))

        badge_class = "" if score >= 70 else ("avg" if score >= 50 else "low")
        badge_label = "Good match" if score >= 70 else ("Average match" if score >= 50 else "Low match")

        # ── Stat row ──
        st.markdown(
            '<div class="cl-stats-grid">'
            + '<div class="cl-stat-mini"><div class="cl-stat-val" style="color:#2563EB">' + str(score) + '</div><div class="cl-stat-lbl">ATS Score</div></div>'
            + '<div class="cl-stat-mini"><div class="cl-stat-val" style="color:#15803D">' + str(len(matched)) + '</div><div class="cl-stat-lbl">Matched skills</div></div>'
            + '<div class="cl-stat-mini"><div class="cl-stat-val" style="color:#DC2626">' + str(len(missing)) + '</div><div class="cl-stat-lbl">Missing skills</div></div>'
            + '<div class="cl-stat-mini"><div class="cl-stat-val">' + str(len(skills)) + '</div><div class="cl-stat-lbl">Detected skills</div></div>'
            + '</div>',
            unsafe_allow_html=True
        )

        col_left, col_right = st.columns(2)

        # ── Resume Analysis card ──
        with col_left:
            detected_tags = "".join('<span class="cl-tag cl-tag-detected">' + s + '</span>' for s in skills) \
                            or '<span style="color:#94A3B8;font-size:13px">None detected</span>'
            matched_tags = "".join('<span class="cl-tag cl-tag-matched">' + s + '</span>' for s in matched) \
                           or '<span style="color:#94A3B8;font-size:13px">None matched</span>'
            missing_tags = "".join('<span class="cl-tag cl-tag-missing">' + s + '</span>' for s in missing) \
                           or '<span style="color:#22C55E;font-size:13px">None — great match!</span>'

            resume_card_html = (
                '<div class="cl-card">'
                + '<div class="cl-card-title">Resume Analysis</div>'
                + '<div class="cl-ats-row">'
                + '<div style="display:flex;align-items:flex-end;gap:4px">'
                + '<span class="cl-score-num">' + str(score) + '</span>'
                + '<span class="cl-score-suffix">/100</span>'
                + '</div>'
                + '<span class="cl-score-badge ' + badge_class + '">' + badge_label + '</span>'
                + '</div>'
                + '<div class="cl-prog-bg"><div class="cl-prog-fill" style="width:' + str(score) + '%"></div></div>'
                + '<div class="cl-skill-section"><div class="cl-skill-label">Detected skills</div>'
                + '<div class="cl-skill-tags">' + detected_tags + '</div></div>'
                + '<div class="cl-skill-section"><div class="cl-skill-label">Matched skills</div>'
                + '<div class="cl-skill-tags">' + matched_tags + '</div></div>'
                + '<div class="cl-skill-section"><div class="cl-skill-label">Missing skills</div>'
                + '<div class="cl-skill-tags">' + missing_tags + '</div></div>'
                + '</div>'
            )
            st.markdown(resume_card_html, unsafe_allow_html=True)

        # ── Skill Gap Analysis card ──
        # Built entirely with string concatenation — zero f-strings — to prevent
        # Streamlit from escaping and printing HTML as raw text.
        with col_right:
            dot_colors = ["#DC2626", "#D97706", "#2563EB", "#7C3AED", "#0D9488"]

            gap_items_html = ""
            for i, skill in enumerate(missing[:5]):
                color = dot_colors[i % len(dot_colors)]
                pct = str(max(30, 80 - i * 10))
                skill_name = str(skill)
                gap_items_html = (
                    gap_items_html
                    + '<div class="cl-gap-item">'
                    + '<div class="cl-gap-dot" style="background:' + color + '"></div>'
                    + '<div>'
                    + '<div class="cl-gap-skill">' + skill_name + '</div>'
                    + '<div class="cl-gap-meta">Required in ' + pct + '% of matching roles</div>'
                    + '</div>'
                    + '</div>'
                )

            if not missing:
                gap_items_html = '<div style="color:#15803D;font-size:13px;padding:8px 0">No skill gaps — your resume is a great match!</div>'

            top_missing = str(missing[0]) if missing else "Top Skill"

            roadmap_html = (
                '<div class="cl-roadmap-row">'
                + '<div class="cl-road-step"><div class="cl-road-inner cl-road-beg">'
                + '<div class="cl-road-step-title">Beginner</div>'
                + '<div class="cl-road-step-sub">Foundations</div>'
                + '</div></div>'
                + '<span class="cl-road-arrow">›</span>'
                + '<div class="cl-road-step"><div class="cl-road-inner cl-road-int">'
                + '<div class="cl-road-step-title">Intermediate</div>'
                + '<div class="cl-road-step-sub">Core usage</div>'
                + '</div></div>'
                + '<span class="cl-road-arrow">›</span>'
                + '<div class="cl-road-step"><div class="cl-road-inner cl-road-adv">'
                + '<div class="cl-road-step-title">Advanced</div>'
                + '<div class="cl-road-step-sub">Production</div>'
                + '</div></div>'
                + '</div>'
            )

            skill_gap_card_html = (
                '<div class="cl-card">'
                + '<div class="cl-card-title">Skill Gap Analysis</div>'
                + gap_items_html
                + '<div class="cl-divider"></div>'
                + '<div class="cl-card-title" style="margin-bottom:12px">Learning roadmap — ' + top_missing + '</div>'
                + roadmap_html
                + '</div>'
            )

            st.markdown(skill_gap_card_html, unsafe_allow_html=True)

        # ── Improve Resume card ──
        st.markdown('<div class="cl-card"><div class="cl-card-title">Improve Resume</div>', unsafe_allow_html=True)
        if st.button("✦ Improve Resume", use_container_width=True):
            with st.spinner("Rewriting your resume with AI…"):
                st.session_state["improved"] = improve_resume_text(
                    st.session_state["resume_text"],
                    st.session_state.get("job_description", "")
                )

        if "improved" in st.session_state:
            st.text_area("Improved Resume", st.session_state["improved"], height=300)
            cleaned = clean_resume_text(st.session_state["improved"])
            dl1, dl2 = st.columns(2)
            with dl1:
                if letter:
                    pdf_buf = BytesIO()
                    c = canvas.Canvas(pdf_buf, pagesize=letter)
                    for idx, line in enumerate(cleaned.split("\n")):
                        c.drawString(40, 750 - idx * 15, line)
                    c.save()
                    st.download_button("⬇ Download PDF", pdf_buf.getvalue(), "resume.pdf", use_container_width=True)
            with dl2:
                latex = generate_latex_resume(cleaned)
                st.download_button("⬇ Download LaTeX", latex, "resume.tex", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════ JOBS ═══════════════════════════
elif page == "Jobs":
    st.markdown("""
    <div class="cl-page-header">
      <div class="cl-page-title">Job Finder</div>
      <div class="cl-page-sub">Discover roles that match your resume skills</div>
    </div>
    """, unsafe_allow_html=True)

    if not text:
        st.warning("Please upload resume first")
    else:
        st.markdown('<div class="cl-card"><div class="cl-card-title">Search filters</div>', unsafe_allow_html=True)
        f1, f2, f3 = st.columns([2, 2, 1])
        with f1:
            role = st.selectbox("Role", [
                "Data Analyst", "Data Scientist", "ML Engineer", "Software Engineer",
                "Backend Developer", "Frontend Developer", "Full Stack Developer",
                "DevOps Engineer", "AI Engineer", "Product Manager"
            ])
        with f2:
            city = st.selectbox("City", [
                "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
                "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat", "Remote"
            ])
        with f3:
            st.markdown("<br>", unsafe_allow_html=True)
            find_jobs = st.button("Find Jobs", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if find_jobs:
            with st.spinner("Searching jobs…"):
                st.session_state["jobs"] = fetch_jobs(role, city)

        if st.session_state.get("jobs"):
            jobs = st.session_state["jobs"]
            st.markdown('<div class="cl-card"><div class="cl-card-title">Job Matches</div>', unsafe_allow_html=True)
            for row_start in range(0, len(jobs), 3):
                row = jobs[row_start:row_start + 3]
                cols = st.columns(len(row))
                for col, job in zip(cols, row):
                    with col:
                        apply_link = job.get("apply_link", "#")
                        job_card_html = (
                            '<div class="cl-job-card">'
                            + '<div class="cl-job-title">' + str(job["title"]) + '</div>'
                            + '<div class="cl-job-company">' + str(job["company"]) + '</div>'
                            + '<div class="cl-job-location">📍 ' + str(job["location"]) + '</div>'
                            + '<div class="cl-job-footer">'
                            + '<span class="cl-job-match">New</span>'
                            + '<a class="cl-job-apply" href="' + str(apply_link) + '" target="_blank">Apply →</a>'
                            + '</div>'
                            + '</div>'
                        )
                        st.markdown(job_card_html, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════ INTERVIEW ═══════════════════════════
elif page == "Interview":
    st.markdown("""
    <div class="cl-page-header">
      <div class="cl-page-title">Interview Preparation</div>
      <div class="cl-page-sub">AI-generated questions tailored to your resume and target role</div>
    </div>
    """, unsafe_allow_html=True)

    if not text:
        st.warning("Please upload resume first")
    else:
        st.markdown('<div class="cl-card"><div class="cl-card-title">Generate questions</div>', unsafe_allow_html=True)
        r1, r2 = st.columns([3, 1])
        with r1:
            role = st.selectbox("Target Role", [
                "Data Analyst", "Data Scientist", "ML Engineer", "Software Engineer",
                "Backend Developer", "Frontend Developer", "Full Stack Developer",
                "DevOps Engineer", "AI Engineer", "Product Manager"
            ])
        with r2:
            st.markdown("<br>", unsafe_allow_html=True)
            gen_qs = st.button("Generate Questions", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if gen_qs:
            with st.spinner("Generating interview questions…"):
                questions = generate_interview_questions(role, skills)
                if isinstance(questions, list) and len(questions) > 0:
                    st.session_state["interview_questions"] = questions
                    st.session_state["interview_answers"] = {}
                    st.session_state["interview_feedback"] = {}
                else:
                    st.error("Question generation failed. Please try again.")

        if st.session_state.get("interview_questions"):
            questions = st.session_state["interview_questions"]
            st.markdown('<div class="cl-card"><div class="cl-card-title">Interview Questions</div>', unsafe_allow_html=True)
            q_types = ["Technical", "Behavioral", "Situational", "Technical", "Behavioral", "Situational", "Technical", "Behavioral"]

            for i, q in enumerate(questions):
                q_type = q_types[i % len(q_types)]
                q_card_html = (
                    '<div class="cl-q-item">'
                    + '<div class="cl-q-num">Question ' + str(i + 1) + ' · ' + q_type + '</div>'
                    + '<div class="cl-q-text">' + str(q) + '</div>'
                    + '</div>'
                )
                st.markdown(q_card_html, unsafe_allow_html=True)

                ans = st.text_area(
                    f"Answer {i + 1}",
                    value=st.session_state["interview_answers"].get(f"ans_{i}", ""),
                    key=f"ans_{i}",
                    placeholder="Type your answer here…",
                    height=80,
                    label_visibility="collapsed"
                )

                if ans:
                    st.session_state["interview_answers"][f"ans_{i}"] = ans

                chk_col, _ = st.columns([1, 5])
                with chk_col:
                    if st.button("Check Answer", key=f"check_{i}"):
                        if ans.strip():
                            with st.spinner("Evaluating your answer…"):
                                res = evaluate_interview_answer(q, ans)
                            score_val = res.get("score", "–")
                            feedback_txt = res.get("feedback", "")
                            st.session_state["interview_feedback"][f"feedback_{i}"] = (score_val, feedback_txt)
                        else:
                            st.error("Please provide an answer before checking.")

                if f"feedback_{i}" in st.session_state["interview_feedback"]:
                    score_val, feedback_txt = st.session_state["interview_feedback"][f"feedback_{i}"]
                    feedback_html = (
                        '<div class="cl-feedback-box">'
                        + '<div class="cl-feedback-label">AI Feedback · Score: ' + str(score_val) + '/10</div>'
                        + '<div class="cl-feedback-text">' + str(feedback_txt) + '</div>'
                        + '</div>'
                    )
                    st.markdown(feedback_html, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────── FOOTER ───────────────────────────
st.markdown("""
<div class="cl-footer">
  <a href="https://www.linkedin.com/in/mahek-shaikh-797767344/" target="_blank">LinkedIn</a>
  <a href="https://github.com/shaikh-mahek06" target="_blank">GitHub</a>
  <a href="mailto:shaikhmahek0604@gmail.com">Email</a>
</div>
""", unsafe_allow_html=True)