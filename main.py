# main.py
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List
import requests
from urllib.parse import urlparse
from google import genai
import os
import markdown2
import pdfkit
from google.genai import types
import tempfile
import dotenv
from datetime import datetime
# Load environment variables from .env file
dotenv.load_dotenv()

app = FastAPI(title="Smart Resume Generator")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ========== Pydantic Models ==========
class GenerateDescriptionRequest(BaseModel):
    readme_content: str
    job_description: str

class GenerateCategoryRequest(BaseModel):
    readme_content: str
    job_description: str

class ProjectData(BaseModel):
    name: str
    description: str
    category: str

class ResumeData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    skills: Optional[str] = None
    education: str
    work_experience: Optional[str] = None
    job_description: str
    projects: List[ProjectData]

class GeneratePDFRequest(BaseModel):
    markdown_text: str

class GenerateCoverLetterRequest(BaseModel):
    company_name: str
    job_description: str
    github_projects: Optional[str] = None
    candidate_name: Optional[str] = None

# ========== Frontend Routes ==========
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main application page"""
    return templates.TemplateResponse("index.html", {"request": request})

# ========== API Endpoints ==========
@app.get("/api")
def api_root():
    return {"message": "Welcome to the Smart Resume Generator API!"}

@app.get("/api/health")
def health_check():
    return {"status": "OK", "message": "API is running!"}

@app.post("/api/generate_description")
async def generate_description_endpoint(request: GenerateDescriptionRequest):
    try:
        prompt = f"""Create a concise resume project description using this README:
        {request.readme_content[:5000]}
        
        Requirements:
        - Focus on technical achievements and outcomes
        - Use action verbs: Developed, Implemented, Optimized
        - Max 5 bullet points
        - No markdown formatting
        - Technical details only"""
        
        if request.job_description:
            prompt += f"\n\nAlign with this job description:\n{request.job_description[:1000]}"
        
        config = types.GenerateContentConfig(max_output_tokens=1550, temperature=0.3)
        response = client.models.generate_content(
            contents=prompt,
            model="gemini-2.0-flash",
            config=config
        )
        return {"description": response.text.strip()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating description: {str(e)}"
        )

@app.post("/api/generate_category")
async def generate_category_endpoint(request: GenerateCategoryRequest):
    try:
        prompt = f"""Classify this project into ONE category:
        like = [Data Science, Data Analyst, Web Dev, Backend Dev, Frontend Dev, Full Stack, DevOps, ML, Java Dev, JS Dev, Python Dev, Mobile Dev, Cloud, Security, QA, Database, Embedded, Networking, AI, Robotics, IoT, Blockchain, AR/VR, Game Dev, UI/UX, Tech Writing, Research, Other]
        
        README: {request.readme_content[:4000]}
        
        Job Context: {request.job_description[:1000] or "General technical role"}
        
        Respond ONLY with the category name."""
        
        config = types.GenerateContentConfig(max_output_tokens=650, temperature=0.3)
        response = client.models.generate_content(
            contents=prompt,
            model="gemini-2.0-flash",
            config=config
        )
        return {"category": response.text.strip()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating category: {str(e)}"
        )

@app.post("/api/generate_resume")
async def generate_resume_endpoint(resume_data: ResumeData):
    try:
        prompt = f"""Generate a professional resume in markdown format with the following structure, optimized for relevance to the job description below.
Job description: {resume_data.job_description[:4500]}
# CONTACT INFORMATION
- Name: {resume_data.name}
- Email: {resume_data.email}
- Phone: {resume_data.phone or 'Not provided'}
- GitHub: {resume_data.github or 'Not provided'}
- LinkedIn: {resume_data.linkedin or 'Not provided'}

# OBJECTIVE
Craft a concise, role-focused objective (2-3 lines) summarizing the candidate's intent and qualifications. Tailor this section based on the job description provided below and the candidate's strengths in projects, education, or experience.

# EDUCATION
{resume_data.education} # Format as: Degree, Major, University, Year.
Example:'BSc in Computer Science, XYZ University, 2023
         Msc in Data Science, ABC University, 2024'

{f"# WORK EXPERIENCE\\n{resume_data.work_experience}" if resume_data.work_experience else ""}

# TECHNICAL PROJECTS
{format_projects(resume_data.projects)}

# TECHNICAL SKILLS
- Extract and list the most relevant technical skills from the project descriptions, work experience, and education.
- Prioritize skills that match the job description.
- Include up to 10 skills in a comma-separated list (e.g., Python, SQL, Docker, AWS).
- If fewer than 5 skills are found, infer additional plausible skills based on context (e.g., Git if GitHub is mentioned).

