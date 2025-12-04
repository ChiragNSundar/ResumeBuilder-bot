# 📄 AI-Powered Interactive Resume Builder

A comprehensive full-stack application built with **Python Flask**, **MongoDB**, and **Google's Gemini API**. This project features an intelligent **Resume Builder** that guides the user through a personal interview process to collect and curate all professional details.

## ✨ Features

### 🤖 AI Interviewer & Profile Builder
*   **🧠 PDF Resume Parsing:** Users can upload a PDF resume, and the Gemini model extracts key details (Name, Email, Skills, Experience) to instantly pre-fill the form.
*   **Conversational Flow:** A step-by-step interview process ensures all mandatory fields are collected in a natural, conversational manner.
*   **📝 Live Form Preview:** The right-hand panel updates in real-time as the user answers questions or uploads a resume, showing a dynamic candidate profile.
*   **💡 Dynamic Suggestions:** The AI suggests appropriate **Job Titles** (based on domain/experience) and relevant **Skills** (based on job title).
*   **📄 Professional Summary Generation:** The AI can generate multiple draft professional summaries for the user to choose from and refine.
*   **🔍 ATS Score Check:** A built-in command calls the AI to critique the complete profile, providing an **ATS Score**, missing keywords, and improvement feedback.
*   **💾 MongoDB Persistence:** Stores chat logs, raw/parsed resume data, and the final submitted profile securely.
*   **⬇️ Client-Side PDF Download:** Generates a professional, print-ready PDF of the completed profile using `html2pdf.js`.

## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **Database:** **MongoDB** (`pymongo`) for persistence and data storage.
*   **AI Engine:** Google Gemini 2.0 Flash (via `google-generativeai`)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript
*   **Utilities:** `PyPDF2` (PDF text extraction), `html2pdf.js` (PDF generation), Dotenv, Regex (Validation)

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.8+
*   MongoDB running locally (default URI is `mongodb://localhost:27017/`)

1.  **Clone the repository** (or download the files):
    ```bash
    git clone https://github.com/yourusername/gemini-resume-builder.git
    cd gemini-resume-builder
    ```

2.  **Install Dependencies:**
    You'll need a `requirements.txt` file listing all the Python dependencies. Based on `app.py`, it should contain:
    ```
    Flask
    python-dotenv
    google-genai
    pymongo
    pypdf2
    ```
    Then run:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    *   Create a file named `.env` in the root directory.
    *   Add your Google Gemini API key inside:
    ```ini
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

4.  **Run the Application:**
    ```bash
    python app.py
    ```

5.  **Open in Browser:**
    Go to `http://127.0.0.1:5001`.

## 📂 Project Structure

```text
/project-root
├── app.py               # Main Flask backend (AI logic, MongoDB, Routes)
├── .env                 # API Key configuration
├── requirements.txt     # Python dependencies
├── static/
│   ├── style.css        # Styling for the split layout, chat, and form
│   └── script.js        # Frontend chat logic, API calls, form updates, and PDF generation
└── templates/
    └── index.html       # The single-page interface (Chat + Form Preview)
