import csv
import re
from pathlib import Path
from typing import List, Set


SKILLS_CSV_PATH = Path(__file__).resolve().parents[1] / "data" / "skills.csv"


def load_skills_from_csv(csv_path: Path = SKILLS_CSV_PATH) -> List[str]:
    """
    Load skill names from a CSV file.
    Expected format: one skill per row (first column used).
    """
    skills: List[str] = []

    if not csv_path.exists():
        return skills

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            if not row:
                continue
            skill = row[0].strip()
            if skill:
                skills.append(skill)

    return skills


def extract_skills(text: str, skills_list: List[str] | None = None) -> List[str]:
    """
    Extract only real skills present in the predefined skills list.
    Uses full-word regex matching to avoid partial/random matches.
    """
    if not text:
        return []

    if skills_list is None:
        skills_list = load_skills_from_csv()

    matched_skills: Set[str] = set()

    for skill in skills_list:
        # Match full skill term only (case-insensitive), e.g., "sql" not "sequelized"
        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"
        if re.search(pattern, text, flags=re.IGNORECASE):
            matched_skills.add(skill)

    return sorted(matched_skills, key=str.lower)
