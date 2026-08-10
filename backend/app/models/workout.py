from pydantic import BaseModel

class WorkoutLog(BaseModel):
    user_id: str | None = None
    exercise_id: str
    exercise_name: str
    sets: int
    reps: int
    weight: float
    rpe: float
    notes: str = ""
