from pydantic import BaseModel, Field
from typing import Optional

class UserInput(BaseModel):
    username: str = Field(..., description="Full name or username of the individual")
    user_id: int = Field(..., description="Unique user identification number")
    age: int = Field(..., ge=10, le=120, description="Age in years")
    weight: float = Field(..., gt=20, lt=400, description="Body weight in kilograms")
    goal: str = Field(..., description="Fitness goal, e.g., weight loss, muscle gain, flexibility")
    intensity: str = Field(..., description="Workout intensity: low, medium, or high")

class FeedbackRequest(BaseModel):
    feedback: str = Field(..., description="User feedback to refine or modify the workout plan")
    user_id: Optional[int] = Field(None, description="Optional user ID for API payloads")

class WorkoutRequest(BaseModel):
    goal: str = Field(..., description="Fitness goal")
    intensity: str = Field(..., description="Workout intensity level")
