# Blood Test Analyzer - AI Internship Assignment Debug Challenge

## Overview
This project is a comprehensive blood test analysis system using CrewAI and Ollama local LLM. It processes PDF blood test reports and provides detailed medical, nutritional, and exercise recommendations through a FastAPI backend with Redis Queue Workers and SQLite database integration.

## 🚀 Features
- 🏥 **Medical Analysis**: Comprehensive blood test interpretation by AI medical doctor
- 🥗 **Nutritional Recommendations**: Evidence-based dietary suggestions
- 💪 **Exercise Planning**: Safe, personalized fitness recommendations
- 🚀 **Queue Workers**: Background processing for concurrent requests (Redis Queue)
- 💾 **Database Integration**: Store analysis results and user data (SQLite/PostgreSQL)
- 🔒 **Privacy-First**: Local AI processing with Ollama (no external API calls)
- ⚡ **Intelligent Fallback**: Works with or without Redis/Database
- 📊 **Real-time Status**: Job tracking and user history

## 🐛 Bugs Found and How I Fixed Them

### 1. **Dependency Conflicts (CRITICAL)**
**Problem**: CrewAI had incompatible dependencies with embedchain and langchain
ERROR: Cannot install crewai==0.130.0 and openai==1.12.0 because these package versions have conflicting dependencies

text
**Root Cause**: embedchain requires langchain>=0.3.1 while CrewAI requires langchain<0.2.0
**Fix**: Used compatible versions and removed problematic dependencies
crewai==0.35.8
httpx==0.27.2 # Fixed proxies argument error
sqlalchemy==1.4.53 # Compatible with CrewAI

text

### 2. **Tool Usage Errors**
**Problem**: `BloodTestReportTool.read_data_tool() missing 1 required positional argument: 'self'`
**Root Cause**: Class-based tool methods not properly instantiated
**Fix**: Converted to standalone function with proper decorator
@tool("Read Blood Test Report")
def read_blood_test_report(path: str) -> str:
# Implementation with PyPDF2

text

### 3. **Agent Delegation Errors**
**Problem**: `BaseAgentTools.delegate_work() missing 1 required positional argument: 'context'`
**Root Cause**: CrewAI delegation system expecting context parameter
**Fix**: Disabled delegation in all agents
doctor = Agent(
allow_delegation=False # Prevents delegation errors
)

text

### 4. **File Path Issues**
**Problem**: Agents using hardcoded paths instead of UUID-based uploaded file paths
**Root Cause**: Improper file path passing through crew execution
**Fix**: Proper file path handling with UUID generation
file_path = f"data/blood_test_report_{uuid.uuid4()}.pdf"
result = medical_crew.kickoff({'query': query, 'file_path': file_path})

text

### 5. **Agent Iteration Limits**
**Problem**: `Agent stopped due to iteration limit or time limit`
**Root Cause**: Default iteration limits too low for complex medical analysis
**Fix**: Increased limits for comprehensive analysis
doctor = Agent(
max_iter=10, # Increased from 3
max_execution_time=600, # 10 minutes
)

text

### 6. **Action Format Errors**
**Problem**: Agents using incorrect tool action format
**Root Cause**: Inconsistent tool calling syntax
**Fix**: Added explicit instructions in task descriptions
description="""Use this exact format:
Action: Read Blood Test Report
Action Input: {file_path}"""

text

### 7. **Type Annotation Errors**
**Problem**: Pylance errors for None values and type mismatches
**Root Cause**: Missing null checks and type conversions
**Fix**: Added proper type checking and conversions
if not file.filename or not file.filename.lower().endswith('.pdf'):
raise HTTPException(status_code=400, detail="Only PDF files are supported")

text

### 8. **HTTP Proxy Argument Deprecation**
**Problem**: `Client.__init__() got an unexpected keyword argument 'proxies'`
**Root Cause**: httpx 0.28.0+ removed deprecated proxies argument
**Fix**: Downgraded to compatible httpx version
httpx==0.27.2 # Maintains proxies argument compatibility

text

## 🛠️ Setup and Usage Instructions

### Prerequisites
- Python 3.11 or later
- Redis server (optional - graceful fallback available)
- Ollama installed and running

### Installation Steps

1. **Clone the repository**
git clone https://github.com/vaibhav071104/Wingify-Software-internship.git
cd Wingify-Software-internship

text

2. **Create and activate virtual environment**
python -m venv venv
source venv/Scripts/activate # Windows

source venv/bin/activate # Linux/Mac
text

3. **Install dependencies**
pip install -r requirements.txt

text

4. **Install and setup Ollama**
Download from https://ollama.ai/
ollama serve
ollama pull llama2

text

5. **Start Redis server (optional)**
redis-server

text

6. **Start RQ Worker (optional - in separate terminal)**
python worker.py

text

7. **Run FastAPI server**
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

text

### Usage

1. **Access API documentation**: http://localhost:8000/docs
2. **Upload blood test PDF** via `/analyze` endpoint
3. **Check job status** using returned job_id at `/status/{job_id}` (if using queue)
4. **View analysis history** at `/history/{user_id}` (if using database)

## 📚 API Documentation

### Core Endpoints

#### `GET /`
- **Description**: Health check endpoint
- **Response**: JSON message confirming API is running

