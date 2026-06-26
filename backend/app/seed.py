from datetime import datetime, timedelta, timezone
from sqlmodel import Session, SQLModel, select
from app.database import engine
from app import models

def seed():
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as db:
        # Check if we already have projects
        if db.exec(select(models.Project)).first():
            print("Database already seeded.")
            return

        # Helper for naive UTC datetime
        def utc_dt(hours_ago):
            return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=hours_ago)

        # 1. Project A
        p1 = models.Project(
            name="LifeTracker App Development",
            description="Design and implement a single-page task and time tracking application using FastAPI and React."
        )
        db.add(p1)
        db.flush()

        t1_1 = models.Task(
            project_id=p1.id,
            title="Initialize backend skeleton & database schemas",
            is_completed=True,
            priority="High",
            due_date=utc_dt(0).date()
        )
        t1_2 = models.Task(
            project_id=p1.id,
            title="Build SPA frontend components in React",
            is_completed=False,
            priority="High",
            due_date=(utc_dt(0) + timedelta(days=2)).date()
        )
        t1_3 = models.Task(
            project_id=p1.id,
            title="Style components using Tailwind CSS v4",
            is_completed=False,
            priority="Medium",
            due_date=(utc_dt(0) + timedelta(days=3)).date()
        )
        t1_4 = models.Task(
            project_id=p1.id,
            title="Implement visual dashboard text reports",
            is_completed=False,
            priority="Low",
            due_date=(utc_dt(0) + timedelta(days=5)).date()
        )
        db.add(t1_1)
        db.add(t1_2)
        db.add(t1_3)
        db.add(t1_4)

        log1_1 = models.TimeLog(
            project_id=p1.id,
            description="Setup FastAPI, SQLite models, schemas, and routes",
            start_time=utc_dt(5),
            end_time=utc_dt(3),
            duration_seconds=7200
        )
        log1_2 = models.TimeLog(
            project_id=p1.id,
            description="Write Database seeding scripts and run initial tests",
            start_time=utc_dt(2.5),
            end_time=utc_dt(1.5),
            duration_seconds=3600
        )
        db.add(log1_1)
        db.add(log1_2)

        # 2. Project B
        p2 = models.Project(
            name="Personal Fitness Website",
            description="A static web page for fitness tracking and workout plans."
        )
        db.add(p2)
        db.flush()

        t2_1 = models.Task(
            project_id=p2.id,
            title="Create responsive layout",
            is_completed=True,
            priority="Medium",
            due_date=utc_dt(10).date()
        )
        t2_2 = models.Task(
            project_id=p2.id,
            title="Add workout routines calculator",
            is_completed=True,
            priority="High",
            due_date=utc_dt(8).date()
        )
        t2_3 = models.Task(
            project_id=p2.id,
            title="Configure continuous integration & hosting",
            is_completed=False,
            priority="Low",
            due_date=(utc_dt(0) + timedelta(days=7)).date()
        )
        db.add(t2_1)
        db.add(t2_2)
        db.add(t2_3)

        log2_1 = models.TimeLog(
            project_id=p2.id,
            description="Bootstrap project, styled landing page layout",
            start_time=utc_dt(24),
            end_time=utc_dt(20.5),
            duration_seconds=12600
        )
        log2_2 = models.TimeLog(
            project_id=p2.id,
            description="Build workouts catalog dynamically in JS",
            start_time=utc_dt(18),
            end_time=utc_dt(15.5),
            duration_seconds=9000
        )
        db.add(log2_1)
        db.add(log2_2)

        db.commit()
        print("Database successfully seeded with mock projects, tasks, and logs!")

if __name__ == "__main__":
    seed()
