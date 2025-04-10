import streamlit as st
import requests
from urllib.parse import urlparse
import os


# API endpoint (adjust if needed)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# ========== Helper Functions ==========

def get_repo_name(url):
    """Extract repository name from URL"""
    parsed = urlparse(url)
    if parsed.netloc != 'github.com':
        return None
    path_parts = parsed.path.strip('/').split('/')
    return path_parts[1] if len(path_parts) >= 2 else None

def call_api(endpoint, method="get", data=None, params=None):
    """Make API call to backend service with better error handling"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method.lower() == "get":
            response = requests.get(url, params=params, timeout=60)
        elif method.lower() == "post":
            response = requests.post(url, json=data, timeout=60)
        else:
            st.error(f"Unsupported method: {method}")
            return None
            
        if response.status_code == 200:
            return response
        elif response.status_code == 500 and "wkhtmltopdf" in response.text:
            st.warning("""
            **wkhtmltopdf not found on the server!** PDF generation requires wkhtmltopdf to be installed:
            
            **Installation Instructions:**
            - **Linux:** `sudo apt-get install wkhtmltopdf`
            - **macOS:** `brew install wkhtmltopdf`
            - **Windows:** Download from [https://wkhtmltopdf.org/downloads.html](https://wkhtmltopdf.org/downloads.html)
            
            After installing, please restart the application.
            
            Using markdown export as fallback.
            """)
            # Return a special response for this specific error
            return {"error": "wkhtmltopdf_not_found", "content": data.get("markdown_text", "")}
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"API Connection Error: {str(e)}")
        return None

# ========== Page Configuration ==========

st.set_page_config(
    page_title="Smart Resume Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== Custom CSS ==========

st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f9f9f9;
    }
    
    /* Header styling */
    .stApp header {
        background-color: #2c3e50;
        color: white;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        min-height: 120px;
        font-size: 14px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 10px;
    }
    
    /* Text input styling */
    .stTextInput > div > div > input {
        font-size: 14px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 8px;
    }
    
    /* Primary button styling */
    .stButton > button {
        background-color: #2c3e50;
        color: white;
        border-radius: 5px;
        padding: 8px 16px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #34495e;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background-color: #27ae60;
        width: 100%;
        border-radius: 5px;
        padding: 10px;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background-color: #219653;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Expander styling */
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Headings styling */
    h1 {
        color: #2c3e50;
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    h2 {
        color: #34495e;
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }
    
    h3 {
        color: #34495e;
        font-size: 18px;
        font-weight: 600;
    }
    
    /* Progress/success message styling */
    div.stAlert > div[data-baseweb="notification"] {
        border-radius: 8px;
        padding: 12px 16px;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 5px 5px 0 0;
        padding: 10px 16px;
        background-color: #f1f1f1;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    
    /* Form styling */
    div[data-testid="stForm"] {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* Card styling for projects */
    .project-card {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #3498db;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    /* Custom header with icon */
    .header-with-icon {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 30px;
    }
    
    /* Step indicator */
    .step-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .step-header {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .step-number {
        background-color: #3498db;
        color: white;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        margin-right: 10px;
        font-weight: bold;
    }
    
    .step-title {
        font-size: 18px;
        font-weight: 600;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)

# ========== App Header ==========

col1, col2 = st.columns([1, 5])
with col1:
    st.markdown("# 📄")
with col2:
    st.markdown("# Smart Resume Generator")

st.markdown("##### Create an ATS-friendly professional resume optimized for your target job")

# ========== Initialize Session State ==========

if 'step' not in st.session_state:
    st.session_state.step = 1

if 'personal_info' not in st.session_state:
    st.session_state.personal_info = {}

if 'projects' not in st.session_state:
    st.session_state.projects = []

if 'resume_markdown' not in st.session_state:
    st.session_state.resume_markdown = None

if 'pdf_data' not in st.session_state:
    st.session_state.pdf_data = None

# ========== Progress Bar ==========

# Calculate progress based on current step
progress = (st.session_state.step - 1) / 3  # We have 4 steps (0-indexed)
st.progress(progress)

# Display current step indicator
step_labels = {
    1: "Personal Information",
    2: "Project Selection",
    3: "Resume Preview",
    4: "Download Resume"
}

st.markdown(f"**Current Step: {step_labels[st.session_state.step]}**")

# ========== Step 1: Personal Information ==========

if st.session_state.step == 1:
    with st.container():
        st.markdown("""
        <div class="step-container">
            <div class="step-header">
                <div class="step-number">1</div>
                <div class="step-title">Personal Information</div>
            </div>
            Enter your details and paste the job description you're targeting.
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("personal_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Full Name*", help="Your complete name as it should appear on your resume")
                email = st.text_input("Email Address*", help="Your professional email address")
                phone = st.text_input("Phone Number", help="Your contact number (optional)")
                
            with col2:
                github = st.text_input("GitHub Profile", help="Your GitHub username or complete URL")
                linkedin = st.text_input("LinkedIn Profile", help="Your LinkedIn username or complete URL")
                skills = st.text_input("Key Skills (optional)", help="Comma-separated list of your top skills")
            
            education = st.text_area("Education*", 
                placeholder="e.g., Bachelor of Science in Computer Science, University of XYZ, 2020-2024")
            
            work_exp = st.text_area("Work Experience",
                placeholder="e.g., Software Engineer at ABC Corp (2022-Present): Developed and maintained...")
                
            job_desc = st.text_area("Target Job Description*",
                placeholder="Paste the complete job description here. This helps tailor your resume to the specific role.")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                submit_button = st.form_submit_button("Continue to Next Step")
            
            if submit_button:
                if not all([name, email, education, job_desc]):
                    st.error("Please fill all required fields marked with *")
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
                    st.session_state.step = 2
                    st.rerun()

# ========== Step 2: Project Selection ==========

elif st.session_state.step == 2:
    with st.container():
        st.markdown("""
        <div class="step-container">
            <div class="step-header">
                <div class="step-number">2</div>
                <div class="step-title">Project Selection</div>
            </div>
            Add GitHub repositories to generate tailored project descriptions.
        </div>
        """, unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Personal Information"):
            st.session_state.step = 1
            st.rerun()
        
        repos = st.text_area("GitHub Repository URLs (one per line)",
            placeholder="https://github.com/username/repository-name",
            help="Enter links to your GitHub repositories that you want to include in your resume")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("Generate Project Descriptions", key="gen_proj_btn", use_container_width=True):
                if not repos:
                    st.error("Please add at least one GitHub repository URL")
                else:
                    with st.spinner("Analyzing repositories and generating tailored descriptions..."):
                        projects = []
                        success_count = 0
                        
                        for url in repos.split("\n"):
                            url = url.strip()
                            if not url:
                                continue
                            
                            # Get repository name
                            repo_name = get_repo_name(url)
                            if not repo_name:
                                st.error(f"Invalid GitHub URL: {url}")
                                continue
                            
                            # Fetch README content
                            readme_response = call_api("/get_readme", params={"url": url})
                            if not readme_response:
                                continue
                            
                            readme_data = readme_response.json()
                            if "error" in readme_data:
                                st.error(f"Failed to fetch README for {url}: {readme_data['error']}")
                                continue
                            
                            readme_content = readme_data.get("content", "")
                            
                            # Generate description
                            desc_response = call_api("/generate_description", "post", {
                                "readme_content": readme_content,
                                "job_description": st.session_state.personal_info["job_description"]
                            })
                            if not desc_response:
                                continue
                                
                            desc_data = desc_response.json()
                            description = desc_data.get("description", "")
                            
                            # Generate category
                            cat_response = call_api("/generate_category", "post", {
                                "readme_content": readme_content,
                                "job_description": st.session_state.personal_info["job_description"]
                            })
                            if not cat_response:
                                continue
                                
                            cat_data = cat_response.json()
                            category = cat_data.get("category", "Other")
                            
                            # Add project
                            projects.append({
                                "name": repo_name,
                                "description": description,
                                "category": category
                            })
                            success_count += 1
                        
                        if success_count > 0:
                            st.session_state.projects = projects
                            st.success(f"Successfully processed {success_count} repositories!")
                        else:
                            st.error("Failed to process any repositories. Please check the URLs and try again.")
        
        with col2:
            if st.session_state.projects and st.button("Continue to Resume Preview", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        
        # Display project previews
        if st.session_state.projects:
            st.subheader("Project Previews")
            
            for idx, proj in enumerate(st.session_state.projects):
                st.markdown(f"""
                <div class="project-card">
                    <h3>{proj['name']}</h3>
                    <p><strong>Category:</strong> {proj['category']}</p>
                    <p>{proj['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([8, 2])
                with col2:
                    if st.button("Remove", key=f"remove_{idx}"):
                        st.session_state.projects.pop(idx)
                        st.rerun()
                st.divider()

# ========== Step 3: Resume Preview ==========

elif st.session_state.step == 3:
    with st.container():
        st.markdown("""
        <div class="step-container">
            <div class="step-header">
                <div class="step-number">3</div>
                <div class="step-title">Resume Preview</div>
            </div>
            Review your generated resume and make final adjustments.
        </div>
        """, unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Project Selection"):
            st.session_state.step = 2
            st.rerun()
        
        # Generate resume
        if not st.session_state.resume_markdown:
            with st.spinner("Generating your professional resume..."):
                resume_data = {
                    **st.session_state.personal_info,
                    "projects": st.session_state.projects
                }
                
                response = call_api("/generate_resume", "post", resume_data)
                if response:
                    data = response.json()
                    st.session_state.resume_markdown = data.get("resume_markdown", "")
        
        # Display and edit resume
        if st.session_state.resume_markdown:
            edited_markdown = st.text_area(
                "Edit your resume content if needed:",
                value=st.session_state.resume_markdown,
                height=400
            )
            
            # Update if edited
            if edited_markdown != st.session_state.resume_markdown:
                st.session_state.resume_markdown = edited_markdown
                st.session_state.pdf_data = None  # Reset PDF if content changed
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("Regenerate Resume", use_container_width=True):
                    st.session_state.resume_markdown = None
                    st.rerun()
            
            with col2:
                if st.button("Continue to Download", use_container_width=True):
                    # Generate PDF when moving to download step
                    with st.spinner("Preparing PDF document..."):
                        response = call_api("/generate_pdf", "post", {
                            "markdown_text": st.session_state.resume_markdown
                        })
                        
                        if response:
                            if isinstance(response, dict) and response.get("error") == "wkhtmltopdf_not_found":
                                # Handle the special wkhtmltopdf error case
                                st.session_state.pdf_data = None
                                st.session_state.fallback_markdown = response.get("content")
                                st.session_state.step = 4
                                st.rerun()
                            else:
                                st.session_state.pdf_data = response.content
                                st.session_state.step = 4
                                st.rerun()

# ========== Step 4: Download Resume ==========

elif st.session_state.step == 4:
    with st.container():
        st.markdown("""
        <div class="step-container">
            <div class="step-header">
                <div class="step-number">4</div>
                <div class="step-title">Download Resume</div>
            </div>
            Your resume is ready! Download it and start applying to your target job.
        </div>
        """, unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Resume Preview"):
            st.session_state.step = 3
            st.rerun()
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Resume Preview")
            st.markdown(st.session_state.resume_markdown)
        
        with col2:
            st.markdown("### Download Options")
            
            if st.session_state.pdf_data:
                filename = f"{st.session_state.personal_info['name'].replace(' ', '_')}_Resume.pdf"
                
                st.download_button(
                    label="Download Resume PDF",
                    data=st.session_state.pdf_data,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                # Fallback to markdown download
                filename = f"{st.session_state.personal_info['name'].replace(' ', '_')}_Resume.md"
                
                st.download_button(
                    label="Download Resume Markdown",
                    data=st.session_state.resume_markdown,
                    file_name=filename,
                    mime="text/markdown",
                    use_container_width=True
                )
                
                st.warning("""
                **PDF generation is not available.**  
                
                To enable PDF generation, please install wkhtmltopdf:
                - **Linux:** `sudo apt-get install wkhtmltopdf`
                - **macOS:** `brew install wkhtmltopdf`
                - **Windows:** Download from [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
                
                After installing, restart the application.
                """)
            
            st.markdown("""
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <h4 style="color: #2980b9;">Tips for using your resume</h4>
                <ul>
                    <li>Tailor your resume further for each specific job application</li>
                    <li>Use the same keywords from the job description</li>
                    <li>Quantify your achievements wherever possible</li>
                    <li>Follow up after submitting your application</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

# ========== Footer ==========

st.divider()
st.markdown("""
<div style="text-align: center; color: #7f8c8d; padding: 20px;">
    Smart Resume Generator | Created with ❤️ | &copy; 2025
</div>
""", unsafe_allow_html=True)