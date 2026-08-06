from pydantic import BaseModel

class Exercise(BaseModel):
    exercise_id: str
    exercise_name: str
    sets: int
    reps: int
    rest_seconds: int
    notes: str

class WorkoutDay(BaseModel):
    name: str
    focus: str
    estimated_duration_minutes: int
    exercises: list[Exercise]

class WorkoutProgram(BaseModel):
    days: list[WorkoutDay]