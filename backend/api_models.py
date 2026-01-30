"""Pydantic models for API requests/responses"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class ConfigUpdate(BaseModel):
    """Update configuration"""
    openrouter_api_key: Optional[str] = None
    xo_url: Optional[str] = None
    xo_username: Optional[str] = None
    xo_password: Optional[str] = None

class ConfigResponse(BaseModel):
    """Configuration response"""
    has_api_key: bool
    xo_url: str
    xo_username: str
    api_key_preview: Optional[str] = None

class ModelInfo(BaseModel):
    """OpenRouter model information"""
    id: str
    name: str
    description: Optional[str] = None
    context_length: Optional[int] = None
    pricing: Optional[Dict[str, Any]] = None

class TaskRequest(BaseModel):
    """Request to start automation tasks"""
    models: List[str] = Field(default_factory=lambda: ["deepseek/deepseek-r1"])
    tasks: Optional[List[str]] = None  # None means all tasks
    max_iterations: int = Field(default=20, ge=1, le=50)

class TaskStatus(BaseModel):
    """Status of an automation task"""
    run_id: str
    status: str  # pending, running, completed, failed, cancelled
    model: str
    task_id: str
    progress: int = 0  # 0-100
    current_iteration: int = 0
    max_iterations: int = 20
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error: Optional[str] = None
    success: bool = False

class RunInfo(BaseModel):
    """Information about an automation run"""
    run_id: str
    status: str  # pending, running, completed, failed, cancelled
    models: List[str]
    tasks: List[str]
    max_iterations: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tasks: int
    completed_tasks: int = 0
    failed_tasks: int = 0
    task_statuses: List[TaskStatus] = Field(default_factory=list)

class LogEntry(BaseModel):
    """Log entry"""
    timestamp: datetime
    level: str
    message: str
    task_id: Optional[str] = None
    model: Optional[str] = None

class DatasetInfo(BaseModel):
    """Information about a generated dataset"""
    filename: str
    model: str
    task_id: str
    timestamp: datetime
    size_bytes: int
    path: str

class ScreenshotInfo(BaseModel):
    """Information about a screenshot"""
    filename: str
    model: str
    task_id: str
    screenshot_type: str  # xo_list, vm_details, resources
    path: str
    url: str
