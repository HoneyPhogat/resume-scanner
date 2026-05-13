from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
import io
import pypdf
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords


app = FastAPI()
stemmer = PorterStemmer()

# --- to check the health status ---
@app.get("/health_status")
async def health_check():
    return {
        "status": "Ready and alive"
    }


# When the user visits the main page, hand them this HTML webpage
@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>The Resume Scanner</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --primary-hover: #4f46e5;
                --bg: #0f172a;
                --surface: #1e293b;
                --text: #f8fafc;
                --text-muted: #94a3b8;
                --border: #334155;
                --success: #10b981;
            }
            body {
                font-family: 'Inter', sans-serif;
                background-color: var(--bg);
                color: var(--text);
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                background-image: radial-gradient(circle at top right, #1e1b4b, var(--bg));
            }
            .container {
                width: 100%;
                max-width: 600px;
                background: rgba(30, 41, 59, 0.7);
                backdrop-filter: blur(16px);
                padding: 40px;
                border-radius: 24px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: transform 0.3s ease;
                box-sizing: border-box;
            }
            h2 {
                text-align: center;
                font-weight: 700;
                font-size: 2.5rem;
                margin-top: 0;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #a5b4fc, #818cf8);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            p.subtitle {
                text-align: center;
                color: var(--text-muted);
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 24px;
            }
            label {
                display: block;
                font-weight: 600;
                margin-bottom: 8px;
                color: #e2e8f0;
            }
            input[type="file"], textarea {
                width: 100%;
                padding: 12px 16px;
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid var(--border);
                border-radius: 12px;
                color: var(--text);
                font-family: 'Inter', sans-serif;
                box-sizing: border-box;
                transition: border-color 0.2s, box-shadow 0.2s;
            }
            input[type="file"]:focus, textarea:focus {
                outline: none;
                border-color: var(--primary);
                box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
            }
            textarea {
                resize: vertical;
                min-height: 120px;
            }
            button {
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, var(--primary), #818cf8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.4);
            }
            button:active {
                transform: translateY(0);
            }
            .hidden {
                display: none !important;
            }
            #loader {
                text-align: center;
                margin-top: 20px;
            }
            .spinner {
                border: 4px solid rgba(255, 255, 255, 0.1);
                border-left-color: var(--primary);
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 10px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            #results {
                margin-top: 20px;
                background: rgba(15, 23, 42, 0.8);
                border-radius: 16px;
                padding: 30px;
                border: 1px solid rgba(16, 185, 129, 0.3);
                animation: fadeIn 0.5s ease-out;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .score-container {
                text-align: center;
                margin-bottom: 24px;
            }
            .score-circle {
                width: 120px;
                height: 120px;
                border-radius: 50%;
                background: conic-gradient(var(--success) 0%, transparent 0%);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 16px auto;
                position: relative;
                transition: background 1s ease-out;
            }
            .score-inner {
                width: 100px;
                height: 100px;
                background: var(--surface);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2rem;
                font-weight: 700;
                color: var(--success);
            }
            .stat-row {
                display: flex;
                justify-content: space-between;
                padding: 12px 0;
                border-bottom: 1px solid var(--border);
            }
            .stat-row:last-child {
                border-bottom: none;
            }
            .skills-list {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 16px;
            }
            .skill-tag {
                background: rgba(99, 102, 241, 0.2);
                color: #a5b4fc;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.875rem;
                font-weight: 600;
                border: 1px solid rgba(99, 102, 241, 0.3);
            }
            #error-message {
                color: #ef4444;
                background: rgba(239, 68, 68, 0.1);
                padding: 12px;
                border-radius: 8px;
                margin-top: 20px;
                border: 1px solid rgba(239, 68, 68, 0.3);
                text-align: center;
            }
            .back-btn {
                background: transparent;
                border: 1px solid var(--border);
                margin-top: 20px;
            }
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.05);
                box-shadow: none;
            }
            /* Responsive */
            @media (max-width: 640px) {
                .container {
                    padding: 20px;
                    margin: 20px;
                    border-radius: 16px;
                }
                h2 {
                    font-size: 2rem;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="text-align: center;">THE RESUME SCANNER</h1>
        
            
            <div id="homePage">
                <p style="text-align: center; color: var(--text); margin-bottom: 30px; font-size: 1.1rem; line-height: 1.6;">
                    Upload your resume and the job description to instantly see how well you match the role. Find missing skills and optimize your chances!
                </p>
                <button id="startBtn" onclick="startScanner()" style="padding: 16px; font-size: 1.2rem;">Get Started</button>
            </div>

            <form id="uploadForm" class="hidden">
                <div class="form-group">
                    <label for="resume_pdf">1. Upload Resume (PDF)</label>
                    <input type="file" id="resume_pdf" name="resume_pdf" accept=".pdf" required>
                </div>
                
                <div class="form-group">
                    <label for="job_description">2. Paste Job Description</label>
                    <textarea id="job_description" name="job_description" placeholder="Paste the job requirements here..." required></textarea>
                </div>
                
                <button type="submit" id="submitBtn">Analyze Resume</button>
            </form>

            <div id="loader" class="hidden">
                <div class="spinner"></div>
                <p>Analyzing document...</p>
            </div>

            <div id="error-message" class="hidden"></div>

            <div id="results" class="hidden">
                <div class="score-container">
                    <div class="score-circle" id="scoreCircle">
                        <div class="score-inner" id="scoreValue">0%</div>
                    </div>
                    <h3>Match Score</h3>
                    <p style="color: var(--text-muted); font-size: 0.9rem;">File: <span id="fileName"></span></p>
                </div>
                
                <div class="stat-row">
                    <span>Matched Skills</span>
                    <strong id="matchedCount">0</strong>
                </div>
                <div class="stat-row">
                    <span>Total Job Skills</span>
                    <strong id="totalSkills">0</strong>
                </div>

                <div style="margin-top: 24px;">
                    <h4>Skills Found</h4>
                    <div class="skills-list" id="skillsList"></div>
                </div>

                <button class="back-btn" onclick="resetForm()">Analyze Another Resume</button>
            </div>
        </div>

        <script>
            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const form = e.target;
                const formData = new FormData(form);
                
                const loader = document.getElementById('loader');
                const results = document.getElementById('results');
                const errorDiv = document.getElementById('error-message');
                
                form.classList.add('hidden');
                errorDiv.classList.add('hidden');
                loader.classList.remove('hidden');
                
                try {
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.detail || 'Something went wrong');
                    }
                    
                    document.getElementById('scoreValue').textContent = data.match_score + '%';
                    document.getElementById('scoreCircle').style.background = `conic-gradient(var(--success) ${data.match_score}%, rgba(255,255,255,0.05) 0%)`;
                    
                    document.getElementById('fileName').textContent = data.filename;
                    document.getElementById('matchedCount').textContent = data.matched_count;
                    document.getElementById('totalSkills').textContent = data.total_jd_skills;
                    
                    const skillsList = document.getElementById('skillsList');
                    skillsList.innerHTML = '';
                    if (data.matched_skills && data.matched_skills.length > 0) {
                        data.matched_skills.forEach(skill => {
                            const span = document.createElement('span');
                            span.className = 'skill-tag';
                            span.textContent = skill;
                            skillsList.appendChild(span);
                        });
                    } else {
                        skillsList.innerHTML = '<span style="color: var(--text-muted); font-size: 0.9rem;">No matching skills found.</span>';
                    }
                    
                    loader.classList.add('hidden');
                    results.classList.remove('hidden');
                    
                } catch (err) {
                    loader.classList.add('hidden');
                    form.classList.remove('hidden');
                    errorDiv.textContent = err.message;
                    errorDiv.classList.remove('hidden');
                }
            });

            function startScanner() {
                document.getElementById('homePage').classList.add('hidden');
                document.getElementById('uploadForm').classList.remove('hidden');
            }

            function resetForm() {
                document.getElementById('uploadForm').reset();
                document.getElementById('results').classList.add('hidden');
                document.getElementById('homePage').classList.remove('hidden');
                document.getElementById('error-message').classList.add('hidden');
            }
        </script>
    </body>
    </html>
    """

# Importing the stop words of english
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_and_chop_text(raw_text: str):

    # Make everthing lowercase
    text = raw_text.lower() 

    # Removing and replacing everything except numbers and alphabets with space
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    # Splitting   
    words_list = text.split()

    # Removing the stop words
    filtered_list = [word for word in words_list if word not in stop_words]
    
    # Stemming the words to their root word
    stemmed_words = [stemmer.stem(word) for word in filtered_list]
    return stemmed_words


@app.post("/api/analyze")
async def analyze_data(
    job_description: str = Form(...),
    resume_pdf: UploadFile = File(...)
):
    # -----------------------------------------------
    #             Name Validation
    # -----------------------------------------------

    file_name = resume_pdf.filename or "unknown"
    if not file_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type . Please upload a PDF file."
        )
    
    # ------------------------------------------------
    #     Reading the file into Memory(RAM)
    # ------------------------------------------------

    try: 
        file_bytes = await resume_pdf.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
    
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    
    # --------------------------------------------------
    #          Security and Size checks
    # --------------------------------------------------

    if len(file_bytes) > (5*1024*1024):  # 5 MB Limit
        raise HTTPException(
            status_code=400,
            detail="The uploaded file should not exceed 5MB limit."
        )
    
    if not file_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=400,
            detail="File does not look like a valid PDF format."
        )
    
    # ------------------------------------------------
    #            Text Extraction & NLP
    # ------------------------------------------------


    try:
        pdf_file_obj = io.BytesIO(file_bytes)
        pdf_reader = pypdf.PdfReader(pdf_file_obj)
        resume_text = ""

        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                resume_text += extracted + "\n"
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to read PDF.")
    
    # Using the clean_and_chop_text function
    resume_words = clean_and_chop_text(resume_text)
    jd_words = clean_and_chop_text(job_description)

    # Removing duplicates
    resume_set = set(resume_words)
    jd_set = set(jd_words)


    # To match the words
    matched_words = resume_set.intersection(jd_set)

    # Calculating the score
    if len(jd_set) == 0:
        score = 0
    else:
        score = len(matched_words) / len(jd_set) * 100

    # Calculating the missing skills
    missing_skills = jd_set - resume_set
    
    return {
        "match_score": round(score, 2),
        "matched_skills": sorted(list(matched_words)),
        "total_jd_skills": len(jd_set),
        "matched_count": len(matched_words),
        "filename": file_name,
        "missing_skills" : sorted(list(missing_skills))
    }



