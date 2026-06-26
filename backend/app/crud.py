from typing import Optional, List
from datetime import datetime, timedelta, timezone
from sqlalchemy import func, Integer
from sqlmodel import Session, select
from app import models, schemas

# Project CRUD
def get_projects(db: Session):
    stmt = select(models.Project).order_by(models.Project.created_at.desc())
    return db.exec(stmt).all()

def get_project(db: Session, project_id: int):
    return db.get(models.Project, project_id)

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(name=project.name, description=project.description)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

def delete_project(db: Session, project_id: int):
    db_project = db.get(models.Project, project_id)
    if db_project:
        db.delete(db_project)
        db.commit()
        return True
    return False

# Task CRUD
def get_tasks(db: Session, project_id: int):
    stmt = select(models.Task).where(models.Task.project_id == project_id).order_by(models.Task.created_at.asc())
    return db.exec(stmt).all()

def create_task(db: Session, project_id: int, task: schemas.TaskCreate):
    db_task = models.Task(
        project_id=project_id,
        title=task.title,
        is_completed=task.is_completed,
        priority=task.priority,
        due_date=task.due_date
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate):
    db_task = db.get(models.Task, task_id)
    if not db_task:
        return None
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.get(models.Task, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
        return True
    return False

# TimeLog CRUD
def get_time_logs(db: Session, project_id: int):
    stmt = select(models.TimeLog).where(models.TimeLog.project_id == project_id).order_by(models.TimeLog.start_time.desc())
    return db.exec(stmt).all()

def create_time_log(db: Session, project_id: int, time_log: schemas.TimeLogCreate):
    duration = int((time_log.end_time - time_log.start_time).total_seconds())
    db_time_log = models.TimeLog(
        project_id=project_id,
        description=time_log.description,
        start_time=time_log.start_time,
        end_time=time_log.end_time,
        duration_seconds=duration
    )
    db.add(db_time_log)
    db.commit()
    db.refresh(db_time_log)
    return db_time_log

def delete_time_log(db: Session, time_log_id: int):
    db_time_log = db.get(models.TimeLog, time_log_id)
    if db_time_log:
        db.delete(db_time_log)
        db.commit()
        return True
    return False

# Dashboard Summary
def get_dashboard_summary(db: Session) -> schemas.DashboardSummary:
    # 1. Total projects
    projects_stmt = select(models.Project)
    projects = db.exec(projects_stmt).all()
    total_projects = len(projects)
    
    # 2. Total time logged across all logs
    work_sum_stmt = select(func.sum(models.TimeLog.duration_seconds)).where(models.TimeLog.duration_seconds > 0)
    total_work_seconds = db.exec(work_sum_stmt).first() or 0
    
    billed_sum_stmt = select(func.sum(models.TimeLog.duration_seconds)).where(models.TimeLog.duration_seconds < 0)
    total_billed_seconds = abs(db.exec(billed_sum_stmt).first() or 0)
    
    total_unbilled_seconds = total_work_seconds - total_billed_seconds
    
    # 3. Total tasks and completed tasks
    tasks_count_stmt = select(
        func.count(models.Task.id),
        func.sum(func.cast(models.Task.is_completed, Integer))
    )
    res = db.execute(tasks_count_stmt).one_or_none()
    total_tasks = res[0] if res and res[0] is not None else 0
    completed_tasks = res[1] if res and res[1] is not None else 0
    
    # 4. Project summaries
    project_summaries = []
    for proj in projects:
        # Work time (positive logs)
        proj_work_stmt = select(func.sum(models.TimeLog.duration_seconds)).where(
            (models.TimeLog.project_id == proj.id) & (models.TimeLog.duration_seconds > 0)
        )
        proj_work = db.exec(proj_work_stmt).first() or 0
        
        # Billed time (negative logs)
        proj_billed_stmt = select(func.sum(models.TimeLog.duration_seconds)).where(
            (models.TimeLog.project_id == proj.id) & (models.TimeLog.duration_seconds < 0)
        )
        proj_billed = abs(db.exec(proj_billed_stmt).first() or 0)
        
        # Unbilled time
        proj_unbilled = proj_work - proj_billed
        
        # Tasks for this project
        proj_tasks_stmt = select(
            func.count(models.Task.id),
            func.sum(func.cast(models.Task.is_completed, Integer))
        ).where(models.Task.project_id == proj.id)
        proj_res = db.execute(proj_tasks_stmt).one_or_none()
        proj_total = proj_res[0] if proj_res and proj_res[0] is not None else 0
        proj_completed = proj_res[1] if proj_res and proj_res[1] is not None else 0
        
        project_summaries.append(
            schemas.ProjectSummary(
                project_id=proj.id,
                project_name=proj.name,
                total_work_seconds=proj_work,
                total_billed_seconds=proj_billed,
                total_unbilled_seconds=proj_unbilled,
                total_tasks=proj_total,
                completed_tasks=proj_completed
            )
        )
        
    return schemas.DashboardSummary(
        total_projects=total_projects,
        total_work_seconds=total_work_seconds,
        total_billed_seconds=total_billed_seconds,
        total_unbilled_seconds=total_unbilled_seconds,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        project_summaries=project_summaries
    )

# ActiveTimer CRUD
def get_active_timer(db: Session):
    stmt = select(models.ActiveTimer)
    return db.exec(stmt).first()

def start_active_timer(db: Session, project_id: int, description: Optional[str] = None):
    active = get_active_timer(db)
    if active:
        if active.project_id != project_id:
            # Different project, save the current one first
            stop_active_timer(db, active.description or "Automated save of previous timer")
            db_timer = models.ActiveTimer(
                project_id=project_id,
                description=description,
                start_time=models.get_utc_now(),
                is_paused=False,
                accumulated_seconds=0
            )
            db.add(db_timer)
        else:
            # Same project, resume it if paused
            if active.is_paused:
                active.is_paused = False
                active.start_time = models.get_utc_now()
                if description is not None:
                    active.description = description
            else:
                if description is not None:
                    active.description = description
            db_timer = active
    else:
        db_timer = models.ActiveTimer(
            project_id=project_id,
            description=description,
            start_time=models.get_utc_now(),
            is_paused=False,
            accumulated_seconds=0
        )
        db.add(db_timer)
        
    db.commit()
    db.refresh(db_timer)
    return db_timer

def pause_active_timer(db: Session):
    active = get_active_timer(db)
    if not active:
        return None
    if not active.is_paused:
        now = models.get_utc_now()
        duration = int((now - active.start_time).total_seconds())
        if duration < 0:
            duration = 0
        active.accumulated_seconds += duration
        active.is_paused = True
        active.start_time = now
        db.commit()
        db.refresh(active)
    return active

def stop_active_timer(db: Session, final_description: Optional[str] = None):
    active = get_active_timer(db)
    if not active:
        return None
        
    end_time = models.get_utc_now()
    duration = active.accumulated_seconds
    if not active.is_paused:
        duration += int((end_time - active.start_time).total_seconds())
    if duration < 0:
        duration = 0
        
    desc = final_description if final_description is not None else active.description
    
    db_log = models.TimeLog(
        project_id=active.project_id,
        description=desc or "Time tracking session",
        start_time=end_time - timedelta(seconds=duration),
        end_time=end_time,
        duration_seconds=duration
    )
    db.delete(active)
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def discard_active_timer(db: Session) -> bool:
    active = get_active_timer(db)
    if active:
        db.delete(active)
        db.commit()
        return True
    return False


# MedTracker CRUD Operations

def get_meds_status(db: Session, date_str: str):
    checklist = db.get(models.DailyChecklist, date_str)
    if not checklist:
        checklist = models.DailyChecklist(date=date_str)
        db.add(checklist)
        db.commit()
        db.refresh(checklist)
    
    stmt = select(models.MealInjectionLog).where(models.MealInjectionLog.date == date_str).order_by(models.MealInjectionLog.timestamp)
    meal_injections = db.exec(stmt).all()
    
    return {
        "checklist": checklist,
        "meal_injections": meal_injections
    }

def toggle_checklist_item(db: Session, date_str: str, item: str):
    checklist = db.get(models.DailyChecklist, date_str)
    if not checklist:
        checklist = models.DailyChecklist(date=date_str)
        db.add(checklist)
    
    current_time_iso = datetime.now(timezone.utc).isoformat()
    if item == "morning_meds":
        checklist.morning_meds = not checklist.morning_meds
        checklist.morning_meds_taken_at = current_time_iso if checklist.morning_meds else None
    elif item == "evening_meds":
        checklist.evening_meds = not checklist.evening_meds
        checklist.evening_meds_taken_at = current_time_iso if checklist.evening_meds else None
    elif item == "morning_inject":
        checklist.morning_inject = not checklist.morning_inject
        checklist.morning_inject_taken_at = current_time_iso if checklist.morning_inject else None
    else:
        return None
    
    db.add(checklist)
    db.commit()
    db.refresh(checklist)
    return checklist

def add_meal_injection(db: Session, date_str: str, note: Optional[str] = None):
    current_time_iso = datetime.now(timezone.utc).isoformat()
    log_entry = models.MealInjectionLog(
        date=date_str,
        timestamp=current_time_iso,
        note=note
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def delete_meal_injection(db: Session, injection_id: int):
    log_entry = db.get(models.MealInjectionLog, injection_id)
    if log_entry:
        db.delete(log_entry)
        db.commit()
        return True
    return False

def get_compliance_history(db: Session, start_date: str, end_date: str):
    checklist_statement = select(models.DailyChecklist).where(
        models.DailyChecklist.date >= start_date,
        models.DailyChecklist.date <= end_date
    )
    checklists = db.exec(checklist_statement).all()
    
    meals_statement = select(models.MealInjectionLog).where(
        models.MealInjectionLog.date >= start_date,
        models.MealInjectionLog.date <= end_date
    )
    meals = db.exec(meals_statement).all()
    
    checklists_by_date = {c.date: c for c in checklists}
    meals_by_date = {}
    for m in meals:
        meals_by_date.setdefault(m.date, []).append({
            "id": m.id,
            "timestamp": m.timestamp,
            "note": m.note
        })
    
    history = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = timedelta(days=1)
    
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        checklist_item = checklists_by_date.get(date_str)
        meal_items = meals_by_date.get(date_str, [])
        
        history.append({
            "date": date_str,
            "checklist": {
                "morning_meds": checklist_item.morning_meds if checklist_item else False,
                "morning_meds_taken_at": checklist_item.morning_meds_taken_at if checklist_item else None,
                "evening_meds": checklist_item.evening_meds if checklist_item else False,
                "evening_meds_taken_at": checklist_item.evening_meds_taken_at if checklist_item else None,
                "morning_inject": checklist_item.morning_inject if checklist_item else False,
                "morning_inject_taken_at": checklist_item.morning_inject_taken_at if checklist_item else None,
            },
            "meal_injections_count": len(meal_items),
            "meal_injections": meal_items
        })
        current += delta
        
    return history
