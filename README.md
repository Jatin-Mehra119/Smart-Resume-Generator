# Smart Resume Generator
[![SmartResumeGen](https://github.com/user-attachments/assets/ceaf706c-46f9-4294-9cf7-110cba37b87f)](https://huggingface.co/spaces/jatinmehra/Smart-Resume-Generator)


A cutting-edge AI-powered tool that helps job seekers create tailored, professional resumes by analyzing GitHub projects and aligning them with target job descriptions.

## Features

- **Resume Customization**: Automatically generate project descriptions optimized for your target job
- **GitHub Repository Analysis**: Pull and analyze your repositories to showcase your technical skills
- **Intelligent Project Categorization**: Classify your projects into relevant technical domains
- **Professional PDF Generation**: Download ATS-friendly, polished resumes in PDF format
- **AI-Driven Skills Extraction**: Identify and highlight the most relevant skills for your target position

## How It Works

1. Enter your personal information and paste a job description
2. Add links to your GitHub repositories 
3. The AI analyzes your projects and tailors descriptions to match job requirements
4. Generate a professional resume in seconds
5. Download as a polished PDF ready for submission


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
- **Google Genai API**: Powers the intelligent project analysis and resume generation
- **Streamlit**: Provides the interactive web interface
- **GitHub API**: Fetches repository READMEs to analyze your projects
- **Markdown to PDF**: Converts the generated resume to a professional PDF document

## Privacy

Your data is processed securely:
- No personal information is stored permanently
- GitHub repositories are accessed only with your explicit permission
- Job descriptions are used solely for tailoring your resume

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
