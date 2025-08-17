// Smart Resume Generator - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Configuration - No need for separate API base URL now
    const API_BASE_URL = ''; // Use relative URLs
    
    // Debug: Check if cover letter elements exist
    console.log('Cover letter button exists:', !!document.getElementById('generate-cover-letter-btn'));
    console.log('Company name input exists:', !!document.getElementById('companyName'));
    
    // State management
    let appState = {
        currentStep: 1,
        personalInfo: {},
        projects: [],
        resumeMarkdown: null,
        pdfData: null,
        coverLetter: null
    };
    
    // DOM Elements
    const progressBar = document.getElementById('progress-bar');
    const stepLabel = document.getElementById('step-label');
    const stepSections = document.querySelectorAll('.step-section');
    
    // Navigation between steps
    function goToStep(step) {
        // Update state
        appState.currentStep = step;
        
        // Update UI
        stepSections.forEach(section => section.classList.remove('active'));
        document.getElementById(`step${step}`).classList.add('active');
        
        // Update progress bar
        const progress = ((step - 1) / 3) * 100;
        progressBar.style.width = `${progress}%`;
        
        // Update step label
        const stepLabels = {
            1: "Personal Information",
            2: "Project Selection",
            3: "Resume Preview",
            4: "Download Resume"
        };
        stepLabel.textContent = stepLabels[step];
        
        // Special handling for step 3 (Resume Preview)
        if (step === 3 && !appState.resumeMarkdown) {
            generateResume();
        }
        
        // Special handling for step 4 (Download)
        if (step === 4 && !appState.pdfData) {
            preparePDF();
        }
    }
    
    // Step 1: Personal Information Form
    document.getElementById('personal-info-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validation
        const requiredFields = ['fullName', 'email', 'education', 'jobDescription'];
        let valid = true;
        
        requiredFields.forEach(field => {
            const input = document.getElementById(field);
            if (!input.value.trim()) {
                valid = false;
                input.classList.add('is-invalid');
            } else {
                input.classList.remove('is-invalid');
            }
        });
        
        if (!valid) {
            showAlert('Please fill all required fields marked with *', 'danger');
            return;
        }
        
        // Store form data
        appState.personalInfo = {
            name: document.getElementById('fullName').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            github: document.getElementById('github').value,
            linkedin: document.getElementById('linkedin').value,
            skills: document.getElementById('skills').value,
            education: document.getElementById('education').value,
            work_experience: document.getElementById('workExperience').value,
            job_description: document.getElementById('jobDescription').value
        };
        
        // Move to next step
        goToStep(2);
    });
    
    // Step 2: Project Selection
    document.getElementById('back-to-step1').addEventListener('click', function() {
        goToStep(1);
    });
    
    document.getElementById('generate-descriptions-btn').addEventListener('click', function() {
        const repoUrls = document.getElementById('repoUrls').value.trim();
        
        if (!repoUrls) {
            showAlert('Please add at least one GitHub repository URL', 'danger');
            return;
        }
        
        generateProjectDescriptions(repoUrls.split('\n').filter(url => url.trim()));
    });
    
    document.getElementById('go-to-step3-btn').addEventListener('click', function() {
        if (appState.projects.length > 0) {
            goToStep(3);
        } else {
            showAlert('Please generate at least one project description first', 'warning');
        }
    });
    
    // Step 3: Resume Preview
    document.getElementById('back-to-step2').addEventListener('click', function() {
        goToStep(2);
    });
    
    document.getElementById('regenerate-resume-btn').addEventListener('click', function() {
        appState.resumeMarkdown = null;
        document.getElementById('resume-content').style.display = 'none';
        document.getElementById('resume-loading').style.display = 'block';
        generateResume();
    });
    
    document.getElementById('go-to-step4-btn').addEventListener('click', function() {
        // Get the possibly edited markdown
        const markdown = document.getElementById('resumeMarkdown').value;
        if (markdown !== appState.resumeMarkdown) {
            appState.resumeMarkdown = markdown;
            appState.pdfData = null; // Reset PDF if content was changed
        }
        
        goToStep(4);
    });
    
    // Step 4: Download Resume
    document.getElementById('back-to-step3').addEventListener('click', function() {
        goToStep(3);
    });
    
    document.getElementById('download-pdf-btn').addEventListener('click', function() {
        if (appState.pdfData) {
            downloadFile(
                appState.pdfData, 
                `${appState.personalInfo.name.replace(/\s+/g, '_')}_Resume.pdf`, 
                'application/pdf'
            );
        } else {
            showAlert('PDF is not available. Please try the Markdown version instead.', 'warning');
            document.getElementById('pdf-warning').style.display = 'block';
        }
    });
    
    document.getElementById('download-markdown-btn').addEventListener('click', function() {
        downloadFile(
            appState.resumeMarkdown, 
            `${appState.personalInfo.name.replace(/\s+/g, '_')}_Resume.md`, 
            'text/markdown'
        );
    });
    
    // Cover Letter Generation
    const coverLetterBtn = document.getElementById('generate-cover-letter-btn');
    if (coverLetterBtn) {
        coverLetterBtn.addEventListener('click', function() {
            console.log('Cover letter button clicked!'); // Debug log
            
            const companyName = document.getElementById('companyName').value.trim();
            console.log('Company name:', companyName); // Debug log
            
            if (!companyName) {
                showAlert('Please enter a company name to generate a cover letter', 'danger');
                document.getElementById('companyName').classList.add('is-invalid');
                return;
            }
            
            document.getElementById('companyName').classList.remove('is-invalid');
            
            // Show alert when cover letter generation starts
            showAlert(`Starting to generate cover letter for ${companyName}...`, 'info');
            
            generateCoverLetter(companyName);
        });
    } else {
        console.error('Cover letter button not found!');
    }
    
    const downloadCoverLetterBtn = document.getElementById('download-cover-letter-btn');
    if (downloadCoverLetterBtn) {
        downloadCoverLetterBtn.addEventListener('click', function() {
            if (appState.coverLetter) {
                const companyName = document.getElementById('companyName').value.trim();
                downloadFile(
                    appState.coverLetter, 
                    `${appState.personalInfo.name.replace(/\s+/g, '_')}_Cover_Letter_${companyName.replace(/\s+/g, '_')}.txt`, 
                    'text/plain'
                );
            } else {
                showAlert('No cover letter available to download', 'warning');
            }
        });
    } else {
        console.error('Download cover letter button not found!');
    }
    
    // API Functions
    async function callAPI(endpoint, method = 'GET', data = null, params = null) {
        try {
            // Update to use /api/ prefix for all endpoints
            const url = new URL(`${API_BASE_URL}/api${endpoint}`, window.location.origin);
            
            // Add query parameters if provided
            if (params) {
                Object.keys(params).forEach(key => {
                    url.searchParams.append(key, params[key]);
                });
            }
            
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };
            
            if (data && (method === 'POST' || method === 'PUT')) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(url, options);
            
            // Handle wkhtmltopdf not found error
            if (response.status === 500 && (await response.text()).includes('wkhtmltopdf')) {
                showAlert('PDF generation is not available. wkhtmltopdf is not installed on the server.', 'warning');
                document.getElementById('pdf-warning').style.display = 'block';
                return { error: 'wkhtmltopdf_not_found' };
            }
            
            if (!response.ok) {
                throw new Error(`API Error: ${response.status} ${response.statusText}`);
            }
            
            // If response is PDF, return blob
            if (response.headers.get('Content-Type') === 'application/pdf') {
                return await response.blob();
            }
            
            return await response.json();
        } catch (error) {
            showAlert(`API Connection Error: ${error.message}`, 'danger');
            console.error('API error:', error);
            return null;
        }
    }
    
    // Generate project descriptions
    async function generateProjectDescriptions(urls) {
        // Show loading
        const generateBtn = document.getElementById('generate-descriptions-btn');
        const originalText = generateBtn.innerHTML;
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing repositories...';
        
        // Reset projects
        appState.projects = [];
        document.getElementById('project-cards-container').innerHTML = '';
        document.getElementById('preview-heading').classList.add('d-none');
        
        let successCount = 0;
        
        for (const url of urls) {
            if (!url.trim()) continue;
            
            // Get repository name
            const repoName = getRepoName(url);
            if (!repoName) {
                showAlert(`Invalid GitHub URL: ${url}`, 'danger');
                continue;
            }
            
            // Fetch README content
            const readmeResponse = await callAPI('/get_readme', 'GET', null, { url });
            if (!readmeResponse) continue;
            
            if (readmeResponse.error) {
                showAlert(`Failed to fetch README for ${url}: ${readmeResponse.error}`, 'danger');
                continue;
            }
            
            const readmeContent = readmeResponse.content;
            
            // Generate description
            const descResponse = await callAPI('/generate_description', 'POST', {
                readme_content: readmeContent,
                job_description: appState.personalInfo.job_description
            });
            
            if (!descResponse) continue;
            
            const description = descResponse.description;
            
            // Generate category
            const catResponse = await callAPI('/generate_category', 'POST', {
                readme_content: readmeContent,
                job_description: appState.personalInfo.job_description
            });
            
            if (!catResponse) continue;
            
            const category = catResponse.category;
            
            // Add project
            const project = {
                name: repoName,
                description: description,
                category: category
            };
            
            appState.projects.push(project);
            addProjectCard(project, appState.projects.length - 1);
            successCount++;
        }
        
        // Update UI
        generateBtn.disabled = false;
        generateBtn.innerHTML = originalText;
        
        if (successCount > 0) {
            showAlert(`Successfully processed ${successCount} repositories!`, 'success');
            document.getElementById('preview-heading').classList.remove('d-none');
            document.getElementById('go-to-step3-btn').disabled = false;
        } else {
            showAlert('Failed to process any repositories. Please check the URLs and try again.', 'danger');
        }
    }
    
    // Add project card to UI
    function addProjectCard(project, index) {
        const cardContainer = document.getElementById('project-cards-container');
        
        const card = document.createElement('div');
        card.className = 'project-card';
        card.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <h3>${project.name}</h3>
                <button class="btn btn-sm btn-outline-danger remove-project" data-index="${index}">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
            <p><span class="badge bg-light text-dark mb-2">Category: ${project.category}</span></p>
            <p>${project.description}</p>
        `;
        
        cardContainer.appendChild(card);
        
        // Add remove event listener
        card.querySelector('.remove-project').addEventListener('click', function() {
            const projectIndex = parseInt(this.dataset.index);
            removeProject(projectIndex);
        });
    }
    
    // Remove project
    function removeProject(index) {
        appState.projects.splice(index, 1);
        
        // Rebuild project cards
        document.getElementById('project-cards-container').innerHTML = '';
        appState.projects.forEach((project, i) => {
            addProjectCard(project, i);
        });
        
        // Update UI
        if (appState.projects.length === 0) {
            document.getElementById('preview-heading').classList.add('d-none');
            document.getElementById('go-to-step3-btn').disabled = true;
        }
    }
    
    // Generate resume
    async function generateResume() {
        document.getElementById('resume-loading').style.display = 'block';
        document.getElementById('resume-content').style.display = 'none';
        
        const resumeData = {
            ...appState.personalInfo,
            projects: appState.projects
        };
        
        const response = await callAPI('/generate_resume', 'POST', resumeData);
        
        if (response) {
            appState.resumeMarkdown = response.resume_markdown;
            document.getElementById('resumeMarkdown').value = appState.resumeMarkdown;
            document.getElementById('resume-loading').style.display = 'none';
            document.getElementById('resume-content').style.display = 'block';
        } else {
            showAlert('Failed to generate resume. Please try again.', 'danger');
            // Stay on step 2 if resume generation fails
            goToStep(2);
        }
    }
    
    // Prepare PDF for step 4
    async function preparePDF() {
        const response = await callAPI('/generate_pdf', 'POST', {
            markdown_text: appState.resumeMarkdown
        });
        
        if (response && !(response.error === 'wkhtmltopdf_not_found')) {
            appState.pdfData = response;
        }
        
        // Render markdown preview
        document.getElementById('resume-preview').innerHTML = marked.parse(appState.resumeMarkdown);
    }
    
    // Generate cover letter
    async function generateCoverLetter(companyName) {
        // Show loading
        document.getElementById('cover-letter-loading').style.display = 'block';
        document.getElementById('cover-letter-content').style.display = 'none';
        document.getElementById('generate-cover-letter-btn').disabled = true;
        
        // Prepare GitHub projects description
        const projectsDescription = appState.projects.map(project => 
            `${project.name} (${project.category}): ${project.description}`
        ).join('\n');
        
        // Call the API with all candidate information
        const response = await callAPI('/generate_cover_letter', 'POST', {
            company_name: companyName,
            job_description: appState.personalInfo.job_description,
            github_projects: projectsDescription,
            candidate_name: appState.personalInfo.name,
            Candidate_email: appState.personalInfo.email,
            Candidate_phone: appState.personalInfo.phone
        });
        
        // Hide loading
        document.getElementById('cover-letter-loading').style.display = 'none';
        document.getElementById('generate-cover-letter-btn').disabled = false;
        
        if (response && response.cover_letter) {
            appState.coverLetter = response.cover_letter;
            document.getElementById('coverLetterText').value = appState.coverLetter;
            document.getElementById('cover-letter-content').style.display = 'block';
            document.getElementById('download-cover-letter-btn').disabled = false;
            showAlert('Cover letter generated successfully!', 'success');
        } else {
            showAlert('Failed to generate cover letter. Please try again.', 'danger');
        }
    }
    
    // Utility Functions
    function getRepoName(url) {
        try {
            const parsed = new URL(url);
            if (parsed.hostname !== 'github.com') {
                return null;
            }
            
            // Split the pathname and get components
            const pathParts = parsed.pathname.replace(/^\/+|\/+$/g, '').split('/');
            
            // For GitHub URLs, the second component is the repository name
            // The first component is the username
            return pathParts.length >= 2 ? pathParts[1] : null;
        } catch (error) {
            return null;
        }
    }
    
    function downloadFile(content, fileName, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        
        setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }, 100);
    }
    
    // Create and display alerts
    function showAlert(message, type) {
        // Create alert container if it doesn't exist
        let alertContainer = document.getElementById('alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alert-container';
            alertContainer.className = 'position-fixed top-0 start-50 translate-middle-x mt-3 z-3';
            document.body.appendChild(alertContainer);
        }
        
        // Create alert
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Add to container
        alertContainer.appendChild(alert);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => {
                alert.remove();
            }, 150);
        }, 5000);
    }
});