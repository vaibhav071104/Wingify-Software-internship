from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blood_analyzer.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String(255))
    file_hash = Column(String(255), index=True)
    query = Column(Text)
    analysis = Column(Text)
    processing_time = Column(Integer)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="completed")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(255), unique=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String(255))
    status = Column(String(50), default="queued")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def store_analysis_result(user_id: int, filename: str, analysis: str, file_hash: str = None):
    db = SessionLocal()
    try:
        result = AnalysisResult(
            user_id=user_id,
            filename=filename,
            file_hash=file_hash,
            analysis=analysis
        )
        db.add(result)
        db.commit()
        return result.id
    finally:
        db.close()
