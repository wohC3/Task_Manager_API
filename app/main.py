from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import select
from typing import Annotated


from .database import create_db_and_tables, SessionDep
from .models import Task
@asynccontextmanager 
async def lifespan(app: FastAPI):
    create_db_and_tables() 
    yield 

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return{"message":"Task manager API is running"}

@app.post("/tasks/")
def create_task(task: Task, session: SessionDep) -> Task:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/")
def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[Task]:
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

@app.get("/tasks/{task_id}")
def read_task(task_id: int, session:SessionDep) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session:SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return{"Ok":True}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task, session:SessionDep)-> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

    