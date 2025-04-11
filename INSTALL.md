# Installation Guide for Smart Resume Generator

This document provides detailed instructions for installing all dependencies required for the Smart Resume Generator application.

## Prerequisites

1. Python 3.8 or higher
2. pip (Python package manager)
3. Git (for cloning the repository)

## Basic Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Smart-Resume-Generator.git
   cd Smart-Resume-Generator
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Installing wkhtmltopdf (Required for PDF Generation)

The application requires wkhtmltopdf for PDF generation. Follow the instructions below for your operating system:

### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install wkhtmltopdf
```

### macOS

Using Homebrew:
```bash
brew install wkhtmltopdf
```

### Windows

1. Download the installer from [wkhtmltopdf downloads page](https://wkhtmltopdf.org/downloads.html)
2. Run the installer and follow the instructions
3. Add the installation directory to your system PATH

## Verifying wkhtmltopdf Installation

To verify that wkhtmltopdf is correctly installed, open a terminal/command prompt and run:

```bash
wkhtmltopdf --version
```

You should see version information if the installation was successful.

## Running the Application

1. Start the main App:
   ```bash
   python main.py
   ```


3. Open your browser and navigate to the URL provided by Streamlit (typically http://localhost:8501)

## Troubleshooting

### PDF Generation Issues

If you encounter errors with PDF generation:

1. Ensure wkhtmltopdf is properly installed
2. Verify that it's in your system PATH
3. Try running a simple wkhtmltopdf command to confirm it works:
   ```bash
   wkhtmltopdf https://google.com test.pdf
   ```

### API Connection Issues

If the frontend can't connect to the API:
1. Ensure the API server is running (`python main.py`)
2. Check that the API_BASE_URL in app.py matches your API server address
3. Default is http://localhost:8000

## For Developers

When developing locally, you can use:
```bash
uvicorn main:app --reload
```

This enables hot-reloading for the API server during development.
