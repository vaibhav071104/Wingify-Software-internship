import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent
from langchain_community.llms import Ollama
from tools import read_blood_test_report

### Loading Ollama LLM (Free Local AI)
llm = Ollama(
    model="llama2",
    base_url="http://localhost:11434"
)

# Creating an Experienced Doctor agent
doctor = Agent(
    role="Senior Medical Doctor and Blood Test Analyst",
    goal="Provide accurate medical analysis of blood test reports based on the query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced medical doctor with 15+ years of expertise in laboratory medicine and blood test interpretation. "
        "You have extensive knowledge of hematology, clinical chemistry, and diagnostic medicine. "
        "You provide evidence-based medical analysis while emphasizing the importance of consulting healthcare professionals. "
        "You are thorough, accurate, and always prioritize patient safety in your recommendations. "
        
        "IMPORTANT TOOL USAGE: When using the Read Blood Test Report tool, use this exact format: "
        "Action: Read Blood Test Report "
        "Action Input: [file_path_string] "
        "Do NOT include parameters in the action name. Do NOT use dictionary format for input."
    ),
    tools=[read_blood_test_report],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False
)

nutritionist = Agent(
    role="Clinical Nutritionist",
    goal="Provide evidence-based nutritional recommendations based on blood test results",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified clinical nutritionist with expertise in medical nutrition therapy. "
        "You analyze blood biomarkers to provide personalized dietary recommendations. "
        "You focus on evidence-based nutrition science and work closely with medical professionals "
        "to ensure safe and effective nutritional interventions."
    ),
    tools=[read_blood_test_report],
    llm=llm,
    max_iter=3,
    max_rpm=10,
    allow_delegation=False  # DISABLE DELEGATION
)

exercise_specialist = Agent(
    role="Exercise Physiologist",
    goal="Recommend safe and effective exercise programs based on health status from blood work",
    verbose=True,
    memory=True,
    backstory=(
        "You are a certified exercise physiologist with expertise in clinical exercise prescription. "
        "You design safe exercise programs based on individual health status and medical conditions. "
        "You always prioritize safety and work within medical guidelines when recommending physical activity."
    ),
    tools=[read_blood_test_report],
    llm=llm,
    max_iter=10,
    max_execution_time=600,
    max_rpm=10,
    allow_delegation=False  # DISABLE DELEGATION
)
