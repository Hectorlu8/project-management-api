from fastapi import FastAPI, HTTPException, status
from app.schemas import UserCreate, User, UserUpdate, ProjectCreate, Project
##Almacenamiento temporal de usuarios
users = []
projects = []
user_id_counter = 0
project_id_counter = 0

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

    users.remove(user)
    return None

@app.patch("/users/{user_id}" , response_model=User, status_code=status.HTTP_200_OK)
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
    
    owner_id_check = next((u for u in users if u.id == project.owner_id), None)
    
    if owner_id_check is None:
        raise HTTPException(status_code=404, detail="No matching user")
    
    project_id_counter += 1        
    new_project = Project(id=project_id_counter,name=project.name, description=project.description, owner_id=project.owner_id)
    projects.append(new_project)
    return new_project