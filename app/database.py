import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Determine root path to ensure fitbuddy.db is always placed at a predictable location
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR)) if os.path.basename(os.path.dirname(CURRENT_DIR)) == "backend" else os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "fitbuddy.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(50), nullable=False)
    schedule = Column(Integer, default=7)
    created_at = Column(DateTime, default=datetime.utcnow)

    plans = relationship("WorkoutPlan", back_populates="user", cascade="all, delete-orphan")

class WorkoutPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True, default=None)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="plans")

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id=user_id).first()
        if existing:
            # Update existing user info
            existing.name = name
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            # Create a new user
            user = User(
                id=user_id,
                name=name,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity,
                schedule=7  # default schedule
            )
            db.add(user)
        db.commit()
    finally:
        db.close()

def save_plan(user_id: int, plan: str):
    db = SessionLocal()
    try:
        existing_plan = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if existing_plan:
            existing_plan.original_plan = plan
            existing_plan.updated_plan = None
        else:
            workout = WorkoutPlan(user_id=user_id, original_plan=plan)
            db.add(workout)
        db.commit()
    finally:
        db.close()

def update_plan(user_id: int, updated_text: str):
    db = SessionLocal()
    try:
        workout = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if workout:
            workout.updated_plan = updated_text
            db.commit()
    finally:
        db.close()

def get_original_plan(user_id: int):
    db = SessionLocal()
    try:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return plan.original_plan if plan else None
    finally:
        db.close()

def get_user(user_id: int):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

def get_all_users():
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()

def get_all_plans():
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).all()
    finally:
        db.close()

def delete_user(user_id: int):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False
    finally:
        db.close()
