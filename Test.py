import streamlit as st
import requests
from urllib.parse import urlparse
import dotenv
import os
from groq import Groq
import markdown2
import pdfkit

# Load environment variables and initialize Groq client
dotenv.load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ========== Core Functions ==========

def generate_description(readme_content, job_description):
    """Generate tailored project description"""
    prompt = f"""Create a concise resume project description using this README:
    {readme_content[:5000]}
    
    Requirements:
    - Focus on technical achievements and outcomes
    - Use action verbs: Developed, Implemented, Optimized
    - Max 5 bullet points
    - No markdown formatting
    - Technical details only"""
    
    if job_description:
        prompt += f"\n\nAlign with this job description:\n{job_description[:1000]}"
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=3500
    )
    return response.choices[0].message.content.strip()

def generate_category(readme_content, job_description):
    """Classify project into specific category"""
    prompt = f"""Classify this project into ONE category:
    like = [Data Science, Data Analyst, Web Dev, Backend Dev, Frontend Dev, Full Stack, DevOps, ML, Java Dev, JS Dev, Python Dev, Mobile Dev, Cloud, Security, QA, Database, Embedded, Networking, AI, Robotics, IoT, Blockchain, AR/VR, Game Dev, UI/UX, Tech Writing, Research, Other]
    
    README: {readme_content[:4000]}
    
    Job Context: {job_description[:1000] or "General technical role"}
    
    Respond ONLY with the category name."""
    
    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=2050
    )
    return response.choices[0].message.content.strip()

def generate_pdf_from_markdown(markdown_text):
    """Convert markdown to PDF"""
    html = markdown2.markdown(markdown_text)
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
    return pdfkit.from_string(full_html, False)

def generate_resume(resume_data):
    """Generate a highly tailored, professional resume text from structured data"""
    prompt = f"""Generate a professional resume with the following structure and enhanced features:

    CONTACT INFORMATION:
    - Name: {resume_data['name']}
    - Email: {resume_data['email']}
    - Phone: {resume_data.get('phone', 'Not provided')}
    - GitHub: {resume_data.get('github', 'Not provided')}
    - LinkedIn: {resume_data.get('linkedin', 'Not provided')}

    EDUCATION:
    {resume_data['education']}

    WORK EXPERIENCE:
    {resume_data['work_experience'] or "No professional experience provided"}

    TECHNICAL PROJECTS:
    {format_projects(resume_data['projects'])}

    TECHNICAL SKILLS:
    - Extract and list the most relevant technical skills from the project descriptions, work experience, and education.
    - Prioritize skills mentioned in the job description: {resume_data['job_description'][:2500]}
    - Include up to 10 skills, formatted as a concise, comma-separated list (e.g., Python, SQL, Docker, AWS).
    - If fewer than 5 skills are found, infer additional plausible skills based on project context (e.g., Git for GitHub projects).

    Instructions:
    - Adhere strictly to the specified section formats and ordering.
    - For TECHNICAL PROJECTS:
      - Generate exactly three bullet points per project based on the provided description.
      - Optimize bullet points to emphasize measurable outcomes (e.g., "Improved X by Y%") where possible, inferring plausible metrics if not explicitly stated.
      - Align language with the job description’s keywords and tone (e.g., 'engineered' vs 'built' if the job emphasizes engineering).
    - Maintain a professional, concise tone throughout; avoid fluff or vague phrases (e.g., 'worked on').
    - Use action verbs (e.g., Developed, Implemented, Optimized, Engineered, Deployed) to start each bullet point.
    - Ensure ATS compatibility: avoid special characters, excessive formatting, or jargon not aligned with the job.
    - Do not include any additional text, explanations, or sections beyond the specified structure.
    - If data is missing or incomplete, use 'Not provided' or infer minimally as needed without fabrication."""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,  # Low temperature for consistency and professionalism
        max_tokens=4500
    )
    return response.choices[0].message.content

def format_projects(projects):
    return "\n".join(
        f"- {p['name']} ({p['category']}): {p['description']}"
        for p in projects
    )

def get_repo_name(url):
    """Extract repository name from URL"""
    parsed = urlparse(url)
    if parsed.netloc != 'github.com':
        return None
    path_parts = parsed.path.strip('/').split('/')
    return path_parts[1] if len(path_parts) >= 2 else None

def get_readme_content(url):
    """Fetch README content from GitHub"""
    try:
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) < 2:
            return "Invalid URL format"
        
        username, repo = path_parts[:2]
        for branch in ['main', 'master']:
            raw_url = f"https://raw.githubusercontent.com/{username}/{repo}/{branch}/README.md"
            response = requests.get(raw_url)
            if response.status_code == 200:
                return response.text
        return "README not found. Ensure the file exists in the main or master branch."
    except Exception as e:
        return f"Error: {str(e)}"

# ========== Streamlit UI ==========

st.set_page_config(page_title="AI Resume Builder", layout="wide")

