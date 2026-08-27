from fastapi import FastAPI, HTTPException, status
from app.schemas import UserCreate, User, UserUpdate, ProjectCreate, Project, ProjectUpdate, TaskCreate, Task, TaskUpdate, TaskStatus, TaskPriority
from app.database import Base, engine
from app import models
##Almacenamiento temporal de usuarios
users = []
projects = []
tasks = []
user_id_counter = 0
project_id_counter = 0
task_id_counter = 0

app = FastAPI(
    title = "Project Management API",
    description = "API for managing projects, tasks, and users.",
    version = "0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Project Management API"}


@app.get("/users/", response_model=list[User])
def get_users():
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int):
    user = next((u for u in users if u.id == user_id), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

@app.post("/users/" , response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    global user_id_counter
    user_id_counter += 1
    new_user = User(id=user_id_counter, username=user.username, email=user.email)
    users.append(new_user)
    return new_user

@app.delete("/users/{user_id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    user = next((u for u in users if u.id == user_id), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_projects = [p for p in projects if p.owner_id == user_id]
    if user_projects:
        raise HTTPException(status_code=409, detail="User has projects and cannot be deleted")

    users.remove(user)
    return None

@app.patch("/users/{user_id}" , response_model=User)
def update_user(user_id: int, user_update: UserUpdate):
    user = next((u for u in users if u.id == user_id), None)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email

    return user

@app.get("/projects/", response_model=list[Project])
def get_projects():
    return projects

@app.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: int):
    project = next((p for p in projects if p.id == project_id), None)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return project  

@app.post("/projects/", status_code=status.HTTP_201_CREATED, response_model=Project)
def create_project(project: ProjectCreate):
    global project_id_counter
    
    owner = next((u for u in users if u.id == project.owner_id), None)
    
    if owner is None:
        raise HTTPException(status_code=404, detail="No matching user")
    
    project_id_counter += 1        
    new_project = Project(id=project_id_counter,name=project.name, description=project.description, owner_id=project.owner_id)
    projects.append(new_project)
    return new_project

@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int):
    project = next((p for p in projects if p.id == project_id), None)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    projects.remove(project)
    return None

@app.patch("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project_update: ProjectUpdate):
    project = next((p for p in projects if p.id == project_id), None)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    if project_update.name is not None:
        project.name = project_update.name
    if project_update.description is not None:
        project.description = project_update.description

    return project

@app.get("/tasks/", response_model=list[Task])
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = next((t for t in tasks if t.id == task_id), None)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.post("/tasks/", status_code=status.HTTP_201_CREATED, response_model=Task)
def create_task(task: TaskCreate):
    global task_id_counter
    
    project = next((p for p in projects if p.id == task.project_id), None)
    
    if project is None:
        raise HTTPException(status_code=404, detail="No matching project")
    
    task_id_counter += 1
    new_task = Task(id=task_id_counter, title=task.title, description=task.description, status=TaskStatus.TODO, priority=task.priority, project_id=task.project_id)
    tasks.append(new_task)
    return new_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task = next((t for t in tasks if t.id == task_id), None)
    
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found" )
    
    tasks.remove(task)
    return None

@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate):
    task = next((t for t in tasks if t.id == task_id), None)
    
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
            
    return task                 