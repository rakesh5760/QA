# AI-Based Intelligent QA Automation System for Web Applications

An end-to-end automated testing system that uses **Playwright**, **BeautifulSoup**, and **Groq AI** to perform deep website analysis, SEO auditing, and intelligent bug detection.

## 🚀 Features

-   **Automated Web Crawling**: Uses Microsoft Playwright to interact with modern web apps, capture titles, discover links, and monitor console errors.
-   **SEO Audit**: Analyzes HTML structure, including meta tags, heading hierarchy (H1-H6), and image alt text accessibility.
-   **Bug Detection**: Performs parallelized checks for broken links (4xx errors) and server-side failures (5xx errors).
-   **AI Insights**: Integrates with the **Groq API** (Llama 3.1) to generate:
    *   **Automated Test Cases**: 5 functional test cases based on the discovered page structure.
    *   **Bug Summaries**: A high-level explanation of technical defects found.
    *   **Fix Suggestions**: Actionable recommendations for SEO and bug resolution.
-   **Historical Tracking**: Saves all analysis results in a MySQL database for long-term progress monitoring.
-   **Interactive Dashboard**: A modern **Streamlit** frontend to run analyses and explore historical reports.

## 🛠️ Tech Stack

-   **Backend**: FastAPI (Python)
-   **Automation**: Playwright (Headless Browser)
-   **SEO Parsing**: BeautifulSoup4
-   **AI Engine**: Groq API (LLM)
-   **Database**: MySQL (SQLAlchemy ORM)
-   **Frontend**: Streamlit

## 📋 Prerequisites

-   Python 3.8 or higher
-   MySQL Server
-   Groq API Key

## ⚙️ Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/rakesh5760/QA.git
    cd QA
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

3.  **Configure Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key
    DB_URL=mysql+pymysql://user:password@localhost:3306/qa_automation
    ```

## 🏃 Usage

1.  **Start the Backend Server**:
    ```bash
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
    ```

2.  **Start the Frontend Dashboard**:
    ```bash
    python -m streamlit run frontend/app.py
    ```

3.  **Access the Dashboard**: Open your browser and navigate to `http://localhost:8501`.

## 📂 Project Structure

-   `backend/`: FastAPI application, database models, and service modules.
-   `frontend/`: Streamlit dashboard code.
-   `screenshots/`: Local storage for website screenshots captured during analysis.
-   `tests/`: Verification and debug scripts for different modules.

