from pydantic import BaseModel, EmailStr
from datetime import datetime




class UserRegister(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:str
    created_at:datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"


class AgentRequest(BaseModel):
    question:str
    session_id:str | None = None

class ToolStep(BaseModel):
    tool:str
    input:str
    output:str

class AgentResponse(BaseModel):
    answer:str
    steps:list[ToolStep]
    session_id:str

class HistoryItem(BaseModel):
    session_id:str
    question:str
    answer:str
    steps:list[dict]
    created_at:datetime

    class Config:
        from_attributes = True

class HistoryResponse(BaseModel):
    sessions: list[HistoryItem]
