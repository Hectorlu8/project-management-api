from fastapi import FastAPI

app = FastAPI(
    title = "Project Management API",
    description = "API for managing projects, tasks, and users.",
    version = "0.1.0"
)

@app.get("/")
def read_root():
    return {"message": "Project Management API"}