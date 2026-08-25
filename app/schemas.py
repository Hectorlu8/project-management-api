from enum import Enum

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
    
class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None    
    
class TaskStatus(str, Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    
class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High" 
            
class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: int    
 
class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: TaskStatus
    priority: TaskPriority
    project_id: int    
    
    
class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None    