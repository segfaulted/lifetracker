from datetime import datetime, date, timezone
from typing import List, Optional
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Date, Boolean
from sqlmodel import Field, SQLModel, Relationship

def get_utc_now():
    # Returns a naive datetime representing UTC time
    return datetime.now(timezone.utc).replace(tzinfo=None)

class Project(SQLModel, table=True):
    __tablename__ = "projects"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=get_utc_now)

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    time_logs: List["TimeLog"] = Relationship(
        back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    project_id: int = Field(
        sa_column=Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    title: str = Field(max_length=200)
    is_completed: bool = Field(default=False)
    priority: str = Field(default="Medium", max_length=20)  # High, Medium, Low
    due_date: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=get_utc_now)

    project: "Project" = Relationship(back_populates="tasks")


class TimeLog(SQLModel, table=True):
    __tablename__ = "time_logs"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    project_id: int = Field(
        sa_column=Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    description: Optional[str] = Field(default=None, max_length=500)
    start_time: datetime
    end_time: datetime
    duration_seconds: int
    created_at: datetime = Field(default_factory=get_utc_now)

    project: "Project" = Relationship(back_populates="time_logs")


class ActiveTimer(SQLModel, table=True):
    __tablename__ = "active_timer"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    project_id: int = Field(
        sa_column=Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    )
    description: Optional[str] = Field(default=None, max_length=500)
    start_time: datetime = Field(default_factory=get_utc_now)
    is_paused: bool = Field(default=False)
    accumulated_seconds: int = Field(default=0)


# MedTracker Models (Start Fresh)

class DailyChecklist(SQLModel, table=True):
    __tablename__ = "dailychecklist"

    date: str = Field(primary_key=True)  # Format: YYYY-MM-DD
    morning_meds: bool = Field(default=False)
    morning_meds_taken_at: Optional[str] = Field(default=None)  # ISO timestamp
    evening_meds: bool = Field(default=False)
    evening_meds_taken_at: Optional[str] = Field(default=None)  # ISO timestamp
    morning_inject: bool = Field(default=False)
    morning_inject_taken_at: Optional[str] = Field(default=None)  # ISO timestamp


class MealInjectionLog(SQLModel, table=True):
    __tablename__ = "mealinjectionlog"

    id: Optional[int] = Field(default=None, primary_key=True)
    date: str = Field(index=True)  # Format: YYYY-MM-DD
    timestamp: str = Field(...)   # ISO timestamp
    note: Optional[str] = Field(default=None)  # e.g., "Breakfast", "Lunch", "Dinner", "Snack", etc.
