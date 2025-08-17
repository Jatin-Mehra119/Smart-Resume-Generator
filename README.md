# Smart Resume Generator
[![SmartResumeGen](https://github.com/user-attachments/assets/ceaf706c-46f9-4294-9cf7-110cba37b87f)](https://huggingface.co/spaces/jatinmehra/Smart-Resume-Generator)


A cutting-edge AI-powered tool that helps job seekers create tailored, professional resumes by analyzing GitHub projects and aligning them with target job descriptions.

## Features

- **Resume Customization**: Automatically generate project descriptions optimized for your target job
- **GitHub Repository Analysis**: Pull and analyze your repositories to showcase your technical skills
- **Intelligent Project Categorization**: Classify your projects into relevant technical domains
- **Professional PDF Generation**: Download ATS-friendly, polished resumes in PDF format
- **AI-Driven Skills Extraction**: Identify and highlight the most relevant skills for your target position
- **Cover Letter Generation**: Create personalized, professional cover letters tailored to specific companies and job positions

## How It Works

1. Enter your personal information and paste a job description
2. Add links to your GitHub repositories 
3. The AI analyzes your projects and tailors descriptions to match job requirements
4. Generate a professional resume in seconds
5. Download as a polished PDF ready for submission
6. **NEW**: Generate personalized cover letters by entering the company name - the AI will create a tailored cover letter using your profile information, projects, and job requirements

## Cover Letter Generation

The Smart Resume Generator now includes an intelligent cover letter generation feature that creates personalized cover letters for your job applications:

### Key Features:
- **Company-Specific Tailoring**: Enter the target company name to generate a cover letter specifically addressed to that organization
- **Automatic Information Integration**: Seamlessly incorporates your personal details, contact information, and job description from the resume generation process
- **Project Highlighting**: Intelligently references your GitHub projects and technical skills relevant to the position
- **Professional Formatting**: Generates well-structured, business-format cover letters ready for submission
- **Easy Download**: Save your cover letter as a text file for further customization in your preferred document editor

### How to Use:
1. Complete the resume generation process (Steps 1-3)
2. Navigate to the "Generate Cover Letter" section
3. Enter the company name you're applying to
4. Click "Generate Cover Letter" to create your personalized letter
5. Review and download the generated cover letter


## Requirements

- Python 3.8+
- Streamlit
- Google-genai==1.7.0
- fastapi
- uvicorn
- PDFKit (with wkhtmltopdf installed)
- Internet connection for GitHub repository access
- Markdown2

## Technical Details

The application leverages:
- **Google Genai API**: Powers the intelligent project analysis, resume generation, and cover letter creation
- **Streamlit**: Provides the interactive web interface
- **GitHub API**: Fetches repository READMEs to analyze your projects
- **Markdown to PDF**: Converts the generated resume to a professional PDF document
- **FastAPI**: Backend API for resume and cover letter generation endpoints

## Privacy

Your data is processed securely:
- No personal information is stored permanently
- GitHub repositories are accessed only with your explicit permission
- Job descriptions are used solely for tailoring your resume

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
