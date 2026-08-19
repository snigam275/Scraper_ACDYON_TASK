# Architectural Decisions & Technical Strategy (`DECISIONS.md`)

**Candidate Name**: Shrey Nigam  
**Track Selected**: Part 1 — Resilient Data Ingestion Pipeline  
**Live Deployed Application**: [https://scraper-2qh7.onrender.com/](https://scraper-2qh7.onrender.com/)  
**GitHub Repository**: [https://github.com/snigam275/Scraper_ACDYON_TASK](https://github.com/snigam275/Scraper_ACDYON_TASK)

---

## 1. Technical Design Document (Part 1 — Ingestion Strategy)

### 1.1 Detection Surface Analysis
Automated clients typically reveal themselves through three signals: what their software looks like, how fast and how regularly they make requests, and how much volume they send from a single identity. My design accounts for each:

* **HTTP User-Agent signature**: A default script announces itself with a `python-requests/...` User-Agent, which is an obvious automated tell and is commonly blocked.  
  *Mitigation*: The fetch layer sends a realistic Chrome User-Agent (`Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36`) so requests resemble a normal browser client.
* **Request timing**: Fixed, perfectly regular intervals look like an automated job.  
  *Mitigation*: A randomised delay (`random.uniform(0.5, 1.5)`) is applied before each fetch to break predictable request cadence.
* **Request volume from one IP**: Rapid, repeated hits burn the origin IP and consume the source's bandwidth.  
  *Mitigation*: A 300-second in-memory cache (`CACHE_DURATION_SECONDS = 300`) shields the upstream sources from redundant requests during normal user interaction, so a page load does not trigger a fresh fetch every time.

> *Note*: Behavioural signals (mouse movement, scroll patterns) are used mainly against full browser-based scrapers; because this pipeline consumes public APIs rather than driving a browser, it does not expose those signals at all.

### 1.2 Multi-Source Ingestion & Fallback ("Plan B")
* **Multi-source aggregation**: To avoid a single point of failure, the engine pulls live listings from two independent sources — Remotive and Arbeitnow — and merges them into one catalogue. The two APIs return different shapes (Remotive nests jobs under a `jobs` key, Arbeitnow under `data`, with different location and date formats), and `clean_job()` normalises both into a single consistent schema.
* **Fallback mechanism**: Each source is fetched through `fetch_from_api()`, which wraps the request in exception handling and returns an empty result on failure instead of crashing. If one source throttles, changes structure, or goes down, the app still returns listings from the other source — so the pipeline degrades gracefully rather than failing completely. This is the "plan B": the design does not depend on any single source staying available.

### 1.3 Pipeline Resilience & Schema-Drift Handling
* **Category normalisation**: Raw feeds return fragmented, inconsistent category tags. `standardize_category()` maps these onto eight structured categories — Software & Tech, Data & AI, Design & Creative, Product & Management, Sales & Marketing, Customer Support, Finance & Business, Operations & HR — using keyword matching, with a sensible default so an unrecognised tag never breaks browsing.
* **Defensive field extraction**: All fields are read with safe dictionary access (`raw_job.get(...)`), so missing attributes (logo, salary, publication date) fall back to clean defaults instead of raising a `KeyError`. On the front end, a failed company-logo image swaps to a generated placeholder rather than a broken image.

### 1.4 Scope & Ethical Compliance
* **Scope guardrail**: In line with the challenge's guidance, the live demo runs only against public, unauthenticated API feeds. It does not touch authenticated accounts (e.g. LinkedIn) or breach a platform's Terms of Service, and it self-limits request volume through caching so it stays a good citizen toward the sources it uses.

---

## 2. Written Decision Explanations

### Q1. Why this ingestion strategy over the obvious alternative you rejected?
* **Alternative rejected**: A headless-browser stack (Puppeteer / Playwright / Selenium) with proxy rotation.
* **Rationale**: Headless browsers carry significant CPU and memory overhead, add rendering latency, and are still vulnerable to TLS fingerprinting (JA3/JA4) on basic cloud instances. For sources that expose a public API, lightweight HTTP ingestion with a realistic User-Agent, randomised pacing, and server-side caching is significantly lighter — far lower memory use, no browser-rendering overhead — and runs reliably on a free cloud tier. A browser-driven approach would only be justified for sources that require rendering JavaScript, which these did not.

### Q2. One trade-off made under the time limit, and the 1-week vision
* **Trade-off**: I used a simple in-memory dictionary cache (`_cache`) for speed of implementation, rather than external persistent storage. This is fine for a single instance but is not shared across multiple workers and is lost on restart.
* **With a real week, I would add**:
  1. **Distributed caching**: A Redis instance so cache is shared across workers and survives restarts.
  2. **Proxy rotation**: A residential proxy pool with automatic IP rotation triggered on HTTP 429/403 responses, to scale request volume safely.
  3. **Background ingestion**: A scheduled worker (e.g. Celery) writing to a persistent database (PostgreSQL), so the catalogue is maintained independently of live web traffic and page loads are always instant.

### Q3. Where did you use AI tools, and what did you personally verify or change?
* **How AI was used**: I used AI tools to accelerate the build — scaffolding the Flask app and HTML/CSS layout, and drafting an initial version of the category-normalisation keywords and the client-side filtering logic. I directed the design decisions throughout (choice of sources, the two-source fallback, caching, pacing, and the feature set).
* **What I personally verified and changed**:
  1. Tested the backend end-to-end — confirmed the request timeout, cache duration, and per-source error handling behave correctly, including when a source returns nothing.
  2. Verified the two-source merge by checking that jobs from both Remotive and Arbeitnow appear and are normalised into one consistent format despite their different response shapes.
  3. Checked the front-end behaviour myself: multi-term search (including the developer/engineer synonym handling), category filtering, starred-jobs persistence via `localStorage`, and "load more" pagination.
  4. Confirmed in the browser that apply links open the correct live postings in a new tab.
