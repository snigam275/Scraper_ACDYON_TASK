import random
import time
import requests
from flask import Flask, render_template

app = Flask(__name__)

REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

CACHE_DURATION_SECONDS = 300
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1

_cache = {
    "jobs": [],
    "fetched_at": 0
}


def is_cache_fresh():
    return (time.time() - _cache["fetched_at"]) < CACHE_DURATION_SECONDS


def fetch_from_api(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return {}


def fetch_jobs():
    if is_cache_fresh() and _cache["jobs"]:
        return _cache["jobs"]

    time.sleep(random.uniform(0.5, 1.5))
    all_raw_jobs = []

    remotive_data = fetch_from_api(REMOTIVE_API_URL)
    remotive_jobs = remotive_data.get("jobs", [])
    for j in remotive_jobs:
        j["_source_api"] = "remotive"
    all_raw_jobs.extend(remotive_jobs)

    arbeit_data = fetch_from_api(ARBEITNOW_API_URL)
    arbeit_jobs = arbeit_data.get("data", [])
    for j in arbeit_jobs:
        j["_source_api"] = "arbeitnow"
    all_raw_jobs.extend(arbeit_jobs)

    if all_raw_jobs:
        _cache["jobs"] = all_raw_jobs
        _cache["fetched_at"] = time.time()
        return all_raw_jobs

    return _cache["jobs"]


def standardize_category(cat):
    cat_lower = str(cat or "").lower().strip()
    if not cat_lower:
        return "Software & Tech"
    if any(k in cat_lower for k in ["softw", "engr", "engineeri", "developer", "code", "tech", "it", "web", "devops", "cloud", "security", "platform", "r&d", "ci"]):
        return "Software & Tech"
    elif any(k in cat_lower for k in ["data", "analytic", "machine learning", "ai"]):
        return "Data & AI"
    elif any(k in cat_lower for k in ["design", "art", "creative", "media", "grafik"]):
        return "Design & Creative"
    elif any(k in cat_lower for k in ["product", "projekt", "program"]):
        return "Product & Management"
    elif any(k in cat_lower for k in ["sale", "market", "brand", "vertrieb", "revenue", "gtm", "partner"]):
        return "Sales & Marketing"
    elif any(k in cat_lower for k in ["customer", "support", "care", "service"]):
        return "Customer Support"
    elif any(k in cat_lower for k in ["finance", "steuern", "account", "business op"]):
        return "Finance & Business"
    else:
        return "Operations & HR"


def clean_job(raw_job):
    source = raw_job.get("_source_api", "remotive")
    title = str(raw_job.get("title") or "").strip()
    company = str(raw_job.get("company_name") or "").strip()
    url = str(raw_job.get("url") or "").strip()

    if source == "arbeitnow":
        location = str(raw_job.get("location") or "").strip()
        tags = raw_job.get("tags")
        category = str(tags[0]) if isinstance(tags, (list, tuple)) and len(tags) > 0 else "Software Engineering"
        salary = ""
        job_types = raw_job.get("job_types")
        job_type = str(job_types[0]) if isinstance(job_types, (list, tuple)) and len(job_types) > 0 else ""
        logo = ""
        created_at = raw_job.get("created_at")
        pub_date = time.strftime('%Y-%m-%d', time.gmtime(created_at)) if isinstance(created_at, (int, float)) else ""
    else:
        location = str(raw_job.get("candidate_required_location") or "").strip()
        category = str(raw_job.get("category") or "").strip()
        salary = str(raw_job.get("salary") or "").strip()
        job_type = str(raw_job.get("job_type") or "").strip()
        logo = str(raw_job.get("company_logo") or "").strip()
        pub_date = str(raw_job.get("publication_date") or "").strip()

    if job_type:
        job_type = job_type.replace("_", " ").title()

    if not title and not company:
        return None

    return {
        "title": title or "Untitled Position",
        "company": company or "Unknown Company",
        "location": location or "Location not specified",
        "url": url or "#",
        "category": standardize_category(category),
        "salary": salary or "",
        "job_type": job_type or "",
        "logo": logo or "",
        "pub_date": pub_date or "",
    }


@app.route("/")
def index():
    raw_jobs = fetch_jobs()
    jobs = [clean_job(j) for j in raw_jobs]
    jobs = [j for j in jobs if j is not None]

    categories = sorted(set(j["category"] for j in jobs if j["category"]))
    error_message = (
        "No job listings available right now. Please try again in a few minutes."
        if not jobs else None
    )

    return render_template(
        "index.html",
        jobs=jobs,
        job_count=len(jobs),
        categories=categories,
        error_message=error_message
    )


if __name__ == "__main__":
    app.run(debug=True)