#### `POST /analyze`
- **Description**: Upload PDF blood test report for analysis
- **Request**: Multipart form data
  - `file`: PDF file of blood test report
  - `query`: Analysis query (optional)
  - `user_id`: User identifier (default: 1)
- **Response**: Analysis result or job ID for background processing

#### `GET /status/{job_id}`
- **Description**: Check analysis job status (queue mode)
- **Response**: Job status (queued/processing/completed/failed) and results

#### `GET /history/{user_id}`
- **Description**: Get user's analysis history (database mode)
- **Response**: List of past analyses

#### `GET /queue/stats`
- **Description**: Get queue statistics
- **Response**: Queue health metrics

### Example Usage

Upload blood test for analysis
curl -X POST "http://localhost:8000/analyze"
-F "file=@blood_test.pdf"
-F "query=Provide comprehensive analysis"
-F "user_id=1"

Check job status (if using queue)
curl "http://localhost:8000/status/job-id-here"

Get user history (if using database)
curl "http://localhost:8000/history/1"

text

## 🎯 Bonus Features Implementation

### ✅ Queue Worker Model
- **Technology**: Redis Queue (RQ) for background processing
- **Benefits**: Handle concurrent requests, prevent timeouts
- **Implementation**: Separate worker process for analysis tasks
- **Fallback**: Graceful degradation to synchronous processing if Redis unavailable

Start worker
python worker.py

Queue analysis
job = analysis_queue.enqueue(analyze_blood_test_task, ...)

text

### ✅ Database Integration
- **Technology**: SQLite (default) / PostgreSQL with SQLAlchemy ORM
- **Features**: User management, analysis results storage, job tracking
- **Tables**: users, analysis_results, analysis_jobs
- **Fallback**: Works without database for basic functionality

class AnalysisResult(Base):
tablename = "analysis_results"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, index=True)
analysis = Column(Text)
created_at = Column(DateTime)

text

## 📁 Project Structure

blood-test-analyser/
├── agents.py # Ollama LLM agents (medical, nutrition, exercise)
├── tools.py # PDF reading and processing tools
├── task.py # Task definitions for agent workflows
├── main.py # FastAPI application with queue integration
├── worker.py # RQ background worker for analysis
├── database.py # SQLAlchemy models and database setup
├── requirements.txt # Python dependencies
├── data/ # Temporary PDF storage
├── README.md # This file
└── .gitignore # Git ignore rules

text

## 🔧 Technology Stack

- **Backend**: FastAPI
- **AI/ML**: CrewAI + Ollama (Llama2)
- **Queue**: Redis Queue (RQ)
- **Database**: SQLite/PostgreSQL + SQLAlchemy
- **PDF Processing**: PyPDF2
- **Deployment**: Uvicorn

## 📊 Performance Metrics

- **Analysis Time**: 3-5 minutes for comprehensive report
- **Concurrent Requests**: Unlimited (queue-based) or limited (synchronous fallback)
- **Database Caching**: Instant results for duplicate analyses
- **Privacy**: 100% local processing (no external API calls)
- **Reliability**: Graceful fallback mechanisms for all external dependencies

## 📋 Sample Output

The system generates comprehensive reports including:

### 1. **Medical Analysis**
- Complete Blood Count (CBC) interpretation
- Liver and kidney function assessment
- Lipid profile analysis
- Diabetes screening (HbA1c)
- Thyroid function evaluation
- Vitamin and mineral levels

### 2. **Nutritional Recommendations**
- Protein intake for immune function
- Omega-3 fatty acids for inflammation
- Vitamin and mineral supplementation
- Dietary modifications based on biomarkers

### 3. **Exercise Planning**
- Aerobic exercise recommendations
- Strength training guidelines
- Safety considerations based on health status
- Progressive training suggestions

## 🔒 Security & Privacy

- **Local AI Processing**: No data sent to external APIs
- **Temporary File Storage**: PDFs deleted after processing
- **Database Security**: User data stored locally
- **Medical Disclaimers**: Appropriate warnings included in all reports

## 🚨 Known Issues & Limitations

- **CrewAI Ecosystem**: Some advanced features limited by embedchain dependency conflicts
- **Processing Time**: Local LLM processing takes 3-5 minutes per analysis
- **Memory Requirements**: Ollama requires sufficient RAM for model loading
- **Windows Line Endings**: Git may show CRLF warnings (cosmetic only)

## 🧪 Testing

The system has been tested with:
- ✅ Real blood test PDF reports (10+ pages)
- ✅ Various file formats and sizes
- ✅ Concurrent request handling
- ✅ Error scenarios and edge cases
- ✅ Database operations and queue processing

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Contact

**Vaibhav Singh**
- Email: vaibhavsingh0711200@gmail.com
- GitHub: [@vaibhav071104](https://github.com/vaibhav071104)
- Repository: [Wingify-Software-internship](https://github.com/vaibhav071104/Wingify-Software-internship)

## 🙏 Acknowledgments

- **VWO GenAI Team** for the challenging and educational assignment
- **CrewAI Community** for the multi-agent framework
- **Ollama Team** for local LLM capabilities
- **FastAPI** for the excellent web framework

---

**⚠️ Medical Disclaimer**: This system is for informational purposes only and should not replace professional medical advice. Always consult healthcare professionals for medical decisions and treatment plans.

**🎯 Assignment Status**: All core requirements met, both bonus features implemented with graceful fallbacks, comprehensive debugging documentation provided.
