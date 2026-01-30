from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import json

# Import automation service and models
from automation_service import automation_service
from api_models import ConfigUpdate, ConfigResponse, TaskRequest, RunInfo
from automation.task_definitions import TASK_ORDER


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# ============================================================================
# AUTOMATION ENDPOINTS
# ============================================================================

@api_router.get("/automation/config")
async def get_automation_config():
    """Get current automation configuration"""
    try:
        config = automation_service.get_config()
        return config
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/automation/config")
async def update_automation_config(config: ConfigUpdate):
    """Update automation configuration"""
    try:
        result = automation_service.update_config(config.model_dump(exclude_unset=True))
        return result
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/models")
async def get_available_models():
    """Get available OpenRouter models"""
    try:
        models = automation_service.get_available_models()
        return {"models": models}
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/tasks")
async def get_available_tasks():
    """Get available task IDs"""
    return {"tasks": TASK_ORDER}

@api_router.post("/automation/start")
async def start_automation(request: TaskRequest):
    """Start automation tasks"""
    try:
        run_id = automation_service.start_automation(
            models=request.models,
            tasks=request.tasks,
            max_iterations=request.max_iterations
        )
        return {"run_id": run_id, "message": "Automation started successfully"}
    except Exception as e:
        logger.error(f"Error starting automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/runs")
async def get_all_runs():
    """Get all automation runs"""
    try:
        runs = automation_service.get_all_runs()
        return {"runs": runs}
    except Exception as e:
        logger.error(f"Error getting runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/runs/{run_id}")
async def get_run_status(run_id: str):
    """Get status of a specific run"""
    try:
        run_info = automation_service.get_run_status(run_id)
        if not run_info:
            raise HTTPException(status_code=404, detail="Run not found")
        return run_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting run status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/automation/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    """Cancel a running automation"""
    try:
        success = automation_service.cancel_run(run_id)
        if not success:
            raise HTTPException(status_code=404, detail="Run not found or not running")
        return {"message": "Run cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/logs")
async def get_automation_logs(lines: int = 100):
    """Get recent automation logs"""
    try:
        log_lines = automation_service.get_logs(lines=lines)
        return {"logs": log_lines}
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/datasets")
async def get_datasets():
    """Get list of generated datasets"""
    try:
        datasets = automation_service.get_datasets()
        return {"datasets": datasets}
    except Exception as e:
        logger.error(f"Error getting datasets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/datasets/{model}/{filename}")
async def download_dataset(model: str, filename: str):
    """Download a specific dataset file"""
    try:
        file_path = Path(f'/app/golden_dataset/dataset/{model}/{filename}')
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Dataset not found")
        return FileResponse(file_path, media_type='application/json', filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading dataset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/automation/screenshots")
async def get_screenshots():
    """Get list of screenshots"""
    try:
        screenshots = automation_service.get_screenshots()
        return {"screenshots": screenshots}
    except Exception as e:
        logger.error(f"Error getting screenshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/screenshots/{filename}")
async def get_screenshot(filename: str):
    """Get a specific screenshot"""
    try:
        file_path = Path(f'/app/golden_dataset/screenshots/{filename}')
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Screenshot not found")
        return FileResponse(file_path, media_type='image/png')
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting screenshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()