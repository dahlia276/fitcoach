from pydantic import BaseModel


class Exercise(BaseModel):
    exercise_id: str
    exercise_name: str
    sets: int
    reps: int
    rest_seconds: int
    notes: str


class WorkoutDay(BaseModel):
    day: str
    exercises: list[Exercise]


class WorkoutPlan(BaseModel):
    weeks: list[WorkoutDay]