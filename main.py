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
        prompt = f"""Generate a professional resume in markdown format with the following structure:

# CONTACT INFORMATION
- Name: {resume_data.name}
- Email: {resume_data.email}
- Phone: {resume_data.phone or 'Not provided'}
- GitHub: {resume_data.github or 'Not provided'}
- LinkedIn: {resume_data.linkedin or 'Not provided'}

# EDUCATION
{resume_data.education}

# WORK EXPERIENCE (Remove this Part if not provided)
{resume_data.work_experience or "No professional experience provided"}

# TECHNICAL PROJECTS
{format_projects(resume_data.projects)}

# TECHNICAL SKILLS
- Extract and list the most relevant technical skills from the project descriptions, work experience, and education.
- Prioritize skills mentioned in the job description: {resume_data.job_description[:4500]}
- Include up to 10 skills, formatted as a concise, comma-separated list (e.g., Python, SQL, Docker, AWS).
- If fewer than 5 skills are found, infer additional plausible skills based on project context (e.g., Git for GitHub projects).

Instructions:
- Use markdown formatting: `#` for headers, `-` for bullet points.
- For TECHNICAL PROJECTS:
  - Generate exactly three bullet points per project based on the provided description.
  - Optimize bullet points to emphasize measurable outcomes (e.g., "Improved X by Y%") where possible, inferring plausible metrics if not explicitly stated.
  - Align language with the job description's keywords and tone (e.g., 'engineered' vs 'built' if the job emphasizes engineering).
- Maintain a professional, concise tone throughout; avoid fluff or vague phrases (e.g., 'worked on').
- Use action verbs (e.g., Developed, Implemented, Optimized, Engineered, Deployed) to start each bullet point.
- Ensure ATS compatibility: avoid special characters, excessive formatting, or jargon not aligned with the job.
- Do not include any additional text, explanations, or sections beyond the specified structure.
- If data is missing or incomplete, use 'Not provided' or infer minimally as needed without fabrication."""
        
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
        html = markdown2.markdown(request.markdown_text)
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            h1 {{ font-size: 24px; margin-bottom: 20px; }}
            h2 {{ font-size: 18px; margin-top: 20px; margin-bottom: 10px; }}
            ul {{ margin-left: 20px; }}
          </style>
        </head>
        <body>
          {html}
        </body>
        </html>
        """
        
        options = {
            'quiet': '',
            'encoding': "UTF-8",
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

# ========== Helper Functions ==========
def format_projects(projects: List[ProjectData]) -> str:
    return "\n".join(
        f"- {p.name} ({p.category}): {p.description}"
        for p in projects
    )

if __name__ == "__main__":
    import uvicorn
    # Get port from environment variable or use default 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)