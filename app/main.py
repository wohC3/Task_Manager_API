from fastapi import FastAPI, Query, HTTPException
from contextlib import asynccontextmanager
from sqlmodel import select
from typing import Annotated
import logging
from .database import create_db_and_tables, SessionDep
from .models import Task
from .schemas import TaskCreate, TaskRead, TaskUpdate, TaskDeleteResponse
@asynccontextmanager 
async def lifespan(app: FastAPI):
    create_db_and_tables() 
    yield 
logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
tags_metadata = [
    {
        "name": "basic",
        "description": "Create, update, remove, delete operations with tasks",
    },
    {
        "name": "filter",
        "description": "Filter items and pagination",
    },
]
logger = logging.getLogger(__name__)
app = FastAPI(
    description="""
Task Manager API : \n
Task features: \n
-**Add**  \n
-**Remove** \n
-**Update** \n
-**Filter** by completion \n
-Show all tasks \n
""",
    Title = "Task Manager API",
    version = "1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan
    )

@app.get("/")
def root():
    return{"message":"Task manager API is running"}
@app.post("/tasks/", response_model = TaskCreate, tags=["basic"])
def create_task(task_data: TaskCreate, session: SessionDep) -> Task:
    task = Task(**task_data.model_dump())
    try:
        session.add(task)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to create task:{e}")
        session.rollback()
        raise
    session.refresh(task)

    logger.info(f"Task created : id = {task.id}, title = {task.title}")
    return task

@app.get("/tasks/", response_model =list[TaskRead], tags=["filter"])
def read_tasks(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
    completed: bool | None = None
) -> list[TaskRead]:
    query = select(Task).offset(offset).limit(limit)
    if completed is not None:
        query = query.where(Task.completed == completed)
    tasks = session.exec(query).all()
    return tasks

@app.get("/tasks/{task_id}",response_model=TaskRead, tags=["basic"])
def read_task(task_id: int, session:SessionDep) -> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404,detail="task not found")
    return task

@app.delete("/tasks/{task_id}", response_model=TaskDeleteResponse, tags=["basic"])
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

@app.put("/tasks/{task_id}", response_model=TaskRead, tags=["basic"])
def update_task(task_id: int, updated_task: TaskUpdate, session:SessionDep)-> TaskRead:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    updated_data = updated_task.model_dump(exclude_unset=True)
    changed_fields = {}
    for key,value in updated_data.items():
        old_value = getattr(task,key)
        if old_value != value:
            changed_fields[key] = {"old":old_value, "new":value}
            setattr(task,key,value)
    try:
        session.add(task)
        session.commit()
    except Exception as e:
        logger.error(f"Failed to update task:{e}")
        session.rollback()
        raise
    session.refresh(task)
    logger.info(f"Task updated : {changed_fields}")
    return task

    