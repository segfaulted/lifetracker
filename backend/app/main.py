from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, SQLModel
from typing import List, Optional
import asyncio

from app import models, schemas, crud
from app.database import engine, get_db

# Create database tables automatically on startup
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(title="Task Tracker API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for live-sync broadcasts
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()
main_loop = None

@app.on_event("startup")
def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()

def trigger_broadcast(message: str = "refresh"):
    global main_loop
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(
            lambda: main_loop.create_task(manager.broadcast(message))
        )

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Root status
@app.get("/api")
def root():
    return {"message": "Task Tracker API is running"}

# Projects API
@app.get("/api/projects", response_model=List[schemas.Project])
def get_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)

@app.post("/api/projects", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    res = crud.create_project(db, project)
    trigger_broadcast("refresh")
    return res

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    success = crud.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    trigger_broadcast("refresh")
    return {"detail": "Project deleted successfully"}

# Tasks API
@app.get("/api/projects/{project_id}/tasks", response_model=List[schemas.Task])
def get_tasks(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_tasks(db, project_id)

@app.post("/api/projects/{project_id}/tasks", response_model=schemas.Task)
def create_task(project_id: int, task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    res = crud.create_task(db, project_id, task)
    trigger_broadcast("refresh")
    return res

@app.put("/api/tasks/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, task_update: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.update_task(db, task_id, task_update)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    trigger_broadcast("refresh")
    return db_task

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    success = crud.delete_task(db, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    trigger_broadcast("refresh")
    return {"detail": "Task deleted successfully"}

# TimeLogs API
@app.get("/api/projects/{project_id}/timelogs", response_model=List[schemas.TimeLog])
def get_time_logs(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return crud.get_time_logs(db, project_id)

@app.post("/api/projects/{project_id}/timelogs", response_model=schemas.TimeLog)
def create_time_log(project_id: int, time_log: schemas.TimeLogCreate, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    res = crud.create_time_log(db, project_id, time_log)
    trigger_broadcast("refresh")
    return res

@app.delete("/api/timelogs/{time_log_id}")
def delete_time_log(time_log_id: int, db: Session = Depends(get_db)):
    success = crud.delete_time_log(db, time_log_id)
    if not success:
        raise HTTPException(status_code=404, detail="Time log not found")
    trigger_broadcast("refresh")
    return {"detail": "Time log deleted successfully"}

# Dashboard Summary API
@app.get("/api/dashboard/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    return crud.get_dashboard_summary(db)

# Active Timer APIs
from pydantic import BaseModel

class StopTimerRequest(BaseModel):
    description: Optional[str] = None

@app.get("/api/timer", response_model=Optional[schemas.ActiveTimer])
def get_active_timer(db: Session = Depends(get_db)):
    return crud.get_active_timer(db)

@app.post("/api/timer/start", response_model=schemas.ActiveTimer)
def start_active_timer(timer_in: schemas.ActiveTimerCreate, db: Session = Depends(get_db)):
    project = crud.get_project(db, timer_in.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    res = crud.start_active_timer(db, project_id=timer_in.project_id, description=timer_in.description)
    trigger_broadcast("refresh")
    return res

@app.post("/api/timer/pause", response_model=schemas.ActiveTimer)
def pause_active_timer(db: Session = Depends(get_db)):
    res = crud.pause_active_timer(db)
    if not res:
        raise HTTPException(status_code=404, detail="No active timer running")
    trigger_broadcast("refresh")
    return res

@app.post("/api/timer/stop", response_model=schemas.TimeLog)
def stop_active_timer(req: StopTimerRequest, db: Session = Depends(get_db)):
    log_entry = crud.stop_active_timer(db, final_description=req.description)
    if not log_entry:
        raise HTTPException(status_code=404, detail="No active timer running")
    trigger_broadcast("refresh")
    return log_entry

@app.delete("/api/timer")
def discard_active_timer(db: Session = Depends(get_db)):
    success = crud.discard_active_timer(db)
    if not success:
        raise HTTPException(status_code=404, detail="No active timer running")
    trigger_broadcast("refresh")
    return {"detail": "Active timer discarded successfully"}


# MedTracker API Endpoints

@app.get("/api/status")
def get_meds_status(date: str = Query(..., description="Date in YYYY-MM-DD format"), db: Session = Depends(get_db)):
    return crud.get_meds_status(db, date)

@app.post("/api/checklist/toggle", response_model=models.DailyChecklist)
def toggle_checklist_item(payload: schemas.ChecklistToggleRequest, db: Session = Depends(get_db)):
    res = crud.toggle_checklist_item(db, payload.date, payload.item)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid checklist item: '{payload.item}'. Must be morning_meds, evening_meds, or morning_inject."
        )
    trigger_broadcast("refresh")
    return res

@app.post("/api/meal-injections", response_model=models.MealInjectionLog)
def add_meal_injection(payload: schemas.MealInjectionRequest, db: Session = Depends(get_db)):
    res = crud.add_meal_injection(db, payload.date, payload.note)
    trigger_broadcast("refresh")
    return res

@app.delete("/api/meal-injections/{id}")
def delete_meal_injection(id: int, db: Session = Depends(get_db)):
    success = crud.delete_meal_injection(db, id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Meal injection log with ID {id} not found."
        )
    trigger_broadcast("refresh")
    return {"success": True}

@app.get("/api/history")
def get_history(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    return crud.get_compliance_history(db, start_date, end_date)

# Serve static frontend files in production
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

frontend_dist_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../frontend/dist")
)

if os.path.exists(frontend_dist_path):
    # Mount assets folder
    assets_path = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")

    # Serve other top-level static files individually
    @app.get("/favicon.svg", include_in_schema=False)
    def favicon():
        return FileResponse(os.path.join(frontend_dist_path, "favicon.svg"))

    @app.get("/icons.svg", include_in_schema=False)
    def icons():
        return FileResponse(os.path.join(frontend_dist_path, "icons.svg"))

    # SPA Fallback for everything else
    @app.get("/{fallback_path:path}", include_in_schema=False)
    async def spa_fallback(fallback_path: str):
        if fallback_path.startswith("api/") or fallback_path.startswith("docs") or fallback_path.startswith("redoc") or fallback_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not Found")
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))

