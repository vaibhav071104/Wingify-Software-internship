from fastapi import FastAPI, File, UploadFile, Form, HTTPException
import os
import uuid
from crewai import Crew, Process
from agents import doctor
from task import help_patients

app = FastAPI(title="Blood Test Report Analyser")

def run_crew(query: str, file_path: str = "data/sample.pdf"):
    """Run the medical analysis crew"""
    try:
        medical_crew = Crew(
            agents=[doctor],
            tasks=[help_patients],
            process=Process.sequential,
            verbose=True
        )
        
        result = medical_crew.kickoff({
            'query': query, 
            'file_path': file_path,
        })
        return result
        
    except Exception as e:
        raise Exception(f"Error running medical crew: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report(
    file: UploadFile = File(...),
    query: str = Form(default="Provide a comprehensive analysis of my blood test report")
):
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    try:
        os.makedirs("data", exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        if not query or query.strip() == "":
            query = "Provide a comprehensive analysis of my blood test report"
        
        response = run_crew(query=query.strip(), file_path=file_path)
        
        return {
            "status": "success",
            "query": query,
            "analysis": str(response),
            "file_processed": file.filename,
            "message": "Analysis completed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing blood report: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