Instructions:
- Use markdown formatting: `#` for headers, `-` for bullet points.
- For TECHNICAL PROJECTS:
- Write exactly three bullet points per project based on the description.
- Emphasize measurable outcomes (e.g., “Increased accuracy by 20%”), inferring realistic metrics where applicable.
- Align language and terminology with keywords from the job description.
- Maintain a professional, concise tone throughout.
- Start each bullet point with strong action verbs (e.g., Developed, Deployed, Engineered).
- Avoid vague or generic phrases (e.g., “worked on”, “helped with”).
- Ensure the resume is ATS-friendly: no special characters, excessive formatting, or unrelated jargon.
- Do not include any text, explanation, or sections outside the defined structure.
"""
        
        config = types.GenerateContentConfig(max_output_tokens=6050, temperature=0.3)
        response = client.models.generate_content(
            contents=prompt,
            model="gemini-2.0-flash",
            config=config
        )
        return {"resume_markdown": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating resume: {str(e)}"
        )

@app.get("/api/get_readme")
async def get_readme_content(url: str):
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return {"error": "Invalid URL format"}
        
        username, repo = path_parts[:2]
        
        # Get actual repository name (second path component)
        repo_name = path_parts[1] if len(path_parts) >= 2 else None
        
        for branch in ['main', 'master']:
            raw_url = f"https://raw.githubusercontent.com/{username}/{repo_name}/{branch}/README.md"
            response = requests.get(raw_url)
            if response.status_code == 200:
                return {"content": response.text, "repo_name": repo_name}
        return {"error": "README not found"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching README: {str(e)}"
        )

@app.post("/api/generate_pdf")
async def generate_pdf_endpoint(request: GeneratePDFRequest):
    try:
        # Convert markdown to HTML with extra features enabled
        html = markdown2.markdown(request.markdown_text, extras=["tables", "cuddled-lists", "header-ids"])
        
        # Create a professional and elegant HTML template
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&family=Open+Sans:wght@300;400;600&display=swap');
            
            body {{
                font-family: 'Open Sans', Arial, sans-serif;
                color: #333;
                line-height: 1.6;
                margin: 0;
                padding: 12px 10px;
                max-width: 100%;
                font-size: 11pt;
                background: #fff;
            }}
            
            .resume-container {{
                max-width: 8.5in;
                margin: 0 auto;
                border: none;
                box-shadow: none;
            }}
            
            h1 {{
                font-family: 'Roboto', sans-serif;
                font-size: 18pt;
                font-weight: 700;
                color: #1a365d;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #3182ce;
            }}
            
            h2 {{
                font-family: 'Roboto', sans-serif;
                font-size: 14pt;
                font-weight: 600;
                color: #2c5282;
                margin-top: 20px;
                margin-bottom: 10px;
                padding-bottom: 3px;
                border-bottom: 1px solid #bee3f8;
            }}
            
            ul {{
                margin-top: 8px;
                margin-left: 20px;
                padding-left: 0;
            }}
            
            ul li {{
                margin-bottom: 6px;
                list-style-type: square;
            }}
            
            /* Contact information section */
            .contact-info {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-bottom: 15px;
                font-size: 10pt;
            }}
            
            .contact-info p {{
                margin: 0;
                display: inline-block;
            }}
            
            /* Education section */
            .education-entry {{
                margin-bottom: 12px;
            }}
            
            /* Projects section */
            .project-title {{
                font-weight: 600;
            }}
            
            /* Skills section */
            .skills-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 8px;
            }}
            
            .skill-item {{
                background-color: #e2e8f0;
                padding: 3px 8px;
                border-radius: 3px;
                font-size: 9pt;
            }}
            
            /* Page break handling */
            .page-break {{
                page-break-after: always;
            }}
            
            /* Print-specific styles */
            @media print {{
                body {{
                    padding: 0;
                    margin: 12mm 10mm 12mm 10mm;
                }}
                
                .resume-container {{
                    box-shadow: none;
                    border: none;
                }}
            }}
          </style>
        </head>
        <body>
          <div class="resume-container">
            {html}
          </div>
        </body>
        </html>
        """
        
        # Configure PDF rendering options for better quality
        options = {
            'quiet': '',
            'encoding': "UTF-8",
            'enable-local-file-access': '',
            'margin-top': '12mm',     # 1.2 cm top margin
            'margin-right': '10mm',   # 1.0 cm right margin
            'margin-bottom': '12mm',  # 1.2 cm bottom margin
            'margin-left': '10mm',    # 1.0 cm left margin
            'page-size': 'Letter',
            'dpi': '300',
            'image-quality': '100',
            'enable-smart-shrinking': '',
        }
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            try:
                pdfkit.from_string(full_html, tmp.name, options=options)
                return FileResponse(
                    tmp.name,
                    media_type="application/pdf",
                    filename="resume.pdf"
                )
            except Exception as e:
                # If wkhtmltopdf is not installed, raise a more specific error
                error_message = str(e)
                if "No wkhtmltopdf executable found" in error_message:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"PDF generation failed: {error_message}\nPlease install wkhtmltopdf - https://github.com/JazzCore/python-pdfkit/wiki/Installing-wkhtmltopdf"
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"PDF generation failed: {error_message}"
                    )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}"
        )
    
# New Function for generating cover letters with agents for research purposes
from agent import generate_cover_letter

@app.post("/api/generate_cover_letter")
async def generate_cover_letter_endpoint(request: GenerateCoverLetterRequest):
    try:
        cover_letter = generate_cover_letter(
            company_name=request.company_name,
            job_description=request.job_description,
            github_projects=request.github_projects,
            candidate_name=request.candidate_name or "Candidate"
        )
        return {"cover_letter": cover_letter}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cover letter: {str(e)}"
        )

# ========== Helper Functions ==========
def format_projects(projects: List[ProjectData]) -> str:
    return "\n".join(
        f"- {p.name} ({p.category}): {p.description}"
        for p in projects
    )

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable or use default 8000 7860 FOR HUGGINGFACE SPACES.
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run(app, host="0.0.0.0", port=port)