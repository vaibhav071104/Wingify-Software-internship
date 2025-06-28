import os
from dotenv import load_dotenv
load_dotenv()

from crewai_tools import tool
import PyPDF2

@tool("Read Blood Test Report")
def read_blood_test_report(path: str) -> str:
    """Tool to read data from a PDF blood test report"""
    try:
        full_report = ""
        with open(path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content = page.extract_text()
                content = content.replace('\n\n\n', '\n\n')
                content = content.replace('  ', ' ')
                content = content.strip()
                full_report += content + "\n\n"
        
        return full_report.strip()
        
    except Exception as e:
        return f"Error reading PDF file: {str(e)}"
