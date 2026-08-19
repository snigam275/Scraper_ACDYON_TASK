# 🚀 JobPulse Launchpad — Real-Time Job Ingestion & Career Board

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.org/)
[![Live APIs](https://img.shields.io/badge/APIs-Remotive%20%7C%20Arbeitnow-orange.svg)](#multi-source-api-ingestion)
[![UI Theme](https://img.shields.io/badge/UI-Creamish%20Yellow%20%7C%20Greenish%20%7C%20Blueish-yellow.svg)](#design-system)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

An automated Python data ingestion pipeline and interactive Flask web dashboard that fetches, cleans, and standardizes live remote job listings from public APIs.

Built as a CS student project demo focusing on clean code, robust API handling, data normalization, and sleek user experience.

---

## 🌟 Key Highlights & Features

| Feature | Technical Implementation |
| :--- | :--- |
| **Multi-Source Ingestion** | Ingests live listings concurrently from **Remotive** and **Arbeitnow** REST APIs. |
| **Data Normalization** | Standardizes 80+ raw API tags into 8 clean, meaningful career categories in Python. |
| **Smart Search & Synonyms** | Client-side multi-term matching with built-in `developer` ↔ `engineer` synonym support. |
| **In-Memory Caching** | 300-second (5-minute) cache TTL to reduce API load and eliminate rate limits. |
| **Resilience & Reliability** | Browser-like User-Agent headers, timeout safeguards, and random pacing delays. |
| **Strict 3-Color UI Theme** | Designed with a **Light Creamish Yellow** base, **Emerald Green** highlights, and **Oceanic Slate Blue** text/buttons. |
| **Platform Overview Flow** | Displays platform capability cards before listings with smooth-scroll navigation. |

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.9+, Flask framework
- **HTTP Client**: `requests` with User-Agent spoofing & error handling
- **Frontend**: HTML5, Vanilla CSS3 (Custom Design Tokens), JavaScript (Client-Side Filtering)
- **Deployment Ready**: Configured for Gunicorn / Render hosting

```
ACDYON/
├── app.py               ← Flask backend, API fetchers, caching & category cleaning logic
├── templates/
│   └── index.html        ← HTML5 Jinja2 template with CSS design tokens & smart JS search
├── requirements.txt      ← Python dependencies (Flask, requests, gunicorn)
├── .gitignore            ← Excludes venv, __pycache__, IDE configs
└── README.md             ← Project documentation
```

---

## 🚀 How to Run Locally

### 1. Clone the Repository

```bash
git clone https://github.com/snigam275/Scraper_ACDYON_TASK.git
cd Scraper_ACDYON_TASK
```

### 2. Create & Activate Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Launch Application Server

```bash
python app.py
```

Open your browser and navigate to **http://127.0.0.1:5000** to explore the dashboard.

---

## 🌐 Deploying to Render (Free Tier)

1. Create a Web Service on [Render.com](https://render.com).
2. Connect your GitHub repository `https://github.com/snigam275/Scraper_ACDYON_TASK`.
3. Set the following build options:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Runtime**: `Python 3`

---

## 👨‍💻 Student Project Demonstration Notes

This project demonstrates core data engineering & web development principles:
- **API Rate Limiting Prevention**: Through in-memory caching and random request delay pacing.
- **Data Normalization Engine**: Python mapping function that converts messy external tags into unified taxonomy.
- **Client-Side UX**: Filtering jobs in memory without triggering server re-fetches for instant responsiveness.

---

## 📜 License

Distributed under the MIT License. Feel free to use and extend!
