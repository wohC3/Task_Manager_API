from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import select
from typing import Annotated


from .database import create_db_and_tables, SessionDep
from .models import Task
from .schemas import TaskCreate, TaskRead, TaskUpdate, TaskDeleteResponse
@asynccontextmanager 
async def lifespan(app: FastAPI):
    create_db_and_tables() 
    yield 

app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return{"message":"Task manager API is running"}

@app.post("/tasks/", response_model = TaskCreate)
def create_task(task_data: TaskCreate, session: SessionDep) -> Task:
    task = Task(**task_data.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/", response_model =list[TaskRead])
def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[TaskRead]:
    tasks = session.exec(select(Task).offset(offset).limit(limit)).all()
    return tasks

@app.get("/tasks/{task_id}",response_model=TaskRead)
def read_task(task_id: int, session:SessionDep) -> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    return task

@app.delete("/tasks/{task_id}", response_model=TaskDeleteResponse)
def delete_task(task_id: int, session:SessionDep):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return TaskDeleteResponse(
        ok=True,
        deleted_id=task_id,
        message="Task deleted successfully"
    )

@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(task_id: int, updated_task: TaskUpdate, session:SessionDep)-> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key,value in updated_task.model_dump(exclude_unset=True).items():
        setattr(task,key,value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

    