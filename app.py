# =============================================================================
# app.py — Job Listings Ingestion Demo
# =============================================================================
# WHAT: A small Flask web app that fetches live remote-job listings from the
#       Remotive public API and displays them as cards on a single web page.
#
# WHY Flask?  Flask is the simplest Python web framework. You only need a few
#       lines to serve a page, so it's perfect for a beginner project that you
#       have to explain in an interview.
#
# WHY requests?  The 'requests' library is the standard, beginner-friendly way
#       to make HTTP calls in Python. It reads almost like English.
# =============================================================================

# ---------------------------------------------------------------------------
# 1. IMPORTS — bring in the libraries we need
# ---------------------------------------------------------------------------
import requests          # For making HTTP requests to the Remotive API
import time              # For adding delays (pacing) and measuring cache age
import random            # For randomizing the delay so it looks more natural
from flask import Flask, render_template   # Flask web framework

# ---------------------------------------------------------------------------
# 2. CREATE THE FLASK APP
# ---------------------------------------------------------------------------
# This single line creates our web application.
# __name__ tells Flask where to find templates and static files.
app = Flask(__name__)

# ---------------------------------------------------------------------------
# 3. CONFIGURATION — things you might want to tweak
# ---------------------------------------------------------------------------

# The URLs of free, public job APIs. No API keys needed.
# WHY multiple APIs? Remotive serves ~17 active listings in its main feed.
# By adding Arbeitnow, we combine listings to get 190+ options!
REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"

# A realistic browser User-Agent string.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

# Cache settings: how long (in seconds) to reuse old results before fetching fresh ones.
CACHE_DURATION_SECONDS = 300

# Retry settings
MAX_RETRIES = 3
INITIAL_BACKOFF_SECONDS = 1

# ---------------------------------------------------------------------------
# 4. SIMPLE IN-MEMORY CACHE
# ---------------------------------------------------------------------------
_cache = {
    "jobs": [],
    "fetched_at": 0
}


def is_cache_fresh():
    """Check whether the cached data is still within the cache duration."""
    age = time.time() - _cache["fetched_at"]
    return age < CACHE_DURATION_SECONDS


# ---------------------------------------------------------------------------
# 5. FETCH JOBS FROM MULTIPLE APIS (Remotive + Arbeitnow)
# ---------------------------------------------------------------------------
def fetch_from_api(url):
    """Helper to fetch JSON from an API endpoint with timeout."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching from {url}: {e}")
        return {}


def fetch_jobs():
    """Fetch job listings from Remotive AND Arbeitnow APIs.

    Returns:
      A list of job dictionaries from all sources combined.
    """
    if is_cache_fresh() and _cache["jobs"]:
        return _cache["jobs"]

    # Pacing delay
    delay = random.uniform(0.5, 1.5)
    time.sleep(delay)

    all_raw_jobs = []

    # 1. Remotive API
    remotive_data = fetch_from_api(REMOTIVE_API_URL)
    remotive_jobs = remotive_data.get("jobs", [])
    for j in remotive_jobs:
        j["_source_api"] = "remotive"
    all_raw_jobs.extend(remotive_jobs)

    # 2. Arbeitnow API
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
    """Normalize raw, fragmented category strings/tags into clean, standard buckets."""
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
    elif any(k in cat_lower for k in ["people", "hr", "recruit", "oper", "supply", "eor", "legal"]):
        return "Operations & HR"
    else:
        return "Operations & HR"


# ---------------------------------------------------------------------------
# 6. CLEAN / VALIDATE INDIVIDUAL JOB RECORDS
# ---------------------------------------------------------------------------
def clean_job(raw_job):
    """Extract and clean fields from raw job dictionary (supports Remotive & Arbeitnow)."""
    source = raw_job.get("_source_api", "remotive")
    title   = str(raw_job.get("title") or "").strip()
    company = str(raw_job.get("company_name") or "").strip()
    url     = str(raw_job.get("url") or "").strip()

    if source == "arbeitnow":
        location = str(raw_job.get("location") or "").strip()
        tags = raw_job.get("tags")
        if isinstance(tags, (list, tuple)) and len(tags) > 0:
            category = str(tags[0])
        else:
            category = "Software Engineering"
        salary = ""
        job_types = raw_job.get("job_types")
        if isinstance(job_types, (list, tuple)) and len(job_types) > 0:
            job_type = str(job_types[0])
        else:
            job_type = ""
        logo = ""
        created_at = raw_job.get("created_at")
        pub_date = time.strftime('%Y-%m-%d', time.gmtime(created_at)) if isinstance(created_at, (int, float)) else ""
    else:
        location = str(raw_job.get("candidate_required_location") or "").strip()
        category = str(raw_job.get("category") or "").strip()
        salary   = str(raw_job.get("salary") or "").strip()
        job_type = str(raw_job.get("job_type") or "").strip()
        logo     = str(raw_job.get("company_logo") or "").strip()
        pub_date = str(raw_job.get("publication_date") or "").strip()

    if job_type:
        job_type = job_type.replace("_", " ").title()

    if not title and not company:
        return None

    return {
        "title":    title    or "Untitled Position",
        "company":  company  or "Unknown Company",
        "location": location or "Location not specified",
        "url":      url      or "#",
        "category": standardize_category(category),
        "salary":   salary   or "",
        "job_type": job_type or "",
        "logo":     logo     or "",
        "pub_date": pub_date or "",
    }


# ---------------------------------------------------------------------------
# 7. THE MAIN (AND ONLY) WEB ROUTE
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the home page with job listings.

    WHAT: This function runs every time someone visits the root URL ("/")
          of our web app.

    HOW:
      1. Fetch raw jobs (from cache or API).
      2. Clean each job, skipping broken ones.
      3. Build a list of unique categories for the filter dropdown.
      4. Pass everything to the HTML template for rendering.
    """
    # Step 1: Get raw job data
    raw_jobs = fetch_jobs()

    # Step 2: Clean each job. 'clean_job' returns None for broken entries,
    # so we filter those out with a list comprehension.
    #
    # In plain English, this line says:
    #   "For each raw_job in raw_jobs, clean it. Keep it only if cleaning
    #    didn't return None."
    jobs = [clean_job(j) for j in raw_jobs]
    jobs = [j for j in jobs if j is not None]

    # Step 3: Build a sorted list of unique categories for the filter dropdown.
    # We use a set() to remove duplicates, then sorted() to alphabetize.
    # WHY?  So the user can filter jobs by category (e.g. "Marketing" only).
    categories = sorted(set(j["category"] for j in jobs if j["category"]))

    # Step 4: Decide what message to show
    if not jobs:
        error_message = (
            "No job listings available right now. "
            "The data source might be temporarily down — please try again "
            "in a few minutes."
        )
    else:
        error_message = None

    # Step 5: Render the HTML template, passing in our data.
    # 'render_template' looks inside the 'templates/' folder for the file.
    return render_template(
        "index.html",
        jobs=jobs,
        job_count=len(jobs),
        categories=categories,
        error_message=error_message
    )


# ---------------------------------------------------------------------------
# 8. RUN THE APP
# ---------------------------------------------------------------------------
# This block only runs when you execute "python app.py" directly.
# It starts Flask's built-in development server on port 5000.
#
# debug=True means:
#   - The server auto-restarts when you edit the code
#   - You get helpful error pages in the browser
#
# In production (e.g., on Render), we'll use Gunicorn instead, so this
# block won't run there — Gunicorn imports the 'app' object directly.
if __name__ == "__main__":
    app.run(debug=True)
