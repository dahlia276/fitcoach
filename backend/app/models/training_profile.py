from pydantic import BaseModel


class TrainingProfile(BaseModel):
    goal: str
    experience: str
    equipment: str
    injuries: str

    training_days: int
    session_minutes: int

    recommended_split: str
    reasoning: str