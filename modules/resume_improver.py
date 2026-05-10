import re
from utils.llm_client import LLMClient


# ================= PROMPT =================
RESUME_IMPROVEMENT_PROMPT = """
Rewrite the resume into a clean, ATS-friendly format tailored to the job description.

Requirements:
- Preserve all real experience and achievements from the original resume
- Rewrite bullet points to highlight quantifiable achievements and results
- Tailor language and keywords to match the job description
- Use strong action verbs (Developed, Built, Implemented, etc.)
- Do NOT invent anything — only enhance what's already there
- Keep it concise and structured
- Improve grammar and clarity

Job Description:
{job_description}

Return ONLY improved resume text.
""".strip()

RESUME_IMPROVEMENT_PROMPT = "You are a professional resume writer. Rewrite the following resume to be ATS-optimized and tailored to this job description. Preserve all real information: actual job titles, company names, dates, education, and projects from the original resume. Do not invent or hallucinate any information. Improve the bullet points to include action verbs and quantified achievements where the original hints at them. Output only the improved resume text, no commentary."


# ================= CLEAN TEXT =================
def clean_resume_text(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'[*#\-\u2022\u2023\u25E6\u2043\u2219]', '', text)
    text = re.sub(r'[^\w\s.,;:()/@]', '', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'\n+', '\n', text)

    return "\n".join([line.strip() for line in text.split("\n")]).strip()


# ================= LATEX GENERATOR =================
def generate_latex_resume(text: str) -> str:
    if not text:
        return _empty_template()

    # Escape LaTeX
    escape_map = str.maketrans({
        '&': '\\&', '%': '\\%', '$': '\\$',
        '#': '\\#', '_': '\\_', '{': '\\{',
        '}': '\\}', '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
        '\\': '\\textbackslash{}'
    })

    text = text.translate(escape_map)

    sections = _parse_sections(text)

    return _build_latex(sections)


# ================= EMPTY TEMPLATE =================
def _empty_template():
    return r"""\documentclass[a4paper,9pt]{article}
\usepackage[hidelinks]{hyperref}
\usepackage{geometry}
\usepackage{enumitem}
\usepackage{titlesec}

\geometry{margin=0.7in}
\titleformat{\section}{\large\bfseries}{}{0em}{}[\titlerule]

\begin{document}

\begin{center}
{\LARGE \textbf{Your Name}}\\
Email | Phone | Location | LinkedIn | GitHub
\end{center}

\section*{Summary}
Add summary here

\section*{Education}
Add education here

\section*{Experience}
\begin{itemize}
\item Add experience
\end{itemize}

\section*{Skills}
Add skills

\section*{Projects}
\begin{itemize}
\item Add project
\end{itemize}

\end{document}"""


# ================= PARSER =================
def _parse_sections(text: str) -> dict:
    sections = {
        "summary": [],
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "certificates": []
    }

    current = None

    keywords = {
        "summary": ["summary", "objective"],
        "education": ["education", "university", "college"],
        "experience": ["experience", "intern", "work"],
        "skills": ["skills", "tools", "technologies"],
        "projects": ["project"],
        "certificates": ["certificate", "certification"]
    }

    for line in text.split("\n"):
        l = line.lower().strip()

        if not l:
            continue

        # Detect section
        for sec, keys in keywords.items():
            if any(k in l for k in keys) and len(l) < 40:
                current = sec
                break
        else:
            if current:
                cleaned = re.sub(r'^[•\-\*]\s*', '', line).strip()
                if len(cleaned) > 3:
                    sections[current].append(cleaned)

    return sections


# ================= LATEX BUILDER =================
def _build_latex(sec: dict) -> str:

    def list_to_items(lst):
        if not lst:
            return r"\item Not available"
        return "\n".join([f"\\item {x}" for x in lst[:5]])

    return rf"""\documentclass[a4paper,9pt]{{article}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{geometry}}
\usepackage{{enumitem}}
\usepackage{{titlesec}}

\geometry{{margin=0.7in}}
\titleformat{{\section}}{{\large\bfseries}}{{}}{{0em}}{{}}[\titlerule]

\begin{{document}}

\begin{{center}}
{{\LARGE \textbf{{Candidate Name}}}}\\
Email | Phone | Location | LinkedIn | GitHub
\end{{center}}

\section*{{Summary}}
{" ".join(sec["summary"]) or "Professional summary not available."}

\section*{{Education}}
{" ".join(sec["education"]) or "Education details not available."}

\section*{{Experience}}
\begin{{itemize}}[noitemsep]
{list_to_items(sec["experience"])}
\end{{itemize}}

\section*{{Skills}}
{", ".join(sec["skills"]) or "Skills not available."}

\section*{{Projects}}
\begin{{itemize}}[noitemsep]
{list_to_items(sec["projects"])}
\end{{itemize}}

\section*{{Certificates}}
\begin{{itemize}}[noitemsep]
{list_to_items(sec["certificates"])}
\end{{itemize}}

\end{{document}}
"""


# ================= LLM =================
def improve_resume_text(resume_text: str, job_description: str = '', llm_client: LLMClient | None = None) -> str:
    if not resume_text.strip():
        raise ValueError("Resume text empty")

    client = llm_client or LLMClient()

    prompt = f"{RESUME_IMPROVEMENT_PROMPT}\n\nResume:\n{resume_text}\n\nJob Description:\n{job_description}"

    result = client.generate_text(prompt)

    if not result:
        raise ValueError("Empty response from LLM")

    return result.strip()
