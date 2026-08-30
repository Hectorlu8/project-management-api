from fastapi import FastAPI, HTTPException, status, Depends
from app.schemas import UserCreate, User, UserUpdate, ProjectCreate, Project, ProjectUpdate, TaskCreate, Task, TaskUpdate
from app.database import SessionLocal
from app import models
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(
    title = "Project Management API",
    description = "API for managing projects, tasks, and users.",
    version = "0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Project Management API"}


@app.get("/users/", response_model=list[User])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

@app.post("/users/" , response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = models.User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.delete("/users/{user_id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.projects:
        raise HTTPException(status_code=400, detail="Cannot delete user with associated projects")
    
    db.delete(user)
    db.commit()
    
    return None

@app.patch("/users/{user_id}" , response_model=User)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
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
def get_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project

@app.post("/projects/", status_code=status.HTTP_201_CREATED, response_model=Project)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    owner = db.get(models.User, project.owner_id)

    if owner is None:
        raise HTTPException(status_code=404, detail="No matching user")

    new_project = models.Project(name=project.name, description=project.description, owner_id=project.owner_id)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.tasks:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot delete project with associated tasks")

    db.delete(project)
    db.commit()
    return None

@app.patch("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project_update: ProjectUpdate, db: Session = Depends(get_db)):
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
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task

@app.post("/tasks/", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    project = db.get(models.Project, task.project_id)

    if project is None:
        raise HTTPException(status_code=404, detail="No matching project")

    new_task = models.Task(title=task.title, description=task.description, priority=task.priority, project_id=task.project_id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(models.Task, task_id)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return None

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
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