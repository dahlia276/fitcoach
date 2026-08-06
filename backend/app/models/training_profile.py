from pydantic import BaseModel, Field


class TrainingProfile(BaseModel):
    goal: str
    experience: str
    equipment: str
    injuries: str
    training_days: int = Field(gt=0)
    session_minutes: int = Field(gt=0)
    recommended_split: str
    reasoning: str