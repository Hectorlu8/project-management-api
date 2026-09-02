import time

from fastapi import FastAPI, HTTPException, status, Depends, Query, Request
from fastapi.responses import JSONResponse
import jwt
from app.schemas import UserCreate, User, UserUpdate, ProjectCreate, Project, ProjectUpdate, TaskCreate, Task, TaskUpdate, TaskStatus, TaskPriority
from app.database import SessionLocal
from app.security import create_access_token, decode_access_token, hash_password, verify_password
from app import models
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
import logging 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI(
    title = "Project Management API",
    description = "API for managing projects, tasks, and users.",
    version = "0.1.0"
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.1f}ms)")
    return response

@app.exception_handler(IntegrityError)
def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning("A database constraint was violated")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": "A database constraint was violated"},
    )

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db))-> models.User:
    try:
        payload = decode_access_token(token)
    except jwt.PyJWTError:
        logger.warning("Invalid token provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    email: str = payload.get("sub")
    if email is None:
        logger.warning("Token does not contain a valid subject")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        logger.warning(f"User not found for email: {email}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return user
    

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    if user is None or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/")
def read_root():
    return {"message": "Project Management API"}


@app.get("/users/", response_model=list[User])
def get_users(db: Session = Depends(get_db),skip: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100), current_user: models.User = Depends(get_current_user)):
    
    query = db.query(models.User)
    
    return query.offset(skip).limit(limit).all()

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.get(models.User, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users/" , response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(username=user.username, email=user.email, hashed_password=hash_password(user.password))
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists")
    db.refresh(new_user)
    return new_user

@app.delete("/users/{user_id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.projects:
        raise HTTPException(status_code=400, detail="Cannot delete user with associated projects")
    
    db.delete(user)
    db.commit()
    
    return None

@app.patch("/users/{user_id}" , response_model=User)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    db.commit()

    return user

@app.get("/projects/", response_model=list[Project])
def get_projects(owner_id: int |None = None, db: Session = Depends(get_db),skip: int = Query(default=0, ge=0), limit: int = Query(default=100, le=100), current_user: models.User = Depends(get_current_user)):
    
    query = db.query(models.Project)
    
    if owner_id is not None:
        query = query.filter(models.Project.owner_id == owner_id)
        
    return query.offset(skip).limit(limit).all()

@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.get(models.Project, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@app.post("/projects/", status_code=status.HTTP_201_CREATED, response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    owner = db.get(models.User, project.owner_id)

    if owner is None:
        raise HTTPException(status_code=404, detail="No matching user")

    new_project = models.Project(name=project.name, description=project.description, owner_id=project.owner_id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.get(models.Project, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.tasks:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete project with associated tasks")

    db.delete(project)
    db.commit()
    return None

@app.patch("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.get(models.Project, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description
    db.commit()

    return project

@app.get("/tasks/", response_model=list[Task])
def get_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    project_id: int | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Task)

    if status is not None:
        query = query.filter(models.Task.status == status)
    if priority is not None:
        query = query.filter(models.Task.priority == priority)
    if project_id is not None:
        query = query.filter(models.Task.project_id == project_id)

    return query.offset(skip).limit(limit).all()



@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.post("/tasks/", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    project = db.get(models.Project, task.project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="No matching project")

    new_task = models.Task(title=task.title, description=task.description, priority=task.priority, project_id=task.project_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.priority is not None:
        task.priority = task_update.priority
    db.commit()

    return task