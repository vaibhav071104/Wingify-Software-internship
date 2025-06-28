from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session
import os
import uuid
import hashlib
import redis
from rq import Queue
from database import get_db, User, AnalysisResult, AnalysisJob
from worker import analyze_blood_test_task

app = FastAPI(title="Blood Test Report Analyser")

# Redis and Queue setup
try:
    redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=False)
    analysis_queue = Queue('blood_analysis', connection=redis_conn)
    print("Redis connection established")
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_conn = None
    analysis_queue = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Blood Test Report Analyser API is running"}

@app.post("/analyze")
async def analyze_blood_report_async(
    file: UploadFile = File(...),
    query: str = Form(default="Provide a comprehensive analysis of my blood test report"),
    user_id: int = Form(default=1),
    db: Session = Depends(get_db)
):
    """Queue blood test analysis for background processing"""
    
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save file and generate hash
    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()
    file_id = str(uuid.uuid4())
    file_path = f"data/blood_test_report_{file_id}.pdf"
    
    os.makedirs("data", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Check if analysis already exists
    existing = db.query(AnalysisResult).filter(
        AnalysisResult.file_hash == file_hash,
        AnalysisResult.user_id == user_id
    ).first()
    
    if existing:
        return {
            "status": "completed",
            "job_id": None,
            "analysis": existing.analysis,
            "message": "Analysis retrieved from database",
            "cached": True
        }
    
    # Check if Redis/Queue is available
    if not analysis_queue:
        # Fallback to synchronous processing
        try:
            from crewai import Crew, Process
            from agents import doctor
            from task import help_patients
            
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
            
            # Store in database
            from database import store_analysis_result
            store_analysis_result(user_id, file.filename, str(result), file_hash)
            
            return {
                "status": "completed",
                "analysis": str(result),
                "message": "Analysis completed (synchronous mode)",
                "cached": False
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    # Queue the analysis job
    try:
        job = analysis_queue.enqueue(
            analyze_blood_test_task,
            file_path=file_path,
            query=query,
            user_id=user_id,
            timeout=600  # 10 minutes
        )
        
        # Store job in database
        job_record = AnalysisJob(
            job_id=job.id,
            user_id=user_id,
            filename=file.filename,
            status="queued"
        )
        db.add(job_record)
        db.commit()
        
        return {
            "status": "queued",
            "job_id": job.id,
            "message": "Analysis queued for processing. Check status with job_id.",
            "estimated_time": "3-5 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue job: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """Check analysis job status"""
    
    if not analysis_queue:
        raise HTTPException(status_code=503, detail="Queue service unavailable")
    
    try:
        job = analysis_queue.fetch_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        job_record = db.query(AnalysisJob).filter(AnalysisJob.job_id == job_id).first()
        
        if job.is_finished:
            result = job.result
            if job_record:
                job_record.status = "completed"
                db.commit()
            
            return {
                "status": "completed",
                "result": result,
                "job_id": job_id
            }
        elif job.is_failed:
            if job_record:
                job_record.status = "failed"
                db.commit()
            return {
                "status": "failed",
                "error": str(job.exc_info) if job.exc_info else "Unknown error",
                "job_id": job_id
            }
        else:
            return {
                "status": "processing",
                "job_id": job_id,
                "message": "Analysis in progress..."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking job status: {str(e)}")

@app.get("/history/{user_id}")
async def get_user_history(user_id: int, db: Session = Depends(get_db)):
    """Get user's analysis history"""
    
    try:
        results = db.query(AnalysisResult).filter(
            AnalysisResult.user_id == user_id
        ).order_by(AnalysisResult.created_at.desc()).limit(10).all()
        
        return {
            "user_id": user_id,
            "total_analyses": len(results),
            "recent_analyses": [
                {
                    "id": r.id,
                    "filename": r.filename,
                    "created_at": r.created_at.isoformat(),
                    "status": r.status
                } for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

@app.get("/queue/stats")
async def queue_stats():
    """Get queue statistics"""
    if not analysis_queue:
        return {"redis_connected": False, "error": "Redis not available"}
    
    try:
        return {
            "queued_jobs": len(analysis_queue),
            "failed_jobs": len(analysis_queue.failed_job_registry),
            "workers_count": len(analysis_queue.workers),
            "redis_connected": True
        }
    except Exception as e:
        return {"redis_connected": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

