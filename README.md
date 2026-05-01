# 🚀 AI Resume Analyzer

An AI-powered web application that analyzes resumes, calculates ATS scores, identifies skill gaps, suggests improvements, fetches jobs, and generates interview questions.

Built using **Streamlit + Python + LLM APIs**

---

##  Features

###  1. ATS Score Analysis
- Calculates resume ATS score
- Shows matched & missing skills
- Provides resume insights

###  2. Skill Gap Analysis
- Compares resume with job description
- Identifies missing skills
- Helps improve job readiness

###  3. Resume Improver
- AI-enhanced resume rewriting
- Clean formatting
- Download as PDF & LaTeX

###  4. Job Finder
- Fetches real job listings
- Filter by role & location
- Direct apply links

###  5. Interview Preparation
- Generates technical questions
- Accepts user answers
- Evaluates answers with score & feedback

---

##  Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **AI:** LLM APIs (OpenAI / Gemini / etc.)
- **PDF Processing:** PyMuPDF / PDF parser
- **Other:** ReportLab

---

## 📂 Project Structure


AI_Resume_Analyzer/
│
├── app.py
├── modules/
│ ├── ats_scorer.py
│ ├── interview_gen.py
│ ├── interview_eval.py
│ ├── job_api.py
│ ├── resume_improver.py
│ ├── skill_gap.py
│
├── utils/
│ ├── parser.py
│ ├── skill_extractor.py
│
├── requirements.txt
└── README.md


