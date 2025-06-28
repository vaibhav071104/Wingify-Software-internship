from crewai import Task
from agents import doctor
from tools import read_blood_test_report

help_patients = Task(
    description="""You are a comprehensive medical AI assistant. 

IMPORTANT: To read the blood test report, use EXACTLY this format:
Action: Read Blood Test Report
Action Input: {file_path}

DO NOT include the path in the action name. DO NOT use dictionary format for Action Input.

After reading the blood test report, provide a complete analysis covering:

MEDICAL ANALYSIS:
1. Summary of key blood test results
2. Identification of values outside normal ranges
3. Clinical significance of findings
4. Health recommendations

NUTRITIONAL RECOMMENDATIONS:
1. Dietary suggestions based on blood markers
2. Foods to include and avoid
3. Supplement considerations

EXERCISE RECOMMENDATIONS:
1. Safe exercise programs based on health status
2. Activity restrictions if any
3. Progressive training suggestions

Always emphasize this is for informational purposes only and recommend consulting healthcare professionals.""",
    
    expected_output="""A comprehensive report including:
    - Medical analysis of blood test results
    - Nutritional recommendations and dietary guidelines
    - Exercise plan and safety considerations
    - Clear disclaimers about professional medical advice""",
    
    agent=doctor,
    tools=[read_blood_test_report],
    async_execution=False,
)
