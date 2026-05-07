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
    <html>
        <head>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; padding: 40px; color: #333; }
                .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
                h2 { color: #2c3e50; text-align: center; }
                label { font-weight: bold; margin-top: 15px; display: block; }
                input[type="file"], textarea { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ccc; border-radius: 5px; }
                button { background-color: #2980b9; color: white; border: none; padding: 12px 20px; margin-top: 20px; cursor: pointer; width: 100%; border-radius: 5px; font-size: 16px; font-weight: bold; }
                button:hover { background-color: #3498db; }
                
                /* Dashboard Styles */
                #dashboard { display: none; margin-top: 30px; padding-top: 30px; border-top: 2px solid #eee; }
                .score-box { text-align: center; margin-bottom: 20px; }
                #scoreText { font-size: 48px; margin: 0; }
                .skills-container { display: flex; justify-content: space-between; gap: 20px; }
                .skill-box { flex: 1; background: #f9f9f9; padding: 15px; border-radius: 8px; border: 1px solid #ddd; }
                .skill-box h4 { margin-top: 0; text-align: center; }
                .match-list { color: #27ae60; list-style-type: none; padding: 0; }
                .missing-list { color: #e74c3c; list-style-type: none; padding: 0; }
                li { padding: 5px 0; border-bottom: 1px solid #eee; }
                li:last-child { border-bottom: none; }
                
                /* Loading Spinner */
                #loader { display: none; text-align: center; margin-top: 20px; font-weight: bold; color: #2980b9; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>🚀 AI Resume Scanner</h2>
                
                <form id="scannerForm">
                    <label>1. Upload Resume (PDF):</label>
                    <input type="file" id="resumeFile" name="resume_pdf" accept=".pdf" required>
                    
                    <label>2. Paste Job Description:</label>
                    <textarea id="jdText" name="job_description" rows="6" required placeholder="Paste the job requirements here..."></textarea>
                    
                    <button type="submit" id="submitBtn">Analyze Match</button>
                </form>

                <div id="loader">🧠 Analyzing with NLP Engine... Please wait.</div>

                <div id="dashboard">
                    <div class="score-box">
                        <h3>Match Score</h3>
                        <h1 id="scoreText">0%</h1>
                    </div>
                    
                    <div class="skills-container">
                        <div class="skill-box">
                            <h4>✅ Skills Matched (<span id="matchCount">0</span>)</h4>
                            <ul id="matchedList" class="match-list"></ul>
                        </div>
                        <div class="skill-box">
                            <h4>❌ Skills Missing (<span id="missingCount">0</span>)</h4>
                            <ul id="missingList" class="missing-list"></ul>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                document.getElementById('scannerForm').addEventListener('submit', async function(event) {
                    event.preventDefault(); // Stop page reload
                    
                    // UI Polish: Show loader, hide dashboard
                    document.getElementById('loader').style.display = "block";
                    document.getElementById('dashboard').style.display = "none";
                    document.getElementById('submitBtn').disabled = true;

                    // Pack the data
                    let formData = new FormData();
                    formData.append("resume_pdf", document.getElementById('resumeFile').files[0]);
                    formData.append("job_description", document.getElementById('jdText').value);

                    try {
                        // Call the API
                        let response = await fetch('/api/analyze', {
                            method: 'POST',
                            body: formData
                        });

                        if (!response.ok) {
                            let errorData = await response.json();
                            alert("Error: " + errorData.detail);
                            throw new Error("API Error");
                        }

                        let data = await response.json();

                        // Update Score & Colors
                        let scoreEl = document.getElementById('scoreText');
                        scoreEl.innerText = data.match_score + "%";
                        if (data.match_score >= 70) scoreEl.style.color = "#27ae60"; // Green
                        else if (data.match_score >= 40) scoreEl.style.color = "#f39c12"; // Orange
                        else scoreEl.style.color = "#e74c3c"; // Red

                        // Update Counts
                        document.getElementById('matchCount').innerText = data.matched_count;
                        document.getElementById('missingCount').innerText = data.missing_skills.length;

                        // Populate Matched Skills Array
                        let matchedHTML = "";
                        data.matched_skills.forEach(skill => {
                            matchedHTML += `<li>✅ ${skill.toUpperCase()}</li>`;
                        });
                        document.getElementById('matchedList').innerHTML = matchedHTML;

                        // Populate Missing Skills Array
                        let missingHTML = "";
                        data.missing_skills.forEach(skill => {
                            missingHTML += `<li>❌ ${skill.toUpperCase()}</li>`;
                        });
                        document.getElementById('missingList').innerHTML = missingHTML;

                        // Show the Dashboard!
                        document.getElementById('dashboard').style.display = "block";

                    } catch (error) {
                        console.error(error);
                    } finally {
                        // Cleanup UI
                        document.getElementById('loader').style.display = "none";
                        document.getElementById('submitBtn').disabled = false;
                    }
                });
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



