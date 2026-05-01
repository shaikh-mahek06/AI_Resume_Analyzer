import json
import os
from typing import Dict, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from dotenv import load_dotenv


DEFAULT_ADZUNA_COUNTRY = "in"
DEFAULT_RESULTS_PER_PAGE = 5


load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


def _build_search_query(user_skills: List[str], roles: List[str]) -> str:
    """
    Build a simple text query for the jobs API.
    """
    cleaned_roles = [role.strip() for role in roles if role and role.strip()]
    cleaned_skills = [skill.strip() for skill in user_skills if skill and skill.strip()]

    query_parts: List[str] = []
    if cleaned_roles:
        query_parts.append(cleaned_roles[0])
    query_parts.extend(cleaned_skills[:3])

    if not query_parts:
        raise ValueError("At least one role or skill is required to search jobs.")

    return " ".join(query_parts)


def fetch_jobs(
    role: str,
    city: str,
    user_skills: List[str] | None = None,
    results_per_page: int = DEFAULT_RESULTS_PER_PAGE,
) -> List[Dict[str, str]] | Dict[str, str]:
    """
    Fetch real job listings from the Adzuna API.
    """
    cleaned_role = role.strip()
    cleaned_city = city.strip()

    # Always use India
    country = "in"

    if not APP_ID or not APP_KEY:
        return {"error": "Missing API keys"}
    if not cleaned_role:
        raise ValueError("Job role is required to search jobs.")
    if not cleaned_city:
        raise ValueError("City is required to search jobs.")

    query = _build_search_query(user_skills or [], [cleaned_role])
    params = urlencode(
        {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "results_per_page": results_per_page,
            "what": query,
            "where": cleaned_city,
            "content-type": "application/json",
        }
    )
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?{params}"

    try:
        with urlopen(url, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        return {"error": f"HTTP error {error.code}: {error.reason}"}
    except URLError as error:
        return {"error": f"Request timeout or network error: {error.reason}"}
    except json.JSONDecodeError as error:
        return {"error": f"Invalid response from API: {error}"}
    except Exception as error:
        return {"error": f"Unable to fetch job listings: {error}"}

    listings: List[Dict[str, str]] = []
    for item in payload.get("results", []):
        job_location = ((item.get("location") or {}).get("display_name") or "").lower()
        city_lower = cleaned_city.lower()
        
        # Exclude non-India locations
        exclude_terms = ["usa", "united states", "california", "los angeles", "uk", "united kingdom"]
        if any(term in job_location for term in exclude_terms):
            continue
        
        # Filter: only keep jobs where location contains the searched city
        if city_lower in job_location:
            listings.append(
                {
                    "title": (item.get("title") or "Unknown Role").strip(),
                    "company": ((item.get("company") or {}).get("display_name") or "Unknown Company").strip(),
                    "location": ((item.get("location") or {}).get("display_name") or "Unknown Location").strip(),
                    "apply_link": (item.get("redirect_url") or "").strip(),
                }
            )

    return listings


def get_real_job_listings(
    user_skills: List[str],
    roles: List[str] | None = None,
    results_per_page: int = DEFAULT_RESULTS_PER_PAGE,
) -> List[Dict[str, str]] | Dict[str, str]:
    """
    Backward-compatible wrapper for role-only job searches.
    """
    cleaned_roles = [role.strip() for role in (roles or []) if role and role.strip()]
    if not cleaned_roles:
        raise ValueError("Select a job role to search live listings.")

    try:
        result = fetch_jobs(
            cleaned_roles[0],
            os.getenv("ADZUNA_DEFAULT_CITY", "New York"),
            user_skills=user_skills,
            results_per_page=results_per_page,
        )
        # If fetch_jobs returns an error dict, convert to empty list
        if isinstance(result, dict) and "error" in result:
            return []
        return result
    except Exception:
        return []
