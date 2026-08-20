from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    
class User(BaseModel):
    id: int
    username: str
    email: EmailStr    
    
class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None    
    
class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    owner_id: int    
    
class Project(BaseModel):
    id: int
    name:str
    description: str | None = None
    owner_id: int    