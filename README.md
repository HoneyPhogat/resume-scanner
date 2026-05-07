# 🚀 AI Resume Scanner

**Live Demo:** [Click here to test the live application](https://YOUR-RENDER-URL-HERE.onrender.com)

## 📌 Overview
An intelligent, Full-Stack web application designed to analyze a candidate's resume against a specific job description. The application utilizes Natural Language Processing (NLP) to extract text, strip grammatical filler, and execute Set Theory mathematics in $O(N)$ time complexity to instantly calculate a match percentage and identify missing keywords.

## 🛠️ Tech Stack
* **Backend:** Python, FastAPI, Uvicorn
* **Frontend:** Vanilla JavaScript, HTML5, CSS3 (Fetch API for asynchronous DOM manipulation)
* **NLP Engine:** NLTK (Natural Language Toolkit), Porter Stemmer Algorithm
* **File Parsing:** PyPDF
* **Deployment:** Render (CI/CD via GitHub)

## ✨ Core Features
* **In-Memory PDF Parsing:** Safely extracts text from uploaded `.pdf` binaries without saving files locally.
* **Lexical Analysis:** Utilizes NLTK's English corpus Hash Set to filter out stop words and filler data.
* **Mathematical Set Difference:** Compares processed resume arrays against job description arrays to accurately highlight matched skills and flag missing requirements.
* **Dynamic UI Dashboard:** Renders results asynchronously without page reloads, featuring conditional color logic based on the candidate's score.

## 💻 Local Setup Instructions

If you want to run this application on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YourUsername/resume-scanner.git](https://github.com/YourUsername/resume-scanner.git)
   cd resume-scanner