# Custom CSS for professional look
st.markdown("""
    <style>
    .stApp { max-width: 900px; margin: 0 auto; }
    .stTextArea textarea { min-height: 120px; font-size: 14px; }
    .stTextInput > div > div > input { font-size: 14px; }
    .stButton > button { 
        background-color: #2c3e50; 
        color: white; 
        border-radius: 5px; 
        padding: 8px 16px; 
    }
    .stButton > button:hover { background-color: #34495e; }
    .stDownloadButton > button { 
        background-color: #27ae60; 
        width: 100%; 
        border-radius: 5px; 
        padding: 10px; 
    }
    .stDownloadButton > button:hover { background-color: #219653; }
    .stExpander { border: 1px solid #e0e0e0; border-radius: 5px; }
    h1 { color: #2c3e50; font-size: 28px; }
    h3 { color: #34495e; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

st.title("Professional Resume Builder")

# Initialize session state
if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}
if 'projects' not in st.session_state:
    st.session_state.projects = []

# Personal Information Section
with st.expander("Personal Information", expanded=True):
    with st.form("personal_form"):
        cols = st.columns(4)
        name = cols[0].text_input("Full Name*", key="name_field")
        email = cols[1].text_input("Email*", key="email_field")
        phone = cols[2].text_input("Phone", key="phone_field")
        github = cols[3].text_input("GitHub Profile", key="github_field")
        linkedin = st.text_input("LinkedIn Profile", key="linkedin_field")
        skills = st.text_input("Skills", key="skills_field i.e. Python, SQL, Machine Learning, Docker, AWS, etc.")
        education = st.text_area("Education*", 
            placeholder="e.g., BS in Computer Science, XYZ University, 2018-2022", 
            key="edu_field")
        work_exp = st.text_area("Work Experience",
            placeholder="e.g., Software Engineer, ABC Corp, 2022-Present...", 
            key="work_field")
        job_desc = st.text_area("Target Job Description*",
            placeholder="Paste the job description you're applying for", 
            key="jobdesc_field")
        
        if st.form_submit_button("Save Profile"):
            if not all([name, email, education, job_desc]):
                st.error("Please fill all required fields (*) before saving.")
            else:
                st.session_state.personal_info = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "github": github,
                    "linkedin": linkedin,
                    "skills": skills,
                    "education": education,
                    "work_experience": work_exp,
                    "job_description": job_desc
                }
                st.success("Profile saved successfully!")

# Project Configuration Section
with st.expander("Add Technical Projects"):
    repos = st.text_area("GitHub Repository URLs (one per line)",
        help="Enter links to your project repositories (e.g., https://github.com/username/repo)", 
        key="repo_field")
    
    if st.button("Generate Project Descriptions", key="gen_proj_btn"):
        if not repos or not st.session_state.personal_info:
            st.error("Please save personal info and add at least one repository URL.")
        else:
            with st.spinner("Analyzing repositories..."):
                projects = []
                for url in repos.split("\n"):
                    url = url.strip()
                    if not url:
                        continue
                    
                    repo_name = get_repo_name(url)
                    if not repo_name:
                        st.error(f"Invalid GitHub URL: {url}")
                        continue
                    
                    readme = get_readme_content(url)
                    if not readme or readme.startswith("Error:") or readme.startswith("Invalid"):
                        st.error(f"Failed to fetch README for {url}: {readme}")
                        continue
                    
                    try:
                        desc = generate_description(
                            readme,
                            st.session_state.personal_info["job_description"]
                        )
                        category = generate_category(
                            readme,
                            st.session_state.personal_info["job_description"]
                        )
                        projects.append({
                            "name": repo_name,
                            "description": desc,
                            "category": category
                        })
                    except Exception as e:
                        st.error(f"Error processing {url}: {str(e)}")
                        continue
                
                st.session_state.projects = projects
                st.success(f"Successfully generated {len(projects)} project descriptions!")

# Preview Section
if st.session_state.projects:
    with st.expander("Preview Projects"):
        for idx, proj in enumerate(st.session_state.projects, 1):
            st.subheader(f"Project {idx}: {proj['name']}")
            st.caption(f"Category: {proj['category']}")
            st.write(proj["description"])

# Resume Generation Section
if st.session_state.personal_info:
    if st.button("Generate Resume PDF", key="gen_pdf_btn"):
        with st.spinner("Creating your professional resume..."):
            resume_data = {
                **st.session_state.personal_info,
                "projects": st.session_state.projects
            }
            
            try:
                resume_text = generate_resume(resume_data)
                pdf_bytes = generate_pdf_from_markdown(resume_text)
                
                st.download_button(
                    label="Download Resume PDF",
                    data=pdf_bytes,
                    file_name=f"{resume_data['name'].replace(' ', '_')}_Resume.pdf",
                    mime="application/pdf",
                    key="download_btn"
                )
                st.success("Resume generated successfully!")
                
                with st.expander("Preview Resume Text"):
                    st.text(resume_text)
                    
            except Exception as e:
                st.error(f"Error generating resume: {str(e)}")