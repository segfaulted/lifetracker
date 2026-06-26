from datetime import datetime, date, timezone
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

# Task schemas
class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    is_completed: bool = False
    priority: str = "Medium"  # High, Medium, Low
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[str] = None
    due_date: Optional[date] = None

class Task(TaskBase):
    id: int
    project_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# TimeLog schemas
class TimeLogBase(BaseModel):
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class TimeLogCreate(TimeLogBase):
    pass

class TimeLog(TimeLogBase):
    id: int
    project_id: int
    duration_seconds: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Project schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    tasks: List[Task] = []
    time_logs: List[TimeLog] = []

    model_config = ConfigDict(from_attributes=True)

# Dashboard / Report schemas
class ProjectSummary(BaseModel):
    project_id: int
    project_name: str
    total_work_seconds: int
    total_billed_seconds: int
    total_unbilled_seconds: int
    total_tasks: int
    completed_tasks: int

class DashboardSummary(BaseModel):
    total_projects: int
    total_work_seconds: int
    total_billed_seconds: int
    total_unbilled_seconds: int
    total_tasks: int
    completed_tasks: int
    project_summaries: List[ProjectSummary]

# ActiveTimer schemas
class ActiveTimerBase(BaseModel):
    project_id: int
    description: Optional[str] = None

class ActiveTimerCreate(ActiveTimerBase):
    pass

class ActiveTimer(ActiveTimerBase):
    id: int
    start_time: datetime
    is_paused: bool = False
    accumulated_seconds: int = 0
    server_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    model_config = ConfigDict(from_attributes=True)


# MedTracker schemas
class ChecklistToggleRequest(BaseModel):
    date: str  # Format: YYYY-MM-DD
    item: str  # Must be "morning_meds", "evening_meds", or "morning_inject"

class MealInjectionRequest(BaseModel):
    date: str  # Format: YYYY-MM-DD
    note: Optional[str] = None  # e.g., "Breakfast", "Lunch", "Dinner", "Snack", etc.


