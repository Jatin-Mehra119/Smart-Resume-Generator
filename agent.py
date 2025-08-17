import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools.tavily_search import TavilySearchResults

# Load API keys
load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0, api_key=os.getenv("GEMINI_API_KEY"))

# Initialize Tavily Search tool
tavily_tool = TavilySearchResults(max_results=5)

# Create agent with Tavily + Gemini
agent = initialize_agent(
    tools=[tavily_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

def generate_cover_letter(company_name: str, job_description: str, github_projects: str = None, CandidateName: str = None) -> str:
    """Generate a tailored cover letter using company info, job description, and projects"""

    # Step 1: Fetch company info
    query = f"Collect latest insights, values, and work culture about {company_name}"
    company_info = agent.run(query)

    # Step 2: Build cover letter prompt
    prompt = f"""
    You are a professional career assistant. Write a tailored cover letter for {CandidateName if CandidateName else "the candidate"} applying to {company_name}.

    ### Company Information
    {company_info}

    ### Job Description
    {job_description}

    ### Candidate Projects
    {github_projects if github_projects else "Candidate projects not provided."}

    ### Instructions
    - Highlight how the candidate’s projects and skills align with the company’s values and job role
    - Keep tone professional but enthusiastic
    - Structure: Opening → Why this company → How candidate fits → Closing
    - Limit to 300-400 words
    """

    # Step 3: Generate cover letter
    response = llm.invoke(prompt)
    return response.content


if __name__ == "__main__":
    company = input("Enter company name: ")
    job_desc = input("Paste job description: ")
    projects = input("Paste GitHub project summary (optional): ")

    cover_letter = generate_cover_letter(company, job_desc, projects)
    print("\n--- Generated Cover Letter ---\n")
    print(cover_letter)