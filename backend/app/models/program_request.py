from pydantic import BaseModel

class ProgramRequest(BaseModel):
    user_id: str