import os
import sys
import hashlib
from rq import Worker, Queue, Connection
from redis import Redis

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import doctor
from task import help_patients
from crewai import Crew, Process

# Redis connection
redis_conn = Redis(host='localhost', port=6379, db=0)

def analyze_blood_test_task(file_path: str, query: str, user_id: int = None):
    """Background task for blood test analysis"""
    try:
        # Import here to avoid circular imports
        from database import store_analysis_result
        
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
        
        # Store result in database if user_id provided
        if user_id is not None:
            # Generate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            store_analysis_result(
                user_id=user_id,
                filename=os.path.basename(file_path),
                analysis=str(result),
                file_hash=file_hash
            )
        
        return str(result)
        
    except Exception as e:
        print(f"Error in background analysis: {str(e)}")
        raise Exception(f"Error in background analysis: {str(e)}")

if __name__ == '__main__':
    with Connection(redis_conn):
        worker = Worker(['blood_analysis'], connection=redis_conn)
        print("Worker started. Listening for jobs...")
        worker.work()
