# 📄 AI-Powered Interactive Resume Builder

A comprehensive full-stack application built with **Python Flask**, **MongoDB**, and **Google's Gemini API**. This project features an intelligent **Resume Builder** that acts as a personal interviewer, guiding users to build a professional profile and exporting it as a PDF.

## ✨ Features

### 🤖 AI Interviewer & Profile Builder
*   **🧠 PDF Resume Parsing:** Users can upload an existing PDF resume. The Gemini model extracts key details (Name, Contact, Skills, Experience) to instantly pre-fill the profile.
*   **💬 Conversational Interface:** A step-by-step AI chat ensures all mandatory details are collected naturally.
*   **📝 Live Form Preview:** The candidate profile form on the right updates in real-time as you chat or upload files.
*   **💡 Dynamic Suggestions:**
    *   **Job Titles:** Suggested based on your experience level and domain.
    *   **Skills:** Relevant technical skills suggested based on your target job title.
*   **✍️ AI Summary Generation:** The AI can generate multiple professional summary options for you to choose from.
*   **🔍 ATS Score Check:** A built-in "Check ATS Score" command analyzes your profile, providing a score (0-100) and feedback on missing keywords.

### 📄 Export & Persistence
*   **⬇️ Robust PDF Download:** Generates a clean, structured, and print-ready PDF resume using a custom HTML template and `html2pdf.js`.
*   **💾 MongoDB Persistence:** Automatically saves chat history, parsed resume data, and the final user profile to a MongoDB database.

## 🛠️ Tech Stack

*   **Backend:** Python, Flask
*   **Database:** MongoDB (`pymongo`)
*   **AI Engine:** Google Gemini 2.0 Flash (via `google-genai`)
*   **Frontend:** HTML5, CSS3, Vanilla JavaScript
*   **PDF Generation:** `html2pdf.js` (Client-side rendering)
*   **PDF Parsing:** `PyPDF2`

## 🚀 Installation & Setup

### Prerequisites
*   Python 3.8+
*   MongoDB installed and running locally (Default: `mongodb://localhost:27017/`)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/gemini-resume-builder.git
    cd gemini-resume-builder
    ```

2.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    *   Create a file named `.env` in the root directory.
    *   Add your Google Gemini API key:
    ```ini
    GOOGLE_API_KEY=your_actual_api_key_here
    ```

4.  **Run the Application:**
    ```bash
    python app.py
    ```

5.  **Access the App:**
    Open your browser and navigate to:
    `http://127.0.0.1:5001`

## 📂 Project Structure

```text
/project-root
├── app.py               # Main Flask backend (Routes, MongoDB, Gemini Logic)
├── .env                 # API Key configuration (Not committed)
├── requirements.txt     # List of Python dependencies
├── static/
│   ├── style.css        # Styles for Chat, Form, and PDF Template
│   └── script.js        # Frontend logic (Chat, API calls, PDF generation)
└── templates/
    └── index.html       # Main HTML interface (Split layout)

📝 Usage Guide

    Start: The AI will ask for your Name or a PDF upload.

    Upload: If you upload a PDF, the AI extracts data and fills the form automatically.

    Chat: Answer the AI's questions to fill in missing details (Email, Phone, Domain, etc.).

    Refine: Use "Generate" to get summary options or "Suggest Skills" for help.

    Critique: Type "Check ATS Score" to get AI feedback on your profile.

    Download: Click "Download PDF" to save your resume.

    Submit: Click "Submit" to save your profile to the MongoDB database.
